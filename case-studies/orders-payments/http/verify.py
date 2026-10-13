#!/usr/bin/env python3
"""One independent oracle for real Java/Rust HTTP and durable recovery."""

from concurrent.futures import ThreadPoolExecutor
import argparse
import csv
import http.client
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import sys
import time

from support import (CASE, HEADER, MESSAGES, PROCESSES, RUN, Server, cleanup, cluster,
                     command, environment, pg_verify, require, state, unique)

# A local run writes only the scratch receipt under .runtime/, so the dated
# receipts tracked in research/ are never replaced by accident. Pass
# --evidence-output or set this variable to publish a receipt somewhere else;
# CI gives each verification phase its own path.
EVIDENCE_ENV = "ROO_EVIDENCE_PATH"
EVIDENCE = {"run_id": RUN, "variants": {}, "restart": {}, "status": "RUNNING"}
BODY_READERS = 16
BODY_READ_DEADLINE_SECONDS = 5


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
        ("disabled_authorization_extra_segment", "GET", path + "/authorization/read/extra", None, 400, "InvalidRequest", {}),
        ("route_before_accept", "GET", path + "/unknown", None, 404, "RouteNotFound", {"headers": [("Accept", "text/html")]}),
        ("path_before_accept", "GET", path + "?x=1", None, 400, "InvalidRequest", {"headers": [("Accept", "text/html")]}),
        ("method_before_accept", "DELETE", pay, {}, 405, "MethodNotAllowed", {"headers": [("Accept", "text/html")]}),
        ("method_before_body_limit", "DELETE", pay, b" " * 8193, 405, "MethodNotAllowed", {"raw": True}),
        ("accept_before_body_limit", "POST", pay, b" " * 8193, 406, "NotAcceptable", {"raw": True, "headers": [*json_headers, ("Accept", "text/html")]}),
        ("media_before_body_limit", "POST", pay, b" " * 8193, 415, "UnsupportedMediaType", {"raw": True, "headers": [("Content-Type", "text/plain")]}),
        ("key_before_body_limit", "POST", pay, b" " * 8193, 400, "InvalidRequest", {"raw": True, "headers": [*json_headers, ("Idempotency-Key", "bad-key")]}),
        ("unknown_route", "GET", path + "/unknown", None, 404, "RouteNotFound", {}),
        ("missing_scope_get", "GET", "/v1/scopes/" + unique("missing"), None, 404, "ScopeNotFound", {}),
        ("missing_scope_post", "POST", "/v1/scopes/" + unique("missing") + "/payments", {"payment_id": "p1"}, 404, "ScopeNotFound", {}),
        ("query_string", "GET", path + "?x=1", None, 400, "InvalidRequest", {}),
        ("fragment", "GET", path + "#ignored", None, 400, "InvalidRequest", {}),
        ("empty_fragment", "GET", path + "#", None, 400, "InvalidRequest", {}),
        ("encoded_path", "GET", path.replace("_", "%5F", 1), None, 400, "InvalidRequest", {}),
        ("trailing_slash", "GET", path + "/", None, 400, "InvalidRequest", {}),
        ("duplicate_content_type", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, *json_headers]}),
        ("duplicate_accept", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Accept", "*/*"), ("Accept", "application/json")]}),
        ("duplicate_before_accept_value", "POST", pay, {}, 400, "InvalidRequest", {"headers": [*json_headers, ("Accept", "text/html"), ("Accept", "application/json")]}),
        ("key_mismatch", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p2")]}),
        ("key_on_non_idempotent_add", "POST", lines, {"unit_minor": "1", "quantity": "1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p1")]}),
        ("duplicate_key_header", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p1"), ("Idempotency-Key", "p1")]}),
        ("comma_joined_key", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("Idempotency-Key", "p1,p1")]}),
        ("unsupported_drop_header", "POST", pay, {"payment_id": "p1"}, 400, "InvalidRequest", {"headers": [*json_headers, ("X-Roo-Test-Drop-Response", "true")]}),
        ("get_body", "GET", path, {}, 400, "InvalidRequest", {}),
        ("invalid_control_enum", "POST", pay, {"payment_id": "p1", "mode": "random"}, 400, "InvalidRequest", {}),
        ("empty_put_missing_media_type", "PUT", path, None, 415, "UnsupportedMediaType", {"headers": []}),
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


class _BodyReaderClient:
    """Bounded raw HTTP reader preserving coalesced interim and final responses."""
    def __init__(self, port, deadline):
        self.socket = socket.create_connection(("127.0.0.1", port), timeout=self.remaining(deadline))
        self.buffer = bytearray()
        self.continues = 0
        self.final = None
        self.closed = False

    @staticmethod
    def remaining(deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise AssertionError("Body-reader observation exceeded its absolute deadline")
        return remaining

    def send(self, data, deadline):
        self.socket.settimeout(self.remaining(deadline))
        self.socket.sendall(data)
        self.socket.setblocking(False)
        self.remaining(deadline)

    def receive(self):
        try:
            data = self.socket.recv(4096)
        except BlockingIOError:
            return
        except ConnectionResetError:
            data = b""
        if not data:
            self.closed = True
            if self.buffer:
                raise AssertionError("Incomplete body-reader HTTP response")
            return
        self.buffer.extend(data)
        if len(self.buffer) > 65536:
            raise AssertionError("Body-reader response exceeded harness bound")
        self.parse()

    def parse(self):
        while b"\r\n\r\n" in self.buffer:
            head, tail = self.buffer.split(b"\r\n\r\n", 1)
            lines = head.decode("ascii").split("\r\n")
            fields = lines[0].split(" ", 2)
            if len(fields) < 2 or fields[0] not in ("HTTP/1.0", "HTTP/1.1"):
                raise AssertionError("Invalid body-reader HTTP status line")
            status = int(fields[1])
            headers = {}
            for line in lines[1:]:
                key, value = line.split(":", 1)
                key = key.lower()
                if key in headers:
                    raise AssertionError("Duplicate body-reader response header")
                headers[key] = value.strip()
            if "transfer-encoding" in headers:
                raise AssertionError("Unsupported body-reader transfer encoding")
            if status == 100:
                if self.final is not None or self.continues or headers.get("content-length", "0") != "0":
                    raise AssertionError("Unexpected interim body-reader response")
                self.continues += 1
                self.buffer = bytearray(tail)
                continue
            length = headers.get("content-length", "")
            if not length.isascii() or not length.isdecimal() or int(length) > 65536:
                raise AssertionError("Unbounded body-reader response framing")
            length = int(length)
            if len(tail) < length:
                return
            if self.final is not None or len(tail) != length:
                raise AssertionError("Unexpected extra body-reader response bytes")
            if (headers.get("content-type", "").lower().split(";")[0] != "application/json"
                    or headers.get("cache-control") != "no-store"
                    or headers.get("connection", "").lower() != "close"):
                raise AssertionError("Incorrect body-reader response headers")
            self.final = (status, json.loads(tail.decode("utf-8")), headers)
            self.buffer.clear()

    def close(self):
        self.socket.close()


def _poll_body_clients(clients, deadline):
    active = [client for client in clients if not client.closed]
    readable, _, _ = select.select([client.socket for client in active], [], [],
                                 min(0.1, _BodyReaderClient.remaining(deadline)))
    _BodyReaderClient.remaining(deadline)
    for client in active:
        if client.socket in readable:
            client.receive()
    # A complete exact Busy response arriving at or after the cutoff is a failure.
    _BodyReaderClient.remaining(deadline)


def _body_error(client, status, code):
    expected = {"error": {"code": code, "message": MESSAGES[code]}}
    if client.final is None or client.final[:2] != (status, expected):
        raise AssertionError(f"Unexpected body-reader response: {client.final}; expected {status} {expected}")


def _body_get(server, path, deadline, observers=()):
    client = _BodyReaderClient(server.port, deadline)
    try:
        client.send((f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n"
                     "Accept: application/json\r\nConnection: close\r\n\r\n").encode("ascii"), deadline)
        while client.final is None:
            _poll_body_clients([*observers, client], deadline)
            if client.closed and client.final is None:
                raise AssertionError("Body-reader GET closed without a response")
        _BodyReaderClient.remaining(deadline)
        return client.final
    finally:
        client.close()


def bounded_body_readers(server):
    """Establish 16 held readers before an unrelated GET can compete for a permit."""
    scope = server.seed("slow_body")
    before = server.get(scope)
    path = "/v1/scopes/" + scope
    target = path + "/payments"
    prefix = (f"POST {target} HTTP/1.1\r\n"
              f"Host: 127.0.0.1:{server.port}\r\n"
              "Accept: application/json\r\nContent-Type: application/json\r\n"
              "Content-Length: 20\r\nExpect: 100-continue\r\n"
              "Connection: close\r\n\r\n").encode("ascii")
    error(server, "POST", target, b"", 400, "InvalidRequest", raw=True)
    clients = []
    started = time.monotonic()
    gate_deadline = started + BODY_READ_DEADLINE_SECONDS - 1
    busy = None
    try:
        # Serial HTTP-parser progress prevents Rust's separate request-line gate
        # from supplying a false body-admission witness. Java sends 100 before
        # application admission: only the final POST Busy below witnesses fullness.
        for _ in range(BODY_READERS):
            client = _BodyReaderClient(server.port, gate_deadline)
            clients.append(client)
            client.send(prefix, gate_deadline)
            while not client.continues:
                _poll_body_clients(clients, gate_deadline)
                if any(item.closed or item.final is not None for item in clients):
                    raise AssertionError("A body reader was rejected before the overflow POST")
            if any(item.closed or item.final is not None for item in clients):
                raise AssertionError("A body reader was rejected before the overflow POST")
        overflow = _BodyReaderClient(server.port, gate_deadline)
        clients.append(overflow)
        overflow.send(prefix, gate_deadline)
        while busy is None:
            _poll_body_clients(clients, gate_deadline)
            finished = [client for client in clients if client.final is not None]
            if len(finished) > 1:
                raise AssertionError("More than one overflow POST: fewer than 16 body readers were held")
            if finished:
                busy = finished[0]
                _body_error(busy, 503, "Busy")
            if any(client.closed and client is not busy for client in clients):
                raise AssertionError("A stalled body reader closed before saturation was witnessed")
        held = [client for client in clients if client is not busy]
        if len(held) != BODY_READERS or any(client.final is not None for client in held):
            raise AssertionError("The overflow witness did not retain 16 stalled readers")
        # This rejected request has no admitted-reader timer. Like the original
        # HTTP GET client, close it after its complete fixed-length response.
        # Never count that client closure as server-deadline evidence.
        busy.close()
        observed = _body_get(server, path, gate_deadline, held)
        expected_busy = {"error": {"code": "Busy", "message": MESSAGES["Busy"]}}
        if observed[:2] != (503, expected_busy):
            raise AssertionError(f"{server.variant}: saturated body-reader GET returned {observed}")
        if any(client.final is not None or client.closed for client in held):
            raise AssertionError("A stalled reader ended before the overflow GET completed")
        observed_after = time.monotonic() - started
        # Preserve the existing five-second transport-observation allowance, but
        # anchor it before setup instead of extending it after Busy is received.
        closure_deadline = started + BODY_READ_DEADLINE_SECONDS + 5
        while any(not client.closed for client in held):
            _poll_body_clients(held, closure_deadline)
            for client in held:
                if client.final is not None:
                    # Rust responds InvalidRequest at its deadline; Java closes.
                    _body_error(client, 400, "InvalidRequest")
        recovery_deadline = time.monotonic() + 2
        while True:
            status, payload, _ = _body_get(server, path, recovery_deadline)
            if status == 200 and payload == {"snapshot": before}:
                break
            if status != 503 or payload != expected_busy:
                raise AssertionError(f"{server.variant}: body-reader recovery returned {status} {payload}")
            _BodyReaderClient.remaining(recovery_deadline)
            time.sleep(min(0.025, _BodyReaderClient.remaining(recovery_deadline)))
    finally:
        for client in clients:
            client.close()
    if server.get(scope) != before:
        raise AssertionError(f"{server.variant}: a stalled body reader mutated existing state")
    EVIDENCE["variants"][server.variant]["slow_body"] = {
        "concurrent_readers": BODY_READERS,
        "deadline_seconds": BODY_READ_DEADLINE_SECONDS,
        "establishment_requests": BODY_READERS + 1,
        "continue_handshakes": BODY_READERS,
        "post_overflow_witness": "503 Busy",
        "overflow_request": "503 Busy",
        "busy_observed_after_seconds": observed_after,
        "connections_closed": len(held),
        "overflow_connection_closed_by_client": True,
        "capacity_recovered": True,
    }


def raw_request_targets(server):
    """Rust transport regressions use actual bytes, before any URI normalization."""
    if server.variant != "Rust composition":
        return
    scope = server.seed("raw_target")
    path = "/v1/scopes/" + scope
    before = server.get(scope)
    expected_error = {"error": {"code": "InvalidRequest", "message": MESSAGES["InvalidRequest"]}}

    def request(target, method="GET", body=b"", framing=None):
        headers = (f"{method} {target} HTTP/1.1\r\nHost: 127.0.0.1:{server.port}\r\n"
                   "Accept: application/json\r\nConnection: keep-alive\r\n")
        if method == "POST":
            headers += "Content-Type: application/json\r\n"
        headers += framing if framing is not None else f"Content-Length: {len(body)}\r\n"
        return (headers + "\r\n").encode("ascii") + body

    def receive(client):
        result = bytearray()
        while True:
            try:
                data = client.recv(4096)
            except ConnectionResetError:
                if not result:
                    raise
                break
            if not data:
                break
            result.extend(data)
            if len(result) > 65536:
                raise AssertionError("Raw-wire response exceeded harness bound")
        return bytes(result)

    def parse(wire, expected_status, expected_payload):
        head, body = wire.split(b"\r\n\r\n", 1)
        lines = head.decode("ascii").split("\r\n")
        headers = dict(line.lower().split(": ", 1) for line in lines[1:])
        if (int(lines[0].split()[1]) != expected_status
                or headers.get("connection") != "close"
                or headers.get("content-type", "").split(";")[0] != "application/json"
                or headers.get("cache-control") != "no-store"
                or int(headers.get("content-length", "-1")) != len(body)
                or json.loads(body) != expected_payload):
            raise AssertionError(f"Unexpected raw-wire response: {wire!r}")

    labels = []
    for label, target, status, payload in (
        ("literal_fragment", path + "#ignored", 400, expected_error),
        ("empty_fragment", path + "#", 400, expected_error),
        ("query_fragment", path + "?x=1#ignored", 400, expected_error),
        ("encoded_fragment", path + "%23ignored", 400, expected_error),
        ("query", path + "?x=1", 400, expected_error),
        ("normal_path", path, 200, {"snapshot": before}),
    ):
        with socket.create_connection(("127.0.0.1", server.port), timeout=8) as client:
            client.sendall(request(target))
            parse(receive(client), status, payload)
        labels.append(label)

    mutation = request(path + "/lines#ignored", "POST", b'{"unit_minor":"1","quantity":"1"}')
    # The second target would mutate state if Hyper were permitted to normalize it.
    with socket.create_connection(("127.0.0.1", server.port), timeout=8) as client:
        client.sendall(request(path) + mutation)
        parse(receive(client), 200, {"snapshot": before})
    labels.append("pipelined_second_request_not_dispatched")
    with socket.create_connection(("127.0.0.1", server.port), timeout=8) as client:
        client.sendall(request(path))
        parse(receive(client), 200, {"snapshot": before})
        try:
            client.sendall(mutation)
            if receive(client):
                raise AssertionError("A closed connection dispatched a second request")
        except (BrokenPipeError, ConnectionResetError):
            pass
    labels.append("sequential_second_request_not_dispatched")

    # A truncated or malformed-framing body is not an oversize body: never 413.
    for label, wire in (
        ("truncated_body", request(path + "/lines", "POST", b"{", "Content-Length: 20\r\n")),
        ("malformed_chunk", request(path + "/lines", "POST", b"invalid\r\n", "Transfer-Encoding: chunked\r\n")),
    ):
        with socket.create_connection(("127.0.0.1", server.port), timeout=8) as client:
            client.sendall(wire)
            client.shutdown(socket.SHUT_WR)
            parse(receive(client), 400, expected_error)
        labels.append(label)

    for label, prefix in (("oversized_request_line", b"GET /" + b"x" * 8192),
                          ("request_line_deadline", b"GET /v1/")):
        with socket.create_connection(("127.0.0.1", server.port), timeout=8) as client:
            started = time.monotonic()
            client.sendall(prefix)
            parse(receive(client), 400, expected_error)
            if time.monotonic() - started > 7:
                raise AssertionError("Request-line rejection exceeded the bounded deadline")
        labels.append(label)
    if server.get(scope) != before:
        raise AssertionError("Raw targets or second requests mutated existing state")
    EVIDENCE["variants"][server.variant]["raw_request_target_cases"] = labels


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
                        status, payload, _ = gated.request("GET", "/v1/scopes/" + scope)
                        if status == 503:
                            # Admission can close before the listener finishes closing.
                            # This is an intermediate state, not evidence of closure.
                            if payload != {"error": {"code": "Busy", "message": MESSAGES["Busy"]}}:
                                raise AssertionError("Unexpected error during graceful shutdown")
                        elif (status != 200 or set(payload) != {"snapshot"}
                              or set(payload["snapshot"]) != set(HEADER)
                              or not all(type(v) is str for v in payload["snapshot"].values())
                              or payload["snapshot"]["scenario"] != scope
                              or payload["snapshot"]["last_result"] != "-"):
                            raise AssertionError("Invalid read during graceful shutdown")
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


def evidence_destination(cli_path=None, environ=os.environ):
    """Pick an extra receipt path, or None to write only the scratch receipt.

    A plain local run returns None, so the dated receipts tracked under research/
    are never replaced by accident. The flag wins over the environment variable.
    """
    chosen = cli_path if cli_path is not None else (environ.get(EVIDENCE_ENV) or None)
    if chosen is None:
        return None
    destination = Path(chosen)
    if destination.is_dir() or not destination.parent.is_dir():
        raise ValueError(f"Evidence output must be a file in an existing directory: {destination}")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-output",
        type=Path,
        help=f"also write the receipt here (overrides {EVIDENCE_ENV})",
    )
    # Resolve before the long run so a bad destination fails fast.
    output = evidence_destination(parser.parse_args().evidence_output)
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
            bounded_body_readers(server)
            raw_request_targets(server)
            default_mode(server)
            record = EVIDENCE["variants"][variant]
            raw_cases = record.get("raw_request_target_cases")
            print(f"PASS {variant}: {record['oracle_rows']} HTTP oracle rows, {len(record['validation_cases'])} rejection cases, {len(record['negotiation_cases'])} negotiation cases, 8 ordinary-mode cases, 4 startup rejections", flush=True)
            transport = f"; {len(raw_cases)} raw-wire transport cases" if raw_cases else ""
            print(f"PASS {variant}: {record['slow_body']['concurrent_readers']} stalled body readers bounded by a {BODY_READ_DEADLINE_SECONDS}s deadline, overflow 503 Busy{transport}", flush=True)
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
    scratch = CASE / ".runtime/http-last-run.json"
    EVIDENCE["evidence_path"] = str(output or scratch)
    scratch.parent.mkdir(parents=True, exist_ok=True)
    receipt = json.dumps(EVIDENCE, indent=2) + "\n"
    scratch.write_text(receipt)
    if output is not None:
        output.write_text(receipt)
    print("PASS PostgreSQL immediate restart: 12 HTTP snapshots preserved/recovered; 3 surviving HTTP servers returned bounded503 then reconnected", flush=True)
    print("PASS all owned HTTP processes stopped", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError, RuntimeError, subprocess.SubprocessError, http.client.HTTPException) as failure:
        print(f"FAIL {failure}", file=sys.stderr)
        sys.exit(1)
