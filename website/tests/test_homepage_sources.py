"""Edition homepages preserve their teaching independently of the publisher."""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build as site

ARCHIVE = "website/releases/v0.2.0-v0.4.0-home.md"


class HomepageSourcesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "publisher"
        self.tagged = Path(temporary.name) / "tagged"
        for root in (self.root, self.tagged):
            (root / "website/pages").mkdir(parents=True)
            (root / "website/releases").mkdir()
            (root / "docs").mkdir()
            (root / "docs/contract.md").write_text("# Contract\n")
        (self.root / "website/assets").mkdir()
        (self.root / ARCHIVE).write_text(
            "# Published teaching\n\n{{edition_status}}\n\n[Contract](../../docs/contract.md)\n[License](license.md)\n"
        )
        (self.root / "website/pages/license.md").write_text("# License\n")
        (self.root / "website/releases/v0.1.0-home.md").write_text("# First edition teaching\n")
        (self.root / "website/pages/index.md").write_text(
            "# Development teaching\n\n[New design](../../docs/new-design.md)\n"
        )
        (self.root / "docs/new-design.md").write_text("# New design\n")
        (self.tagged / "website/pages/index.md").write_text(
            "# Tagged future teaching\n\n[Contract](../../docs/contract.md)\n"
        )
        self.patches = patch.multiple(site, ROOT=self.root, WEBSITE=self.root / "website", BUILD=self.root / ".site-build")
        self.patches.start()
        self.addCleanup(self.patches.stop)

    def prepare(self, edition, pages=None):
        entry = {"id": edition, "source_ref": "HEAD" if edition == "dev" else "refs/tags/" + edition,
                 "source_commit": "tagged-commit", "pages": pages or ["index.md", "docs/contract.md", "license.md"]}
        return site.prepare(entry, self.root if edition == "dev" else self.tagged, "publisher-commit", False, "v0.4.0")

    def test_existing_eight_field_editions_use_unchanged_archive(self):
        for edition in ("v0.2.0", "v0.3.0", "v0.4.0"):
            with self.subTest(edition=edition):
                content, manifest = self.prepare(edition)
                text = (content / "index.md").read_text()
                self.assertIn("Published teaching", text)
                self.assertIn(f"Release documentation from the {edition} tag.", text)
                self.assertIn("[Contract](docs/contract.md)", text)
                self.assertIn("[License](license.md)", text)
                self.assertNotIn("Development teaching", text)
                self.assertNotIn("{{edition_status}}", text)
                record = manifest["pages"][0]
                self.assertEqual(record["source"], ARCHIVE)
                self.assertEqual(record["origin"], "publisher")
                self.assertEqual(record["sha256"], hashlib.sha256((self.root / ARCHIVE).read_bytes()).hexdigest())

    def test_development_uses_current_home_and_new_local_navigation(self):
        content, manifest = self.prepare("dev", ["index.md", "docs/new-design.md"])
        self.assertIn("[New design](docs/new-design.md)", (content / "index.md").read_text())
        self.assertEqual(manifest["pages"][0]["source"], "website/pages/index.md")

    def test_future_edition_uses_tagged_home_and_records_release_origin(self):
        content, manifest = self.prepare("v0.5.0")
        text = (content / "index.md").read_text()
        self.assertIn("Tagged future teaching", text)
        self.assertIn("[Contract](docs/contract.md)", text)
        record = manifest["pages"][0]
        self.assertEqual(record["origin"], "release")
        self.assertEqual(record["commit"], "tagged-commit")
        self.assertEqual(record["sha256"], hashlib.sha256((self.tagged / "website/pages/index.md").read_bytes()).hexdigest())

    def test_future_missing_home_fails_instead_of_using_current_home(self):
        (self.tagged / "website/pages/index.md").unlink()
        with self.assertRaisesRegex(ValueError, "regular Markdown source"):
            self.prepare("v1.0.0")

    def test_first_edition_keeps_its_original_overlay(self):
        content, manifest = self.prepare("v0.1.0")
        self.assertEqual((content / "index.md").read_text(), "# First edition teaching\n")
        self.assertEqual(manifest["pages"][0]["source"], "website/releases/v0.1.0-home.md")

    def test_real_compatibility_archive_is_the_published_homepage(self):
        archive = Path(__file__).resolve().parents[2] / ARCHIVE
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         "2fdb04b0145f516d9b76c9d2cc6d35805d29fbd9ef69bc839eb97cb368059669")


if __name__ == "__main__":
    unittest.main()
