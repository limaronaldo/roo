#!/usr/bin/env python3
"""Run one independent oracle against three real PostgreSQL implementations.

Only cluster.py's marked, synthetic, loopback cluster is permitted. Processes
are interrupted at observed database barriers; elapsed sleeps are not evidence.
"""

import argparse
import csv
import io
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time
import uuid

import cluster

CASE = Path(__file__).resolve().parent
# Ordinary runs keep refreshing the tracked historical receipt. Isolated
# verification redirects it with --evidence-output or this environment variable.
EVIDENCE_ENV = "ROO_EVIDENCE_PATH"
HISTORICAL_EVIDENCE = CASE.parents[2] / "research/postgres-integration-evidence.json"
HEADER = "scenario state total charge_count refund_count event_count consumer_count pending_outbox last_result payment_id refund_id".split()
RUN = "pg_" + uuid.uuid4().hex[:12]
EVIDENCE = {"run_id": RUN, "variants": {}, "barriers": [], "restart": {}, "constraints": []}
COUNTER = 0


def unique(label):
    global COUNTER
    COUNTER += 1
    return f"{RUN}_{label}_{COUNTER}"


def table(text):
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    if not rows or rows[0] != HEADER or any(len(row) != len(HEADER) for row in rows[1:]):
        raise AssertionError("Incorrect normalized output")
    if len({row[0] for row in rows[1:]}) != len(rows) - 1:
        raise AssertionError("Duplicate output scope")
    return [dict(zip(HEADER, row)) for row in rows[1:]]


