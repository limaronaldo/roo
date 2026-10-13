#!/usr/bin/env python3
"""Fail when a tracked file carries an authoring machine's local paths.

This repository is public, and its evidence records are produced on a
contributor's workstation. Absolute home directories, assistant session
transcript paths and session identifiers are authoring detail, not evidence:
they name a filesystem nobody else has and a transcript nobody else can read.
Recorded SHA-256 values stay, because those are the integrity anchors a reader
can actually check.

Run from anywhere; paths are resolved against the repository root.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each pattern is (compiled regex, what to do about a match).
FORBIDDEN = (
    (
        re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
        "absolute home directory; replace with a <home>/... placeholder",
    ),
    (
        re.compile(r"\.codex/(?:sessions|attachments)/"),
        "assistant transcript or attachment path; drop it and keep the SHA-256",
    ),
    (
        re.compile(r"\b(?:session_id|transcript_path)\b\s*[\"']?\s*[:=]"),
        "assistant session identifier; drop it and keep the SHA-256",
    ),
)

# This guard must be able to name the patterns it forbids.
EXEMPT = frozenset({"scripts/check_local_paths.py"})


def tracked_text_files():
    """Every tracked path git does not consider binary, as repo-relative strings."""
    listing = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    for name in listing.stdout.split("\0"):
        if not name or name in EXEMPT:
            continue
        path = ROOT / name
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable: nothing to scan for a path string
        yield name, text


def offences():
    """Yield (file, line number, reason, line) for every forbidden match."""
    for name, text in tracked_text_files():
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern, reason in FORBIDDEN:
                if pattern.search(line):
                    yield name, number, reason, line.strip()[:160]
                    break


def main():
    found = list(offences())
    if found:
        for name, number, reason, line in found:
            print(f"{name}:{number}: {reason}\n    {line}", file=sys.stderr)
        print(
            f"\n{len(found)} local-path leak(s) in tracked files. "
            "This repository is public; see scripts/check_local_paths.py.",
            file=sys.stderr,
        )
        return 1
    scanned = sum(1 for _ in tracked_text_files())
    print(f"PASS no authoring-machine paths or session identifiers in {scanned} tracked text files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
