"""Publish pinned release content and working-tree development documentation."""

import argparse
import hashlib
import io
import json
import posixpath
import re
import shutil
import subprocess
import tarfile
from html import escape
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from mkdocs.commands.build import build
from mkdocs.config import load_config

import release_tags

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
BUILD = ROOT / ".site-build"
SITE = BUILD / "site"
BASE = "https://limaronaldo.github.io/roo/"
CUSTOM = {
    "index.md": "website/pages/index.md",
    "overview.md": "README.md",
    "license.md": "website/pages/license.md",
    "maintaining.md": "website/pages/maintaining.md",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


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


def route(page):
    path = Path(page)
    if path.name in {"index.md", "README.md"}:
        return "" if path.parent == Path(".") else path.parent.as_posix() + "/"
    return path.with_suffix("").as_posix() + "/"


def registry(requested_tag=""):
    data = release_tags.discover(ROOT, requested_tag)
    for entry in data["versions"]:
        entry["pages"] = list(documents(entry["nav"]))
        if len(entry["pages"]) != len(set(entry["pages"])):
            raise ValueError("Duplicate documentation navigation entries")
        for page in entry["pages"]:
            if Path(page).is_absolute() or ".." in Path(page).parts or not page.endswith(".md"):
                raise ValueError(f"Unsafe documentation page: {page}")
        entry["routes"] = [route(page) for page in entry["pages"]]
        if len(entry["routes"]) != len(set(entry["routes"])):
            raise ValueError("Documentation pages collide at a public route")
    return data


def snapshot(entry):
    if entry["id"] == "dev":
        return ROOT
    target = BUILD / "sources" / entry["id"]
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    archive = subprocess.check_output(["git", "archive", entry["source_commit"]], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        files.extractall(target, filter="data")
    return target


def prepare(entry, source_root, publisher_commit, dirty, default="v0.1.0"):
    content = BUILD / "content" / entry["id"]
    if content.exists():
        shutil.rmtree(content)
    content.mkdir(parents=True)
    commit = publisher_commit if entry["id"] == "dev" else entry["source_commit"]
    sources = {page: CUSTOM.get(page, page) for page in entry["pages"]}
    if entry["id"] == "v0.1.0" and "index.md" in sources:
        sources["index.md"] = "website/releases/v0.1.0-home.md"
    elif entry["id"] in {"v0.2.0", "v0.3.0", "v0.4.0"} and "index.md" in sources:
        sources["index.md"] = "website/releases/v0.2.0-v0.4.0-home.md"
    reverse = {source: page for page, source in sources.items()}

    def origin(source):
        # Existing editions retain their published introductions. Future homes
        # belong to their tags; only the surrounding interface remains current.
        if source == "website/pages/index.md":
            return source_root, commit, "development" if entry["id"] == "dev" else "release"
        overlay = source.startswith("website/") or source in {".github/workflows/docs.yml", ".github/workflows/docs-release.yml"}
        return (ROOT, publisher_commit, "publisher") if overlay else (source_root, commit, "release" if entry["id"] != "dev" else "development")

    def source_path(source):
        base, _, _ = origin(source)
        path = base / source
        path.resolve().relative_to(base.resolve())
        return path

    def destination(url, source, page):
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return url
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parts.path)))
        path = source_path(target)
        if not path.exists():
            raise ValueError(f"Missing source link in {source}: {url}")
        if target in reverse:
            relative = posixpath.relpath(reverse[target], posixpath.dirname(page) or ".")
            return urlunsplit(("", "", relative, parts.query, parts.fragment))
        _, ref, _ = origin(target)
        kind = "tree" if path.is_dir() else "blob"
        return urlunsplit(("https", "github.com", f"/limaronaldo/roo/{kind}/{ref}/{quote(target, safe='/')}", parts.query, parts.fragment))

    def render_links(text, source, page):
        # Escape Mermaid punctuation only in the generated publication copy.
        text = re.sub(
            r"(?m)^(```mermaid\n)(sequenceDiagram\b[\s\S]*?)(^```)",
            lambda m: m[1] + re.sub(r"(\#(?:[0-9]+|[A-Za-z]+);)|;", lambda s: s[1] or "#59;", m[2]) + m[3], text,
        )
        lines, fence = [], None
        for line in text.splitlines(keepends=True):
            marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
            if marker:
                value = marker.group(1)
                if fence is None:
                    fence = value
                elif value[0] == fence[0] and len(value) >= len(fence):
                    fence = None
            elif fence is None:
                line = re.sub(r"(\]\()([^\s)]+)(\))", lambda m: m[1] + destination(m[2], source, page) + m[3], line)
                line = re.sub(r"^(\[[^\]]+\]:\s*)(\S+)", lambda m: m[1] + destination(m[2], source, page), line)
            lines.append(line)
        return "".join(lines)

    records = []
    for page, source in sources.items():
        relative = Path(source)
        path = source_path(source)
        if relative.parts[0] not in {"docs", "templates", "case-studies", "website"} and len(relative.parts) != 1:
            raise ValueError(f"Unexpected documentation source: {source}")
        if not path.is_file() or path.suffix != ".md" or path.is_symlink():
            raise ValueError(f"Expected a regular Markdown source: {source}")
        if any(part in relative.parts for part in ("research", ".runtime", ".deps", "target", "build")):
            raise ValueError(f"Excluded documentation source: {source}")
        data = path.read_bytes()
        text = data.decode("utf-8")
        if page == "index.md":
            status = f"Release documentation from the {entry['id']} tag." if entry["id"] != "dev" else f"Development documentation from main. Changes here are not part of {default}."
            text = text.replace("{{edition_status}}", status)
            text = text.replace("{{checkout_ref}}", entry["id"] if entry["id"] != "dev" else "main")
            text = text.replace("{{release_version}}", entry["id"] if entry["id"] != "dev" else default)
        target = content / page
        target.parent.mkdir(parents=True, exist_ok=True)
        # The compatibility copy retains links relative to its original home.
        link_source = "website/pages/index.md" if source == "website/releases/v0.2.0-v0.4.0-home.md" else source
        target.write_text(render_links(text, link_source, page))
        _, ref, kind = origin(source)
        records.append({"source": source, "page": page, "origin": kind, "commit": ref, "sha256": hashlib.sha256(data).hexdigest()})
    shutil.copytree(WEBSITE / "assets", content / "assets")
    manifest = {"edition": entry["id"], "source_ref": entry["source_ref"], "documentation_commit": commit, "publisher_commit": publisher_commit, "working_tree_dirty": dirty, "pages": records}
    if entry["id"] != "dev":
        manifest.update({key: entry[key] for key in ("tag_object", "navigation_sha256") if key in entry})
    (content / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return content, manifest


def redirect(target):
    # Query strings and fragment links survive the migration from flat URLs.
    canonical = BASE.rstrip("/") + target.removeprefix("/roo")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Open ROO documentation</title><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={escape(target, quote=True)}">
<link rel="canonical" href="{escape(canonical, quote=True)}"></head>
<body><p><a href="{escape(target, quote=True)}">Open the release documentation</a>.</p>
<script>const target = new URL({json.dumps(target)}, location.origin); target.search = location.search; target.hash = location.hash; location.replace(target.href);</script>
</body></html>\n'''


def legacy_redirects(data):
    # Newer editions win; a removed chapter keeps its newest available release.
    redirects = {}
    for entry in data["versions"]:
        if entry["id"] != "dev":
            for path in entry["routes"]:
                redirects.setdefault(path, f"/roo/{entry['id']}/{path}")
    return redirects


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-tag", default="", help="Require this stable tag to be present in the edition set")
    parser.add_argument("--previous-state", type=Path, help="Fail if any published release identity, navigation, or document changes")
    args = parser.parse_args()
    data = registry(args.release_tag)
    previous = json.loads(args.previous_state.read_text()) if args.previous_state else None
    if previous is not None:
        release_tags.verify_previous(data, previous)
    publisher = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=normal"))
    if SITE.exists():
        shutil.rmtree(SITE)
    versions = [{"id": e["id"], "label": e["label"], "url": f"/roo/{e['id']}/", "routes": e["routes"],
                 **{key: e[key] for key in ("source_commit", "tag_object", "navigation_sha256") if key in e}} for e in data["versions"]]
    for entry in data["versions"]:
        content, manifest = prepare(entry, snapshot(entry), publisher, dirty, data["default"])
        if previous is not None:
            release_tags.verify_manifest(manifest, previous)
        config = load_config(
            config_file=str(WEBSITE / "mkdocs.yml"), docs_dir=str(content), site_dir=str(SITE / entry["id"]),
            site_url=BASE + entry["id"] + "/", nav=entry["nav"],
            extra={"source_commit": manifest["documentation_commit"], "publisher_commit": publisher, "edition": entry["id"], "edition_label": entry["label"], "versions": versions, "default_edition": data["default"]},
        )
        build(config)
    redirects = legacy_redirects(data)
    (SITE / "versions.json").write_text(json.dumps({"schema": 2, "default": data["default"], "versions": versions, "redirects": redirects}, indent=2) + "\n")
    for path, destination in redirects.items():
        target = SITE / path / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(redirect(destination))
    (SITE / "404.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ROO — Page not found</title></head><body><h1>Page not found</h1><p>Choose a documentation edition:</p>' + "".join(f'<p><a href="{v["url"]}">{escape(v["label"])}</a></p>' for v in versions) + '</body></html>\n')
    import check_site
    check_site.main()
    preview = BUILD / "preview" / "roo"
    if preview.exists():
        shutil.rmtree(preview)
    preview.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SITE, preview)
    print("PASS versioned documentation; preview at http://localhost:8000/roo/")


if __name__ == "__main__":
    main()
