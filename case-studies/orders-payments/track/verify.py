#!/usr/bin/env python3
"""Independent learner-policy evaluator; real durable and HTTP recovery boundaries."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback

TRACK = Path(__file__).resolve().parent
CASE = TRACK.parent
VARIANTS = {"java-composition": "Java composition", "java-inheritance": "Java inheritance", "rust": "Rust composition"}
FIELDS = "exercise phase state total payment_id last_result pending_outbox requested_payment_id unit quantity lookup".split()
EXERCISES = [f"e{i}" for i in range(1, 7)]
EVIDENCE = {"status": "RUNNING", "variants": {}, "errors": []}


class Behavior(AssertionError):
    pass


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command(source, variant):
    if variant == "rust":
        return [str(TRACK / "rust" / source / "target/debug" / ("roo-track-" + source))]
    return ["java", "-cp", str(TRACK / "java/build" / source / "classes"), "roo.payments.TrackMain"]


def invoke(cmd, *args):
    return subprocess.run([*cmd, *args], capture_output=True, text=True, timeout=45,
                          env={k: v for k, v in os.environ.items() if not k.upper().startswith("PG")})


def valid_action(action):
    identity = r"[A-Za-z0-9]{1,64}"
    number = r"-?[0-9]+"
    if action in ("inspect", "stop", "relay:ok", "reconcile:ok:none", "reconcile:unavailable:none"):
        return True
    if re.fullmatch(r"pay:" + identity + r":approve:none", action):
        return True
    if re.fullmatch(r"add:" + number + ":" + number, action):
        return all(-(2**63) <= int(x) < 2**63 for x in action.split(":")[1:])
    return False


def policy(cmd, args, transcript):
    result = invoke(cmd, "policy", *args)
    if result.returncode != 0:
        raise RuntimeError(f"Policy process failed ({result.returncode}): {result.stderr.strip()}")
    action = result.stdout.removesuffix("\n")
    if result.stdout != action + "\n" or "\n" in action or not valid_action(action):
        raise RuntimeError("Policy returned invalid action protocol")
    transcript.append({"observation": dict(zip(FIELDS, args)), "action": action})
    return action


def observed(cmd, exercise, phase, row, transcript, requested="p1", unit="50", quantity="1", lookup="ok"):
    return policy(cmd, [exercise, phase, row["state"], row["total"], row["payment_id"],
                        row["last_result"], row["pending_outbox"], requested, unit, quantity, lookup], transcript)


def expect_action(action, expected, exercise):
    if action != expected:
        raise Behavior(f"BEHAVIOR {exercise}: expected action {expected}, observed {action}")


def negative_control(action, expected, exercise):
    try:
        expect_action(action, expected, exercise)
    except Behavior as failure:
        if not str(failure).startswith(f"BEHAVIOR {exercise}:"):
            raise AssertionError("Negative control lacks specific behavioral diagnosis")
        return {"injected_action": action, "required_action": expected, "rejected": True, "diagnostic": str(failure)}
    raise AssertionError("Boundary negative control unexpectedly accepted")


def inputs():
    with (TRACK / "policy-cases.tsv").open() as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != ["case_id", *FIELDS, "expected_action"]:
            raise ValueError("Independent policy oracle header mismatch")
        rows = list(reader)
    if not rows or len({r["case_id"] for r in rows}) != len(rows):
        raise ValueError("Independent oracle is empty or has duplicate cases")
    if any(set(r) != {"case_id", *FIELDS, "expected_action"} or None in r.values() for r in rows):
        raise ValueError("Malformed independent oracle row")
    malformed = json.loads((TRACK / "malformed-cases.json").read_text())
    if not isinstance(malformed, list) or not malformed:
        raise ValueError("Malformed-input oracle must be a nonempty list")
    return rows, malformed


def malformed_check(cmd, cases):
    for case in cases:
        result = invoke(cmd, "policy", *case["args"])
        if result.returncode != 2 or result.stdout or not result.stderr.strip():
            raise RuntimeError(f"Malformed input {case['case_id']} was not rejected with exit 2 and empty stdout")


def native(cmd, exercise, variant):
    result = invoke(cmd, "native", exercise, "composition" if variant != "java-inheritance" else "inheritance")
    if result.returncode == 1 and result.stderr.startswith(f"BEHAVIOR {exercise}:"):
        raise Behavior(result.stderr.strip())
    if result.returncode or not result.stdout.startswith("PASS"):
        raise RuntimeError(f"Native {exercise} failed outside behavioral contract: {result.returncode} {result.stderr.strip()}")
    return result.stdout.strip()


def pg_runner(pg, variant):
    name = VARIANTS[variant]
    if variant == "rust":
        cmd = [str(CASE / "postgres/rust/target/debug/roo-postgres")]
    else:
        entry = "CompositionRunner" if variant == "java-composition" else "TemplateRunner"
        cp = os.pathsep.join([str(CASE / "postgres/java/build/classes"), str(CASE / "postgres/.deps/postgresql-42.7.14.jar")])
        cmd = ["java", "-cp", cp, "roo.postgres." + entry]
    runner = pg.Runner(name, cmd)
    runner.env = {**pg.cluster.utility_environment(), **pg.cluster.environment()}
    for name in ("ROO_GATE_POINT", "ROO_GATE_LOCK", "ROO_WORKER_ID", "ROO_RUN_ID"):
        runner.env.pop(name, None)
    return runner


def prepare_e5(pg, variant, cmd, record):
    runner = pg_runner(pg, variant)
    scope = pg.race(runner, "track_pay_before_add", "Draft", "pay:p1:approve:none", "add:50:1",
                    "inside_prepare", "Approved", "InvalidState")
    pg.state(runner, scope, "Paid")
    amount = pg.cluster.sql(f"SELECT amount FROM roo_provider.records WHERE scope='{scope}'").strip()
    if amount != "250":
        raise AssertionError("Pay-before-add provider amount differs from locked order total")
    record["row_lock_scope"] = scope
    retained = runner.seed("track_effect")
    worker = None
    try:
        with pg.Barrier() as barrier:
            worker, identity = runner.spawn(retained, "pay:p1:approve:none", point="after_effect", key=barrier.key)
            pg.witnessed(identity, "after_effect", worker)
            pg.kill(worker)
        before = pg.state(runner, retained, "Pending", events=0)
        action = observed(cmd, "e5", "uncertain_commit", before, record["transcript"])
        expect_action(action, "inspect", "e5")
        # Inspection is a separate fresh process, never learner-provided state.
        if runner.row("snapshot", retained) != before:
            raise AssertionError("Inspection changed retained Pending snapshot")
        record.update(scope=retained, before_restart=before, kill="SIGKILL", gate="after_effect")
        return runner, retained, before, cmd, record
    finally:
        if worker is not None and worker.poll() is None:
            pg.kill(worker)


def restart_e5(pg, retained):
    cluster = pg.cluster
    before = cluster.sql("SELECT pg_postmaster_start_time()").strip()
    offset = (cluster.RUNTIME / "server.log").stat().st_size
    cluster.stop("immediate")
    cluster.start()
    after = cluster.sql("SELECT pg_postmaster_start_time()").strip()
    with (cluster.RUNTIME / "server.log").open("rb") as stream:
        stream.seek(offset)
        lines = stream.read().decode(errors="replace").splitlines()
    wal = [line for line in lines if any(word in line for word in ("redo", "interrupted", "not properly shut down", "ready to accept"))]
    if before == after or not any("redo" in line for line in wal):
        raise AssertionError("Immediate restart lacks changed start time or WAL redo")
    EVIDENCE["restart"] = {"before": before, "after": after, "mode": "immediate", "wal": wal, "scopes": len(retained)}
    for runner, scope, snapshot, cmd, record in retained:
        fresh = runner.row("snapshot", scope)
        if fresh != snapshot:
            raise AssertionError("Normalized retained snapshot differs after restart")
        record["after_restart"] = fresh
        record["negative_controls"] = [
            negative_control("pay:pNEW:approve:none", "inspect", "e5"),
            negative_control("stop", "reconcile:ok:none", "e5")]
        action = observed(cmd, "e5", "recover", fresh, record["transcript"])
        expect_action(action, "reconcile:ok:none", "e5")
        runner.step(scope, action, "Approved")
        record["final"] = pg.state(runner, scope, "Paid")
        record["status"] = "PASS"


def lost_response(future):
    try:
        future.result(timeout=15)
    except (http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError) as error:
        return type(error).__name__
    raise AssertionError("Killed server did not produce connection loss before response headers")


def e6(http, variant, cmd, record):
    server = http.Server(VARIANTS[variant])
    try:
        for kind, action, phase in (("payment", "pay:p1:approve:none", "payment_response_lost"),
                                    ("line", "add:50:1", "line_response_lost")):
            scope = server.seed("track_lost_" + kind)
            gated = fresh = None
            try:
                with http.pg_verify.Barrier() as barrier:
                    gated = http.Server(VARIANTS[variant], http_key=barrier.key)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(gated.step, scope, action)
                        http.pg_verify.witnessed(gated.worker, "http_after_snapshot", gated.process)
                        gated.stop(crash=True)
                        loss = lost_response(future)
                fresh = http.Server(VARIANTS[variant])
                snapshot = http.state(fresh, scope, "Paid") if kind == "payment" else http.state(fresh, scope, "Draft", total=300, charges=0, events=0, payment="-")
                selected = observed(cmd, "e6", phase, snapshot, record["transcript"], requested="pNEW")
                if kind == "payment":
                    # A different caller key cannot replace a persisted intent.
                    expect_action(selected, "pay:p1:approve:none", "e6")
                    fresh.step(scope, selected, "AlreadyApplied")
                    final = http.state(fresh, scope, "Paid")
                    fresh.step(scope, "pay:pNEW:approve:none", "IntentConflict")
                    if fresh.get(scope) != final:
                        raise AssertionError("Changed-key negative control mutated committed payment")
                else:
                    expect_action(selected, "inspect", "e6")
                    inspected = fresh.get(scope)
                    selected = observed(cmd, "e6", "line_inspected", inspected, record["transcript"])
                    expect_action(selected, "stop", "e6")
                    if fresh.get(scope) != snapshot:
                        raise AssertionError("Line recovery automatically replayed a non-idempotent addition")
                    record["automatic_line_posts"] = 0
                    # Explicit second caller action demonstrates absence of a line receipt.
                    fresh.step(scope, "add:50:1", "Added")
                    final = http.state(fresh, scope, "Draft", total=350, charges=0, events=0, payment="-")
                record[kind] = {"scope": scope, "client_exception": loss, "fresh_get": snapshot, "final": final,
                                "gate": "http_after_snapshot", "signal": "SIGKILL"}
            finally:
                if gated is not None: gated.stop()
                if fresh is not None: fresh.stop()
        scope = server.seed("track_202")
        server.step(scope, "pay:p202:timeout_after:none", "Unknown")
        pending = http.state(server, scope, "Pending", events=0, payment="p202")
        # GET is observational: HTTP 202 schedules no hidden reconciliation.
        if server.get(scope) != pending:
            raise AssertionError("202 unexpectedly started recovery work")
        # This supplementary caller action demonstrates 202 recovery without
        # requiring the learner to implement another exercise's policy.
        selected = "reconcile:ok:none"
        server.step(scope, selected, "Approved")
        record["explicit_202_reconcile"] = {
            "origin": "explicit harness/caller action, outside learner policy",
            "before": pending, "action": selected, "result": "Approved",
            "final": http.state(server, scope, "Paid", payment="p202")}
        if any(item["observation"]["exercise"] != "e6" for item in record["transcript"]):
            raise AssertionError("e6 invoked another exercise's learner policy")
        record["negative_controls"] = [
            {"changed_payment_key": "pNEW", "domain_result": "IntentConflict", "unchanged_snapshot": True},
            negative_control("add:50:1", "inspect", "e6"),
            negative_control("add:50:1", "stop", "e6")]
        record["status"] = "PASS"
    finally:
        server.stop()


def source_hashes():
    files = list(TRACK.glob("java/**/*.java")) + list(TRACK.glob("rust/*/src/**/*.rs")) + list(TRACK.glob("rust/*.rs"))
    files += list(TRACK.glob("rust/*/Cargo.toml")) + [TRACK / "build.sh", TRACK / "verify.sh", TRACK / "check_independence.py"]
    files += [TRACK / "SPEC.md", TRACK / "policy-cases.tsv", TRACK / "malformed-cases.json", Path(__file__)]
    return {str(path.relative_to(TRACK)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("starter", "solution"), default="starter")
    parser.add_argument("--exercise", choices=(*EXERCISES, "all"), default="all")
    parser.add_argument("--variant", choices=(*VARIANTS, "all"), default="all")
    parser.add_argument("--expect-incomplete", action="store_true")
    options = parser.parse_args()
    if options.expect_incomplete and options.source != "starter":
        parser.error("--expect-incomplete is only valid for starter")
    variants = list(VARIANTS) if options.variant == "all" else [options.variant]
    exercises = EXERCISES if options.exercise == "all" else [options.exercise]
    EVIDENCE.update(source=options.source, selected_exercises=exercises, source_hashes=source_hashes())
    rows, malformed = inputs()
    qualified = []
    failures = []
    # All protocol/malformed validation precedes any database ownership or RED claim.
    for variant in variants:
        cmd = command(options.source, variant)
        malformed_check(cmd, malformed)
        counts = EVIDENCE.setdefault("qualification_counts", {})[variant] = {
            "malformed_rejections": len(malformed), "policy_cases": 0, "native_passes": 0}
        records = EVIDENCE["variants"][variant] = {}
        for exercise in exercises:
            record = records[exercise] = {"transcript": [], "cases": [], "status": "RUNNING"}
            mismatches = []
            selected = [row for row in rows if row["exercise"] == exercise]
            if not selected:
                raise ValueError(f"Independent oracle has no {exercise} cases")
            for row in selected:
                action = policy(cmd, [row[field] for field in FIELDS], record["transcript"])
                record["cases"].append(row["case_id"])
                counts["policy_cases"] += 1
                if action != row["expected_action"]:
                    mismatches.append(f"{row['case_id']}: expected {row['expected_action']}, observed {action}")
            try:
                if exercise in EXERCISES[:4]:
                    record["native"] = native(cmd, exercise, variant)
                    counts["native_passes"] += 1
                if mismatches:
                    raise Behavior(f"BEHAVIOR {exercise}: " + mismatches[0])
                qualified.append((variant, exercise, cmd, record))
            except Behavior as failure:
                record.update(status="RED", failure=str(failure))
                failures.append((variant, exercise))
                print(f"RED {variant} {failure}", flush=True)
    if failures and not options.expect_incomplete:
        raise Behavior(f"{len(failures)} exercise groups failed")
    if options.expect_incomplete:
        if len(failures) != len(variants) * len(exercises):
            raise AssertionError("Starter must independently fail every selected exercise group")
        EVIDENCE["status"] = "EXPECTED_INCOMPLETE"
        return
    boundary = [item for item in qualified if item[1] in ("e5", "e6")]
    if boundary:
        sys.path.insert(0, str(CASE / "postgres"))
        http = load("roo_track_http_support", CASE / "http/support.py")
        pg, cluster = http.pg_verify, http.cluster
        if cluster.CONFIG.exists() and cluster.running(cluster.configuration()):
            raise RuntimeError("Refusing an already running cluster; lifecycle ownership is required")
        owned = False
        try:
            # Set ownership before start so partial startup is also cleaned up.
            owned = True
            cluster.start()
            cluster.apply_schema()
            retained = [prepare_e5(pg, variant, cmd, record) for variant, ex, cmd, record in boundary if ex == "e5"]
            if retained:
                restart_e5(pg, retained)
            for variant, exercise, cmd, record in boundary:
                if exercise == "e6":
                    e6(http, variant, cmd, record)
            EVIDENCE["barriers"] = pg.EVIDENCE["barriers"]
        finally:
            try:
                http.cleanup()
            finally:
                if owned and cluster.CONFIG.exists():
                    cluster.stop()
            EVIDENCE["all_http_processes_stopped"] = all(s.process.poll() is not None for s in http.PROCESSES)
    for variant, exercise, _, record in qualified:
        record["status"] = "PASS"
        print(f"PASS {variant} {exercise}", flush=True)
    EVIDENCE["status"] = "PASS"


if __name__ == "__main__":
    code = 0
    try:
        main()
    except Exception as error:
        code = 1
        EVIDENCE["status"] = "FAIL"
        EVIDENCE["errors"].append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
        print(f"FAIL {type(error).__name__}: {error}", file=sys.stderr)
    finally:
        runtime = TRACK / ".runtime"
        runtime.mkdir(exist_ok=True)
        (runtime / "last-run.json").write_text(json.dumps(EVIDENCE, indent=2) + "\n")
    sys.exit(code)
