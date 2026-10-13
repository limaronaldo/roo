"""Cluster-free regression tests for where verify.py writes its evidence receipt."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


CASE = Path(__file__).resolve().parents[1]


def load_verify():
    # verify.py imports its sibling cluster.py; importing it starts nothing.
    sys.path.insert(0, str(CASE))
    try:
        spec = importlib.util.spec_from_file_location("payments_postgres_verify", CASE / "verify.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(CASE))


verify = load_verify()


class EvidenceDestinationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="roo-verify-evidence-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_default_is_the_tracked_historical_receipt(self):
        expected = CASE.parents[2] / "research/postgres-integration-evidence.json"
        self.assertEqual(verify.HISTORICAL_EVIDENCE, expected)
        self.assertEqual(verify.evidence_destination(None, {}), expected)

    def test_empty_environment_value_keeps_the_historical_default(self):
        self.assertEqual(
            verify.evidence_destination(None, {verify.EVIDENCE_ENV: ""}),
            verify.HISTORICAL_EVIDENCE,
        )

    def test_environment_override_redirects_the_receipt(self):
        target = self.directory / "env.json"
        self.assertEqual(
            verify.evidence_destination(None, {verify.EVIDENCE_ENV: str(target)}), target
        )

    def test_flag_overrides_the_environment(self):
        flag, env = self.directory / "flag.json", self.directory / "env.json"
        self.assertEqual(
            verify.evidence_destination(flag, {verify.EVIDENCE_ENV: str(env)}), flag
        )

    def test_directory_and_missing_parent_are_rejected_before_any_run(self):
        with self.assertRaisesRegex(ValueError, "existing directory"):
            verify.evidence_destination(self.directory, {})
        with self.assertRaisesRegex(ValueError, "existing directory"):
            verify.evidence_destination(self.directory / "missing" / "evidence.json", {})
        with self.assertRaisesRegex(ValueError, "existing directory"):
            verify.evidence_destination(None, {verify.EVIDENCE_ENV: str(self.directory / "missing" / "e.json")})


if __name__ == "__main__":
    unittest.main()
