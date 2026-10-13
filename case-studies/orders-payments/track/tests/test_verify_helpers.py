"""Unit coverage for the evaluator helpers that measure real boundary behavior.

Nothing here starts a database, an HTTP server, or a container.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


TRACK_DIR = Path(__file__).resolve().parents[1]


def load_verify(path: Path):
    spec = importlib.util.spec_from_file_location("roo_track_verify_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeServer:
    """Stands in for the HTTP harness client; records what its methods dispatch."""

    def __init__(self):
        self.dispatched = []

    def snapshot_response(self, method, path, body=None, **options):
        self.dispatched.append((method, path))
        return {"method": method}

    def get(self, scope):
        return self.snapshot_response("GET", "/v1/scopes/" + scope)

    def step(self, scope, action, outcome=None):
        return self.snapshot_response("POST", "/v1/scopes/" + scope + "/lines")


class FakeRunner:
    def __init__(self):
        self.calls = []

    def row(self, *args):
        self.calls.append(("row", *args))
        return {"state": "Pending"}

    def step(self, scope, action, outcome=None):
        self.calls.append(("step", scope, action, outcome))
        return {"last_result": outcome}


class SourceHashPathTests(unittest.TestCase):
    def test_source_hashes_work_through_a_symlinked_checkout_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            link = Path(temporary) / "track-link"
            link.symlink_to(TRACK_DIR, target_is_directory=True)
            module = load_verify(link / "verify.py")

            hashes = module.source_hashes()

        self.assertIn("verify.py", hashes)
        self.assertEqual(hashes, load_verify(TRACK_DIR / "verify.py").source_hashes())


class HttpDispatchCountingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.verify = load_verify(TRACK_DIR / "verify.py")

    def test_counter_reports_requests_that_were_actually_sent(self) -> None:
        server = FakeServer()
        counts = self.verify.http_request_counter(server)
        before = dict(counts)

        self.verify.http_decision(server, "s1", "inspect")
        self.verify.http_decision(server, "s1", "stop")
        inspect_and_stop = self.verify.request_delta(counts, before)
        self.verify.http_decision(server, "s1", "add:50:1", "Added")
        with_add = self.verify.request_delta(counts, before)

        self.assertEqual(inspect_and_stop, {"GET": 1, "PUT": 0, "POST": 0})
        self.assertEqual(with_add, {"GET": 1, "PUT": 0, "POST": 1})
        self.assertEqual([method for method, _ in server.dispatched], ["GET", "POST"])

    def test_stop_sends_nothing(self) -> None:
        server = FakeServer()
        counts = self.verify.http_request_counter(server)

        self.assertIsNone(self.verify.http_decision(server, "s1", "stop"))

        self.assertEqual(counts, {"GET": 0, "PUT": 0, "POST": 0})
        self.assertEqual(server.dispatched, [])


class PostgresDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.verify = load_verify(TRACK_DIR / "verify.py")

    def test_decisions_reach_the_runner_only_when_they_are_real_actions(self) -> None:
        runner = FakeRunner()

        self.assertEqual(self.verify.postgres_decision(runner, "s1", "inspect"), {"state": "Pending"})
        self.assertIsNone(self.verify.postgres_decision(runner, "s1", "stop"))
        applied = self.verify.postgres_decision(runner, "s1", "pay:pNEW:approve:none", "IntentConflict")

        self.assertEqual(applied, {"last_result": "IntentConflict"})
        self.assertEqual(
            runner.calls,
            [("row", "snapshot", "s1"), ("step", "s1", "pay:pNEW:approve:none", "IntentConflict")],
        )


if __name__ == "__main__":
    unittest.main()
