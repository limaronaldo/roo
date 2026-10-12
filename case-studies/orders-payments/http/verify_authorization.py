#!/usr/bin/env python3
"""Exercise fixture authorization over real HTTP and the owned PostgreSQL cluster."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import http.client
import json
from pathlib import Path
import subprocess
import sys

from support import (CASE, MESSAGES, PROCESSES, RUN, Server, cleanup, cluster,
                     command, environment, pg_verify, translate, unique)

VARIANTS = ("Java composition", "Java inheritance", "Rust composition")
PRINCIPAL = "alice"
OTHER_PRINCIPAL = "bob"
OPERATIONS = ("read", "init", "add", "pay", "refund", "reconcile", "relay", "provider_conflict")
_UNSET = object()
EVIDENCE = {
    "run_id": RUN,
    "status": "RUNNING",
    "variants": {},
    "schedules": [],
    "barriers": pg_verify.EVIDENCE["barriers"],
    "restart": {},
    "errors": [],
}
_WORKER_CODES = {"Java composition": "jc", "Java inheritance": "jt", "Rust composition": "r"}
_WORKER_SEQUENCE = {variant: 0 for variant in VARIANTS}


def worker(variant, prefix="auth"):
    _WORKER_SEQUENCE[variant] += 1
    result = f"{prefix}_{_WORKER_CODES[variant]}_{_WORKER_SEQUENCE[variant]}"
    if len(result) > 22:
        raise AssertionError("PostgreSQL application name witness worker is too long")
    return result


def expect_error(server, method, path, body, status, code, **options):
    observed, payload, headers = server.request(method, path, body, **options)
    expected = {"error": {"code": code, "message": MESSAGES[code]}}
    if observed != status or payload != expected:
        raise AssertionError(
            f"{server.variant} {method} {path}: expected {status} {expected}; "
            f"observed {observed} {payload}"
        )
    if status == 405 and not {key.lower(): value for key, value in headers.items()}.get("allow"):
        raise AssertionError("Method rejection did not provide Allow")
    return observed, payload, headers


def authorization(server, scope, principal=_UNSET, *, operation="read"):
    options = {} if principal is _UNSET else {"principal": principal}
    status, payload, _ = server.request(
        "GET", f"/v1/scopes/{scope}/authorization/{operation}", None, **options
    )
    if status != 200 or set(payload) != {"authorization"} or set(payload["authorization"]) != {"operation", "allowed"} or payload["authorization"]["operation"] != operation:
        raise AssertionError(f"{server.variant}: invalid authorization observation {status} {payload}")
    if type(payload["authorization"]["allowed"]) is not bool:
        raise AssertionError("Authorization observation did not return a boolean")
    return payload["authorization"]["allowed"]


def action_request(server, scope, action, principal=_UNSET):
    endpoint, body = translate(action)
    headers = [("Accept", "application/json"), ("Content-Type", "application/json")]
    if endpoint in ("payments", "refunds"):
        headers.append(("Idempotency-Key", body.get("payment_id", body.get("refund_id"))))
    options = {"headers": headers}
    if principal is not _UNSET:
        options["principal"] = principal
    return server.request("POST", f"/v1/scopes/{scope}/{endpoint}", body, **options)


def expect_action(result, server, status, outcome):
    observed, payload, _ = result
    if observed != status or set(payload) != {"snapshot"}:
        raise AssertionError(f"{server.variant}: expected action {status}/{outcome}, observed {observed} {payload}")
    row = payload["snapshot"]
    if set(row) != {"scenario", "state", "total", "charge_count", "refund_count", "event_count",
                    "consumer_count", "pending_outbox", "last_result", "payment_id", "refund_id"}:
        raise AssertionError("Action returned an invalid snapshot shape")
    if row["last_result"] != outcome:
        raise AssertionError(f"{server.variant}: expected {outcome}, observed {row['last_result']}")
    return row


def set_grant(scope, principal, operation, allowed):
    if operation not in OPERATIONS:
        raise AssertionError("Unknown operation in grant fixture")
    value = "TRUE" if allowed else "FALSE"
    observed = cluster.sql(
        "INSERT INTO roo_authorization.operation_grants(scope,principal,operation,allowed) "
        f"VALUES('{scope}','{principal}','{operation}',{value}) "
        "ON CONFLICT(scope,principal,operation) DO UPDATE SET allowed=EXCLUDED.allowed "
        "RETURNING allowed"
    ).strip()
    if observed != ("t" if allowed else "f"):
        raise AssertionError("Operation policy fixture UPSERT returned an unexpected value")


def set_all_grants(scope, principal, allowed):
    """Explicit compatibility setup for broad legacy schedules, never a runtime fallback."""
    for operation in OPERATIONS:
        set_grant(scope, principal, operation, allowed)


def grant_state(scope, principal, operation="read"):
    value = cluster.sql(
        "SELECT allowed FROM roo_authorization.operation_grants "
        f"WHERE scope='{scope}' AND principal='{principal}' AND operation='{operation}'"
    ).strip()
    return {"t": True, "f": False}.get(value)


def effects(scope):
    return tuple(int(value) for value in cluster.sql(
        "SELECT "
        f"(SELECT count(*) FROM roo_app.orders WHERE scope='{scope}'),"
        f"(SELECT count(*) FROM roo_app.lines WHERE scope='{scope}'),"
        f"(SELECT count(*) FROM roo_app.outbox WHERE scope='{scope}'),"
        f"(SELECT count(*) FROM roo_provider.records WHERE scope='{scope}'),"
        f"(SELECT count(*) FROM roo_consumer.inbox WHERE scope='{scope}'),"
        f"(SELECT count(*) FROM roo_app.outbox WHERE scope='{scope}' AND NOT delivered)"
    ).strip().split("|"))


def seed(legacy, label, *, paid=False):
    scope = unique(label)
    legacy.init(scope)
    legacy.step(scope, "add:250:1", "Added")
    if paid:
        legacy.step(scope, "pay:p1:approve:none", "Approved")
    return scope


def startup_rejections(variant):
    cases = [
        ("auth_requires_test_mode", environment(test=False, auth_mode="fixture")),
        ("unknown_auth_mode", environment(auth_mode="production")),
        ("auth_gate_requires_fixture", environment(auth_key="12")),
        ("signed_plus_auth_gate", environment(auth=True, auth_key="+12")),
        ("zero_auth_gate", environment(auth=True, auth_key="0")),
    ]
    passed = []
    for name, env in cases:
        result = subprocess.run(command(variant), env=env, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or result.stdout.strip() or not result.stderr.strip():
            raise AssertionError(f"{variant}: invalid authorization startup configuration was accepted: {name}")
        passed.append(name)
    EVIDENCE["variants"][variant]["startup_rejections"] = passed


def identity_and_isolation(variant, legacy, auth):
    record = EVIDENCE["variants"][variant]
    existing = seed(legacy, "auth_identity_existing")
    missing = unique("auth_identity_missing")
    before = effects(existing)
    before_missing = effects(missing)

    expect_error(auth, "GET", f"/v1/scopes/{existing}", None, 401, "PrincipalRequired", principal=None)
    expect_error(auth, "GET", f"/v1/scopes/{existing}", None, 400, "InvalidRequest", principal="bad-id")
    expect_error(auth, "GET", f"/v1/scopes/{existing}", None, 400, "InvalidRequest", principal="a" * 33)
    expect_error(
        auth, "GET", f"/v1/scopes/{existing}", None, 400, "InvalidRequest",
        headers=[("Accept", "application/json"), ("X-Roo-Principal", PRINCIPAL),
                 ("X-Roo-Principal", OTHER_PRINCIPAL)], principal=None,
    )

    existing_denial = expect_error(auth, "GET", f"/v1/scopes/{existing}", None, 403, "Forbidden")
    missing_denial = expect_error(auth, "GET", f"/v1/scopes/{missing}", None, 403, "Forbidden")
    if existing_denial[1] != missing_denial[1]:
        raise AssertionError("Denied existing and missing scopes were distinguishable")
    expect_error(auth, "POST", f"/v1/scopes/{existing}/lines", {"unit_minor": "5", "quantity": "1"},
                 403, "Forbidden")
    expect_error(auth, "POST", f"/v1/scopes/{missing}/lines", {"unit_minor": "5", "quantity": "1"},
                 403, "Forbidden")
    expect_error(auth, "PUT", f"/v1/scopes/{missing}", {}, 403, "Forbidden")
    if effects(existing) != before or effects(missing) != before_missing:
        raise AssertionError("Denied read, mutation, or initialization changed business data")
    if legacy.get(existing)["state"] != "Draft":
        raise AssertionError("Denied requests changed the existing order state")
    if authorization(auth, missing):
        raise AssertionError("Missing policy row did not report default deny")

    set_all_grants(missing, PRINCIPAL, True)
    expect_error(auth, "GET", f"/v1/scopes/{missing}", None, 404, "ScopeNotFound")
    if effects(missing) != (0, 0, 0, 0, 0, 0):
        raise AssertionError("Permitted missing scope was created by a read")
    init_status, init_payload, _ = auth.request("PUT", f"/v1/scopes/{missing}", {})
    if init_status != 200 or set(init_payload) != {"snapshot"} or init_payload["snapshot"]["state"] != "Draft":
        raise AssertionError(f"Authorized initialization failed: {init_status} {init_payload}")

    scope_a = seed(legacy, "auth_scope_a")
    scope_b = seed(legacy, "auth_scope_b")
    set_all_grants(scope_a, PRINCIPAL, True)
    set_all_grants(scope_b, OTHER_PRINCIPAL, True)
    if not authorization(auth, scope_a) or authorization(auth, scope_b):
        raise AssertionError("Authorization observation crossed scope or principal")
    if authorization(auth, scope_a, OTHER_PRINCIPAL) or not authorization(auth, scope_b, OTHER_PRINCIPAL):
        raise AssertionError("Authorization observation crossed principals")
    auth.get(scope_a)
    auth.get(scope_b, principal=OTHER_PRINCIPAL)
    expect_error(auth, "GET", f"/v1/scopes/{scope_a}", None, 403, "Forbidden", principal=OTHER_PRINCIPAL)
    expect_error(auth, "GET", f"/v1/scopes/{scope_b}", None, 403, "Forbidden")

    status, payload, _ = auth.request("GET", f"/v1/scopes/{missing}/authorization/read", {})
    if status != 400 or payload != {"error": {"code": "InvalidRequest", "message": MESSAGES["InvalidRequest"]}}:
        raise AssertionError("Authorization observation accepted a GET body")
    expect_error(auth, "GET", f"/v1/scopes/{missing}/authorization/read", None, 400, "InvalidRequest",
                 headers=[("Accept", "application/json"), ("Idempotency-Key", "p1")])
    _, _, headers = expect_error(auth, "POST", f"/v1/scopes/{missing}/authorization/read", {}, 405,
                                 "MethodNotAllowed")
    if {key.lower(): value for key, value in headers.items()}.get("allow") != "GET":
        raise AssertionError("Authorization route did not advertise GET only")
    expect_error(legacy, "GET", f"/v1/scopes/{existing}/authorization", None, 404, "RouteNotFound")
    record["identity_cases"] = [
        "missing_principal", "malformed_principal", "oversized_principal", "duplicate_principal",
        "default_deny_existing_and_missing", "denied_read_and_write_no_effects", "denied_init_before_insert",
        "allowed_missing_scope", "scope_and_principal_isolation", "detached_observation_validation",
        "authorization_route_disabled_by_default",
    ]


def operation_request(server, scope, operation, principal=_UNSET):
    options = {} if principal is _UNSET else {"principal": principal}
    if operation in ("read", "init"):
        return server.request("GET" if operation == "read" else "PUT", f"/v1/scopes/{scope}",
                              None if operation == "read" else {}, **options)
    return action_request(server, scope, {
        "add": "add:250:1", "pay": "pay:p1:approve:none", "refund": "refund:r1:approve:none",
        "reconcile": "reconcile:ok:none", "relay": "relay:ok", "provider_conflict": "conflict:p1:999",
    }[operation], principal)


def expect_forbidden(result):
    status, payload, _ = result
    if status != 403 or payload != {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}:
        raise AssertionError(f"Operation escaped exact-grant denial: {status} {payload}")


def operation_matrix(variant, legacy, auth):
    cells = []
    for granted in OPERATIONS:
        scope = unique("auth_matrix_init") if granted == "init" else seed(
            legacy, "auth_matrix_" + granted, paid=granted in ("refund", "relay", "provider_conflict"))
        if granted == "reconcile":
            set_grant(scope, PRINCIPAL, "reconcile", True)
            draft_effects = effects(scope)
            expect_action(operation_request(auth, scope, "reconcile"), auth, 409, "InvalidState")
            if effects(scope) != draft_effects or legacy.get(scope)["state"] != "Draft":
                raise AssertionError("Reconcile-only grant created a new payment intent")
            legacy.step(scope, "pay:p1:timeout_after:none", "Unknown")
        set_grant(scope, PRINCIPAL, granted, True)
        before = effects(scope)
        for requested in OPERATIONS:
            observed = authorization(auth, scope, operation=requested)
            if observed != (requested == granted):
                raise AssertionError("Detached observation did not distinguish operation grants")
            if requested == granted:
                continue  # Exercise the successful diagonal after all no-effect denials.
            expect_forbidden(operation_request(auth, scope, requested))
            if effects(scope) != before:
                raise AssertionError("Off-diagonal denied request changed business effects")
            cells.append({"granted": granted, "requested": requested, "status": 403,
                          "observed_allowed": observed, "effects_unchanged": True})
        result = operation_request(auth, scope, granted)
        if granted in ("read", "init"):
            status, payload, _ = result
            if status != 200 or set(payload) != {"snapshot"} or payload["snapshot"]["state"] != "Draft":
                raise AssertionError(f"Single {granted} grant failed: {status} {payload}")
        else:
            expected = {"add": (200, "Added"), "pay": (200, "Approved"), "refund": (200, "Approved"),
                        "reconcile": (200, "Approved"), "relay": (200, "RelayOk"),
                        "provider_conflict": (409, "KeyConflict")}[granted]
            expect_action(result, auth, *expected)
        cells.append({"granted": granted, "requested": granted, "status": result[0],
                      "observed_allowed": True})
        if granted != "read":
            expect_forbidden(operation_request(auth, scope, "read"))
        set_grant(scope, PRINCIPAL, granted, False)
        after_success = effects(scope)
        expect_forbidden(operation_request(auth, scope, granted))
        if authorization(auth, scope, operation=granted) or grant_state(scope, PRINCIPAL, granted) is not False:
            raise AssertionError("False operation tombstone was not retained and denied")
        if effects(scope) != after_success:
            raise AssertionError("False operation tombstone allowed a business effect")
        cells[-1]["subsequent_tombstone_denied"] = True
    EVIDENCE["variants"][variant]["operation_matrix"] = cells
    EVIDENCE["variants"][variant]["reconcile_cannot_create_intent"] = True


def coarse_and_route_contract(variant, legacy, auth):
    scope = seed(legacy, "auth_coarse_inert")
    cluster.sql("INSERT INTO roo_authorization.grants(scope,principal,allowed) "
                f"VALUES('{scope}','{PRINCIPAL}',TRUE)")
    # Reinstall with an existing coarse allow to exercise the migration boundary.
    cluster.sql((CASE / "schema.sql").read_text())
    before = effects(scope)
    for operation in OPERATIONS:
        if grant_state(scope, PRINCIPAL, operation) is not None or authorization(auth, scope, operation=operation):
            raise AssertionError("Coarse grant backfilled or enabled an operation grant")
        expect_forbidden(operation_request(auth, scope, operation))
    if effects(scope) != before:
        raise AssertionError("Inert coarse grant allowed business effects")
    count = cluster.sql("SELECT count(*) FROM roo_authorization.operation_grants "
                        f"WHERE scope='{scope}' AND principal='{PRINCIPAL}'").strip()
    if count != "0":
        raise AssertionError("Authorization requests backfilled coarse grants")
    cluster.sql("DO $test$ BEGIN BEGIN "
                "INSERT INTO roo_authorization.operation_grants(scope,principal,operation,allowed) "
                f"VALUES('{scope}','{PRINCIPAL}','unknown_operation',TRUE); "
                "RAISE EXCEPTION 'Unknown operation token accepted'; "
                "EXCEPTION WHEN check_violation THEN NULL; END; END $test$")
    expect_error(auth, "GET", f"/v1/scopes/{scope}/authorization", None, 400, "InvalidRequest")
    expect_error(auth, "GET", f"/v1/scopes/{scope}/authorization/unknown_operation", None, 400, "InvalidRequest")
    expect_error(auth, "GET", f"/v1/scopes/{scope}/authorization/read?operation=add", None, 400, "InvalidRequest")
    expect_error(legacy, "GET", f"/v1/scopes/{scope}/authorization/read", None, 404, "RouteNotFound")
    precedence = [
        ("extra_authorization_segment", "GET", f"/v1/scopes/{scope}/authorization/read/extra", None, 400, "InvalidRequest", {}),
        ("principal_before_accept", "GET", f"/v1/scopes/{scope}", None, 401, "PrincipalRequired",
         {"principal": None, "headers": [("Accept", "text/html")]}),
        ("principal_before_body_limit", "POST", f"/v1/scopes/{scope}/payments", b" " * 8193, 401, "PrincipalRequired",
         {"principal": None, "raw": True}),
        ("method_before_principal", "DELETE", f"/v1/scopes/{scope}/payments", {}, 405, "MethodNotAllowed",
         {"principal": None}),
    ]
    for label, method, target, body, status, code, options in precedence:
        expect_error(auth, method, target, body, status, code, **options)
        if effects(scope) != before:
            raise AssertionError(f"Rejected authorization case {label} changed business effects")
    EVIDENCE["variants"][variant]["validation_precedence"] = [case[0] for case in precedence]
    EVIDENCE["variants"][variant]["operation_policy_contract"] = {
        "coarse_true_inert": True, "no_backfill": True, "unknown_sql_token_rejected": True,
        "old_route_enabled_400": True, "old_route_disabled_404": True,
        "operation_route_disabled_404": True, "unknown_route_token_400": True, "query_rejected": True,
    }


def hidden_outcomes(variant, legacy, auth):
    scope = seed(legacy, "auth_denied_hidden_outcomes", paid=True)
    before = effects(scope)
    if grant_state(scope, PRINCIPAL) is not None:
        raise AssertionError("Test fixture unexpectedly inherited a principal grant")
    expect_error(auth, "POST", f"/v1/scopes/{scope}/payments", {"payment_id": "p1"}, 403, "Forbidden",
                 headers=[("Accept", "application/json"), ("Content-Type", "application/json"),
                          ("Idempotency-Key", "p1")])
    for action in ("reconcile:ok:none", "relay:ok", "conflict:p1:999"):
        observed, payload, _ = action_request(auth, scope, action)
        expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
        if observed != 403 or payload != expected:
            raise AssertionError(f"Denied {action} leaked an outcome: {observed} {payload}")
    if effects(scope) != before:
        raise AssertionError("Denied duplicate, reconciliation, relay, or provider probe changed effects")
    if legacy.get(scope)["state"] != "Paid":
        raise AssertionError("Denied outcome probes changed the completed order")
    EVIDENCE["variants"][variant]["denied_outcome_cases"] = [
        "duplicate_payment", "reconciliation", "relay", "provider_conflict_probe",
    ]


def witnessed_action(server, scope, action, worker_id, point, barrier):
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(action_request, server, scope, action)
    try:
        pg_verify.witnessed(worker_id, point, server.process)
    except BaseException:
        barrier.close()
        try:
            future.result(timeout=45)
        except BaseException:
            pass
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    return pool, future


def finish_future(pool, future):
    try:
        return future.result(timeout=45)
    finally:
        pool.shutdown(wait=True, cancel_futures=True)


def observation_schedules(variant, legacy, auth):
    record = EVIDENCE["variants"][variant]

    scope = seed(legacy, "auth_observed_allow_then_revoke_add")
    set_all_grants(scope, PRINCIPAL, True)
    if not authorization(auth, scope, operation="add"):
        raise AssertionError("Stale-allow schedule did not begin with an allowed observation")
    before = effects(scope)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, auth_key=barrier.key,
                       worker=worker(variant))
        pool, future = witnessed_action(
            gated, scope, "add:250:1", gated.worker, "http_after_authorization_observation", barrier,
        )
        try:
            if effects(scope) != before:
                raise AssertionError("Execution began before the authorization observation gate opened")
            set_grant(scope, PRINCIPAL, "add", False)
            barrier.close()
            observed, payload, _ = finish_future(pool, future)
            expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
            if observed != 403 or payload != expected:
                raise AssertionError(f"Stale allowed observation survived revocation: {observed} {payload}")
            if effects(scope) != before:
                raise AssertionError("Revoked add mutated order data")
            row = legacy.get(scope)
            if row["state"] != "Draft" or row["total"] != "250":
                raise AssertionError("Revoked add changed the order snapshot")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    record["observed_revocation"] = ["add"]
    EVIDENCE["schedules"].append({"variant": variant, "case": "observed_allow_then_revoke_add",
                                  "witness": "http_after_authorization_observation", "application_name_worker": gated.worker})

    scope = seed(legacy, "auth_observed_deny_then_grant_add")
    set_grant(scope, PRINCIPAL, "add", False)
    if authorization(auth, scope, operation="add"):
        raise AssertionError("Stale-deny schedule did not begin with a denied observation")
    before = effects(scope)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, auth_key=barrier.key, worker=worker(variant))
        pool, future = witnessed_action(gated, scope, "add:250:1", gated.worker,
                                        "http_after_authorization_observation", barrier)
        try:
            if effects(scope) != before:
                raise AssertionError("Observation-only deny executed before the authorization gate")
            set_grant(scope, PRINCIPAL, "add", True)
            barrier.close()
            row = expect_action(finish_future(pool, future), gated, 200, "Added")
            if row["total"] != "500":
                raise AssertionError("Fresh grant did not permit the requested line addition")
            if effects(scope)[1] != before[1] + 1:
                raise AssertionError("Fresh grant did not authorize the observed-denied request")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    record["observed_grant"] = ["add"]
    EVIDENCE["schedules"].append({"variant": variant, "case": "observed_deny_then_grant_add",
                                  "witness": "http_after_authorization_observation"})

    scope = seed(legacy, "auth_observed_allow_then_revoke_payment")
    set_all_grants(scope, PRINCIPAL, True)
    before = effects(scope)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, auth_key=barrier.key, worker=worker(variant))
        pool, future = witnessed_action(gated, scope, "pay:p1:approve:none", gated.worker,
                                        "http_after_authorization_observation", barrier)
        try:
            if effects(scope) != before:
                raise AssertionError("Payment execution began before its authorization observation gate")
            set_grant(scope, PRINCIPAL, "pay", False)
            barrier.close()
            observed, payload, _ = finish_future(pool, future)
            expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
            if observed != 403 or payload != expected:
                raise AssertionError(f"Stale payment authorization survived revocation: {observed} {payload}")
            if effects(scope) != before:
                raise AssertionError("Revoked payment changed order, provider, or outbox state")
            if legacy.get(scope)["state"] != "Draft":
                raise AssertionError("Revoked payment changed the order state")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    record["observed_revocation"].append("payment")
    EVIDENCE["schedules"].append({"variant": variant, "case": "observed_allow_then_revoke_payment",
                                  "witness": "http_after_authorization_observation"})


def policy_revoker(scope, principal, operation, worker_id):
    if operation not in OPERATIONS:
        raise AssertionError("Unknown revoker operation")
    env = cluster.utility_environment()
    env["PGAPPNAME"] = f"roo:{worker_id}"
    query = (
        "BEGIN; "
        f"UPDATE roo_authorization.operation_grants SET allowed=FALSE WHERE scope='{scope}' AND principal='{principal}' AND operation='{operation}'; "
        "COMMIT"
    )
    process = subprocess.Popen(
        [*pg_verify.psql_command(), "-c", cluster.endpoint_guard() + query],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return process


def finish_revoker(process):
    stdout, stderr = process.communicate(timeout=20)
    if process.returncode:
        raise AssertionError(f"Policy revoker failed: {stderr.strip() or stdout.strip()}")


def execution_before_revocation(variant, legacy):
    scope = seed(legacy, "auth_execution_before_revocation")
    set_all_grants(scope, PRINCIPAL, True)
    before = effects(scope)
    worker_id = worker(variant)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="inside_prepare",
                       key=barrier.key, worker=worker_id)
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(action_request, gated, scope, "add:250:1")
        revoker = None
        try:
            pg_verify.witnessed(worker_id, "inside_prepare", gated.process)
            revoker_id = worker(variant, prefix="rev")
            revoker = policy_revoker(scope, PRINCIPAL, "add", revoker_id)
            pg_verify.witnessed(revoker_id, process=revoker)
            unrelated = policy_revoker(scope, PRINCIPAL, "refund", worker(variant, prefix="oth"))
            try:
                finish_revoker(unrelated)
            finally:
                if unrelated.poll() is None:
                    unrelated.kill()
                    unrelated.communicate(timeout=5)
            if revoker.poll() is not None or grant_state(scope, PRINCIPAL, "add") is not True:
                raise AssertionError("Same-operation revoker did not remain blocked behind execution")
            if grant_state(scope, PRINCIPAL, "refund") is not False:
                raise AssertionError("Different-operation revocation could not commit while add was locked")
            barrier.close()
            finish_revoker(revoker)
            observed, payload, _ = finish_future(pool, future)
            if (observed, payload) not in (
                (200, {"snapshot": {"scenario": scope, "state": "Draft", "total": "500",
                                     "charge_count": "0", "refund_count": "0", "event_count": "0",
                                     "consumer_count": "0", "pending_outbox": "0", "last_result": "Added",
                                     "payment_id": "-", "refund_id": "-"}}),
                (403, {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}),
            ):
                raise AssertionError(f"Execution/revocation returned an invalid result: {observed} {payload}")
            if effects(scope) != (1, before[1] + 1, 0, 0, 0, 0) or grant_state(scope, PRINCIPAL, "add") is not False:
                raise AssertionError("Revocation preceded or erased the already-authorized add")
        finally:
            barrier.close()
            if revoker is not None and revoker.poll() is None:
                revoker.kill()
                revoker.communicate(timeout=5)
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    EVIDENCE["variants"][variant]["execution_before_revocation"] = True
    EVIDENCE["schedules"].append({"variant": variant, "case": "execution_before_queued_revocation",
                                  "witnesses": ["inside_prepare", "policy_row_lock_wait"],
                                  "locked_operation": "add", "unrelated_committed_operation": "refund"})


def relay_vs_queued_revocation(variant, legacy):
    scope = seed(legacy, "auth_relay_queued_revoker", paid=True)
    set_all_grants(scope, PRINCIPAL, True)
    worker_id = worker(variant)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="before_delivery",
                       key=barrier.key, worker=worker_id)
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(action_request, gated, scope, "relay:ok")
        revoker = None
        try:
            pg_verify.witnessed(worker_id, "before_delivery", gated.process)
            if int(cluster.sql(f"SELECT count(*) FROM roo_consumer.inbox WHERE scope='{scope}'").strip()) != 0:
                raise AssertionError("Relay gate was reached after its nested inbox effect")
            revoker_id = worker(variant, prefix="rev")
            revoker = policy_revoker(scope, PRINCIPAL, "relay", revoker_id)
            pg_verify.witnessed(revoker_id, process=revoker)
            barrier.close()
            finish_revoker(revoker)
            observed, payload, _ = finish_future(pool, future)
            expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
            if observed != 403 or payload != expected:
                raise AssertionError(f"Post-revocation relay rescan did not deny: {observed} {payload}")
            if int(cluster.sql(f"SELECT count(*) FROM roo_consumer.inbox WHERE scope='{scope}'").strip()) != 1:
                raise AssertionError("Queued revoker caused a duplicate nested relay effect")
            if int(cluster.sql(f"SELECT count(*) FROM roo_app.outbox WHERE scope='{scope}' AND delivered").strip()) != 1:
                raise AssertionError("Authorized relay transaction did not commit its acknowledgement")
            if grant_state(scope, PRINCIPAL, "relay") is not False:
                raise AssertionError("Queued revocation did not commit")
        finally:
            barrier.close()
            if revoker is not None and revoker.poll() is None:
                revoker.kill()
                revoker.communicate(timeout=5)
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    EVIDENCE["variants"][variant]["relay_vs_queued_revoker"] = True
    EVIDENCE["schedules"].append({"variant": variant, "case": "relay_vs_queued_revoker",
                                  "witnesses": ["before_delivery", "policy_row_lock_wait"],
                                  "inbox_effects": 1, "delivered_outbox": 1})


def recovery_fingerprint(scope):
    # Retained identities, provider effects, lines and inbox must not change during lookup/finalize.
    return cluster.sql(
        "SELECT json_build_object("
        "'intent',(SELECT json_build_array(order_id,currency,total,payment_id,refund_id) "
        f"FROM roo_app.orders WHERE scope='{scope}'),"
        "'provider',(SELECT coalesce(json_agg(r ORDER BY kind,operation_id),'[]'::json) "
        f"FROM roo_provider.records r WHERE scope='{scope}'),"
        "'lines',(SELECT coalesce(json_agg(l ORDER BY line_no),'[]'::json) "
        f"FROM roo_app.lines l WHERE scope='{scope}'),"
        "'inbox',(SELECT coalesce(json_agg(i ORDER BY event_id),'[]'::json) "
        f"FROM roo_consumer.inbox i WHERE scope='{scope}'))"
    ).strip()


def reconcile_only_recovery(auth, legacy, scope, outcome, state):
    set_grant(scope, OTHER_PRINCIPAL, "reconcile", True)
    before = recovery_fingerprint(scope)
    prior_outbox = cluster.sql(
        f"SELECT row_to_json(o) FROM roo_app.outbox o WHERE scope='{scope}' ORDER BY event_id"
    ).splitlines()
    for operation in OPERATIONS:
        if authorization(auth, scope, OTHER_PRINCIPAL, operation=operation) != (operation == "reconcile"):
            raise AssertionError("Recovery principal unexpectedly received another operation")
        if operation != "reconcile":
            expect_forbidden(operation_request(auth, scope, operation, OTHER_PRINCIPAL))
    row = expect_action(action_request(auth, scope, "reconcile:ok:none", OTHER_PRINCIPAL), auth,
                        200 if outcome == "Approved" else 202, outcome)
    if row["state"] != state or recovery_fingerprint(scope) != before:
        raise AssertionError("Reconcile-only recovery changed retained identities or created provider/line/inbox effects")
    recovered_outbox = cluster.sql(
        f"SELECT row_to_json(o) FROM roo_app.outbox o WHERE scope='{scope}' ORDER BY event_id"
    ).splitlines()
    if not set(prior_outbox).issubset(recovered_outbox) or len(recovered_outbox) != len(prior_outbox) + (outcome == "Approved"):
        raise AssertionError("Recovery changed prior outbox records or produced incorrect terminal events")
    if legacy.get(scope)["state"] != state:
        raise AssertionError("Recovery snapshot disagrees with persisted state")
    EVIDENCE["variants"][auth.variant].setdefault("reconcile_only_recoveries", []).append({
        "scope": scope, "principal": OTHER_PRINCIPAL, "only_operation": "reconcile",
        "outcome": outcome, "state": state, "payment_id": row["payment_id"], "refund_id": row["refund_id"],
        "retained_fingerprint_sha256": hashlib.sha256(before.encode()).hexdigest(),
        "provider_lines_inbox_unchanged": True, "prior_outbox_preserved": True,
        "terminal_events_added": len(recovered_outbox) - len(prior_outbox),
    })
    return row


def durable_gaps(variant, legacy, auth):
    record = EVIDENCE["variants"][variant]

    scope = seed(legacy, "auth_revoke_after_prepare")
    set_all_grants(scope, PRINCIPAL, True)
    worker_id = worker(variant)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="after_prepare",
                       key=barrier.key, worker=worker_id)
        pool, future = witnessed_action(gated, scope, "pay:p1:approve:none", worker_id,
                                        "after_prepare", barrier)
        try:
            if legacy.get(scope)["state"] != "Pending" or effects(scope)[2:5] != (0, 0, 0):
                raise AssertionError("Prepare gate did not preserve only the pending intent")
            set_grant(scope, PRINCIPAL, "pay", False)
            barrier.close()
            observed, payload, _ = finish_future(pool, future)
            expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
            if observed != 403 or payload != expected:
                raise AssertionError(f"Prepare/effect gap was not denied after revocation: {observed} {payload}")
            if legacy.get(scope)["state"] != "Pending" or effects(scope)[2:5] != (0, 0, 0):
                raise AssertionError("Revoked prepare gap caused provider or terminal effects")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    reconcile_only_recovery(auth, legacy, scope, "NotFound", "Pending")
    if grant_state(scope, PRINCIPAL, "pay") is not False:
        raise AssertionError("Recovery erased the pay tombstone")
    set_grant(scope, PRINCIPAL, "pay", True)
    expect_action(action_request(auth, scope, "pay:p1:approve:none"), auth, 200, "Approved")
    if legacy.get(scope)["state"] != "Paid" or effects(scope)[2:4] != (1, 1):
        raise AssertionError("Same payment identity did not recover a revoked prepare gap exactly once")

    scope = seed(legacy, "auth_revoke_after_effect")
    set_all_grants(scope, PRINCIPAL, True)
    worker_id = worker(variant)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="after_effect",
                       key=barrier.key, worker=worker_id)
        pool, future = witnessed_action(gated, scope, "pay:p1:approve:none", worker_id,
                                        "after_effect", barrier)
        try:
            if legacy.get(scope)["state"] != "Pending" or effects(scope)[2:5] != (0, 1, 0):
                raise AssertionError("Effect gate did not preserve one provider effect and a pending intent")
            set_grant(scope, PRINCIPAL, "pay", False)
            barrier.close()
            observed, payload, _ = finish_future(pool, future)
            expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
            if observed != 403 or payload != expected:
                raise AssertionError(f"Effect/finalization gap was not denied after revocation: {observed} {payload}")
            if legacy.get(scope)["state"] != "Pending" or effects(scope)[2:5] != (0, 1, 0):
                raise AssertionError("Denied finalization changed the retained provider effect")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    reconcile_only_recovery(auth, legacy, scope, "Approved", "Paid")
    expect_forbidden(action_request(auth, scope, "pay:p1:approve:none"))
    set_grant(scope, PRINCIPAL, "pay", True)
    expect_action(action_request(auth, scope, "pay:p1:approve:none"), auth, 200, "AlreadyApplied")
    if legacy.get(scope)["state"] != "Paid" or effects(scope)[2:4] != (1, 1):
        raise AssertionError("Authorized same-key reconciliation did not finalize one retained provider effect")
    record["durable_gaps"] = [
        {"case": "revoked_after_prepare", "witness": "after_prepare", "recovery": "bob reconcile-only NotFound; original payment retry"},
        {"case": "revoked_after_effect", "witness": "after_effect", "recovery": "bob reconcile-only; original payment identity retained"},
    ]
    EVIDENCE["schedules"].extend([
        {"variant": variant, "case": "revoked_after_prepare", "witness": "after_prepare"},
        {"variant": variant, "case": "revoked_after_effect", "witness": "after_effect"},
    ])


def observed_disconnect(future):
    try:
        result = future.result(timeout=20)
    except (http.client.HTTPException, OSError) as error:
        return type(error).__name__
    raise AssertionError(f"Killed HTTP process unexpectedly returned {result}")


def process_crash(variant, legacy):
    scope = seed(legacy, "auth_process_crash_after_effect")
    set_all_grants(scope, PRINCIPAL, True)
    worker_id = worker(variant)
    gated = fresh = None
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="after_effect",
                       key=barrier.key, worker=worker_id)
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(action_request, gated, scope, "pay:p1:approve:none")
        try:
            pg_verify.witnessed(worker_id, "after_effect", gated.process)
            if effects(scope)[2:5] != (0, 1, 0):
                raise AssertionError("Crash gate did not witness the durable provider effect")
            set_grant(scope, PRINCIPAL, "pay", False)
            set_grant(scope, PRINCIPAL, "reconcile", False)
            policy_before = {operation: grant_state(scope, PRINCIPAL, operation) for operation in OPERATIONS}
            gated.stop(crash=True)
            disconnect = observed_disconnect(future)
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            if gated.process.poll() is None:
                gated.stop(crash=True)
    try:
        if legacy.get(scope)["state"] != "Pending" or effects(scope)[2:5] != (0, 1, 0):
            raise AssertionError("Killed request did not preserve a pending intent and one provider effect")
        fresh = Server(variant, auth=True, principal=PRINCIPAL, worker=worker(variant))
        expect_error(fresh, "POST", f"/v1/scopes/{scope}/reconciliation", {}, 403, "Forbidden")
        policy_after = {operation: grant_state(scope, PRINCIPAL, operation) for operation in OPERATIONS}
        if policy_after != policy_before:
            raise AssertionError("API restart changed operation grants or tombstones")
        reconcile_only_recovery(fresh, legacy, scope, "Approved", "Paid")
        expect_forbidden(action_request(fresh, scope, "pay:p1:approve:none"))
        if legacy.get(scope)["state"] != "Paid" or effects(scope)[2:4] != (1, 1):
            raise AssertionError("Fresh authorized process did not recover the single effect")
    finally:
        if fresh is not None:
            fresh.stop()
    EVIDENCE["variants"][variant]["process_crash"] = {
        "signal": "SIGKILL", "gate": "after_effect", "client_disconnect": disconnect,
        "recovery": "fresh HTTP process; denial then distinct reconcile-only principal",
        "operation_policy_before": policy_before, "operation_policy_after": policy_after,
    }


def refund_prepare_gap(variant, legacy, auth):
    scope = seed(legacy, "auth_refund_prepare_gap", paid=True)
    set_all_grants(scope, PRINCIPAL, True)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="after_prepare",
                       key=barrier.key, worker=worker(variant))
        pool, future = witnessed_action(gated, scope, "refund:r1:approve:none", gated.worker,
                                        "after_prepare", barrier)
        try:
            row = legacy.get(scope)
            if row["state"] != "Refunding" or row["refund_id"] != "r1" or effects(scope)[2:5] != (1, 1, 0):
                raise AssertionError("Refund prepare gap did not preserve only the retained refund intent")
            set_grant(scope, PRINCIPAL, "refund", False)
            barrier.close()
            expect_forbidden(finish_future(pool, future))
            if legacy.get(scope)["state"] != "Refunding" or effects(scope)[2:5] != (1, 1, 0):
                raise AssertionError("Revoked refund prepare gap created an effect or terminal event")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()
    reconcile_only_recovery(auth, legacy, scope, "NotFound", "Refunding")
    expect_forbidden(action_request(auth, scope, "refund:r1:approve:none"))
    set_grant(scope, PRINCIPAL, "refund", True)
    recovered = expect_action(action_request(auth, scope, "refund:r1:approve:none"), auth, 200, "Approved")
    if recovered["state"] != "Refunded" or recovered["refund_id"] != "r1" or effects(scope)[2:4] != (2, 2):
        raise AssertionError("Same refund identity retry did not create exactly one retained effect")
    EVIDENCE["variants"][variant]["refund_prepare_gap"] = {
        "witness": "after_prepare", "denied_operation": "refund", "retained_refund_id": "r1",
        "recovery": "bob reconcile-only NotFound; original refund retry", "refund_effects": 1,
    }
    EVIDENCE["schedules"].append({"variant": variant, "case": "revoked_after_refund_prepare",
                                  "witness": "after_prepare", "operation": "refund"})


def refund_recovery(variant, legacy, auth):
    scope = seed(legacy, "auth_refund_recovery", paid=True)
    set_all_grants(scope, PRINCIPAL, True)
    worker_id = worker(variant)
    with pg_verify.Barrier() as barrier:
        gated = Server(variant, auth=True, principal=PRINCIPAL, point="after_effect",
                       key=barrier.key, worker=worker_id)
        pool, future = witnessed_action(gated, scope, "refund:r1:approve:none", worker_id,
                                        "after_effect", barrier)
        try:
            pending = legacy.get(scope)
            refund_effects = int(cluster.sql(
                f"SELECT count(*) FROM roo_provider.records WHERE scope='{scope}' AND kind='refund'"
            ).strip())
            refund_events = int(cluster.sql(
                f"SELECT count(*) FROM roo_app.outbox WHERE scope='{scope}' AND event_kind='RefundApproved'"
            ).strip())
            if pending["state"] != "Refunding" or pending["refund_id"] != "r1":
                raise AssertionError("Refund effect gate did not preserve the prepared refund intent")
            if refund_effects != 1 or refund_events != 0:
                raise AssertionError("Refund effect gate did not expose one effect and no terminal event")
            set_grant(scope, PRINCIPAL, "refund", False)
            barrier.close()
            observed, payload, _ = finish_future(pool, future)
            expected = {"error": {"code": "Forbidden", "message": MESSAGES["Forbidden"]}}
            if observed != 403 or payload != expected:
                raise AssertionError(f"Revoked refund finalization was not denied: {observed} {payload}")
            if legacy.get(scope)["state"] != "Refunding" or int(cluster.sql(
                f"SELECT count(*) FROM roo_provider.records WHERE scope='{scope}' AND kind='refund'"
            ).strip()) != 1:
                raise AssertionError("Denied refund finalization changed its retained provider effect")
        finally:
            barrier.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gated.stop()

    reconciled = reconcile_only_recovery(auth, legacy, scope, "Approved", "Refunded")
    expect_forbidden(action_request(auth, scope, "refund:r1:approve:none"))
    set_grant(scope, PRINCIPAL, "refund", True)
    if reconciled["state"] != "Refunded" or reconciled["refund_id"] != "r1":
        raise AssertionError("Authorized reconciliation did not complete the retained refund")
    replay = expect_action(action_request(auth, scope, "refund:r1:approve:none"), auth, 200, "AlreadyApplied")
    if replay["state"] != "Refunded":
        raise AssertionError("Same refund key replay changed the terminal state")
    refund_effects = int(cluster.sql(
        f"SELECT count(*) FROM roo_provider.records WHERE scope='{scope}' AND kind='refund'"
    ).strip())
    refund_events = int(cluster.sql(
        f"SELECT count(*) FROM roo_app.outbox WHERE scope='{scope}' AND event_kind='RefundApproved'"
    ).strip())
    if refund_effects != 1 or refund_events != 1 or effects(scope)[2:4] != (2, 2):
        raise AssertionError("Refund recovery did not preserve exactly one provider effect and terminal event")
    EVIDENCE["variants"][variant]["refund_recovery"] = {
        "case": "revoked_after_refund_effect",
        "witness": "after_effect",
        "denied_state": "Refunding",
        "refund_provider_effects": refund_effects,
        "refund_terminal_events": refund_events,
        "recovery": "distinct reconcile-only principal; original refund tombstone then explicit same-key replay",
    }
    EVIDENCE["schedules"].append({"variant": variant, "case": "revoked_after_refund_effect",
                                  "witness": "after_effect", "refund_provider_effects": 1,
                                  "refund_terminal_events": 1})


def restart(auth_servers, legacy_servers):
    scopes = []
    operation_policies = {}
    for variant in VARIANTS:
        auth = auth_servers[variant]
        legacy = legacy_servers[variant]
        denied = seed(legacy, "auth_restart_denied_effect")
        granted = seed(legacy, "auth_restart_granted_effect")
        for scope in (denied, granted):
            set_all_grants(scope, PRINCIPAL, True)
            expect_action(action_request(auth, scope, "pay:p1:timeout_after:none"), auth, 202, "Unknown")
        set_grant(denied, PRINCIPAL, "read", False)
        set_grant(denied, PRINCIPAL, "reconcile", False)
        for scope in (denied, granted):
            for operation in ("init", "add", "refund", "relay", "provider_conflict"):
                set_grant(scope, PRINCIPAL, operation, False)
            operation_policies[scope] = {operation: grant_state(scope, PRINCIPAL, operation) for operation in OPERATIONS}
        scopes.extend(((variant, "denied", denied, legacy), (variant, "granted", granted, legacy)))

    before = cluster.sql(
        "SELECT pg_postmaster_start_time(),current_setting('server_version_num'),"
        "current_setting('fsync'),current_setting('synchronous_commit'),current_setting('full_page_writes')"
    ).strip()
    log_path = cluster.RUNTIME / "server.log"
    log_offset = log_path.stat().st_size
    pids = {variant: auth_servers[variant].process.pid for variant in VARIANTS}
    try:
        cluster.stop("immediate")
        for variant in VARIANTS:
            server = auth_servers[variant]
            scope = next(scope for item_variant, _, scope, _ in scopes if item_variant == variant)
            expect_error(server, "GET", f"/v1/scopes/{scope}", None, 503, "DatabaseUnavailable")
    finally:
        cluster.start()
    after = cluster.sql(
        "SELECT pg_postmaster_start_time(),current_setting('server_version_num'),"
        "current_setting('fsync'),current_setting('synchronous_commit'),current_setting('full_page_writes')"
    ).strip()
    if before.split("|")[0] == after.split("|")[0]:
        raise AssertionError("PostgreSQL postmaster did not restart")
    with log_path.open("rb") as handle:
        handle.seek(log_offset)
        lines = handle.read().decode(errors="replace").splitlines()
    recovery = [line for line in lines if any(term in line for term in
                ("interrupted", "not properly shut down", "redo starts", "redo done", "ready to accept"))]
    if not any("redo" in line for line in recovery):
        raise AssertionError("No WAL redo evidence after immediate PostgreSQL restart")

    for variant, kind, scope, legacy in scopes:
        server = auth_servers[variant]
        if server.process.poll() is not None or server.process.pid != pids[variant]:
            raise AssertionError(f"{variant}: HTTP process did not survive PostgreSQL restart")
        after_policy = {operation: grant_state(scope, PRINCIPAL, operation) for operation in OPERATIONS}
        if after_policy != operation_policies[scope]:
            raise AssertionError("Immediate PostgreSQL restart changed operation grants or tombstones")
        for operation in OPERATIONS:
            if authorization(server, scope, operation=operation) != after_policy[operation]:
                raise AssertionError("Post-restart observation disagreed with durable operation policy")
        if kind == "denied":
            if grant_state(scope, PRINCIPAL) is not False:
                raise AssertionError("Revoked policy tombstone did not survive PostgreSQL restart")
            expect_error(server, "GET", f"/v1/scopes/{scope}", None, 403, "Forbidden")
            expect_error(server, "POST", f"/v1/scopes/{scope}/reconciliation", {}, 403, "Forbidden")
            if legacy.get(scope)["state"] != "Pending" or effects(scope)[2:5] != (0, 1, 0):
                raise AssertionError("Denied post-restart reconciliation changed durable state")
            reconcile_only_recovery(server, legacy, scope, "Approved", "Paid")
            expect_forbidden(operation_request(server, scope, "read"))
            expect_forbidden(action_request(server, scope, "reconcile:ok:none"))
        else:
            if grant_state(scope, PRINCIPAL) is not True:
                raise AssertionError("Allowed policy did not survive PostgreSQL restart")
            if server.get(scope)["state"] != "Pending":
                raise AssertionError("Allowed post-restart read did not observe persisted pending state")
            expect_action(action_request(server, scope, "reconcile:ok:none"), server, 200, "Approved")
        if legacy.get(scope)["state"] != "Paid" or effects(scope)[2:4] != (1, 1):
            raise AssertionError("Restart recovery did not finalize exactly one existing provider effect")

    EVIDENCE["restart"] = {
        "mode": "immediate",
        "operation_policies": operation_policies,
        "policy_rows_compared": len(operation_policies) * len(OPERATIONS),
        "before": before,
        "after": after,
        "wal_recovery_log": recovery,
        "preserved_policy_and_effect_scopes": len(scopes),
        "surviving_http_pids": pids,
        "database_unavailable_responses": len(VARIANTS),
        "denied_original_then_distinct_principal_reconciliation": len(VARIANTS),
        "allowed_reconciliation": len(VARIANTS),
    }


def source_hashes():
    paths = [
        CASE / "support.py", CASE / "verify_authorization.py", CASE / "schema.sql",
        CASE / "java/src/roo/postgres/HttpProtocol.java", CASE / "java/src/roo/postgres/HttpService.java",
        CASE / "java/src/roo/postgres/HttpUnitTests.java",
        CASE / "rust/src/lib.rs", CASE / "rust/src/main.rs",
        CASE.parent / "postgres/schema.sql", CASE.parent / "postgres/java/src/roo/postgres/Database.java",
        CASE.parent / "postgres/java/src/roo/postgres/Store.java",
        CASE.parent / "postgres/java/src/roo/postgres/Provider.java",
        CASE.parent / "postgres/java/src/roo/postgres/Operation.java",
        CASE.parent / "postgres/java/src/roo/postgres/UnitTests.java",
        CASE.parent / "postgres/rust/src/database.rs", CASE.parent / "postgres/rust/src/lib.rs",
    ]
    return {str(path.relative_to(CASE.parents[2])): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def write_receipt():
    EVIDENCE["source_sha256"] = source_hashes()
    EVIDENCE["barriers"] = pg_verify.EVIDENCE["barriers"]
    EVIDENCE["http_processes"] = [
        {"variant": server.variant, "worker": server.worker, "pid": server.process.pid,
         "returncode": server.process.poll()}
        for server in PROCESSES
    ]
    EVIDENCE["all_http_processes_stopped"] = all(server.process.poll() is not None for server in PROCESSES)
    path = CASE / ".runtime/authorization-last-run.json"
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.write_text(json.dumps(EVIDENCE, indent=2) + "\n")


def main():
    failure = None
    auth_servers = {}
    legacy_servers = {}
    cluster_ready = False
    try:
        cluster.start()
        cluster_ready = True
        cluster.apply_schema()
        cluster.sql((CASE / "schema.sql").read_text())
        if cluster.sql("SELECT to_regclass('roo_authorization.operation_grants')").strip() != "roo_authorization.operation_grants":
            raise AssertionError("HTTP authorization fixture schema was not installed")

        for variant in VARIANTS:
            EVIDENCE["variants"][variant] = {}
            startup_rejections(variant)
            legacy = Server(variant)
            legacy_servers[variant] = legacy
            auth = Server(variant, auth=True, principal=PRINCIPAL)
            auth_servers[variant] = auth
            expect_error(legacy, "GET", "/v1/scopes/legacy_auth_route/authorization", None,
                         404, "RouteNotFound")
            identity_and_isolation(variant, legacy, auth)
            operation_matrix(variant, legacy, auth)
            coarse_and_route_contract(variant, legacy, auth)
            hidden_outcomes(variant, legacy, auth)
            observation_schedules(variant, legacy, auth)
            execution_before_revocation(variant, legacy)
            relay_vs_queued_revocation(variant, legacy)
            durable_gaps(variant, legacy, auth)
            process_crash(variant, legacy)
            refund_prepare_gap(variant, legacy, auth)
            refund_recovery(variant, legacy, auth)
            EVIDENCE["variants"][variant]["status"] = "PASS"
            print(f"PASS {variant}: authorization boundary, witnessed revocation, durable gaps and process recovery", flush=True)

        restart(auth_servers, legacy_servers)
        EVIDENCE["status"] = "PASS"
    except BaseException as error:
        EVIDENCE["status"] = "FAIL"
        EVIDENCE["errors"].append(f"{type(error).__name__}: {error}")
        failure = error
    finally:
        if cluster_ready:
            try:
                config = cluster.configuration()
                if not cluster.running(config):
                    cluster.start()
            except BaseException as error:
                EVIDENCE["status"] = "FAIL"
                EVIDENCE["errors"].append(f"cluster cleanup: {type(error).__name__}: {error}")
                if failure is None:
                    failure = error
        try:
            cleanup()
        except BaseException as error:
            EVIDENCE["status"] = "FAIL"
            EVIDENCE["errors"].append(f"HTTP cleanup: {type(error).__name__}: {error}")
            if failure is None:
                failure = error
        EVIDENCE["all_http_processes_stopped"] = all(server.process.poll() is not None for server in PROCESSES)
        if not EVIDENCE["all_http_processes_stopped"]:
            EVIDENCE["status"] = "FAIL"
            EVIDENCE["errors"].append("one or more owned HTTP processes remained alive")
            if failure is None:
                failure = AssertionError("Owned HTTP process cleanup incomplete")
        try:
            write_receipt()
        except BaseException as error:
            EVIDENCE["status"] = "FAIL"
            EVIDENCE["errors"].append(f"receipt: {type(error).__name__}: {error}")
            if failure is None:
                failure = error
    if failure is not None:
        raise failure
    print("PASS PostgreSQL immediate restart: persisted grants, tombstones and provider effects recovered", flush=True)
    print("PASS all owned HTTP processes stopped; receipt: http/.runtime/authorization-last-run.json", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError, RuntimeError, subprocess.SubprocessError,
            http.client.HTTPException) as failure:
        print(f"FAIL {failure}", file=sys.stderr)
        sys.exit(1)