class Runner:
    def __init__(self, name, command):
        self.name, self.command = name, command
        self.env = {**os.environ, **cluster.environment()}
        for key in ("ROO_GATE_POINT", "ROO_GATE_LOCK", "ROO_WORKER_ID", "ROO_RUN_ID"):
            self.env.pop(key, None)
        EVIDENCE["variants"][name] = {"oracle_rows": 0, "malformed_fixtures": 0,
                                     "persistent_guards": [], "concurrency": [],
                                     "process_crashes": [], "restart_scopes": []}

    def call(self, *args, extra=None, success=True):
        result = subprocess.run([*self.command, *args], env={**self.env, **(extra or {})},
                                capture_output=True, text=True, timeout=45)
        if success and result.returncode:
            raise AssertionError(f"{self.name} {args[:2]}: {result.stderr.strip()}")
        return result

    def row(self, *args):
        rows = table(self.call(*args).stdout)
        if len(rows) != 1:
            raise AssertionError("Persistent command must return one row")
        return rows[0]

    def step(self, scope, action, outcome=None):
        row = self.row("step", scope, action)
        if outcome is not None:
            require(row, last_result=outcome)
        return row

    def seed(self, label, state="Draft"):
        scope = unique(label)
        self.row("init", scope)
        self.step(scope, "add:250:1", "Added")
        if state in ("Paid", "Refunded"):
            self.step(scope, "pay:p1:approve:none", "Approved")
        if state == "Refunded":
            self.step(scope, "refund:r1:approve:none", "Approved")
        return scope

    def spawn(self, scope, action, *, point=None, key=None):
        worker = unique("w")[-32:]
        env = {**self.env, "ROO_WORKER_ID": worker}
        if point:
            env.update(ROO_GATE_POINT=point, ROO_GATE_LOCK=str(key))
        process = subprocess.Popen([*self.command, "step", scope, action], env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return process, worker


def require(row, **expected):
    for key, value in expected.items():
        if row[key] != str(value):
            raise AssertionError(f"{row['scenario']} {key}: expected {value}, observed {row[key]}")


def state(runner, scope, name, total=250, charges=1, refunds=0, events=1,
          consumers=0, pending=None, payment="p1", refund="-"):
    row = runner.row("snapshot", scope)
    require(row, state=name, total=total, charge_count=charges, refund_count=refunds,
            event_count=events, consumer_count=consumers,
            pending_outbox=events if pending is None else pending,
            payment_id=payment, refund_id=refund, last_result="-")
    return row


def psql_command():
    c = cluster.configuration()
    return [str(Path(c["bindir"]) / "psql"), "-XAtq", "-v", "ON_ERROR_STOP=1",
            "-h", c["host"], "-p", str(c["port"]), "-U", c["user"], "-d", c["database"]]


class Barrier:
    """Retain a PostgreSQL session lock until workers are witnessed or killed."""
    def __init__(self):
        self.key = 100000 + uuid.uuid4().int % (2**62)
        self.process = None

    def __enter__(self):
        self.process = subprocess.Popen(psql_command(), stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env=cluster.utility_environment(), text=True)
        self.process.stdin.write(cluster.endpoint_guard() + f"SELECT pg_advisory_lock({self.key});\n\\echo ROO_READY\n")
        self.process.stdin.flush()
        # psql emits an empty result line before the marker. Read one character
        # at a time on the descriptor to avoid TextIO buffering hiding the marker.
        selector = selectors.DefaultSelector()
        selector.register(self.process.stdout, selectors.EVENT_READ)
        received = b""
        deadline = time.monotonic() + 10
        try:
            while b"ROO_READY\n" not in received:
                if time.monotonic() >= deadline or self.process.poll() is not None:
                    raise AssertionError("Barrier controller did not acquire its lock")
                if selector.select(timeout=0.1):
                    chunk = os.read(self.process.stdout.fileno(), 4096)
                    if not chunk:
                        raise AssertionError("Barrier controller closed unexpectedly")
                    received += chunk
        except BaseException:
            self.close()
            raise
        finally:
            selector.close()
        return self

    def close(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(f"SELECT pg_advisory_unlock({self.key});\n")
                self.process.stdin.flush()
                self.process.communicate(timeout=10)
            finally:
                if self.process.poll() is None:
                    self.process.kill()
                    self.process.communicate(timeout=5)

    def __exit__(self, *_):
        self.close()


def witnessed(worker, point=None, process=None):
    deadline = time.monotonic() + 12
    application = f"roo:{worker}:{point}" if point else f"roo:{worker}"
    predicate = f"application_name = '{application}'" if point else (
        f"(application_name = '{application}' OR application_name LIKE '{application}:%')")
    while time.monotonic() < deadline:
        query = ("SELECT application_name,wait_event_type,wait_event FROM pg_stat_activity "
                 f"WHERE {predicate} AND wait_event_type='Lock'"
                 + (" AND wait_event='advisory'" if point else ""))
        observed = cluster.sql(query).strip()
        if observed:
            EVIDENCE["barriers"].append({"worker": worker, "phase": point or "contender_row_lock",
                                         "observation": observed})
            return
        if process is not None and process.poll() is not None:
            out, err = process.communicate()
            raise AssertionError(f"Worker ended before barrier: {out} {err}")
        time.sleep(0.02)
    raise AssertionError(f"No database lock witness for {application}")


def finished(process, outcome):
    out, err = process.communicate(timeout=45)
    if process.returncode:
        raise AssertionError(f"Concurrent worker failed: {err.strip()}")
    rows = table(out)
    if len(rows) != 1:
        raise AssertionError("Worker returned incorrect row count")
    require(rows[0], last_result=outcome)


def kill(process):
    process.kill()
    process.communicate(timeout=10)
    if process.returncode != -9:
        raise AssertionError("Expected SIGKILL termination")


def race(runner, label, seed_state, first, second, point, first_result, second_result,
         *, row_wait=True):
    scope = runner.seed(label, seed_state)
    processes = []
    try:
        with Barrier() as barrier:
            a, aw = runner.spawn(scope, first, point=point, key=barrier.key)
            processes.append(a)
            witnessed(aw, point, a)
            b, bw = runner.spawn(scope, second)
            processes.append(b)
            if row_wait:
                witnessed(bw, process=b)
            else:
                finished(b, second_result)
            barrier.close()
            finished(a, first_result)
            if row_wait:
                finished(b, second_result)
    finally:
        for process in processes:
            if process.poll() is None:
                kill(process)
    EVIDENCE["variants"][runner.name]["concurrency"].append(label)
    return scope


def concurrency(r):
    s = race(r, "different_payment_keys", "Draft", "pay:p1:approve:none", "pay:p2:approve:none",
             "inside_prepare", "Approved", "IntentConflict")
    state(r, s, "Paid")
    s = race(r, "same_payment_key", "Draft", "pay:p1:approve:none", "pay:p1:approve:none",
             "after_effect", "AlreadyApplied", "Approved", row_wait=False)
    state(r, s, "Paid")
    s = race(r, "different_refund_keys", "Paid", "refund:r1:approve:none", "refund:r2:approve:none",
             "inside_prepare", "Approved", "IntentConflict")
    state(r, s, "Refunded", refunds=1, events=2, refund="r1")
    s = race(r, "add_before_pay", "Draft", "add:50:1", "pay:p1:approve:none",
             "inside_prepare", "Added", "Approved")
    state(r, s, "Paid", total=300)
    if cluster.sql(f"SELECT amount FROM roo_provider.records WHERE scope='{s}'").strip() != "300":
        raise AssertionError("Provider amount did not include the committed concurrent line")
    s = race(r, "pay_before_add", "Draft", "pay:p1:approve:none", "add:50:1",
             "inside_prepare", "Approved", "InvalidState")
    state(r, s, "Paid")
    s = race(r, "concurrent_relays", "Refunded", "relay:ok", "relay:ok",
             "after_delivery", "RelayOk", "RelayOk")
    state(r, s, "Refunded", refunds=1, events=2, consumers=2, pending=0, refund="r1")
    s = race(r, "same_refund_key", "Paid", "refund:r1:approve:none", "refund:r1:approve:none",
             "after_effect", "AlreadyApplied", "Approved", row_wait=False)
    state(r, s, "Refunded", refunds=1, events=2, refund="r1")


def crashed(r, label, seed_state, action, point, expected, recovery):
    s = r.seed(label, seed_state)
    process = None
    try:
        with Barrier() as barrier:
            process, worker = r.spawn(s, action, point=point, key=barrier.key)
            witnessed(worker, point, process)
            kill(process)
        state(r, s, **expected)
        recovery(r, s)
    finally:
        if process is not None and process.poll() is None:
            kill(process)
    EVIDENCE["variants"][r.name]["process_crashes"].append({"case": label, "signal": "SIGKILL", "phase": point})


def process_crashes(r):
    def prepared(r, s):
        r.step(s, "reconcile:ok:none", "NotFound")
        r.step(s, "pay:p1:approve:none", "Approved")
        state(r, s, "Paid")
    def effect(r, s):
        r.step(s, "reconcile:ok:none", "Approved")
        state(r, s, "Paid")
    def finalized(r, s):
        r.step(s, "pay:p1:approve:none", "AlreadyApplied")
        r.step(s, "relay:ok", "RelayOk")
        state(r, s, "Paid", consumers=1, pending=0)
    def delivery(r, s):
        r.step(s, "relay:ok", "RelayOk")
        state(r, s, "Refunded", refunds=1, events=2, consumers=2, pending=0, refund="r1")
    def refund(r, s):
        r.step(s, "reconcile:ok:none", "Approved")
        state(r, s, "Refunded", refunds=1, events=2, refund="r1")
    crashed(r, "kill_after_prepare", "Draft", "pay:p1:approve:none", "after_prepare",
            dict(name="Pending", charges=0, events=0), prepared)
    crashed(r, "kill_after_effect", "Draft", "pay:p1:approve:none", "after_effect",
            dict(name="Pending", events=0), effect)
    crashed(r, "kill_after_finalize", "Draft", "pay:p1:approve:none", "after_finalize",
            dict(name="Paid"), finalized)
    crashed(r, "kill_after_delivery", "Refunded", "relay:ok", "after_delivery",
            dict(name="Refunded", refunds=1, events=2, consumers=1, refund="r1"), delivery)
    crashed(r, "kill_after_refund_effect", "Paid", "refund:r1:approve:none", "after_effect",
            dict(name="Refunding", refunds=1, events=1, refund="r1"), refund)


def fixtures(r):
    expected = table((CASE.parent / "expected.tsv").read_text())
    result = r.call("fixtures", str(CASE.parent / "scenarios.tsv"), extra={"ROO_RUN_ID": unique("f")})
    actual = table(result.stdout)
    if actual != expected:
        for index in range(max(len(actual), len(expected))):
            a = actual[index] if index < len(actual) else "missing"
            e = expected[index] if index < len(expected) else "extra"
            if a != e:
                raise AssertionError(f"{r.name} oracle row {index+1}: expected {e}, observed {a}")
    invalid = {
        "wrong_header": "scenario\tactions\nx\tadd:1:1\n",
        "duplicate_id": "scenario\tsteps\nx\tadd:1:1\nx\trelay:ok\n",
        "unknown_action": "scenario\tsteps\nx\tcharge:p1\n",
        "wrong_arity": "scenario\tsteps\nx\tadd:100\n",
        "bad_number": "scenario\tsteps\nx\tadd:one:1\n",
        "bad_mode": "scenario\tsteps\nx\tpay:p1:random:none\n",
        "empty_action": "scenario\tsteps\nx\tadd:1:1;\n",
        "extra_column": "scenario\tsteps\nx\tadd:1:1\textra\n",
        "invalid_identity": "scenario\tsteps\nx\tpay:bad-id:approve:none\n",
        "bad_late_action": "scenario\tsteps\nx\tadd:1:1;unknown\n",
    }
    with tempfile.TemporaryDirectory(prefix="roo-pg-fixtures-") as directory:
        for label, content in invalid.items():
            path = Path(directory) / f"{label}.tsv"
            path.write_text(content)
            prefix = unique("bad")
            rejected = r.call("fixtures", str(path), extra={"ROO_RUN_ID": prefix}, success=False)
            if not rejected.returncode or not rejected.stderr.strip():
                raise AssertionError(f"{r.name} accepted malformed fixture {label}")
            if cluster.sql(f"SELECT count(*) FROM roo_app.orders WHERE scope LIKE '{prefix}_%'").strip() != "0":
                raise AssertionError("Malformed fixture mutated the database before validation")
    EVIDENCE["variants"][r.name].update(oracle_rows=len(expected), malformed_fixtures=len(invalid))


def persistent_guards(r):
    # A collision in the second fixture must roll back the first reservation;
    # the existing scope and its data must remain unchanged.
    prefix = unique("atomic")
    existing = prefix + "_z"
    r.row("init", existing)
    r.step(existing, "add:23:1", "Added")
    before = r.row("snapshot", existing)
    with tempfile.TemporaryDirectory(prefix="roo-pg-atomic-") as directory:
        path = Path(directory) / "collision.tsv"
        path.write_text("scenario\tsteps\na\tadd:7:1\nz\tadd:9:1\n")
        rejected = r.call("fixtures", str(path), extra={"ROO_RUN_ID": prefix}, success=False)
    if not rejected.returncode or not rejected.stderr.strip():
        raise AssertionError("Existing fixture scope was accepted")
    if cluster.sql(f"SELECT count(*) FROM roo_app.orders WHERE scope='{prefix}_a'").strip() != "0":
        raise AssertionError("Fixture scope reservation was not atomic")
    if r.row("snapshot", existing) != before:
        raise AssertionError("Fixture rejection changed existing data")
    r.row("init", existing)
    if r.row("snapshot", existing) != before:
        raise AssertionError("Idempotent init reset existing data")
    invalid = r.call("step", existing, "add:1:1", extra={"ROO_PG_HOST": "192.0.2.1"}, success=False)
    if not invalid.returncode or not invalid.stderr.strip() or r.row("snapshot", existing) != before:
        raise AssertionError("Non-loopback configuration was not rejected before mutation")
    EVIDENCE["variants"][r.name]["persistent_guards"] = [
        "atomic_fixture_reservation", "init_preserves_existing_data", "reject_non_loopback_configuration"]


def restart(runners):
    durable = []
    for r in runners:
        pending = r.seed("restart_pending")
        r.step(pending, "pay:p1:timeout_after:none", "Unknown")
        refunding = r.seed("restart_refunding", "Paid")
        r.step(refunding, "refund:r1:timeout_after:none", "Unknown")
        inbox = r.seed("restart_inbox", "Refunded")
        r.step(inbox, "relay:ack_fail", "RelayAckFailed")
        paid = r.seed("restart_paid", "Paid")
        for kind, scope in (("pending", pending), ("refunding", refunding), ("inbox", inbox), ("paid", paid)):
            durable.append((r, kind, scope, r.row("snapshot", scope)))
    before = cluster.sql("SELECT pg_postmaster_start_time(), current_setting('server_version_num'), current_setting('fsync'), current_setting('synchronous_commit'), current_setting('full_page_writes')").strip()
    log_position = (cluster.RUNTIME / "server.log").stat().st_size
    cluster.stop("immediate")
    cluster.start()
    after = cluster.sql("SELECT pg_postmaster_start_time(), current_setting('server_version_num'), current_setting('fsync'), current_setting('synchronous_commit'), current_setting('full_page_writes')").strip()
    if before.split("|")[0] == after.split("|")[0]:
        raise AssertionError("PostgreSQL postmaster did not restart")
    with (cluster.RUNTIME / "server.log").open("rb") as log:
        log.seek(log_position)
        lines = log.read().decode(errors="replace").splitlines()
    recovery = [line for line in lines if any(s in line for s in ("interrupted", "redo starts", "redo done", "not properly shut down", "ready to accept"))]
    if not any("redo" in line for line in recovery):
        raise AssertionError("No WAL redo evidence after immediate server shutdown")
    EVIDENCE["restart"] = {"mode": "immediate", "before": before, "after": after, "wal_recovery_log": recovery, "preserved_scopes": len(durable)}
    for r, kind, scope, before_row in durable:
        if r.row("snapshot", scope) != before_row:
            raise AssertionError(f"Durable snapshot changed after restart: {kind}")
        if kind == "pending":
            r.step(scope, "reconcile:ok:none", "Approved")
            state(r, scope, "Paid")
        elif kind == "refunding":
            r.step(scope, "reconcile:ok:none", "Approved")
            state(r, scope, "Refunded", refunds=1, events=2, refund="r1")
        elif kind == "inbox":
            r.step(scope, "relay:ok", "RelayOk")
            state(r, scope, "Refunded", refunds=1, events=2, consumers=2, pending=0, refund="r1")
        else:
            r.step(scope, "pay:p1:approve:none", "AlreadyApplied")
            r.step(scope, "relay:ok", "RelayOk")
            state(r, scope, "Paid", consumers=1, pending=0)
        EVIDENCE["variants"][r.name]["restart_scopes"].append(kind)


def constraints():
    s = unique("constraint")
    cluster.sql(f"INSERT INTO roo_app.orders(scope) VALUES('{s}')")
    probes = {
        "positive_quantity": (f"INSERT INTO roo_app.lines VALUES('{s}',1,10,0)", "23514"),
        "checked_product": (f"INSERT INTO roo_app.lines VALUES('{s}',1,9223372036854775807,2)", "23514"),
        "intent_shape": (f"UPDATE roo_app.orders SET state='Pending',total=10 WHERE scope='{s}'", "23514"),
        "stable_event_identity": (f"INSERT INTO roo_app.outbox(scope,event_id,event_kind,order_id,currency,payment_id,amount) VALUES('{s}','payment:p1','PaymentApproved','O1','USD','p1',10); INSERT INTO roo_app.outbox(scope,event_id,event_kind,order_id,currency,payment_id,amount) VALUES('{s}','payment:p1','PaymentApproved','O1','USD','p1',10)", "23505"),
        "one_full_refund": (f"INSERT INTO roo_provider.records VALUES('{s}','refund','r1','O1','USD',10,'p1','Approved'); INSERT INTO roo_provider.records VALUES('{s}','refund','r2','O1','USD',10,'p1','Approved')", "23505"),
    }
    for name, (query, code) in probes.items():
        result = subprocess.run([*psql_command(), "-v", "VERBOSITY=verbose", "-c", cluster.endpoint_guard() + f"BEGIN; {query}; ROLLBACK;"], env=cluster.utility_environment(), capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or code not in result.stderr:
            raise AssertionError(f"Database constraint {name} did not reject with {code}")
        EVIDENCE["constraints"].append({"case": name, "sqlstate": code})


def evidence_destination(cli_path=None, environ=os.environ):
    """Pick the receipt path: flag, then ROO_EVIDENCE_PATH, then the historical file."""
    chosen = cli_path if cli_path is not None else (environ.get(EVIDENCE_ENV) or None)
    destination = Path(chosen) if chosen else HISTORICAL_EVIDENCE
    if destination.is_dir() or not destination.parent.is_dir():
        raise ValueError(f"Evidence output must be a file in an existing directory: {destination}")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-output",
        type=Path,
        help=f"write evidence here (overrides {EVIDENCE_ENV} and the historical default)",
    )
    # Resolve before the long run so a bad destination fails fast.
    output = evidence_destination(parser.parse_args().evidence_output)
    if not cluster.running(cluster.configuration()):
        raise AssertionError("Start the owned cluster and apply schema first")
    classes = str(CASE / "java/build/classes")
    jar = str(CASE / ".deps/postgresql-42.7.14.jar")
    runners = [Runner("Java composition", ["java", "-cp", classes + os.pathsep + jar, "roo.postgres.CompositionRunner"]),
               Runner("Java inheritance", ["java", "-cp", classes + os.pathsep + jar, "roo.postgres.TemplateRunner"]),
               Runner("Rust composition", [str(CASE / "rust/target/debug/roo-postgres")])]
    for runner in runners:
        evidence = EVIDENCE["variants"][runner.name]
        fixtures(runner)
        print(f"PASS {runner.name}: {evidence['oracle_rows']} shared oracle rows and {evidence['malformed_fixtures']} malformed fixtures", flush=True)
        persistent_guards(runner)
        print(f"PASS {runner.name}: {len(evidence['persistent_guards'])} persistent boundary guards", flush=True)
        concurrency(runner)
        print(f"PASS {runner.name}: {len(evidence['concurrency'])} witnessed concurrent schedules", flush=True)
        process_crashes(runner)
        print(f"PASS {runner.name}: {len(evidence['process_crashes'])} SIGKILL and fresh-process recovery cases", flush=True)
    restart(runners)
    constraints()
    EVIDENCE["status"] = "PASS"
    output.write_text(json.dumps(EVIDENCE, indent=2) + "\n")
    recovered = sum(len(variant["restart_scopes"]) for variant in EVIDENCE["variants"].values())
    print(f"PASS PostgreSQL immediate restart: {recovered} durable snapshots preserved and recovered", flush=True)
    print(f"PASS {len(EVIDENCE['constraints'])} SQL constraint probes; all {len(runners)} implementations satisfy one shared contract", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
