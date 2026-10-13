#!/usr/bin/env python3
"""Fetch the pinned public JDBC artifact; verify bytes before using the jar."""

import hashlib
from pathlib import Path
import tempfile
import urllib.request

VERSION = "42.7.14"
SHA256 = "73914527305a40cce504b0d3d90b23caf565136912d607ae8ae7c5895512332c"
DIRECTORY = Path(__file__).resolve().parent / ".deps"
JAR = DIRECTORY / f"postgresql-{VERSION}.jar"
URL = f"https://jdbc.postgresql.org/download/postgresql-{VERSION}.jar"


def main():
    if JAR.exists():
        if hashlib.sha256(JAR.read_bytes()).hexdigest() != SHA256:
            raise SystemExit("Existing JDBC artifact failed its pinned SHA-256 check")
    else:
        with urllib.request.urlopen(URL, timeout=30) as response:
            artifact = response.read(4_000_001)
        if len(artifact) > 4_000_000 or hashlib.sha256(artifact).hexdigest() != SHA256:
            raise SystemExit("Downloaded JDBC artifact failed its size or SHA-256 check")
        DIRECTORY.mkdir(mode=0o700, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=DIRECTORY,
                prefix=f".{JAR.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(artifact)
            temporary_path.replace(JAR)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    print(f"PASS pgJDBC {VERSION}: pinned SHA-256 verified")


if __name__ == "__main__":
    main()
