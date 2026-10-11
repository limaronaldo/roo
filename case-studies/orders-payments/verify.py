#!/usr/bin/env python3
"""Compare three prebuilt runners with the independent contract oracle.

Builds are intentionally separate so the top-level verification script can
serialize compilers. No third-party Python packages or services are required.
"""

import csv
import io
from pathlib import Path
import subprocess
import sys
import tempfile

CASE = Path(__file__).resolve().parent
HEADER = (
    "scenario state total charge_count refund_count event_count consumer_count "
    "pending_outbox last_result payment_id refund_id"
).split()


def table(text, label):
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    if not rows or rows[0] != HEADER:
        raise ValueError(f"{label}: incorrect output header")
    if any(len(row) != len(HEADER) for row in rows[1:]):
        raise ValueError(f"{label}: incorrect output field count")
    ids = [row[0] for row in rows[1:]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label}: duplicate scenario output")
    return rows[1:]


def run(command, fixture):
    return subprocess.run(
        [*command, str(fixture)], capture_output=True, text=True,
        encoding="utf-8", timeout=30, check=False,
    )


def main():
    expected = table((CASE / "expected.tsv").read_text(), "oracle")
    fixture_rows = list(csv.reader(
        io.StringIO((CASE / "scenarios.tsv").read_text()), delimiter="\t",
    ))
    if fixture_rows[0] != ["scenario", "steps"]:
        raise ValueError("incorrect input fixture header")
    if [row[0] for row in fixture_rows[1:]] != [row[0] for row in expected]:
        raise ValueError("oracle must cover every input exactly once in input order")
    classes = str(CASE / "java/build/classes")
    runners = {
        "Java composition": ["java", "-cp", classes, "roo.payments.CompositionRunner"],
        "Java inheritance": ["java", "-cp", classes, "roo.payments.TemplateRunner"],
        "Rust composition": [str(CASE / "rust/target/debug/roo-payments")],
    }
    # These are structural errors, distinct from valid domain rejections.
    invalid = {
        "wrong_header": "scenario\tactions\nx\tadd:1:1\n",
        "duplicate_id": "scenario\tsteps\nx\tadd:1:1\nx\trelay:ok\n",
        "unknown_action": "scenario\tsteps\nx\tcharge:p1\n",
        "wrong_arity": "scenario\tsteps\nx\tadd:100\n",
        "bad_number": "scenario\tsteps\nx\tadd:one:1\n",
        "bad_mode": "scenario\tsteps\nx\tpay:p1:random:none\n",
        "empty_action": "scenario\tsteps\nx\tadd:1:1;\n",
        "extra_column": "scenario\tsteps\nx\tadd:1:1\textra\n",
        "invalid_identity": "scenario\tsteps\nx\tpay:bad-id:approve:none\n",
        "bad_late_action": "scenario\tsteps\nx\tadd:1:1;unknown\n",
    }
    with tempfile.TemporaryDirectory(prefix="roo-fixtures-") as directory:
        for name, command in runners.items():
            result = run(command, CASE / "scenarios.tsv")
            if result.returncode:
                raise ValueError(f"{name}: runner failed: {result.stderr.strip()}")
            actual = table(result.stdout, name)
            if actual != expected:
                for index in range(max(len(actual), len(expected))):
                    observed = actual[index] if index < len(actual) else "<missing>"
                    required = expected[index] if index < len(expected) else "<extra>"
                    if observed != required:
                        raise ValueError(
                            f"{name}: oracle mismatch at row {index + 1}\n"
                            f"expected: {required}\nobserved: {observed}"
                        )
            for label, text in invalid.items():
                fixture = Path(directory) / f"{label}.tsv"
                fixture.write_text(text)
                rejected = run(command, fixture)
                if rejected.returncode == 0 or not rejected.stderr.strip():
                    raise ValueError(f"{name}: malformed fixture {label} was not diagnosed")
            print(f"PASS {name}: {len(expected)} oracle rows, {len(invalid)} malformed fixtures")
    print("PASS shared contract: all three variants match the independent oracle")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
