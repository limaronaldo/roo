"""Reject retired contract labels in current practitioner documentation."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"target", "build", ".runtime", ".deps", "__pycache__"}
RULES = {
    "retired field 'Mutation authority'": r"\bmutation[\s-]+authority\b",
    "retired seven-field contract": r"\b(?:seven|7)[\s-]+fields?\b",
    "retired seven-field enumeration": r"\b(?:custody|custodian|owner),\s*identity,\s*authority,\s*access,\s*horizon,\s*execution,\s*(?:and\s+)?failure\b",
    "ambiguous matrix header": r"\|\s*authority\s+and\s+access\s*\|",
    "ambiguous laboratory header": r"\|\s*owner\s+and\s+authority\s*\|",
    "retired diagram label": r"\[\s*owner,\s*access,\s*and\s+authority\s*\]",
}

# Exact migration quotations are permitted only at their named source paths.
# No whole-file exemption applies to the current chapters or overview.
HISTORICAL_QUOTES = {
    "docs/02-relationship-design.md": (
        "**Change from v0.1.0:** the first edition used seven fields and grouped coordination with\n"
        "caller permission under “Mutation authority.” This edition splits those roles.\n"
        "The tagged first edition remains available with its original wording."
    ),
    "README.md": "v0.1.0's combined Mutation\nauthority field",
}


def current_sources(root):
    """Scan current prose, excluding tagged snapshots and historical records."""
    for name in ("README.md", "CONTRIBUTING.md", "RELEASING.md", "CHANGELOG.md"):
        path = root / name
        if path.is_file():
            yield path
    for directory in ("docs", "templates", "case-studies/orders-payments", "website/pages"):
        for path in sorted((root / directory).rglob("*.md")):
            if not EXCLUDED.intersection(path.relative_to(root).parts) and not path.is_symlink():
                yield path


def violations(text, source):
    if source == "CHANGELOG.md":
        # Released entries describe past vocabulary; only new work is checked.
        heading = re.search(r"(?m)^## \[Unreleased\]\s*$", text)
        if heading is None:
            return [(1, "missing Unreleased changelog section")]
        end = re.search(r"(?m)^## ", text[heading.end():])
        stop = heading.end() + end.start() if end else len(text)
        text = "\n" * text[:heading.end()].count("\n") + text[heading.end():stop]
    quote = HISTORICAL_QUOTES.get(source)
    if quote:
        # Mask the first exact historical statement, preserving line numbers.
        text = text.replace(quote, re.sub(r"[^\n]", " ", quote), 1)
    plain = re.sub(r"[*_`]", "", text)
    found = []
    for label, pattern in RULES.items():
        for match in re.finditer(pattern, plain, re.IGNORECASE):
            found.append((plain.count("\n", 0, match.start()) + 1, label))
    return sorted(found)


def check(root=ROOT):
    errors = []
    sources = list(current_sources(root))
    for path in sources:
        source = path.relative_to(root).as_posix()
        errors.extend(f"{source}:{line}: {message}" for line, message in violations(path.read_text(), source))
    return sources, errors


def main():
    sources, errors = check()
    if errors:
        raise SystemExit("FAIL current ROO vocabulary\n" + "\n".join(errors))
    print(f"PASS current ROO vocabulary in {len(sources)} documents; migration quotations and published history preserved")


if __name__ == "__main__":
    main()
