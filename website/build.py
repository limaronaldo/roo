"""Render allowlisted repository documents without changing their sources."""

import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
BUILD = ROOT / ".site-build"
CONTENT = BUILD / "content"
SITE = BUILD / "site"
CUSTOM = {
    "index.md": "website/pages/index.md",
    "overview.md": "README.md",
    "license.md": "website/pages/license.md",
    "maintaining.md": "website/pages/maintaining.md",
}


def documents(nav):
    for item in nav:
        if isinstance(item, str):
            yield item
        else:
            for value in item.values():
                if isinstance(value, list):
                    yield from documents(value)
                else:
                    yield value


def prepare():
    # BaseLoader reads navigation as data, without evaluating YAML Python tags.
    config = yaml.load((WEBSITE / "mkdocs.yml").read_text(), Loader=yaml.BaseLoader)
    pages = list(documents(config["nav"]))
    if len(pages) != len(set(pages)):
        raise ValueError("Duplicate documentation navigation entries")
    sources = {page: (ROOT / CUSTOM.get(page, page)).resolve() for page in pages}
    for source in sources.values():
        relative = source.relative_to(ROOT)
        if relative.parts[0] not in {"docs", "templates", "case-studies", "website"} and len(relative.parts) != 1:
            raise ValueError(f"Unexpected documentation source: {relative}")
        if not source.is_file() or source.suffix != ".md" or source.is_symlink():
            raise ValueError(f"Expected a regular Markdown source: {relative}")
        if any(part in relative.parts for part in ("research", ".runtime", ".deps", "target", "build")):
            raise ValueError(f"Excluded documentation source: {relative}")
    reverse = {source: page for page, source in sources.items()}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("Expected an exact Git source commit")
    if CONTENT.exists():
        shutil.rmtree(CONTENT)
    CONTENT.mkdir(parents=True)

    def destination(url, source, page):
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return url
        target = (source.parent / unquote(parts.path)).resolve()
        target.relative_to(ROOT)
        if not target.exists():
            raise ValueError(f"Missing source link in {source.relative_to(ROOT)}: {url}")
        if target in reverse:
            path = posixpath.relpath(reverse[target], posixpath.dirname(page) or ".")
            return urlunsplit(("", "", path, parts.query, parts.fragment))
        kind = "tree" if target.is_dir() else "blob"
        path = quote(target.relative_to(ROOT).as_posix(), safe="/")
        return urlunsplit(("https", "github.com", f"/limaronaldo/roo/{kind}/{commit}/{path}", parts.query, parts.fragment))

    def render_links(text, source, page):
        # Mermaid treats literal semicolons as statements in sequence diagrams.
        # Escape message punctuation only in the generated publication copy.
        text = re.sub(
            r"(?m)^(```mermaid\n)(sequenceDiagram\b[\s\S]*?)(^```)",
            lambda m: m[1] + re.sub(r"(\#(?:[0-9]+|[A-Za-z]+);)|;", lambda s: s[1] or "#59;", m[2]) + m[3],
            text,
        )
        lines = []
        fence = None
        for line in text.splitlines(keepends=True):
            marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
            if marker:
                value = marker.group(1)
                if fence is None:
                    fence = value
                elif value[0] == fence[0] and len(value) >= len(fence):
                    fence = None
                lines.append(line)
                continue
            if fence is None:
                line = re.sub(r"(\]\()([^\s)]+)(\))", lambda m: m[1] + destination(m[2], source, page) + m[3], line)
                line = re.sub(r"^(\[[^\]]+\]:\s*)(\S+)", lambda m: m[1] + destination(m[2], source, page), line)
            lines.append(line)
        return "".join(lines)

    records = []
    for page, source in sources.items():
        data = source.read_bytes()
        target = CONTENT / page
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_links(data.decode("utf-8"), source, page))
        records.append({"source": source.relative_to(ROOT).as_posix(), "page": page, "sha256": hashlib.sha256(data).hexdigest()})
    shutil.copytree(WEBSITE / "assets", CONTENT / "assets")
    manifest = {"release_edition": "v0.1.0", "documentation_commit": commit, "pages": records}
    (CONTENT / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    os.environ["ROO_DOCS_COMMIT"] = commit
    return pages


def main():
    os.chdir(ROOT)
    pages = prepare()
    subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "--config-file", str(WEBSITE / "mkdocs.yml")], check=True)
    subprocess.run([sys.executable, str(WEBSITE / "check_site.py")], check=True)
    preview = BUILD / "preview" / "roo"
    if preview.exists():
        shutil.rmtree(preview)
    preview.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SITE, preview)
    print(f"PASS documentation build: {len(pages)} pages; preview at http://localhost:8000/roo/")


if __name__ == "__main__":
    main()
