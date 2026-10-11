"""Discover stable release editions and protect already published sources."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://limaronaldo.github.io/roo/"
VERSION = re.compile(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
COMMIT = re.compile(r"[a-f0-9]{40}")


def version_key(name):
    match = VERSION.fullmatch(name)
    if not match:
        raise ValueError(f"Expected a stable release tag vX.Y.Z: {name!r}")
    return tuple(int(part) for part in match.groups())


def edition_label(name, latest):
    """Version identifies a snapshot; pre-1.0 editions remain previews."""
    if name == "v0.1.0":
        status = "first edition · preview"
    elif version_key(name)[0] == 0:
        status = "preview"
    else:
        status = "release"
    if name != latest:
        status += " · archived"
    return f"{name} ({status})"


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def navigation(text):
    # Imported here so the event dispatcher needs only Python's standard library.
    import yaml
    value = yaml.load(text, Loader=yaml.BaseLoader)
    if not isinstance(value, dict) or not isinstance(value.get("nav"), list):
        raise ValueError("Expected an explicit documentation navigation mapping")
    return value["nav"]


def discover(root, requested_tag=""):
    policy = json.loads((root / "website/versions.json").read_text())
    if policy.get("default_policy") != "highest-stable-tag":
        raise ValueError("Expected the highest stable tag default policy")
    ids = [entry["id"] for entry in policy["versions"]]
    if len(ids) != len(set(ids)) or ids.count("dev") != 1:
        raise ValueError("Expected unique bootstrap editions and one development edition")
    for name in ids:
        if name != "dev":
            version_key(name)
    seeds = {entry["id"]: entry for entry in policy["versions"] if entry["id"] != "dev"}
    names = git(root, "tag", "--list").splitlines()
    names = sorted((name for name in names if VERSION.fullmatch(name)), key=version_key, reverse=True)
    if requested_tag:
        version_key(requested_tag)
        if requested_tag not in names:
            raise ValueError(f"Requested release tag is absent: {requested_tag}")
    if not names or not set(seeds).issubset(names):
        raise ValueError("A bootstrap release tag is missing; publication would lose an edition")
    entries = []
    for name in names:
        ref = f"refs/tags/{name}"
        commit = git(root, "rev-parse", f"{ref}^{{commit}}")
        tag_object = git(root, "rev-parse", ref)
        if not COMMIT.fullmatch(commit) or not COMMIT.fullmatch(tag_object):
            raise ValueError("Expected exact Git release identities")
        if name in seeds:
            seed = seeds[name]
            if seed["source_ref"] != ref or seed["source_commit"] != commit:
                raise ValueError(f"Release tag does not match its frozen commit: {name}")
            path = (root / seed["navigation"]).resolve()
            path.relative_to((root / "website").resolve())
            text = path.read_text()
            nav_origin = seed["navigation"]
        else:
            # Only read the tag's navigation as data. Never run tagged code,
            # plugins, dependency files, or workflow definitions.
            text = git(root, "show", f"{commit}:website/mkdocs.yml")
            nav_origin = f"{commit}:website/mkdocs.yml"
        nav = navigation(text)
        nav_hash = hashlib.sha256(json.dumps(nav, sort_keys=True).encode()).hexdigest()
        entries.append({"id": name, "label": edition_label(name, names[0]),
                        "source_ref": ref, "source_commit": commit, "tag_object": tag_object,
                        "navigation": nav_origin, "navigation_sha256": nav_hash, "nav": nav})
    dev = next(entry for entry in policy["versions"] if entry["id"] == "dev")
    if dev["source_ref"] != "HEAD" or "source_commit" in dev:
        raise ValueError("Development must follow the checked-out HEAD")
    nav_path = (root / dev["navigation"]).resolve()
    nav_path.relative_to((root / "website").resolve())
    entries.append({**dev, "nav": navigation(nav_path.read_text())})
    return {"default": names[0], "requested_tag": requested_tag, "versions": entries}


def read_json(url):
    # A cache-busting query requests the publication that just completed.
    request = Request(f"{url}?publication-check={time.time_ns()}", headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=20) as response:
        data = response.read(5_000_001)
    if len(data) > 5_000_000:
        raise ValueError("Published metadata exceeds the size limit")
    return json.loads(data)


def capture_previous(output):
    index = read_json(BASE + "versions.json")
    releases = []
    seen = set()
    for version in index["versions"]:
        name = version["id"]
        if name == "dev":
            continue
        version_key(name)
        if name in seen:
            raise ValueError("Duplicate published release edition")
        seen.add(name)
        manifest = read_json(BASE + name + "/source-manifest.json")
        commit = manifest["documentation_commit"]
        if manifest["edition"] != name or not COMMIT.fullmatch(commit):
            raise ValueError("Invalid published release provenance")
        if version.get("source_commit", commit) != commit:
            raise ValueError("The published edition index and source manifest disagree")
        records = [{key: record[key] for key in ("source", "page", "sha256")}
                   for record in manifest["pages"] if record["origin"] == "release"]
        if not records:
            raise ValueError("Published release has no pinned source documents")
        releases.append({"id": name, "source_commit": commit, "pages": records,
                         "tag_object": version.get("tag_object"),
                         "navigation_sha256": version.get("navigation_sha256"), "routes": version["routes"]})
    if not releases:
        raise ValueError("Expected the existing public release editions; refusing an empty baseline")
    state = {"schema": 1, "releases": releases}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2) + "\n")
    print(f"Captured {len(releases)} published release edition(s)")
    return state


def verify_previous(data, state):
    if state.get("schema") != 1 or not state.get("releases"):
        raise ValueError("Expected a nonempty publication preservation baseline")
    current = {entry["id"]: entry for entry in data["versions"]}
    for previous in state["releases"]:
        name = previous["id"]
        entry = current.get(name)
        if entry is None:
            raise ValueError(f"Previously published release is missing: {name}")
        for key in ("source_commit", "tag_object", "navigation_sha256"):
            if previous.get(key) is not None and previous[key] != entry[key]:
                raise ValueError(f"Previously published release changed its {key}: {name}")
        if previous["routes"] != entry["routes"]:
            raise ValueError(f"Previously published release navigation changed: {name}")


def verify_manifest(manifest, state):
    previous = next((entry for entry in state["releases"] if entry["id"] == manifest["edition"]), None)
    if previous is None:
        return
    records = [{key: record[key] for key in ("source", "page", "sha256")}
               for record in manifest["pages"] if record["origin"] == "release"]
    if records != previous["pages"]:
        raise ValueError(f"Previously published release document hashes changed: {manifest['edition']}")


def event_tag(event_name, event):
    if event_name == "push":
        ref = event.get("ref", "")
        if event.get("deleted") or not ref.startswith("refs/tags/"):
            return ""
        name = ref.removeprefix("refs/tags/")
    elif event_name == "release":
        release = event.get("release", {})
        if event.get("action") != "published" or release.get("draft") or release.get("prerelease"):
            return ""
        name = release.get("tag_name", "")
    elif event_name == "workflow_dispatch":
        name = event.get("inputs", {}).get("release_tag", "")
    else:
        return ""
    return name if VERSION.fullmatch(name) else ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture = commands.add_parser("capture", help="Read the public preservation baseline; fail closed on errors")
    capture.add_argument("--output", type=Path, required=True)
    commands.add_parser("event", help="Select a stable tag from the GitHub event without executing its text")
    args = parser.parse_args()
    if args.command == "capture":
        capture_previous(args.output)
    else:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        name = event_tag(os.environ["GITHUB_EVENT_NAME"], event)
        if os.environ["GITHUB_EVENT_NAME"] == "workflow_dispatch" and not name:
            raise ValueError("Manual publication requires an existing stable tag name vX.Y.Z")
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write(f"publish={'true' if name else 'false'}\ntag={name}\n")
        print(f"Stable documentation release: {name}" if name else "No stable release tag to publish")


if __name__ == "__main__":
    main()
