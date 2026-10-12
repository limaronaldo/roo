"""Compile both realizations, test controlled schedules, and compare one oracle."""

import difflib
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(*command):
    result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8",
                            capture_output=True, timeout=120, check=False)
    if result.returncode:
        raise SystemExit(f"FAIL {' '.join(map(str, command))}\n{result.stdout}{result.stderr}")
    return result.stdout


def rows(path):
    return [line for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("#")]


def main():
    inputs = rows(HERE / "cases.tsv")
    expected = rows(HERE / "expected.tsv")
    scenarios = set()
    current, step = None, 0
    if not inputs or len(inputs) != len(expected):
        raise SystemExit("FAIL empty or mismatched fixture/oracle length")
    for source, target in zip(inputs, expected, strict=True):
        fields, output = source.split("\t"), target.split("\t")
        if len(fields) != 4 or len(output) != 5:
            raise SystemExit("FAIL fixture/oracle column count")
        if fields[0] != current:
            if fields[0] in scenarios:
                raise SystemExit("FAIL noncontiguous scenario")
            current, step = fields[0], 0
            scenarios.add(current)
        step += 1
        if output[:2] != [current, str(step)]:
            raise SystemExit("FAIL fixture/oracle scenario or step mismatch")

    print(run("cargo", "test", "--locked", "--offline", "--lib", "authorization::tests"), end="", flush=True)
    with tempfile.TemporaryDirectory(prefix="roo-authorization-") as directory:
        # Honor JAVA_HOME consistently with the documentation workflow.
        def java_tool(name):
            return str(Path(os.environ["JAVA_HOME"]) / "bin" / name) if os.environ.get("JAVA_HOME") else name

        sources = sorted(str(path) for path in (HERE / "java").rglob("*.java"))
        run(java_tool("javac"), "--release", "21", "-Xlint:all", "-Werror", "-d", directory, *sources)
        java = [java_tool("java"), "-cp", directory]
        print(run(*java, "roo.authorization.ConcurrencyTests"), end="", flush=True)
        outputs = {
            "Java": run(*java, "roo.authorization.FixtureRunner", str(HERE / "cases.tsv")),
            "Rust": run("cargo", "run", "--quiet", "--locked", "--offline", "--example",
                        "authorization_cases", "--", str(HERE / "cases.tsv")),
        }
    for language, output in outputs.items():
        actual = output.splitlines()
        if actual != expected:
            difference = "\n".join(difflib.unified_diff(expected, actual, fromfile="oracle", tofile=language))
            raise SystemExit(f"FAIL {language} authorization parity\n{difference}")
        print(f"PASS {language}: {len(scenarios)} scenarios, {len(expected)} exact state/result checkpoints")
    print("PASS authorization parity; observations never authorize execution")


if __name__ == "__main__":
    main()
