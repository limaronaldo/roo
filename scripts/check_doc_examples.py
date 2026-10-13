"""Compile and run marked examples and guard published Markdown fences.

Run from any directory with Python 3, Rust 1.96+, and JDK 21+ installed.
No PostgreSQL, Docker, network access, or third-party Python package is needed.
"""

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENING_FENCE = re.compile(r"^[ \t]*(?P<marker>`{3,}|~{3,})(?P<info>[^`]*)$")
TARGET_LANGUAGE = re.compile(r"(?i)^(?P<language>rust|rs|java)(?=$|[\s,])")
MARKER = re.compile(
    r"<!-- roo-example: ([a-z0-9-]+) -->[ \t]*\r?\n"
    r"\*\*Compiled and tested in CI · (Rust|Java)\.\*\*[ \t]*(?:\r?\n[ \t]*)*\Z"
)
JAVA_MAIN = {
    "closed-payment-java": "ClosedPaymentExample",
    "reader-injection-java": "ReaderInjectionExample",
    "library-checkout-java": "Library",
}

# The case-study README explicitly labels this one block as an excerpt from the
# separately compiled recovery.rs example. Pin its bytes so that a changed or
# newly added block cannot inherit the exception silently.
EXCERPT_HASHES = {
    ("case-studies/orders-payments/README.md", "a8ba1f3ed742b935c8d7ec9bed85d93a4184eb444a50a96f9f8d34211b7688d2"):
        "The full runnable recovery example is compiled by the orders/payments case suite.",
}


def published_markdown(root=ROOT):
    """Return current Markdown inputs that can appear in the published site."""
    paths = set(root.glob("*.md"))
    for directory in ("docs", "templates", "case-studies", "website/pages", "website/releases"):
        base = root / directory
        if base.is_dir():
            paths.update(base.rglob("*.md"))
    return [path for path in sorted(paths) if not path.is_symlink()]


def fences(text):
    """Yield Markdown fenced blocks, including tilde and indented variants."""
    lines = text.splitlines(keepends=True)
    offset = 0
    index = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.rstrip("\r\n")
        opening = OPENING_FENCE.match(line)
        if opening is None:
            offset += len(raw)
            index += 1
            continue

        marker = opening.group("marker")
        info = opening.group("info").strip()
        start = offset
        code_lines = []
        index += 1
        offset += len(raw)
        closed = False
        while index < len(lines):
            raw = lines[index]
            line = raw.rstrip("\r\n")
            closing = re.fullmatch(rf"[ \t]*{re.escape(marker[0])}{{{len(marker)},}}[ \t]*", line)
            if closing:
                closed = True
                index += 1
                offset += len(raw)
                break
            code_lines.append(raw)
            index += 1
            offset += len(raw)
        yield {
            "start": start,
            "info": info,
            "code": "".join(code_lines),
            "closed": closed,
            "marker": marker,
        }


def _relative_source(path):
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def examples(path):
    """Reject unclassified Rust/Java fences instead of silently skipping them."""
    text = path.read_text()
    source = _relative_source(path)
    for fence in fences(text):
        language_match = TARGET_LANGUAGE.match(fence["info"])
        if language_match is None:
            continue
        language = language_match.group("language").lower()
        language = "rust" if language in {"rust", "rs"} else "java"
        if not fence["closed"]:
            raise ValueError(f"Unclosed {language} fence in {path.name}")
        marker = MARKER.search(text[:fence["start"]])
        if marker is None:
            digest = hashlib.sha256(fence["code"].encode()).hexdigest()
            if (source, digest) in EXCERPT_HASHES:
                continue
            raise ValueError(f"Unclassified {language} fence in {path.name}")
        if text[marker.end():fence["start"]].strip():
            raise ValueError(f"Example marker must immediately precede its fence in {path.name}")
        marked_language = marker[2].lower()
        if marked_language != language:
            raise ValueError(f"Unclassified {language} fence in {path.name}")
        if fence["info"][language_match.end():].strip():
            raise ValueError(f"Tested fence must not skip compilation: {marker[1]}")
        yield {"id": marker[1], "language": language, "code": fence["code"], "path": path}


def main():
    snippets = [example for path in published_markdown() for example in examples(path)]
    ids = [snippet["id"] for snippet in snippets]
    if not snippets or len(ids) != len(set(ids)):
        raise ValueError("Expected nonempty examples with unique identities")
    registered = (ROOT / "src/lib.rs").read_text()
    for snippet in snippets:
        if snippet["language"] == "rust":
            try:
                relative = snippet["path"].resolve().relative_to((ROOT / "docs").resolve()).as_posix()
            except ValueError as error:
                raise ValueError(f"Rust example must be included in root rustdoc: {snippet['path']}") from error
            include = f'include_str!("../docs/{relative}")'
            if include not in registered:
                raise ValueError(f"Rust example must be included in root rustdoc: {snippet['path']}")
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
