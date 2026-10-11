#!/usr/bin/env python3
"""Owned HTTP process lifecycle and real HTTP client; no database mutation."""

import http.client
import importlib.util
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time
import uuid

CASE = Path(__file__).resolve().parent
PG = CASE.parent / "postgres"
sys.path.insert(0, str(PG))
import cluster  # noqa: E402

spec = importlib.util.spec_from_file_location("roo_pg_verify", PG / "verify.py")
pg_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg_verify)
HEADER = pg_verify.HEADER
RUN = "http_" + uuid.uuid4().hex[:12]
PROCESSES = []
STATUS = {**dict.fromkeys(("Added", "Approved", "Declined", "AlreadyApplied", "AlreadyDeclined", "RelayOk"), 200),
          **dict.fromkeys(("Unknown", "NotFound"), 202),
          **dict.fromkeys(("InvalidState", "IntentConflict", "KeyConflict"), 409),
          **dict.fromkeys(("InvalidLine", "Overflow", "InvalidOrder"), 422),
          **dict.fromkeys(("LocalPrepareFailed", "LocalCommitFailed", "RelaySendFailed", "RelayAckFailed"), 503)}
MESSAGES = {"InvalidRequest": "Invalid request", "RouteNotFound": "Route not found",
            "MethodNotAllowed": "Method not allowed", "ScopeNotFound": "Scope not found",
            "UnsupportedMediaType": "Unsupported media type", "BodyTooLarge": "Body too large",
            "NotAcceptable": "Not acceptable", "DatabaseUnavailable": "Database unavailable",
            "InternalError": "Internal error", "Busy": "Server busy"}


def unique(label):
    return f"{RUN}_{label}_{uuid.uuid4().hex[:6]}"


def require(row, **expected):
    pg_verify.require(row, **expected)


def command(variant):
    if variant.startswith("Java"):
        classes = str(CASE / "java/build/classes")
        jars = [str(PG / ".deps/postgresql-42.7.14.jar"), str(CASE / ".deps/jackson-core-2.22.3.jar")]
        entry = "HttpCompositionServer" if variant == "Java composition" else "HttpTemplateServer"
        return ["java", "--add-modules", "jdk.httpserver", "-cp", os.pathsep.join([classes, *jars]), "roo.postgres." + entry]
    return [str(CASE / "rust/target/debug/roo-http")]


def environment(test=True, point=None, key=None, http_key=None, worker=None):
    env = {**os.environ, **cluster.environment()}
    for name in ("ROO_GATE_POINT", "ROO_GATE_LOCK", "ROO_HTTP_GATE_LOCK", "ROO_HTTP_TEST_MODE", "ROO_RUN_ID"):
        env.pop(name, None)
    env.update(ROO_HTTP_HOST="127.0.0.1", ROO_HTTP_PORT="0", ROO_WORKER_ID=worker or unique("worker")[-32:])
    if test:
        env["ROO_HTTP_TEST_MODE"] = "1"
    if point:
        env.update(ROO_GATE_POINT=point, ROO_GATE_LOCK=str(key))
    if http_key:
        env["ROO_HTTP_GATE_LOCK"] = str(http_key)
    return env


