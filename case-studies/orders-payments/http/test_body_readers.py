"""Exercise the body-reader oracle against independent, local wire peers."""

import importlib.util
import json
from pathlib import Path
import socket
import threading
import time
import unittest
from unittest.mock import patch

# Other HTTP tests import the PostgreSQL harness, which also has a verify.py.
# Resolve this sibling explicitly so unittest discovery order cannot select it.
_spec = importlib.util.spec_from_file_location(
    "roo_http_body_verify", Path(__file__).with_name("verify.py"))
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


def response(status, payload):
    body = json.dumps(payload).encode("utf-8")
    return (f"HTTP/1.1 {status} Test\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\nCache-Control: no-store\r\n"
            "Connection: close\r\n\r\n").encode("ascii") + body


def failure(code):
    return {"error": {"code": code, "message": verify.MESSAGES[code]}}


class WireServer:
    """A semaphore-limited peer, with deliberately broken variants of behavior.

    This implements no oracle polling or scheduling: each accepted socket has
    its own handler and independent body timeout. All waits are interruptible.
    """

    variant = "loopback fixture"
    snapshot = {"scope": "body_test", "total": "0"}

    def __init__(self, capacity=16, *, post_delay=0, get_delay=0,
                 transport_busy=False, timeout_reply=False, no_deadline=False,
                 extra_busy=False, recovery_bad=False, recovery_stuck=False,
                 mutation=False, wait_rejected_eof=False):
        self.permits = threading.BoundedSemaphore(capacity)
        self.post_delay = post_delay
        self.get_delay = get_delay
        self.transport_busy = transport_busy
        self.timeout_reply = timeout_reply
        self.no_deadline = no_deadline
        self.extra_busy = extra_busy
        self.recovery_bad = recovery_bad
        self.recovery_stuck = recovery_stuck
        self.mutation = mutation
        self.wait_rejected_eof = wait_rejected_eof
        self.overflow_client_closed = False
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.active = 0
        self.maximum = 0
        self.get_calls = 0
        self.events = []
        self.errors = []
        self.handlers = []
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.port = self.listener.getsockname()[1]
        self.listener.listen(32)
        self.listener.settimeout(0.05)
        self.acceptor = threading.Thread(target=self.accept, daemon=True)

    def __enter__(self):
        self.acceptor.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.acceptor.join(1)
        self.listener.close()
        for thread in self.handlers:
            thread.join(1)
        if self.acceptor.is_alive() or any(t.is_alive() for t in self.handlers):
            raise AssertionError("Loopback fixture leaked a thread")
        if self.errors:
            raise AssertionError(f"Loopback fixture failed: {self.errors}")

    def seed(self, label):
        assert label == "slow_body"
        return "body_test"

    def get(self, scope):
        assert scope == "body_test"
        self.get_calls += 1
        if self.mutation and self.get_calls > 1:
            return {**self.snapshot, "total": "1"}
        return self.snapshot.copy()

    def request(self, method, path, body, **options):
        # The preliminary empty-body validation is outside this wire scenario.
        assert (method, path, body, options) == (
            "POST", "/v1/scopes/body_test/payments", b"", {"raw": True})
        return 400, failure("InvalidRequest"), {}

    def accept(self):
        while not self.stop.is_set():
            try:
                connection, _ = self.listener.accept()
            except socket.timeout:
                continue
            thread = threading.Thread(target=self.handle, args=(connection,), daemon=True)
            self.handlers.append(thread)
            thread.start()

    def handle(self, connection):
        acquired = False
        try:
            with connection:
                connection.settimeout(1)
                wire = b""
                while b"\r\n\r\n" not in wire:
                    part = connection.recv(4096)
                    if not part:
                        return
                    wire += part
                    if len(wire) > 8192:
                        raise AssertionError("Fixture request exceeded its bound")
                method = wire.split(b" ", 1)[0]
                if method == b"GET":
                    with self.lock:
                        saturated = self.active >= 16
                        self.events.append(("GET", self.active))
                    if saturated or self.recovery_stuck:
                        if not self.stop.wait(self.get_delay):
                            connection.sendall(response(503, failure("Busy")))
                    else:
                        payload = {} if self.recovery_bad else {"snapshot": self.snapshot}
                        connection.sendall(response(200, payload))
                    return
                assert method == b"POST"
                assert b"Expect: 100-continue\r\n" in wire
                if self.transport_busy:
                    connection.sendall(response(503, failure("Busy")))
                    return
                acquired = self.permits.acquire(blocking=False)
                if not acquired:
                    with self.lock:
                        self.events.append(("POST Busy", self.active))
                    # Include Java's pre-admission continue in the same write.
                    if not self.stop.wait(self.post_delay):
                        connection.sendall(b"HTTP/1.1 100 Continue\r\n\r\n" +
                                           response(503, failure("Busy")))
                    if self.wait_rejected_eof:
                        connection.settimeout(0.05)
                        while not self.stop.is_set():
                            try:
                                part = connection.recv(1)
                            except socket.timeout:
                                continue
                            if not part:
                                self.overflow_client_closed = True
                                break
                            raise AssertionError("Overflow peer sent unexpected body bytes")
                    return
                with self.lock:
                    self.active += 1
                    self.maximum = max(self.maximum, self.active)
                    self.events.append(("admitted", self.active))
                connection.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")
                if self.stop.wait(30 if self.no_deadline else 2):
                    return
                if self.extra_busy:
                    connection.sendall(response(503, failure("Busy")))
                elif self.timeout_reply:
                    connection.sendall(response(400, failure("InvalidRequest")))
        except (BrokenPipeError, ConnectionResetError):
            # A failed oracle closes its peers while fixture timers are running.
            pass
        except Exception as exc:
            with self.lock:
                self.errors.append(repr(exc))
        finally:
            if acquired:
                with self.lock:
                    self.active -= 1
                self.permits.release()


