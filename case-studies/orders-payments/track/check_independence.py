#!/usr/bin/env python3
"""Compile an e6-only learner and qualify real HTTP recovery with e2 incomplete."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

TRACK = Path(__file__).resolve().parent
CASE = TRACK.parent


def method(source, signature):
    """Copy one complete method body without changing any other exercise."""
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 1
    cursor = brace + 1
    while depth and cursor < len(source):
        depth += (source[cursor] == "{") - (source[cursor] == "}")
        cursor += 1
    if depth:
        raise ValueError("Incomplete learner method")
    return source[start:cursor]


def checked(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(f"Temporary learner build failed: {result.stderr.strip()}")


def compile_learners(directory):
    java_starter = (TRACK / "java/starter/roo/payments/LearnerPolicy.java").read_text()
    java_solution = (TRACK / "java/solution/roo/payments/LearnerPolicy.java").read_text()
    signature = "private static String lostResponse(TrackInput input)"
    java = java_starter.replace(method(java_starter, signature), method(java_solution, signature))
    helper = method(java_solution, "private static String payOrInspect(String identity)")
    java = java[:java.rindex("}")] + "    " + helper + "\n}\n"
    java_file = directory / "java/LearnerPolicy.java"
    java_file.parent.mkdir()
    java_file.write_text(java)
    classes = directory / "java/classes"
    classes.mkdir()
    sources = sorted(str(p) for folder in (CASE / "java/src", TRACK / "java/common")
                     for p in folder.rglob("*.java"))
    checked(["javac", "--release", "21", "-Xlint:all", "-Werror", "-d", str(classes),
             *sources, str(java_file)])

    rust_starter = (TRACK / "rust/starter/src/learner.rs").read_text()
    rust_solution = (TRACK / "rust/solution/src/learner.rs").read_text()
    rust = rust_starter.replace(method(rust_starter, "fn response_lost("),
                               method(rust_solution, "fn response_lost("))
    rust_dir = directory / "rust"
    (rust_dir / "src").mkdir(parents=True)
    (rust_dir / "src/learner.rs").write_text(rust)
    (rust_dir / "src/main.rs").write_text(
        "#[path = " + json.dumps(str(TRACK / "rust/shared.rs")) + "]\nmod shared;\n"
        "mod learner;\nfn main() { std::process::exit(shared::run(learner::decide)); }\n")
    (rust_dir / "Cargo.toml").write_text(
        '[package]\nname = "roo-track-e6-only"\nversion = "0.1.0"\n'
        'edition = "2024"\nrust-version = "1.96"\npublish = false\n'
        '[workspace]\n[dependencies]\norders-payments-case = { path = '
        + json.dumps(str(CASE / "rust")) + ' }\n[lints.rust]\nunsafe_code = "forbid"\n')
    checked(["cargo", "build", "--manifest-path", str(rust_dir / "Cargo.toml"), "--offline"])
    commands = {"rust": [str(rust_dir / "target/debug/roo-track-e6-only")]}
    for variant in ("java-composition", "java-inheritance"):
        commands[variant] = ["java", "-cp", str(classes), "roo.payments.TrackMain"]
    hashes = {"temporary_java_learner": hashlib.sha256(java.encode()).hexdigest(),
              "temporary_rust_learner": hashlib.sha256(rust.encode()).hexdigest()}
    return commands, hashes


def main():
    spec = importlib.util.spec_from_file_location("roo_track_independence", TRACK / "verify.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    receipt = verifier.EVIDENCE
    runtime = TRACK / ".runtime"
    runtime.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="roo-e6-only-") as temporary:
            commands, hashes = compile_learners(Path(temporary))
            receipt.update(qualification="e6-only completed starter, all other gaps unchanged",
                           temporary_policy_source_hashes=hashes)
            # These are actual compiled Java/Rust policies, not a fake HTTP client.
            for variant, command in commands.items():
                result = verifier.invoke(command, "policy", "e2", "recover", "Pending",
                                         "250", "p1", "LocalCommitFailed", "0", "p1", "0", "0", "ok")
                if result.returncode or result.stdout != "stop\n":
                    raise AssertionError(f"{variant}: e2 must remain incomplete")
            verifier.command = lambda source, variant: commands[variant]
            sys.argv = [str(TRACK / "verify.py"), "--source", "starter", "--exercise", "e6", "--variant", "all"]
            verifier.main()
            if any(item["observation"]["exercise"] != "e6"
                   for groups in receipt["variants"].values()
                   for item in groups["e6"]["transcript"]):
                raise AssertionError("Another learner exercise was invoked")
            receipt["e2_incomplete_verified_for_variants"] = sorted(commands)
            print("PASS e6 independently with e2 incomplete in Java and Rust", flush=True)
    except Exception as error:
        receipt.update(status="FAIL", errors=[{"type": type(error).__name__, "message": str(error)}])
        raise
    finally:
        (runtime / "e6-independent-last-run.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
