"""Real Git fixtures exercise tag discovery, preservation, and full publication."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build as site
import release_tags as releases

PUBLISHER = Path(__file__).resolve().parents[1]


class ReleaseTagsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Documentation test")
        self.git("config", "user.email", "docs-test@example.invalid")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        (self.root / "website/pages").mkdir(parents=True)
        (self.root / "website/releases").mkdir()
        (self.root / "docs").mkdir()
        (self.root / ".gitignore").write_text(".site-build/\n__pycache__/\n")
        (self.root / "docs/chapter.md").write_text("# Release chapter\n\nFrozen initial text.\n")
        (self.root / "website/pages/index.md").write_text("# ROO\n\n{{edition_status}}\n\nRelease {{release_version}}.\n")
        (self.root / "website/releases/v0.1.0-home.md").write_text("# ROO first edition\n\n{{edition_status}}\n\nRelease {{release_version}}.\n")
        self.config = """site_name: ROO
site_url: https://limaronaldo.github.io/roo/
strict: true
theme:
  name: material
  custom_dir: overrides
  language: en
  font: false
plugins:
  - search
extra_javascript:
  - assets/versions.js
nav:
  - Home: index.md
  - Chapter: docs/chapter.md
"""
        (self.root / "website/mkdocs.yml").write_text(self.config)
        self.policy = {"default_policy": "highest-stable-tag", "versions": [
            {"id": "dev", "label": "Development (main)", "source_ref": "HEAD", "navigation": "website/mkdocs.yml"}]}
        self.write_policy()
        for name in ("build.py", "check_site.py", "release_tags.py"):
            shutil.copyfile(PUBLISHER / name, self.root / "website" / name)
        for name in ("assets", "overrides"):
            shutil.copytree(PUBLISHER / name, self.root / "website" / name)
        self.first = self.commit("Initial fixture")
        self.git("tag", "-a", "v0.1.0", "-m", "Fixture release")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def write_policy(self):
        (self.root / "website/versions.json").write_text(json.dumps(self.policy))

    def registry(self, requested=""):
        with patch.multiple(site, ROOT=self.root, WEBSITE=self.root / "website"):
            return site.registry(requested)

    def baseline(self, data):
        return {"schema": 1, "releases": [
            {**{key: entry[key] for key in ("id", "source_commit", "tag_object", "navigation_sha256", "routes")}, "pages": []}
            for entry in data["versions"] if entry["id"] != "dev"]}

    def test_semantic_order_lightweight_tags_and_ignored_prereleases(self):
        for name in ("v0.2.0", "v0.10.0", "v1.0.0", "v8.0.0-rc.1", "v09.0.0", "unrelated"):
            self.git("tag", name)
        data = self.registry("v0.10.0")
        self.assertEqual(data["default"], "v1.0.0")
        self.assertEqual([entry["id"] for entry in data["versions"]], ["v1.0.0", "v0.10.0", "v0.2.0", "v0.1.0", "dev"])
        self.assertEqual(data, self.registry("v0.10.0"))
        self.assertEqual(data["versions"][1]["tag_object"], self.first)
        self.assertNotEqual(data["versions"][3]["tag_object"], self.first)

    def test_navigation_is_read_from_each_tag_and_development_can_grow(self):
        (self.root / "website/mkdocs.yml").write_text(self.config + "  - New chapter: docs/new.md\n")
        (self.root / "docs/new.md").write_text("# New chapter\n")
        second = self.commit("Second fixture")
        self.git("tag", "v0.2.0")
        (self.root / "website/mkdocs.yml").write_text(self.config + "  - Development only: docs/unreleased.md\n")
        data = self.registry()
        self.assertEqual(data["versions"][0]["source_commit"], second)
        self.assertIn("docs/new/", data["versions"][0]["routes"])
        self.assertNotIn("docs/new/", data["versions"][1]["routes"])
        self.assertIn("docs/unreleased/", data["versions"][2]["routes"])
        self.assertNotIn("docs/unreleased/", data["versions"][0]["routes"])

    def test_legacy_bootstrap_pin_is_verified(self):
        (self.root / "website/releases/v0.1.0.yml").write_text("nav:\n  - Frozen: docs/chapter.md\n")
        self.policy["versions"].insert(0, {"id": "v0.1.0", "source_ref": "refs/tags/v0.1.0",
            "source_commit": self.first, "navigation": "website/releases/v0.1.0.yml"})
        self.write_policy()
        self.assertEqual(self.registry()["versions"][0]["routes"], ["docs/chapter/"])
        self.policy["versions"][0]["source_commit"] = "0" * 40
        self.write_policy()
        with self.assertRaisesRegex(ValueError, "frozen commit"):
            self.registry()

    def test_missing_and_unsafe_requested_tags_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            self.registry("v0.2.0")
        for name in ("v1.2.3-rc1", "../v1.2.3", "v1.2.3\npublish=true", "--all"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "stable release tag"):
                self.registry(name)

    def test_deleted_and_moved_published_tags_stop_publication(self):
        self.git("tag", "v0.2.0")
        state = self.baseline(self.registry())
        self.git("tag", "-d", "v0.2.0")
        with self.assertRaisesRegex(ValueError, "missing"):
            releases.verify_previous(self.registry(), state)
        (self.root / "docs/chapter.md").write_text("# Changed tag content\n")
        self.commit("Move target in disposable fixture")
        self.git("tag", "v0.2.0")
        with self.assertRaisesRegex(ValueError, "source_commit"):
            releases.verify_previous(self.registry(), state)

    def test_replacing_an_annotated_tag_at_the_same_commit_is_detected(self):
        state = self.baseline(self.registry())
        self.git("tag", "-f", "-a", "v0.1.0", self.first, "-m", "Different fixture tag object")
        with self.assertRaisesRegex(ValueError, "tag_object"):
            releases.verify_previous(self.registry(), state)

    def test_navigation_and_document_hash_changes_are_rejected(self):
        data = self.registry()
        state = self.baseline(data)
        altered = copy.deepcopy(data)
        altered["versions"][0]["navigation_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "navigation_sha256"):
            releases.verify_previous(altered, state)
        manifest = {"edition": "v0.1.0", "pages": [{"origin": "release", "source": "docs/chapter.md", "page": "docs/chapter.md", "sha256": "0" * 64}]}
        with self.assertRaisesRegex(ValueError, "document hashes"):
            releases.verify_manifest(manifest, state)

    def test_full_build_adds_an_edition_and_preserves_tagged_content(self):
        def build(*args):
            result = subprocess.run([sys.executable, "website/build.py", *args], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        build()
        output = self.root / ".site-build/site"
        old_manifest = json.loads((output / "v0.1.0/source-manifest.json").read_text())
        old_content = (self.root / ".site-build/content/v0.1.0/docs/chapter.md").read_bytes()
        index = json.loads((output / "versions.json").read_text())
        responses = {releases.BASE + "versions.json": index, releases.BASE + "v0.1.0/source-manifest.json": old_manifest}
        baseline = self.root / ".site-build/previous.json"
        with patch.object(releases, "read_json", side_effect=responses.__getitem__):
            releases.capture_previous(baseline)
        (self.root / "docs/chapter.md").write_text("# Release chapter\n\nSecond release text.\n")
        (self.root / "docs/new.md").write_text("# New release chapter\n")
        (self.root / "website/mkdocs.yml").write_text(self.config + "  - New chapter: docs/new.md\n")
        self.commit("New release fixture")
        self.git("tag", "v0.2.0")
        (self.root / "docs/chapter.md").write_text("# Release chapter\n\nDevelopment only text.\n")
        build("--release-tag", "v0.2.0", "--previous-state", str(baseline))
        index = json.loads((output / "versions.json").read_text())
        self.assertEqual(index["default"], "v0.2.0")
        self.assertEqual([entry["id"] for entry in index["versions"]], ["v0.2.0", "v0.1.0", "dev"])
        self.assertEqual((self.root / ".site-build/content/v0.1.0/docs/chapter.md").read_bytes(), old_content)
        frozen = lambda manifest: [record for record in manifest["pages"] if record["origin"] == "release"]
        self.assertEqual(frozen(json.loads((output / "v0.1.0/source-manifest.json").read_text())), frozen(old_manifest))
        html = (output / "dev/docs/new/index.html").read_text()
        self.assertIn('value="/roo/v0.1.0/" data-same-page="false"', html)
        self.assertIn('value="/roo/v0.2.0/docs/new/" data-same-page="true"', html)
        search = (output / "v0.1.0/search/search_index.json").read_text()
        self.assertNotIn("Second release text", search)
        self.assertNotIn("Development only text", search)
        self.assertIn("Second release text", (output / "v0.2.0/search/search_index.json").read_text())
        self.assertIn("Development only text", (output / "dev/search/search_index.json").read_text())

    def test_unavailable_or_empty_baselines_do_not_become_a_reset(self):
        target = self.root / ".site-build/previous.json"
        with patch.object(releases, "read_json", side_effect=ConnectionError("Fixture network failure")):
            with self.assertRaises(ConnectionError):
                releases.capture_previous(target)
        self.assertFalse(target.exists())
        with patch.object(releases, "read_json", return_value={"versions": []}):
            with self.assertRaisesRegex(ValueError, "empty baseline"):
                releases.capture_previous(target)
        with self.assertRaisesRegex(ValueError, "nonempty"):
            releases.verify_previous(self.registry(), {"schema": 1, "releases": []})


class ReleaseEventTests(unittest.TestCase):
    def test_tag_push_and_stable_release_events_request_publication(self):
        self.assertEqual(releases.event_tag("push", {"ref": "refs/tags/v0.2.0", "deleted": False}), "v0.2.0")
        self.assertEqual(releases.event_tag("release", {"action": "published", "release": {"tag_name": "v0.2.0", "draft": False, "prerelease": False}}), "v0.2.0")
        self.assertEqual(releases.event_tag("workflow_dispatch", {"inputs": {"release_tag": "v0.1.0"}}), "v0.1.0")

    def test_deleted_prerelease_unrelated_and_injected_events_are_ignored(self):
        events = [
            ("push", {"ref": "refs/tags/v0.2.0", "deleted": True}),
            ("push", {"ref": "refs/tags/v0.2.0-rc.1"}),
            ("push", {"ref": "refs/heads/main"}),
            ("release", {"action": "published", "release": {"tag_name": "v0.2.0", "prerelease": True}}),
            ("release", {"action": "published", "release": {"tag_name": "v0.2.0", "draft": True}}),
            ("workflow_dispatch", {"inputs": {"release_tag": "v0.2.0\npublish=true"}}),
        ]
        for name, event in events:
            with self.subTest(event=event):
                self.assertEqual(releases.event_tag(name, event), "")


if __name__ == "__main__":
    unittest.main()
