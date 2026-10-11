"""Prevent documentation checks from silently skipping newly added fences."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from check_doc_examples import examples


class DocExampleTests(unittest.TestCase):
    def parse(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chapter.md"
            path.write_text(source)
            return list(examples(path))

    def test_unclassified_fence_fails(self):
        with self.assertRaisesRegex(ValueError, "Unclassified"):
            self.parse("```java\nclass Silent {}\n```\n")

    def test_rust_ignore_cannot_bypass_execution(self):
        with self.assertRaisesRegex(ValueError, "must not skip"):
            self.parse("<!-- roo-example: skipped -->\n**Compiled and tested in CI · Rust.**\n\n```rust,ignore\ninvalid code\n```\n")

    def test_language_label_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError, "Unclassified"):
            self.parse("<!-- roo-example: mislabeled -->\n**Compiled and tested in CI · Java.**\n\n```rust\nassert!(true);\n```\n")


if __name__ == "__main__":
    unittest.main()
