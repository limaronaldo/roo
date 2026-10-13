"""Keep completed variants out of later schedules' finite process budget."""

import copy
from contextlib import ExitStack
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import verify_authorization as verify


SCENARIOS = (
    "identity_and_isolation", "operation_matrix", "coarse_and_route_contract",
    "hidden_outcomes", "observation_schedules", "execution_before_revocation",
    "relay_vs_queued_revocation", "durable_gaps", "process_crash",
    "refund_prepare_gap", "refund_recovery",
)


class AuthorizationLifecycleTests(unittest.TestCase):
    def exercise(self, failing_variant=None):
        processes = []
        observed = {variant: [] for variant in verify.VARIANTS}
        scenario_servers = []
        restart_pairs = []

        class Server:
            def __init__(self, variant, **_):
                self.variant = variant
                self.process = SimpleNamespace(returncode=None, pid=len(processes) + 1)
                self.process.poll = lambda: self.process.returncode
                processes.append(self)

            def stop(self):
                self.process.returncode = 0

        def scenario(name):
            def check(variant, legacy, *args):
                self.assertFalse(
                    any(p.variant != variant and p.process.poll() is None for p in processes),
                    "A completed variant still consumes the next variant's process budget",
                )
                observed[variant].append(name)
                if legacy not in scenario_servers:
                    scenario_servers.append(legacy)
                if variant == failing_variant:
                    raise RuntimeError("Synthetic scenario failure")
            return check

        def restart(auth, legacy):
            self.assertEqual(set(auth), set(verify.VARIANTS))
            self.assertEqual(set(legacy), set(verify.VARIANTS))
            self.assertTrue(all(p.process.poll() is not None for p in scenario_servers))
            for variant in verify.VARIANTS:
                self.assertIsNone(auth[variant].process.poll())
                self.assertIsNone(legacy[variant].process.poll())
                self.assertNotIn(legacy[variant], scenario_servers)
                restart_pairs.append(variant)

        def cleanup():
            for server in processes:
                server.stop()

        evidence = copy.deepcopy(verify.EVIDENCE)
        evidence.update(variants={}, errors=[], status="RUNNING")
        with ExitStack() as stack:
            replacements = {
                "Server": Server, "PROCESSES": processes, "EVIDENCE": evidence,
                "startup_rejections": lambda variant: None,
                "expect_error": lambda *args, **kwargs: None,
                "restart": restart, "cleanup": cleanup, "write_receipt": lambda: None,
                **{name: scenario(name) for name in SCENARIOS},
            }
            for name, replacement in replacements.items():
                stack.enter_context(patch.object(verify, name, replacement))
            for name in ("start", "apply_schema"):
                stack.enter_context(patch.object(verify.cluster, name))
            stack.enter_context(patch.object(verify.cluster, "sql", return_value="roo_authorization.operation_grants"))
            stack.enter_context(patch.object(verify.cluster, "configuration", return_value={}))
            stack.enter_context(patch.object(verify.cluster, "running", return_value=True))
            if failing_variant:
                with self.assertRaisesRegex(RuntimeError, "Synthetic scenario failure"):
                    verify.main()
            else:
                verify.main()
        self.assertTrue(all(p.process.poll() is not None for p in processes))
        return observed, restart_pairs, evidence

    def test_scenarios_release_previous_variants_and_keep_shared_restart(self):
        observed, restart_pairs, evidence = self.exercise()
        for variant in verify.VARIANTS:
            self.assertEqual(observed[variant], list(SCENARIOS))
            self.assertTrue(evidence["variants"][variant]["scenario_servers_stopped"])
        self.assertEqual(restart_pairs, list(verify.VARIANTS))
        self.assertEqual(evidence["status"], "PASS")

    def test_scenario_failure_stops_owned_servers_and_skips_restart(self):
        _, restart_pairs, evidence = self.exercise(verify.VARIANTS[1])
        self.assertEqual(restart_pairs, [])
        self.assertEqual(evidence["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