class BodyReaderOracleTests(unittest.TestCase):
    def exercise(self, **options):
        evidence = {"variants": {WireServer.variant: {}}}
        with WireServer(**options) as server:
            with patch.object(verify, "BODY_READ_DEADLINE_SECONDS", 2), \
                    patch.object(verify, "EVIDENCE", evidence):
                verify.bounded_body_readers(server)
            self.assertEqual(server.maximum, 16)
            self.assertEqual(server.events[:16], [("admitted", n) for n in range(1, 17)])
            self.assertEqual(server.events[16:18], [("POST Busy", 16), ("GET", 16)])
            if options.get("wait_rejected_eof"):
                self.assertTrue(server.overflow_client_closed)
        return evidence["variants"][WireServer.variant]["slow_body"]

    def test_valid_eof_and_invalid_request_timeout_transports(self):
        for timeout_reply in (False, True):
            with self.subTest(timeout_reply=timeout_reply):
                receipt = self.exercise(timeout_reply=timeout_reply)
                self.assertEqual(receipt["connections_closed"], 16)
                self.assertTrue(receipt["overflow_connection_closed_by_client"])
                self.assertTrue(receipt["capacity_recovered"])

    def test_rejected_probe_closure_is_separate_from_admitted_deadlines(self):
        receipt = self.exercise(wait_rejected_eof=True)
        self.assertEqual(receipt["connections_closed"], 16)
        self.assertTrue(receipt["overflow_connection_closed_by_client"])

    def test_wrong_capacity_cannot_pass(self):
        for capacity in (15, 17):
            with self.subTest(capacity=capacity), self.assertRaises(AssertionError):
                self.exercise(capacity=capacity)

    def test_transport_busy_is_not_body_admission(self):
        with self.assertRaisesRegex(AssertionError, "before the overflow POST"):
            self.exercise(transport_busy=True)

    def test_exact_busy_payload_received_after_cutoff_fails(self):
        for options in ({"post_delay": 1.15}, {"get_delay": 1.15}):
            with self.subTest(options=options), self.assertRaisesRegex(AssertionError, "absolute deadline"):
                self.exercise(**options)

    def test_absent_body_deadline_fails_even_after_busy(self):
        with self.assertRaisesRegex(AssertionError, "absolute deadline"):
            self.exercise(no_deadline=True)

    def test_more_than_one_post_busy_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "Unexpected body-reader response"):
            self.exercise(extra_busy=True)

    def test_recovery_payload_and_final_snapshot_are_checked(self):
        for options in ({"recovery_bad": True}, {"mutation": True}):
            with self.subTest(options=options), self.assertRaises(AssertionError):
                self.exercise(**options)

    def test_recovery_must_finish_within_two_seconds(self):
        with self.assertRaisesRegex(AssertionError, "absolute deadline"):
            self.exercise(recovery_stuck=True)


class BodyReaderFramingTests(unittest.TestCase):
    def setUp(self):
        self.reader_socket, self.writer = socket.socketpair()
        self.reader_socket.setblocking(False)
        self.client = verify._BodyReaderClient.__new__(verify._BodyReaderClient)
        self.client.socket = self.reader_socket
        self.client.buffer = bytearray()
        self.client.continues = 0
        self.client.final = None
        self.client.closed = False

    def tearDown(self):
        self.client.close()
        self.writer.close()

    def feed(self, data):
        self.writer.sendall(data)
        self.client.receive()

    def test_coalesced_continue_and_final_are_preserved(self):
        self.feed(b"HTTP/1.1 100 Continue\r\n\r\n" + response(503, failure("Busy")))
        self.assertEqual(self.client.continues, 1)
        self.assertEqual(self.client.final[:2], (503, failure("Busy")))

    def test_split_continue_headers_and_json_are_preserved(self):
        packet = b"HTTP/1.1 100 Continue\r\n\r\n" + response(503, failure("Busy"))
        for byte in packet:
            self.feed(bytes([byte]))
        self.assertEqual(self.client.continues, 1)
        self.assertEqual(self.client.final[:2], (503, failure("Busy")))
        self.assertFalse(self.client.buffer)

    def test_missing_length_and_duplicate_headers_fail(self):
        for packet in (
            b"HTTP/1.1 503 Test\r\n\r\n{}",
            b"HTTP/1.1 503 Test\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\n{}",
            b"bogus 503 Test\r\nContent-Length: 2\r\n\r\n{}",
        ):
            with self.subTest(packet=packet):
                self.client.buffer.clear()
                with self.assertRaises(AssertionError):
                    self.feed(packet)

    def test_truncated_body_is_rejected_at_eof(self):
        self.feed(response(503, failure("Busy"))[:-1])
        self.assertIsNone(self.client.final)
        self.writer.shutdown(socket.SHUT_WR)
        with self.assertRaisesRegex(AssertionError, "Incomplete"):
            self.client.receive()

    def test_transfer_encoding_cannot_override_fixed_length(self):
        packet = response(503, failure("Busy")).replace(
            b"Content-Length:", b"Transfer-Encoding: chunked\r\nContent-Length:")
        with self.assertRaisesRegex(AssertionError, "transfer encoding"):
            self.feed(packet)

    def test_extra_final_bytes_are_rejected(self):
        with self.assertRaisesRegex(AssertionError, "extra"):
            self.feed(response(503, failure("Busy")) + b"surplus")


if __name__ == "__main__":
    unittest.main()
