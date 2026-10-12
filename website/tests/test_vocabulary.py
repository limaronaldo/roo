"""Regression cases for vocabulary drift without banning ordinary English."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import check_vocabulary as vocabulary


class VocabularyTests(unittest.TestCase):
    def test_retired_field_variants_and_old_summaries_fail(self):
        for text in (
            "**Mutation authority**", "mutation\nauthority", "MUTATION-AUTHORITY",
            "The seven-field contract", "All 7 fields", "all seven fields",
            "The seven\nfield contract", "all 7\nfields",
            "custody, identity, authority, access, horizon, execution, and failure",
            "Custodian, Identity, Authority, Access, Horizon, Execution, Failure",
            "| Authority and access |", "| Owner and authority |",
            "C[Owner, access, and authority]",
        ):
            with self.subTest(text=text):
                self.assertTrue(vocabulary.violations(text, "docs/chapter.md"))

    def test_normal_english_and_current_fields_are_allowed(self):
        self.assertFalse(vocabulary.violations(
            "The provider is the serialization authority.\n"
            "Capabilities convey authority under a policy.\n"
            "Custodian, Identity, Coordinator, Authorization, Access, Horizon, Execution, Failure",
            "docs/chapter.md"))

    def test_historical_exception_is_exact_path_specific_and_single_use(self):
        quote = vocabulary.HISTORICAL_QUOTES["docs/02-relationship-design.md"]
        self.assertFalse(vocabulary.violations(quote, "docs/02-relationship-design.md"))
        self.assertTrue(vocabulary.violations(quote, "docs/another.md"))
        issues = vocabulary.violations(quote + "\n\nUse mutation authority", "docs/02-relationship-design.md")
        self.assertEqual(issues, [(5, "retired field 'Mutation authority'")])
        self.assertTrue(vocabulary.violations(quote + "\n" + quote, "docs/02-relationship-design.md"))

    def test_current_sources_exclude_runtime_and_historical_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("docs/new.md", "case-studies/orders-payments/.runtime/copy.md",
                         "research/old.md", "website/releases/v0.1.0-home.md", "RELEASE_NOTES.md"):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("mutation authority")
            sources, errors = vocabulary.check(root)
            self.assertEqual([p.relative_to(root).as_posix() for p in sources], ["docs/new.md"])
            self.assertEqual(errors, ["docs/new.md:1: retired field 'Mutation authority'"])

    def test_only_unreleased_changelog_prose_is_checked(self):
        text = "# Changelog\n\n## [Unreleased]\n\n- Use mutation authority\n\n## [0.1.0]\n\nThe seven-field contract."
        self.assertEqual(vocabulary.violations(text, "CHANGELOG.md"), [(5, "retired field 'Mutation authority'")])
        self.assertFalse(vocabulary.violations(text.replace("- Use mutation authority", "- Clarify the contract"), "CHANGELOG.md"))


if __name__ == "__main__":
    unittest.main()