class Server:
    def __init__(self, variant, **settings):
        self.variant = variant
        self.env = environment(**settings)
        self.worker = self.env["ROO_WORKER_ID"]
        runtime = CASE / ".runtime"
        runtime.mkdir(mode=0o700, exist_ok=True)
        self.log = (runtime / f"{self.worker}.stderr.log").open("w")
        self.process = subprocess.Popen(command(variant), env=self.env, stdout=subprocess.PIPE, stderr=self.log)
        PROCESSES.append(self)
        selector = selectors.DefaultSelector()
        selector.register(self.process.stdout, selectors.EVENT_READ)
        deadline, received = time.monotonic() + 15, b""
        try:
            while b"\n" not in received:
                if time.monotonic() >= deadline or self.process.poll() is not None:
                    raise AssertionError(f"{variant}: server did not become ready ({self.worker})")
                if selector.select(timeout=0.1):
                    data = os.read(self.process.stdout.fileno(), 4096)
                    if not data:
                        raise AssertionError(f"{variant}: startup stream closed")
                    received += data
                    if len(received) > 2048:
                        raise AssertionError("Unbounded readiness output")
            ready = json.loads(received.split(b"\n", 1)[0])
            if set(ready) != {"host", "port", "ready"} or ready["host"] != "127.0.0.1" or ready["ready"] is not True or type(ready["port"]) is not int or not 1 <= ready["port"] <= 65535:
                raise AssertionError("Invalid readiness contract")
            self.port = ready["port"]
        except BaseException:
            self.stop()
            raise
        finally:
            selector.close()

    def stop(self, crash=False):
        if self.process.poll() is None:
            if crash:
                self.process.kill()
            else:
                self.process.terminate()
            try:
                self.process.wait(timeout=190)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
                if not crash:
                    raise AssertionError("Graceful HTTP server termination exceeded its bound")
        if crash and self.process.returncode != -9:
            raise AssertionError("HTTP crash did not terminate with SIGKILL")
        self.process.stdout.close()
        self.log.close()

    def request(self, method, path, body=None, *, headers=None, raw=False, chunked=False):
        data = body if raw else json.dumps(body, separators=(",", ":")).encode() if body is not None else None
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=35)
        try:
            connection.putrequest(method, path)
            for key, value in (headers if headers is not None else [("Accept", "application/json"), *([("Content-Type", "application/json")] if data is not None else [])]):
                connection.putheader(key, value)
            if chunked:
                connection.putheader("Transfer-Encoding", "chunked")
            elif data is not None:
                connection.putheader("Content-Length", str(len(data)))
            connection.endheaders()
            if data is not None:
                connection.send((f"{len(data):X}\r\n".encode() + data + b"\r\n0\r\n\r\n") if chunked else data)
            response = connection.getresponse()
            content = response.read(65537)
            if len(content) > 65536:
                raise AssertionError("Response exceeded harness bound")
            if response.getheader("Content-Type", "").lower().split(";")[0] != "application/json" or response.getheader("Cache-Control") != "no-store" or response.getheader("Connection", "").lower() != "close":
                raise AssertionError(f"Incorrect JSON/cache/connection headers: {response.getheaders()}")
            payload = json.loads(content.decode("utf-8"))
            return response.status, payload, dict(response.getheaders())
        finally:
            connection.close()

    def snapshot_response(self, method, path, body=None, **options):
        status, payload, _ = self.request(method, path, body, **options)
        if set(payload) != {"snapshot"} or set(payload["snapshot"]) != set(HEADER) or not all(type(v) is str for v in payload["snapshot"].values()):
            raise AssertionError(f"{self.variant}: incorrect snapshot response {status}: {payload}")
        row = payload["snapshot"]
        requested_scope = path.split("/")[3]
        if row["scenario"] != requested_scope:
            raise AssertionError(f"{self.variant}: snapshot scenario does not match requested scope")
        expected = 200 if row["last_result"] == "-" else STATUS[row["last_result"]]
        if status != expected:
            raise AssertionError(f"{self.variant}: {row['last_result']} status {status}, expected {expected}")
        return row

    def get(self, scope):
        return self.snapshot_response("GET", "/v1/scopes/" + scope)

    def init(self, scope):
        return self.snapshot_response("PUT", "/v1/scopes/" + scope, {})

    def step(self, scope, action, outcome=None):
        endpoint, body = translate(action)
        headers = [("Accept", "application/json"), ("Content-Type", "application/json")]
        if endpoint in ("payments", "refunds"):
            headers.append(("Idempotency-Key", body.get("payment_id", body.get("refund_id"))))
        row = self.snapshot_response("POST", "/v1/scopes/" + scope + "/" + endpoint, body, headers=headers)
        if outcome is not None:
            require(row, last_result=outcome)
        return row

    def seed(self, label, state="Draft"):
        scope = unique(label)
        self.init(scope)
        self.step(scope, "add:250:1", "Added")
        if state in ("Paid", "Refunded"):
            self.step(scope, "pay:p1:approve:none", "Approved")
        if state == "Refunded":
            self.step(scope, "refund:r1:approve:none", "Approved")
        return scope


def translate(action):
    f = action.split(":")
    if f[0] == "add":
        return "lines", {"unit_minor": f[1], "quantity": f[2]}
    if f[0] in ("pay", "refund"):
        name, identity = ("payments", "payment_id") if f[0] == "pay" else ("refunds", "refund_id")
        body = {identity: f[1]}
        if f[2] != "approve": body["mode"] = f[2]
        if f[3] != "none": body["failure"] = f[3]
        return name, body
    if f[0] == "reconcile":
        return "reconciliation", {**({"lookup": f[1]} if f[1] != "ok" else {}), **({"failure": f[2]} if f[2] != "none" else {})}
    if f[0] == "relay":
        return "relay", {"mode": f[1]} if f[1] != "ok" else {}
    if f[0] == "conflict":
        return "_test/provider-conflicts", {"payment_id": f[1], "different_amount": f[2]}
    raise AssertionError("Unknown source fixture action")


def state(server, scope, name, total=250, charges=1, refunds=0, events=1,
          consumers=0, pending=None, payment="p1", refund="-"):
    row = server.get(scope)
    require(row, state=name, total=total, charge_count=charges, refund_count=refunds,
            event_count=events, consumer_count=consumers, pending_outbox=events if pending is None else pending,
            payment_id=payment, refund_id=refund, last_result="-")
    return row


def cleanup():
    failures = []
    for server in reversed(PROCESSES):
        try:
            server.stop()
        except (OSError, subprocess.SubprocessError, AssertionError) as error:
            failures.append(str(error))
    if failures:
        raise AssertionError("HTTP cleanup failed: " + "; ".join(failures))
