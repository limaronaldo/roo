#!/usr/bin/env python3
"""Run the unchanged PostgreSQL qualification without replacing its old receipt."""

from pathlib import Path
from unittest.mock import patch

from support import CASE, pg_verify


if __name__ == "__main__":
    previous = CASE.parents[2] / "research/postgres-integration-evidence.json"
    current = CASE.parents[2] / "research/http-postgres-regression-evidence.json"
    original = Path.write_text

    def evidence_destination(path, data, *args, **kwargs):
        return original(current if path == previous else path, data, *args, **kwargs)

    # Only the evidence destination changes; source, SQL, inputs and assertions
    # execute exactly as they did in the accepted PostgreSQL qualification.
    with patch.object(Path, "write_text", evidence_destination):
        pg_verify.main()
