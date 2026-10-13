#!/usr/bin/env python3
"""Fetch one pinned Jackson streaming parser from Maven Central."""

import hashlib
from pathlib import Path
import tempfile
import urllib.request

VERSION = "2.22.3"
SHA256 = "8a501126a385b25841915d839508f8a66e2a0dbc8a6709d055ef3b3e852b094c"
MAX_BYTES = 4 * 1024 * 1024
DIRECTORY = Path(__file__).resolve().parent / ".deps"
JAR = DIRECTORY / f"jackson-core-{VERSION}.jar"
URL = ("https://repo.maven.apache.org/maven2/com/fasterxml/jackson/core/"
       f"jackson-core/{VERSION}/jackson-core-{VERSION}.jar")


def main():
    if JAR.exists():
        if hashlib.sha256(JAR.read_bytes()).hexdigest() != SHA256:
            raise SystemExit("Existing Jackson artifact failed its pinned SHA-256 check")
    else:
        with urllib.request.urlopen(URL, timeout=20) as response:
            artifact = response.read(MAX_BYTES + 1)
        if len(artifact) > MAX_BYTES or hashlib.sha256(artifact).hexdigest() != SHA256:
            raise SystemExit("Downloaded Jackson artifact failed its size or SHA-256 check")
        DIRECTORY.mkdir(mode=0o700, exist_ok=True)
        # Publish verified bytes as one rename so no consumer ever opens a partial jar.
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
    print(f"PASS Jackson-core {VERSION}: pinned SHA-256 verified")


if __name__ == "__main__":
    main()
