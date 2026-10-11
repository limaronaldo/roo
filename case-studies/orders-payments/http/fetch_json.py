#!/usr/bin/env python3
"""Fetch one pinned Jackson streaming parser from Maven Central."""

import hashlib
from pathlib import Path
import urllib.request

CASE = Path(__file__).resolve().parent
VERSION = "2.22.3"
SHA256 = "8a501126a385b25841915d839508f8a66e2a0dbc8a6709d055ef3b3e852b094c"
URL = ("https://repo.maven.apache.org/maven2/com/fasterxml/jackson/core/"
       f"jackson-core/{VERSION}/jackson-core-{VERSION}.jar")
DESTINATION = CASE / ".deps" / f"jackson-core-{VERSION}.jar"


def main():
    if DESTINATION.exists():
        data = DESTINATION.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=20) as response:
            data = response.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != SHA256:
        raise SystemExit("Jackson artifact failed pinned size/integrity verification")
    DESTINATION.parent.mkdir(exist_ok=True)
    DESTINATION.write_bytes(data)
    print(f"PASS Jackson-core {VERSION}: pinned SHA-256 verified")


if __name__ == "__main__":
    main()
