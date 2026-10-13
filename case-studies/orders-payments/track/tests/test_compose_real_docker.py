"""Run the real wrapper against a live container that tries to forge host receipts.

The container image is a tiny synthetic one built from a base image that is already
present locally. The tests are skipped when the Docker daemon or that base image is
unavailable, so they never pull images or touch the network.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
TRACK = Path("case-studies/orders-payments/track")
BASE_IMAGE = "debian:bookworm-slim"


def docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    for command in (["docker", "info"], ["docker", "image", "inspect", BASE_IMAGE]):
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
        if result.returncode != 0:
            return False
    return True


DOCKERFILE = f"""\
FROM {BASE_IMAGE}
RUN mkdir -p /workspace/evidence && chown -R 10001:10001 /workspace
COPY --chmod=755 adv/entrypoint.sh /entrypoint.sh
WORKDIR /workspace
USER 10001:10001
ENTRYPOINT ["/entrypoint.sh"]
"""

# Hostile "student code": forge every host-written receipt name, then exit with the real status.
ENTRYPOINT = textwrap.dedent(
    """\
    #!/bin/sh
    mkdir -p /workspace/evidence
    for f in container-exit-code.txt container-exit-inspect-code.txt isolation-check-exit-code.txt \\
             wrapper-exit-code.txt export-exit-code.txt; do
      printf '%s\\n' "$ADV_FORGED" > "/workspace/evidence/$f"
    done
    printf 'linux/amd64\\n' > /workspace/evidence/image-platform.txt
    printf '{"forged":true}\\n' > /workspace/evidence/container-isolation.json
    exit "$ADV_EXIT"
    """
)


@unittest.skipUnless(docker_ready(), f"Docker daemon or local {BASE_IMAGE} image unavailable")
class RealDockerForgeryTests(unittest.TestCase):
    def run_wrapper(self, *, container_exit: int, forged: int, compose_edit=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve()
        (root / TRACK).mkdir(parents=True)
        (root / "case-studies/orders-payments/README").write_text("synthetic\n", encoding="utf-8")
        (root / "adv").mkdir()
        shutil.copyfile(REPO_ROOT / TRACK / "compose.sh", root / TRACK / "compose.sh")
        (root / "adv/Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
        (root / "adv/entrypoint.sh").write_text(ENTRYPOINT, encoding="utf-8")
        compose = (REPO_ROOT / "compose.yaml").read_text(encoding="utf-8")
        compose = compose.replace(
            "dockerfile: case-studies/orders-payments/track/docker/Dockerfile", "dockerfile: adv/Dockerfile"
        ).replace("    command: [qualify]\n", "    environment: [ADV_EXIT, ADV_FORGED]\n    command: [qualify]\n")
        if compose_edit is not None:
            compose = compose_edit(compose)
        (root / "compose.yaml").write_text(compose, encoding="utf-8")
        env = {**os.environ, "ADV_EXIT": str(container_exit), "ADV_FORGED": str(forged)}
        result = subprocess.run(
            ["bash", str(root / TRACK / "compose.sh"), "qualify"],
            cwd=root, env=env, text=True, capture_output=True, check=False, timeout=600,
        )
        runs = sorted((root / "artifacts/roo-track").iterdir())
        self.assertEqual(len(runs), 1, result.stderr)
        # Remove the disposable image this run built; the wrapper itself never prunes.
        self.addCleanup(subprocess.run, ["docker", "rmi", "-f", f"roo-track:{runs[0].name}"],
                        capture_output=True, check=False)
        return result, runs[0]

    def test_container_cannot_forge_a_passing_status(self) -> None:
        result, evidence = self.run_wrapper(container_exit=7, forged=0)

        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual((evidence / "container-exit-code.txt").read_text(), "7\n")
        self.assertEqual((evidence / "container-exit-inspect-code.txt").read_text(), "7\n")
        self.assertEqual((evidence / "isolation-check-exit-code.txt").read_text(), "0\n")
        platform = subprocess.run(
            ["docker", "image", "inspect", (evidence / "image-id.txt").read_text().strip(),
             "--format", "{{.Os}}/{{.Architecture}}"],
            capture_output=True, text=True, check=True,
        ).stdout
        self.assertEqual((evidence / "image-platform.txt").read_text(), platform)
        self.assertNotIn("forged", (evidence / "container-isolation.json").read_text())
        self.assertEqual(
            (evidence / "container-evidence/container-isolation.json").read_text(), '{"forged":true}\n'
        )
        self.assertEqual((evidence / "container-evidence/container-exit-code.txt").read_text(), "0\n")

    def test_container_cannot_forge_a_failing_status(self) -> None:
        result, evidence = self.run_wrapper(container_exit=0, forged=9)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((evidence / "container-exit-code.txt").read_text(), "0\n")
        self.assertEqual((evidence / "container-evidence/container-exit-code.txt").read_text(), "9\n")

    def test_missing_process_limit_fails_the_live_isolation_check(self) -> None:
        result, evidence = self.run_wrapper(
            container_exit=0, forged=0,
            compose_edit=lambda text: "".join(
                line for line in text.splitlines(keepends=True) if "pids_limit" not in line
            ),
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("isolation check failed", result.stderr)
        self.assertEqual((evidence / "isolation-check-exit-code.txt").read_text(), "1\n")
        self.assertFalse((evidence / "container-exit-code.txt").exists())


if __name__ == "__main__":
    unittest.main()
