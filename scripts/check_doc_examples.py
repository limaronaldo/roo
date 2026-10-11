"""Compile and run chapter examples from Markdown: Rust doctests and Java 21.

Run from any directory with Python 3, Rust 1.96+, and JDK 21+ installed.
No PostgreSQL, Docker, network access, or third-party Python package is needed.
"""

import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r"^```(rust|java)([^\n]*)\n(.*?)^```\s*$", re.M | re.S)
MARKER = re.compile(
    r"<!-- roo-example: ([a-z0-9-]+) -->\n"
    r"\*\*Compiled and tested in CI · (Rust|Java)\.\*\*\n\n$"
)
JAVA_MAIN = {
    "closed-payment-java": "ClosedPaymentExample",
    "reader-injection-java": "ReaderInjectionExample",
    "library-checkout-java": "Library",
}


def examples(path):
    """Reject unclassified or silently skipped language fences."""
    text = path.read_text()
    for fence in FENCE.finditer(text):
        marker = MARKER.search(text[:fence.start()])
        if marker is None or marker[2].lower() != fence[1]:
            raise ValueError(f"Unclassified {fence[1]} fence in {path.name}")
        if fence[2].strip():
            raise ValueError(f"Tested fence must not skip compilation: {marker[1]}")
        yield {"id": marker[1], "language": fence[1], "code": fence[3], "path": path}


def main():
    snippets = [example for path in sorted((ROOT / "docs").glob("*.md")) for example in examples(path)]
    ids = [snippet["id"] for snippet in snippets]
    if not snippets or len(ids) != len(set(ids)):
        raise ValueError("Expected nonempty examples with unique identities")
    registered = (ROOT / "src/lib.rs").read_text()
    for snippet in snippets:
        if snippet["language"] == "rust":
            include = f'include_str!("../docs/{snippet["path"].name}")'
            if include not in registered:
                raise ValueError(f"Chapter missing from rustdoc: {snippet['path'].name}")
    subprocess.run(["cargo", "test", "--locked", "--offline", "--doc"], cwd=ROOT, check=True)
    java = [snippet for snippet in snippets if snippet["language"] == "java"]
    if {snippet["id"] for snippet in java} != set(JAVA_MAIN):
        raise ValueError("Java examples and executable entry points differ")
    with tempfile.TemporaryDirectory(prefix="roo-doc-examples-") as directory:
        for snippet in java:
            destination = Path(directory) / snippet["id"]
            destination.mkdir()
            source = destination / "Snippet.java"
            source.write_text(snippet["code"])
            subprocess.run(["javac", "--release", "21", "-Xlint:all", "-Werror", "-d", str(destination), str(source)], check=True)
            subprocess.run(["java", "-cp", str(destination), JAVA_MAIN[snippet["id"]]], check=True)
            print(f"PASS {snippet['id']}: compiled for Java 21 and assertions executed", flush=True)
    print(f"PASS chapter examples: {len(snippets) - len(java)} Rust and {len(java)} Java", flush=True)


if __name__ == "__main__":
    main()
