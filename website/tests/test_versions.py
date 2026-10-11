"""Regression checks for release isolation and safe edition configuration."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build as site


class VersionTests(unittest.TestCase):
    def test_working_tree_changes_do_not_enter_release_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "working"
            release = Path(directory) / "tag"
            for base in (root, release):
                (base / "docs").mkdir(parents=True)
            (root / "website/assets").mkdir(parents=True)
            (root / "website/assets/roo.css").write_text("/* publisher interface */")
            (release / "docs/chapter.md").write_text("# Tagged chapter\n\nFixed release content.\n")
            (root / "docs/chapter.md").write_text("# Development chapter\n\nUnreleased change.\n")
            stable = {"id": "v0.1.0", "source_ref": "refs/tags/v0.1.0", "source_commit": "a" * 40, "pages": ["docs/chapter.md"]}
            dev = {"id": "dev", "source_ref": "HEAD", "pages": ["docs/chapter.md"]}
            with patch.multiple(site, ROOT=root, WEBSITE=root / "website", BUILD=Path(directory) / "build"):
                content, first = site.prepare(stable, release, "b" * 40, True)
                original = (content / "docs/chapter.md").read_bytes()
                (root / "docs/chapter.md").write_text("# Another unreleased change\n")
                content, second = site.prepare(stable, release, "c" * 40, True)
                self.assertEqual((content / "docs/chapter.md").read_bytes(), original)
                self.assertEqual(first["pages"], second["pages"])
                self.assertEqual(second["documentation_commit"], "a" * 40)
                self.assertEqual(second["pages"][0]["origin"], "release")
                content, manifest = site.prepare(dev, root, "c" * 40, True)
                self.assertIn("Another unreleased change", (content / "docs/chapter.md").read_text())
                self.assertNotEqual(first["pages"][0]["sha256"], manifest["pages"][0]["sha256"])

    def test_legacy_links_keep_the_newest_release_that_contains_the_page(self):
        data = {"versions": [
            {"id": "v0.2.0", "routes": ["", "docs/new/"]},
            {"id": "v0.1.0", "routes": ["", "docs/old/"]},
            {"id": "dev", "routes": ["", "docs/unreleased/"]},
        ]}
        self.assertEqual(site.legacy_redirects(data), {
            "": "/roo/v0.2.0/", "docs/new/": "/roo/v0.2.0/docs/new/",
            "docs/old/": "/roo/v0.1.0/docs/old/",
        })

    def test_readme_and_index_routes_match_mkdocs(self):
        self.assertEqual(site.route("index.md"), "")
        self.assertEqual(site.route("case-studies/orders-payments/README.md"), "case-studies/orders-payments/")
        self.assertEqual(site.route("docs/01-foundations.md"), "docs/01-foundations/")

    def test_legacy_redirect_keeps_an_english_fallback_and_fragment_logic(self):
        html = site.redirect("/roo/v0.1.0/docs/01-foundations/")
        self.assertIn('lang="en"', html)
        self.assertIn('href="/roo/v0.1.0/docs/01-foundations/"', html)
        self.assertIn("target.hash = location.hash", html)
        self.assertIn("target.search = location.search", html)


if __name__ == "__main__":
    unittest.main()
