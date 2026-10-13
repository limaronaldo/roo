"""Keep compose.yaml's resource limits and the wrapper's expected values in step."""

from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
COMPOSE_YAML = (REPO_ROOT / "compose.yaml").read_text(encoding="utf-8")
WRAPPER = (REPO_ROOT / "case-studies/orders-payments/track/compose.sh").read_text(encoding="utf-8")
GIB = 1024**3


def yaml_value(key: str) -> str:
    match = re.search(rf"^\s+{key}:\s*(\S+)\s*$", COMPOSE_YAML, re.MULTILINE)
    if match is None:
        raise AssertionError(f"compose.yaml does not set {key}")
    return match.group(1)


def wrapper_value(name: str) -> int:
    match = re.search(rf"^{name}=(\d+)\s*$", WRAPPER, re.MULTILINE)
    if match is None:
        raise AssertionError(f"compose.sh does not define {name}")
    return int(match.group(1))


class ComposeLimitTests(unittest.TestCase):
    def test_memory_limit_matches_wrapper_expectation(self) -> None:
        value = yaml_value("mem_limit")
        self.assertRegex(value, r"^\d+g$", "extend this test before using another unit")
        self.assertEqual(int(value[:-1]) * GIB, wrapper_value("expected_memory_bytes"))

    def test_cpu_limit_matches_wrapper_expectation(self) -> None:
        self.assertEqual(round(float(yaml_value("cpus")) * 1_000_000_000), wrapper_value("expected_nano_cpus"))

    def test_process_limit_matches_wrapper_expectation(self) -> None:
        self.assertEqual(int(yaml_value("pids_limit")), wrapper_value("expected_pids_limit"))

    def test_isolation_settings_are_still_present(self) -> None:
        self.assertEqual(yaml_value("network_mode"), "none")
        self.assertEqual(yaml_value("cap_drop"), "[ALL]")
        self.assertEqual(yaml_value("security_opt"), "[no-new-privileges:true]")


if __name__ == "__main__":
    unittest.main()
