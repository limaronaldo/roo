#!/usr/bin/env python3
"""Check that Rust negative examples fail for their declared error code."""

import json
from pathlib import Path
import re
import subprocess
import tempfile

CASE = Path(__file__).resolve().parent
CRATE = CASE / "rust"


def main():
    libraries = list((CRATE / "target/debug/deps").glob("libroo_postgres_case-*.rlib"))
    if not libraries:
        raise SystemExit("Build the Rust library before checking negative examples")
    library = max(libraries, key=lambda path: path.stat().st_mtime_ns)
    driver = max((CRATE / "target/debug/deps").glob("libpostgres-*.rlib"), key=lambda path: path.stat().st_mtime_ns)
    records = []
    with tempfile.TemporaryDirectory(prefix="roo-negative-") as directory:
        for path in sorted((CRATE / "src").glob("*.rs")):
            doc = "\n".join(
                re.sub(r"^\s*//[/!] ?", "", line)
                for line in path.read_text().splitlines()
            )
            for index, match in enumerate(re.finditer(
                r"```compile_fail,(E\d{4})\n(.*?)```", doc, re.S,
            )):
                expected, body = match.groups()
                sample = Path(directory) / f"{path.stem}_{index}.rs"
                sample.write_text("fn main() {\n" + body + "\n}\n")
                result = subprocess.run([
                    "rustc", "--edition=2024", "--emit=metadata",
                    "--error-format=json", "--crate-name", "roo_negative",
                    "--extern", f"roo_postgres_case={library}",
                    "--extern", f"postgres={driver}",
                    "-L", f"dependency={library.parent}",
                    "--out-dir", directory, str(sample),
                ], capture_output=True, text=True, check=False, timeout=30)
                codes = set()
                for line in result.stderr.splitlines():
                    diagnostic = json.loads(line)
                    if diagnostic.get("level") == "error" and diagnostic.get("code"):
                        codes.add(diagnostic["code"]["code"])
                if result.returncode == 0 or codes != {expected}:
                    raise SystemExit(
                        f"{path.name} example {index}: expected only {expected}, "
                        f"observed {sorted(codes)}; exit {result.returncode}\n{result.stderr}"
                    )
                records.append({"source": str(path.relative_to(CASE)),
                                "example": index, "expected": expected,
                                "observed": sorted(codes), "exit_code": result.returncode})
    if len(records) != 4:
        raise SystemExit("Expected exactly four declared compiler-negative examples")
    (CASE / "rust/target/negative-evidence.json").write_text(
        json.dumps(records, indent=2) + "\n",
    )
    print(f"PASS Rust compiler negatives: {len(records)} intended diagnostics")


if __name__ == "__main__":
    main()
