#!/usr/bin/env python3
"""One independent oracle for real Java/Rust HTTP and durable recovery."""

from concurrent.futures import ThreadPoolExecutor
import csv
import http.client
import json
from pathlib import Path
import subprocess
import sys
import time

from support import (CASE, HEADER, MESSAGES, PROCESSES, RUN, Server, cleanup, cluster,
                     command, environment, pg_verify, require, state, unique)

EVIDENCE = {"run_id": RUN, "variants": {}, "restart": {}, "status": "RUNNING"}


def error(server, method, path, body, status, code, **options):
    observed, payload, headers = server.request(method, path, body, **options)
    expected = {"error": {"code": code, "message": MESSAGES[code]}}
    if observed != status or payload != expected:
        raise AssertionError(f"{server.variant} {method} {path}: expected {status} {expected}; observed {observed} {payload}")
    if status == 405 and not {k.lower(): v for k, v in headers.items()}.get("allow"):
        raise AssertionError("Method rejection did not provide Allow")


def oracle(server):
    with (CASE.parent / "scenarios.tsv").open() as handle:
        scenarios = list(csv.DictReader(handle, delimiter="\t"))
    with (CASE.parent / "expected.tsv").open() as handle:
        expected = list(csv.DictReader(handle, delimiter="\t"))
    if [r["scenario"] for r in scenarios] != [r["scenario"] for r in expected]:
        raise AssertionError("Independent oracle does not cover source fixtures")
    actual = []
    for scenario in scenarios:
        scope = unique(scenario["scenario"])
        row = server.init(scope)
        for action in scenario["steps"].split(";"):
            row = server.step(scope, action)
        actual.append({**row, "scenario": scenario["scenario"]})
    if actual != expected:
        for a, e in zip(actual, expected):
            if a != e:
                raise AssertionError(f"{server.variant} oracle mismatch: expected {e}, observed {a}")
        raise AssertionError("Incorrect oracle row count")
    EVIDENCE["variants"][server.variant]["oracle_rows"] = len(actual)


