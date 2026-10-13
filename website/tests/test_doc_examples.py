"""Prevent documentation checks from silently skipping newly added fences."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from check_doc_examples import examples, published_markdown


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

    def test_case_and_alias_labels_tilde_indentation_and_long_fences_are_recognized(self):
        cases = (
            ("```Rust\nfn main() {}\n```\n", "rust"),
            ("~~~rs\nfn main() {}\n~~~\n", "rust"),
            ("   ````JAVA\nclass Example {}\n   ````\n", "java"),
            ("````rs\nfn main() { let marker = \\\"```\\\"; }\n```\n````\n", "rust"),
        )
        for index, (fence, language) in enumerate(cases):
            marker_language = "Rust" if language == "rust" else "Java"
            source = f"<!-- roo-example: variant-{index} -->\n**Compiled and tested in CI · {marker_language}.**\n\n{fence}"
            with self.subTest(fence=fence):
                snippets = self.parse(source)
                self.assertEqual([snippet["language"] for snippet in snippets], [language])

    def test_unmarked_tilde_rs_and_indented_java_fences_fail(self):
        for fence in ("~~~RS\nfn main() {}\n~~~\n", "    ```java\nclass Example {}\n    ```\n"):
            with self.subTest(fence=fence), self.assertRaisesRegex(ValueError, "Unclassified"):
                self.parse(fence)

    def test_tested_fences_cannot_use_renderer_or_skip_attributes(self):
        source = "<!-- roo-example: attributes -->\n**Compiled and tested in CI · Rust.**\n\n```rs title=sample\nfn main() {}\n```\n"
        with self.assertRaisesRegex(ValueError, "must not skip"):
            self.parse(source)

    def test_published_markdown_includes_root_case_studies_and_site_pages_not_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ("README.md", "docs/chapter.md", "case-studies/demo/README.md",
                     "website/pages/index.md", "website/releases/v0.1.0-home.md", "research/old.md")
            for name in names:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# Source\n")
            sources = {path.relative_to(root).as_posix() for path in published_markdown(root)}
            self.assertEqual(sources, set(names[:-1]))


if __name__ == "__main__":
    unittest.main()
