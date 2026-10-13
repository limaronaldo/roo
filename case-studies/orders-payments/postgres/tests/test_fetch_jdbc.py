"""Network-free regression tests for publishing the pinned JDBC artifact."""

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parents[1] / "fetch_jdbc.py"
SPEC = importlib.util.spec_from_file_location("payments_fetch_jdbc", SOURCE)
assert SPEC is not None and SPEC.loader is not None
fetch_jdbc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch_jdbc)


class FetchJdbcTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="roo-fetch-jdbc-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / ".deps"
        self.directory.mkdir()
        self.jar = self.directory / "postgresql-test.jar"
        self.artifact = b"small mocked JDBC artifact"
        self.digest = hashlib.sha256(self.artifact).hexdigest()
        constants = mock.patch.multiple(
            fetch_jdbc,
            VERSION="test",
            SHA256=self.digest,
            DIRECTORY=self.directory,
            JAR=self.jar,
            URL="https://example.invalid/postgresql-test.jar",
        )
        constants.start()
        self.addCleanup(constants.stop)

    @staticmethod
    def response(payload):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = payload
        return response

    def assert_no_temporary_artifacts(self):
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_verified_mocked_download_is_published(self):
        with mock.patch.object(
            fetch_jdbc.urllib.request,
            "urlopen",
            return_value=self.response(self.artifact),
        ) as urlopen:
            fetch_jdbc.main()

        urlopen.assert_called_once_with(fetch_jdbc.URL, timeout=30)
        self.assertEqual(self.jar.read_bytes(), self.artifact)
        self.assert_no_temporary_artifacts()

    def test_replace_failure_leaves_no_partial_jar_and_cleans_temporary_file(self):
        original_replace = Path.replace

        def fail_publish(source, target):
            if target == self.jar:
                raise OSError("simulated atomic publish failure")
            return original_replace(source, target)

        with (
            mock.patch.object(
                fetch_jdbc.urllib.request,
                "urlopen",
                return_value=self.response(self.artifact),
            ),
            mock.patch.object(Path, "replace", fail_publish),
        ):
            with self.assertRaisesRegex(OSError, "simulated atomic publish failure"):
                fetch_jdbc.main()

        self.assertFalse(self.jar.exists())
        self.assert_no_temporary_artifacts()

    def test_existing_valid_artifact_is_not_rewritten_or_fetched(self):
        self.jar.write_bytes(self.artifact)
        before = self.jar.stat()

        with (
            mock.patch.object(
                fetch_jdbc.urllib.request,
                "urlopen",
                side_effect=AssertionError("valid artifact must not be fetched"),
            ),
            mock.patch.object(
                fetch_jdbc.tempfile,
                "NamedTemporaryFile",
                side_effect=AssertionError("valid artifact must not be rewritten"),
            ),
        ):
            fetch_jdbc.main()

        after = self.jar.stat()
        self.assertEqual(self.jar.read_bytes(), self.artifact)
        self.assertEqual((after.st_ino, after.st_mtime_ns, after.st_size),
                         (before.st_ino, before.st_mtime_ns, before.st_size))
        self.assert_no_temporary_artifacts()

    def test_hash_mismatch_is_rejected_without_publishing(self):
        with mock.patch.object(
            fetch_jdbc.urllib.request,
            "urlopen",
            return_value=self.response(b"not the pinned artifact"),
        ):
            with self.assertRaisesRegex(SystemExit, "failed its size or SHA-256 check"):
                fetch_jdbc.main()

        self.assertFalse(self.jar.exists())
        self.assert_no_temporary_artifacts()


if __name__ == "__main__":
    unittest.main()