def validation(server):
    scope = server.seed("validation")
    path = "/v1/scopes/" + scope
    pay = path + "/payments"
    lines = path + "/lines"
    before = server.get(scope)
    json_headers = [("Content-Type", "application/json")]
    cases = [
        ("empty_body", "POST", pay, b"", 400, "InvalidRequest", {"raw": True}),
        ("malformed_json", "POST", pay, b'{"payment_id":', 400, "InvalidRequest", {"raw": True}),
        ("trailing_json", "POST", pay, b'{"payment_id":"p1"}{}', 400, "InvalidRequest", {"raw": True}),
        ("duplicate_field", "POST", pay, b'{"payment_id":"p1","payment_id":"p2"}', 400, "InvalidRequest", {"raw": True}),
        ("escaped_duplicate", "POST", pay, b'{"payment_id":"p1","payment_\\u0069d":"p2"}', 400, "InvalidRequest", {"raw": True}),
        ("unknown_field", "POST", pay, {"payment_id": "p1", "amount": "250"}, 400, "InvalidRequest", {}),
        ("array_body", "POST", pay, [], 400, "InvalidRequest", {}),
        ("null_body", "POST", pay, b"null", 400, "InvalidRequest", {"raw": True}),
        ("wrong_numeric_type", "POST", lines, {"unit_minor": 10, "quantity": "1"}, 400, "InvalidRequest", {}),
        ("missing_field", "POST", lines, {"unit_minor": "10"}, 400, "InvalidRequest", {}),
        ("invalid_id", "POST", pay, {"payment_id": "bad-id"}, 400, "InvalidRequest", {}),
        ("long_id", "POST", pay, {"payment_id": "p" * 65}, 400, "InvalidRequest", {}),
        ("long_scope", "GET", "/v1/scopes/" + "s" * 97, None, 400, "InvalidRequest", {}),
        ("missing_scope_segment", "GET", "/v1/scopes", None, 400, "InvalidRequest", {}),
        ("punctuation_route", "GET", path + "/unknown.ext", None, 400, "InvalidRequest", {}),
        ("decimal_text", "POST", lines, {"unit_minor": "1.0", "quantity": "1"}, 400, "InvalidRequest", {}),
        ("unicode_digit", "POST", lines, {"unit_minor": "１２", "quantity": "1"}, 400, "InvalidRequest", {}),
        ("long_integer", "POST", lines, {"unit_minor": "1" * 129, "quantity": "1"}, 400, "InvalidRequest", {}),
        ("invalid_utf8", "POST", pay, b'{"payment_id":"\xff"}', 400, "InvalidRequest", {"raw": True}),
        ("oversized_body", "POST", pay, b" " * 8193, 413, "BodyTooLarge", {"raw": True}),
        ("chunked_oversized_body", "POST", pay, b" " * 8193, 413, "BodyTooLarge", {"raw": True, "chunked": True}),
        ("wrong_media_type", "POST", pay, {"payment_id": "p1"}, 415, "UnsupportedMediaType", {"headers": [("Content-Type", "text/plain")]}),
        ("missing_media_type", "POST", pay, {"payment_id": "p1"}, 415, "UnsupportedMediaType", {"headers": []}),
        ("wrong_charset", "POST", pay, {"payment_id": "p1"}, 415, "UnsupportedMediaType", {"headers": [("Content-Type", "application/json; charset=latin1")]}),
        ("wrong_accept", "POST", pay, {"payment_id": "p1"}, 406, "NotAcceptable", {"headers": [*json_headers, ("Accept", "text/html")]}),
        ("wrong_method", "DELETE", pay, {}, 405, "MethodNotAllowed", {}),
        ("unknown_route", "GET", path + "/unknown", None, 404, "RouteNotFound", {}),
        ("missing_scope_get", "GET", "/v1/scopes/" + unique("missing"), None, 404, "ScopeNotFound", {}),
        ("missing_scope_post", "POST", "/v1/scopes/" + unique("missing") + "/payments", {"payment_id": "p1"}, 404, "ScopeNotFound", {}),
        ("query_string", "GET", path + "?x=1", None, 400, "InvalidRequest", {}),
        ("encoded_path", "GET", path.replace("_", "%5F", 1), None, 400, "InvalidRequest", {}),
        ("trailing_slash", "GET", path + "/", None, 400, "InvalidRequest", {}),
        ("duplicate_content_type", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, *json_headers]}),
        ("duplicate_accept", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Accept", "*/*"), ("Accept", "application/json")]}),
        ("key_mismatch", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p2")]}),
        ("key_on_non_idempotent_add", "POST", lines, {"unit_minor": "1", "quantity": "1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p1")]}),
        ("duplicate_key_header", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p1"), ("Idempotency-Key", "p1")]}),
        ("comma_joined_key", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p1,p1")]}),
        ("unsupported_drop_header", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("X-Roo-Test-Drop-Response", "true")]}),
        ("get_body", "GET", path, {}, 400, "InvalidRequest", {}),
        ("invalid_control_enum", "POST", pay, {"payment_id": "p1", "mode": "random"}, 400, "InvalidRequest", {}),
    ]
    for label, method, target, body, status, code, options in cases:
        error(server, method, target, body, status, code, **options)
        if server.get(scope) != before:
            raise AssertionError(f"Rejected HTTP case {label} mutated existing state")
    EVIDENCE["variants"][server.variant]["validation_cases"] = [case[0] for case in cases]


def negotiation(server):
    scope = server.seed("negotiation")
    before = server.get(scope)
    headers = [("Content-Type", "Application/JSON ; charset = UTF-8"), ("Accept", " */* ")]
    row = server.snapshot_response("PUT", "/v1/scopes/" + scope, {}, headers=headers)
    if row != before:
        raise AssertionError("Accepted media/charset spelling changed existing order")
    row = server.snapshot_response("GET", "/v1/scopes/" + scope, headers=[])
    if row != before:
        raise AssertionError("Absent Accept changed response")
    EVIDENCE["variants"][server.variant]["negotiation_cases"] = ["media_case_charset_whitespace_wildcard_accept", "absent_accept"]


def admission(server):
    scopes = [server.seed("admission") for _ in range(16)]
    gated = None
    try:
        with pg_verify.Barrier() as barrier:
            gated = Server(server.variant, http_key=barrier.key)
            with ThreadPoolExecutor(max_workers=16) as pool:
                requests = [pool.submit(gated.step, scope, "add:1:1", "Added") for scope in scopes]
                deadline = time.monotonic() + 12
                count = 0
                while time.monotonic() < deadline:
                    count = int(cluster.sql("SELECT count(*) FROM pg_stat_activity WHERE application_name='roo:"
                                            + gated.worker + ":http_after_snapshot' AND wait_event_type='Lock' AND wait_event='advisory'").strip())
                    if count == 16:
                        break
                    if any(request.done() for request in requests):
                        raise AssertionError("Admitted operation left its held witness gate")
                    time.sleep(0.02)
                if count != 16:
                    raise AssertionError("Did not observe all sixteen database-bearing requests")
                error(gated, "GET", "/v1/scopes/" + scopes[0], None, 503, "Busy")
                barrier.close()
                for request in requests:
                    request.result(timeout=35)
            for scope in scopes:
                state(server, scope, "Draft", total=251, charges=0, events=0, payment="-")
            gated.get(scopes[0])
    finally:
        if gated is not None:
            gated.stop()
    EVIDENCE["variants"][server.variant]["admission"] = {"simultaneously_witnessed_operations": count, "seventeenth_request": "503 Busy", "all_admitted_completed": True, "capacity_recovered": True}


def graceful_drain(server):
    scope = server.seed("drain")
    gated = None
    try:
        with pg_verify.Barrier() as barrier:
            gated = Server(server.variant, http_key=barrier.key)
            with ThreadPoolExecutor(max_workers=1) as pool:
                request = pool.submit(gated.step, scope, "add:1:1", "Added")
                witness(gated, "http_after_snapshot")
                gated.process.terminate()
                deadline = time.monotonic() + 5
                listener_closed = False
                while time.monotonic() < deadline:
                    try:
                        gated.get(scope)
                    except (ConnectionRefusedError, ConnectionResetError, http.client.RemoteDisconnected):
                        listener_closed = True
                        break
                    time.sleep(0.02)
                if not listener_closed or gated.process.poll() is not None or request.done():
                    raise AssertionError("Graceful stop did not close listener while retaining admitted work")
                barrier.close()
                request.result(timeout=35)
        gated.stop()
        if gated.process.returncode not in (0, 143):
            raise AssertionError("Graceful drain required forced termination")
        state(server, scope, "Draft", total=251, charges=0, events=0, payment="-")
    finally:
        if gated is not None:
            gated.stop()
    EVIDENCE["variants"][server.variant]["graceful_drain"] = {"signal": "SIGTERM", "listener_closed_with_request_active": True, "admitted_request_completed": True, "exit_code": gated.process.returncode, "forced_termination": False}


def default_mode(server):
    ordinary = Server(server.variant, test=False)
    try:
        scope = server.seed("ordinary")
        path = "/v1/scopes/" + scope
        before = ordinary.get(scope)
        controls = [
            ("payment_control_disabled", "/payments", {"payment_id": "p1", "mode": "approve"}, 400, "InvalidRequest"),
            ("refund_control_disabled", "/refunds", {"refund_id": "r1", "failure": "none"}, 400, "InvalidRequest"),
            ("lookup_control_disabled", "/reconciliation", {"lookup": "ok"}, 400, "InvalidRequest"),
            ("relay_control_disabled", "/relay", {"mode": "ok"}, 400, "InvalidRequest"),
            ("probe_disabled", "/_test/provider-conflicts", {"payment_id": "p1", "different_amount": "999"}, 404, "RouteNotFound"),
        ]
        for label, suffix, body, status, code in controls:
            error(ordinary, "POST", path + suffix, body, status, code)
            if ordinary.get(scope) != before:
                raise AssertionError(f"Disabled control {label} changed state")
        ordinary.step(scope, "pay:p1:approve:none", "Approved")
        ordinary.step(scope, "pay:p1:approve:none", "AlreadyApplied")
        state(ordinary, scope, "Paid")
        ordinary.step(scope, "refund:r1:approve:none", "Approved")
        ordinary.step(scope, "refund:r1:approve:none", "AlreadyApplied")
        state(ordinary, scope, "Refunded", refunds=1, events=2, refund="r1")
        ordinary.init(scope)
        state(ordinary, scope, "Refunded", refunds=1, events=2, refund="r1")
        EVIDENCE["variants"][server.variant]["ordinary_mode"] = [c[0] for c in controls] + ["same_payment_key", "same_refund_key", "put_preserves_existing"]
    finally:
        ordinary.stop()


def witness(server, point=None):
    pg_verify.witnessed(server.worker, point, server.process)


def race(server, label, seed_state, first, second, point, first_result, second_result, row_wait=True):
    scope = server.seed(label, seed_state)
    gated = None
    try:
        with pg_verify.Barrier() as barrier:
            gated = Server(server.variant, point=point, key=barrier.key)
            with ThreadPoolExecutor(max_workers=2) as pool:
                a = pool.submit(gated.step, scope, first, first_result)
                witness(gated, point)
                b = pool.submit(server.step, scope, second, second_result)
                if row_wait:
                    witness(server)
                else:
                    b.result(timeout=15)
                barrier.close()
                a.result(timeout=35)
                b.result(timeout=35)
    finally:
        if gated is not None:
            gated.stop()
    EVIDENCE["variants"][server.variant]["concurrency"].append(label)
    return scope


def concurrency(server):
    s = race(server, "different_payment_keys", "Draft", "pay:p1:approve:none", "pay:p2:approve:none", "inside_prepare", "Approved", "IntentConflict")
    state(server, s, "Paid")
    s = race(server, "same_payment_key", "Draft", "pay:p1:approve:none", "pay:p1:approve:none", "after_effect", "AlreadyApplied", "Approved", False)
    state(server, s, "Paid")
    s = race(server, "different_refund_keys", "Paid", "refund:r1:approve:none", "refund:r2:approve:none", "inside_prepare", "Approved", "IntentConflict")
    state(server, s, "Refunded", refunds=1, events=2, refund="r1")
    s = race(server, "add_before_pay", "Draft", "add:50:1", "pay:p1:approve:none", "inside_prepare", "Added", "Approved")
    state(server, s, "Paid", total=300)
    s = race(server, "pay_before_add", "Draft", "pay:p1:approve:none", "add:50:1", "inside_prepare", "Approved", "InvalidState")
    state(server, s, "Paid")
    s = race(server, "concurrent_relays", "Refunded", "relay:ok", "relay:ok", "after_delivery", "RelayOk", "RelayOk")
    state(server, s, "Refunded", refunds=1, events=2, consumers=2, pending=0, refund="r1")
    s = race(server, "same_refund_key", "Paid", "refund:r1:approve:none", "refund:r1:approve:none", "after_effect", "AlreadyApplied", "Approved", False)
    state(server, s, "Refunded", refunds=1, events=2, refund="r1")


def response_lost(future):
    try:
        future.result(timeout=15)
    except (http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError):
        return
    raise AssertionError("SIGKILL did not produce observed HTTP loss before response headers")


def crash(server, label, initial, action, point, expected, recover, http_boundary=False):
    scope = server.seed(label, initial)
    gated = fresh = None
    try:
        with pg_verify.Barrier() as barrier:
            gated = Server(server.variant, http_key=barrier.key) if http_boundary else Server(server.variant, point=point, key=barrier.key)
            with ThreadPoolExecutor(max_workers=1) as pool:
                request = pool.submit(gated.step, scope, action)
                witness(gated, "http_after_snapshot" if http_boundary else point)
                gated.stop(crash=True)
                response_lost(request)
        fresh = Server(server.variant)
        state(fresh, scope, **expected)
        recover(fresh, scope)
    finally:
        if gated is not None: gated.stop()
        if fresh is not None: fresh.stop()
    EVIDENCE["variants"][server.variant]["process_recovery"].append({"case": label, "signal": "SIGKILL", "gate": "http_after_snapshot" if http_boundary else point, "client": "connection lost before response headers", "recovery": "fresh HTTP server"})


def recoveries(server):
    def prepared(s, scope):
        s.step(scope, "reconcile:ok:none", "NotFound")
        s.step(scope, "pay:p1:approve:none", "Approved")
        state(s, scope, "Paid")
    def effect(s, scope):
        s.step(scope, "reconcile:ok:none", "Approved")
        state(s, scope, "Paid")
    def paid(s, scope):
        s.step(scope, "pay:p1:approve:none", "AlreadyApplied")
        state(s, scope, "Paid")
    def delivery(s, scope):
        s.step(scope, "relay:ok", "RelayOk")
        state(s, scope, "Refunded", refunds=1, events=2, consumers=2, pending=0, refund="r1")
    def refund(s, scope):
        s.step(scope, "reconcile:ok:none", "Approved")
        state(s, scope, "Refunded", refunds=1, events=2, refund="r1")
    def refund_replay(s, scope):
        s.step(scope, "refund:r1:approve:none", "AlreadyApplied")
        state(s, scope, "Refunded", refunds=1, events=2, refund="r1")
    def add_inspection(s, scope):
        # Deliberate second caller action after inspecting persisted total; this
        # demonstrates lack of a durable add key rather than automatic replay.
        s.step(scope, "add:50:1", "Added")
        state(s, scope, "Draft", total=350, charges=0, events=0, payment="-")
    crash(server, "kill_after_prepare", "Draft", "pay:p1:approve:none", "after_prepare", dict(name="Pending", charges=0, events=0), prepared)
    crash(server, "kill_after_effect", "Draft", "pay:p1:approve:none", "after_effect", dict(name="Pending", events=0), effect)
    crash(server, "kill_after_finalize", "Draft", "pay:p1:approve:none", "after_finalize", dict(name="Paid"), paid)
    crash(server, "kill_after_delivery", "Refunded", "relay:ok", "after_delivery", dict(name="Refunded", refunds=1, events=2, consumers=1, refund="r1"), delivery)
    crash(server, "kill_refund_effect", "Paid", "refund:r1:approve:none", "after_effect", dict(name="Refunding", refunds=1, events=1, refund="r1"), refund)
    crash(server, "lost_payment_response", "Draft", "pay:p1:approve:none", None, dict(name="Paid"), paid, True)
    crash(server, "lost_refund_response", "Paid", "refund:r1:approve:none", None, dict(name="Refunded", refunds=1, events=2, refund="r1"), refund_replay, True)
    crash(server, "lost_add_response", "Draft", "add:50:1", None, dict(name="Draft", total=300, charges=0, events=0, payment="-"), add_inspection, True)


def restart(servers):
    scopes = []
    for server in servers:
        pending = server.seed("restart_pending")
        server.step(pending, "pay:p1:timeout_after:none", "Unknown")
        refunding = server.seed("restart_refunding", "Paid")
        server.step(refunding, "refund:r1:timeout_after:none", "Unknown")
        inbox = server.seed("restart_inbox", "Refunded")
        server.step(inbox, "relay:ack_fail", "RelayAckFailed")
        paid = server.seed("restart_paid", "Paid")
        for kind, scope in (("pending", pending), ("refunding", refunding), ("inbox", inbox), ("paid", paid)):
            scopes.append((server, kind, scope, server.get(scope)))
    before = cluster.sql("SELECT pg_postmaster_start_time(),current_setting('server_version_num'),current_setting('fsync'),current_setting('synchronous_commit'),current_setting('full_page_writes')").strip()
    offset = (cluster.RUNTIME / "server.log").stat().st_size
    pids = {server.variant: server.process.pid for server in servers}
    try:
        cluster.stop("immediate")
        for server in servers:
            scope = next(scope for s, _, scope, _ in scopes if s is server)
            error(server, "GET", "/v1/scopes/" + scope, None, 503, "DatabaseUnavailable")
    finally:
        cluster.start()
    after = cluster.sql("SELECT pg_postmaster_start_time(),current_setting('server_version_num'),current_setting('fsync'),current_setting('synchronous_commit'),current_setting('full_page_writes')").strip()
    if before.split("|")[0] == after.split("|")[0]:
        raise AssertionError("PostgreSQL did not restart")
    with (cluster.RUNTIME / "server.log").open("rb") as handle:
        handle.seek(offset)
        lines = handle.read().decode(errors="replace").splitlines()
    wal = [line for line in lines if any(s in line for s in ("interrupted", "not properly shut down", "redo starts", "redo done", "ready to accept"))]
    if not any("redo" in line for line in wal):
        raise AssertionError("No server WAL recovery evidence")
    for server, kind, scope, snapshot in scopes:
        if server.process.poll() is not None or server.process.pid != pids[server.variant] or server.get(scope) != snapshot:
            raise AssertionError("Surviving HTTP process failed to reconnect or durable snapshot changed")
        if kind == "pending":
            server.step(scope, "reconcile:ok:none", "Approved")
            state(server, scope, "Paid")
        elif kind == "refunding":
            server.step(scope, "reconcile:ok:none", "Approved")
            state(server, scope, "Refunded", refunds=1, events=2, refund="r1")
        elif kind == "inbox":
            server.step(scope, "relay:ok", "RelayOk")
            state(server, scope, "Refunded", refunds=1, events=2, consumers=2, pending=0, refund="r1")
        else:
            server.step(scope, "pay:p1:approve:none", "AlreadyApplied")
            state(server, scope, "Paid")
        EVIDENCE["variants"][server.variant]["restart_scopes"].append(kind)
    EVIDENCE["restart"] = {"mode": "immediate", "before": before, "after": after, "wal_recovery_log": wal, "preserved_scopes": len(scopes), "surviving_http_pids": pids, "database_unavailable_responses": 3}


def configuration(variant):
    cases = [{"ROO_HTTP_HOST": "192.0.2.1"}, {"ROO_HTTP_PORT": "65536"},
             {"ROO_HTTP_TEST_MODE": "0"}, {"ROO_HTTP_GATE_LOCK": "3", "ROO_HTTP_TEST_MODE": None}]
    for changes in cases:
        env = environment()
        for key, value in changes.items():
            if value is None: env.pop(key, None)
            else: env[key] = value
        result = subprocess.run(command(variant), env=env, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or result.stdout.strip() or not result.stderr.strip():
            raise AssertionError(f"{variant}: invalid listener configuration was not rejected before readiness")
    EVIDENCE["variants"][variant]["startup_rejections"] = len(cases)


def main():
    servers = []
    try:
        for variant in ("Java composition", "Java inheritance", "Rust composition"):
            EVIDENCE["variants"][variant] = {"concurrency": [], "process_recovery": [], "restart_scopes": []}
            configuration(variant)
            server = Server(variant)
            servers.append(server)
            oracle(server)
            validation(server)
            negotiation(server)
            default_mode(server)
            record = EVIDENCE["variants"][variant]
            print(f"PASS {variant}: {record['oracle_rows']} HTTP oracle rows, {len(record['validation_cases'])} rejection cases, {len(record['negotiation_cases'])} negotiation cases, 8 ordinary-mode cases, 4 startup rejections", flush=True)
            admission(server)
            print(f"PASS {variant}: 16 admitted operations witnessed; request 17 returned Busy; capacity recovered", flush=True)
            graceful_drain(server)
            print(f"PASS {variant}: SIGTERM closed listener and drained the witnessed active request", flush=True)
            concurrency(server)
            print(f"PASS {variant}: 7 HTTP concurrent schedules with database lock witnesses", flush=True)
            recoveries(server)
            print(f"PASS {variant}: 5 durable-gap and 3 completed-response-loss SIGKILL recoveries through fresh HTTP servers", flush=True)
        restart(servers)
        EVIDENCE["barriers"] = pg_verify.EVIDENCE["barriers"]
        EVIDENCE["status"] = "PASS"
    finally:
        cleanup()
    EVIDENCE["all_http_processes_stopped"] = all(s.process.poll() is not None for s in PROCESSES)
    (CASE.parents[2] / "research/http-integration-evidence.json").write_text(json.dumps(EVIDENCE, indent=2) + "\n")
    print("PASS PostgreSQL immediate restart: 12 HTTP snapshots preserved/recovered; 3 surviving HTTP servers returned bounded503 then reconnected", flush=True)
    print("PASS all owned HTTP processes stopped", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError, RuntimeError, subprocess.SubprocessError, http.client.HTTPException) as failure:
        print(f"FAIL {failure}", file=sys.stderr)
        sys.exit(1)
