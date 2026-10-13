"""Regression coverage for the host-owned Docker evidence boundary.

These tests copy the wrapper and compose file into a temporary project and put
a deterministic fake Docker CLI first on PATH. They never build or start a
container and do not inspect or modify repository evidence.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
TRACK_DIR = REPO_ROOT / "case-studies" / "orders-payments" / "track"
FAKE_DOCKER = r'''#!{python}
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with open(os.environ["DOCKER_MOCK_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\n")

if args == ["version"]:
    print("Docker mock version")
elif args[:2] == ["compose", "version"]:
    print("Docker Compose mock version")
elif args and args[0] == "compose" and "build" in args:
    print("mock build complete")
elif args and args[0] == "compose" and "run" in args:
    print("mock-container-id")
elif args and args[0] == "inspect" and "--format" in args:
    template = args[args.index("--format") + 1]
    if template == "{{.Image}}":
        print("sha256:mock-image")
    elif template == "{{.State.ExitCode}}":
        print(os.environ["MOCK_INSPECT_STATUS"])
    elif "{{and " in template:
        print("true" if os.environ["MOCK_ISOLATION_OK"] == "1" else "false")
    else:
        print('{"container_id":"mock-container","image_id":"sha256:mock-image",'
              '"running":false,"user":"10001:10001","network_mode":"none",'
              '"mounts":[],"port_bindings":{},"ports":{},"cap_drop":["ALL"],'
              '"privileged":false,"security_opt":["no-new-privileges:true"],'
              '"memory_bytes":4294967296,"nano_cpus":2000000000,"pids_limit":256}')
elif args and args[0] == "image" and args[1:2] == ["inspect"]:
    print("linux/amd64")
elif args and args[0] == "wait":
    print(os.environ["MOCK_WAIT_STATUS"])
elif args and args[0] == "logs":
    print("mock container logs")
elif args and args[0] == "cp":
    destination = Path(args[-1])
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "container-exit-code.txt").write_text(
        os.environ["MOCK_FORGED_STATUS"] + "\n", encoding="utf-8"
    )
elif args and args[0] in {"stop", "rm"}:
    pass
else:
    print("unexpected mock docker arguments: " + repr(args), file=sys.stderr)
    sys.exit(97)
'''


class ComposeEvidenceTests(unittest.TestCase):
    def run_wrapper(
        self,
        *,
        wait_status: str,
        inspect_status: str,
        forged_status: str,
        isolation_ok: bool = True,
    ) -> tuple[subprocess.CompletedProcess[str], Path, list[list[str]]]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        copied_track = root / "case-studies" / "orders-payments" / "track"
        copied_track.mkdir(parents=True)
        (root / "case-studies" / "orders-payments").mkdir(exist_ok=True)
        shutil.copyfile(TRACK_DIR / "compose.sh", copied_track / "compose.sh")
        shutil.copyfile(REPO_ROOT / "compose.yaml", root / "compose.yaml")

        bin_dir = root / "mock-bin"
        bin_dir.mkdir()
        docker = bin_dir / "docker"
        docker.write_text(FAKE_DOCKER.replace("{python}", sys.executable), encoding="utf-8")
        docker.chmod(0o755)
        log_path = root / "docker-args.jsonl"
        env = os.environ.copy()
        env.update(
            {
                "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
                "DOCKER_MOCK_LOG": str(log_path),
                "MOCK_WAIT_STATUS": wait_status,
                "MOCK_INSPECT_STATUS": inspect_status,
                "MOCK_FORGED_STATUS": forged_status,
                "MOCK_ISOLATION_OK": "1" if isolation_ok else "0",
            }
        )
        result = subprocess.run(
            ["bash", str(copied_track / "compose.sh"), "qualify"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        calls = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
        return result, root, calls

    @staticmethod
    def evidence_dir(result: subprocess.CompletedProcess[str], root: Path) -> Path:
        marker = "Evidence: "
        evidence_line = next(line for line in result.stdout.splitlines() if line.startswith(marker))
        evidence = Path(evidence_line[len(marker) :])
        if not evidence.is_absolute():
            evidence = root / evidence
        return evidence

    def test_forged_zero_cannot_replace_nonzero_host_status(self) -> None:
        result, root, _ = self.run_wrapper(
            wait_status="7", inspect_status="7", forged_status="0"
        )
        evidence = self.evidence_dir(result, root)

        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual((evidence / "container-exit-code.txt").read_text(), "7\n")
        self.assertEqual((evidence / "container-exit-inspect-code.txt").read_text(), "7\n")
        self.assertEqual(
            (evidence / "container-evidence" / "container-exit-code.txt").read_text(),
            "0\n",
        )
        self.assertEqual(
            {path.relative_to(evidence) for path in evidence.rglob("container-exit-code.txt")},
            {Path("container-evidence/container-exit-code.txt"), Path("container-exit-code.txt")},
        )

    def test_wait_and_inspect_disagreement_fails_closed(self) -> None:
        result, root, calls = self.run_wrapper(
            wait_status="7", inspect_status="8", forged_status="0"
        )
        evidence = self.evidence_dir(result, root)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("disagree", result.stderr)
        self.assertEqual((evidence / "wrapper-exit-code.txt").read_text(), "1\n")
        self.assertFalse((evidence / "container-exit-code.txt").exists())
        self.assertEqual(
            (evidence / "container-evidence" / "container-exit-code.txt").read_text(),
            "0\n",
        )
        self.assertTrue(any(call and call[0] == "wait" for call in calls))

    def test_forged_nonzero_cannot_change_zero_host_status(self) -> None:
        result, root, _ = self.run_wrapper(
            wait_status="0", inspect_status="0", forged_status="7"
        )
        evidence = self.evidence_dir(result, root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((evidence / "container-exit-code.txt").read_text(), "0\n")
        self.assertEqual((evidence / "container-exit-inspect-code.txt").read_text(), "0\n")
        self.assertEqual((evidence / "wrapper-exit-code.txt").read_text(), "0\n")
        self.assertEqual(
            (evidence / "container-evidence" / "container-exit-code.txt").read_text(),
            "7\n",
        )

    def test_resource_cap_inspection_is_still_mandatory(self) -> None:
        result, root, calls = self.run_wrapper(
            wait_status="0", inspect_status="0", forged_status="0", isolation_ok=False
        )
        evidence = self.evidence_dir(result, root)
        isolation_call = next(
            call
            for call in calls
            if call and call[0] == "inspect" and "--format" in call
            and "{{and " in call[call.index("--format") + 1]
        )
        template = isolation_call[isolation_call.index("--format") + 1]

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual((evidence / "isolation-check-exit-code.txt").read_text(), "1\n")
        self.assertFalse(any(call and call[0] == "wait" for call in calls))
        # Docker's templates expose numbers as json.Number, so the wrapper compares their text.
        self.assertIn('(eq (printf "%v" .HostConfig.Memory) "4294967296")', template)
        self.assertIn('(eq (printf "%v" .HostConfig.NanoCpus) "2000000000")', template)
        self.assertIn('(eq (printf "%v" .HostConfig.PidsLimit) "256")', template)


if __name__ == "__main__":
    unittest.main()
