#!/usr/bin/env python3
"""Compare the historical research manifests with what git actually contains.

The manifests in research/ (`*candidate*.json`, `*baseline*.json`) list
`{path, sha256, bytes}` entries that photographed a working tree before it was
committed. This script is read-only: it never writes to the repository, and it
only reads blobs through `git`. It reports, for each manifest, how many entries

  * match no blob reachable from any ref (the content was never committed), and
  * are identical, changed or absent in the tree of each requested commit.

Usage (from the repository root):

    python3 research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0 \
        --output research/manifest-provenance-8bf017f.json

Revisions are resolved to full commit ids and recorded in the output, so the
result stays attributable to a commit even after the branch moves on.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MANIFEST_GLOBS = ("*candidate*.json", "*baseline*.json")


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode().strip()}")
    return result.stdout


def resolve_commit(rev):
    return git("rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()


def reachable_blob_hashes():
    """SHA-256 of every blob reachable from any ref."""
    listing = git("rev-list", "--objects", "--all").decode().splitlines()
    ids = "\n".join(line.split(" ", 1)[0] for line in listing) + "\n"
    kinds = subprocess.run(["git", "cat-file", "--batch-check"], input=ids.encode(),
                           capture_output=True, check=True).stdout.decode().splitlines()
    blob_ids = [line.split()[0] for line in kinds if line.split()[1] == "blob"]
    data = subprocess.run(["git", "cat-file", "--batch"], input=("\n".join(blob_ids) + "\n").encode(),
                          capture_output=True, check=True).stdout
    hashes, position = set(), 0
    while position < len(data):
        newline = data.index(b"\n", position)
        _, _, size = data[position:newline].decode().split()
        size = int(size)
        hashes.add(hashlib.sha256(data[newline + 1:newline + 1 + size]).hexdigest())
        position = newline + 1 + size + 1
    return hashes


def tree_entry(commit, path):
    """(sha256, bytes) of `path` at `commit`, or (None, None) when absent."""
    result = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True)
    if result.returncode != 0:
        return None, None
    return hashlib.sha256(result.stdout).hexdigest(), len(result.stdout)


def load_manifest(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    files = document.get("files")
    valid = isinstance(files, list) and files and all(
        isinstance(item, dict) and {"path", "sha256", "bytes"} <= item.keys() for item in files)
    return files if valid else None


def classify(files, commit):
    """Count manifest entries as identical, changed or absent in `commit`'s tree."""
    counts = {"identical": 0, "changed": 0, "absent": 0}
    for entry in files:
        sha, _ = tree_entry(commit, entry["path"])
        key = "absent" if sha is None else "identical" if sha == entry["sha256"] else "changed"
        counts[key] += 1
    return counts


def audit(manifest_paths, primary, extra, blob_hashes):
    commits = {primary: resolve_commit(primary), **{rev: resolve_commit(rev) for rev in extra}}
    manifests, pairs = [], {}
    for path in manifest_paths:
        files = load_manifest(path)
        if files is None:
            continue
        counts = {rev: classify(files, commit) for rev, commit in commits.items()}
        missing = [f for f in files if f["sha256"] not in blob_hashes]
        for f in missing:
            key = (f["path"], f["sha256"], f["bytes"])
            pairs.setdefault(key, []).append(path.as_posix())
        manifests.append({
            "manifest": path.as_posix(),
            "entries": len(files),
            "no_git_blob": len(missing),
            "against_commit_tree": counts,
        })
    pair_rows = []
    for (file_path, sha, size), owners in sorted(pairs.items()):
        current_sha, current_size = tree_entry(commits[primary], file_path)
        pair_rows.append({"path": file_path, "recorded_sha256": sha, "recorded_bytes": size,
                          "in_manifests": owners, f"{primary}_sha256": current_sha,
                          f"{primary}_bytes": current_size})
    return {
        "purpose": ("Historical research manifests recorded a working tree before it was committed. "
                    "This file measures them against git and does not modify them."),
        "regenerate": "python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0",
        "commits": commits,
        "blob_universe": "blobs reachable from any ref (git rev-list --objects --all)",
        "totals": {
            "manifests": len(manifests),
            "entries": sum(m["entries"] for m in manifests),
            "no_git_blob": sum(m["no_git_blob"] for m in manifests),
            "unique_path_hash_pairs_no_git_blob": len(pair_rows),
        },
        "manifests": manifests,
        "no_git_blob_pairs": pair_rows,
    }


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--rev", required=True, help="commit whose tree is the reference")
    parser.add_argument("--also", action="append", default=[], help="extra commit to count against")
    parser.add_argument("--output", help="write JSON here instead of stdout")
    args = parser.parse_args(argv)

    research = Path("research")
    if not research.is_dir():
        parser.error("run from the repository root")
    paths = sorted({p for pattern in MANIFEST_GLOBS for p in research.glob(pattern)})
    report = audit(paths, args.rev, args.also, reachable_blob_hashes())
    text = json.dumps(report, indent=2, sort_keys=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main(sys.argv[1:])
