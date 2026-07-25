from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro import a5_testing_adapter
from noetide_micro.cli import main as cli_main


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/a5_app_shell_v1/fixture.json").read_text(encoding="utf-8"))
ORACLES = json.loads((ROOT / "tests/fixtures/a5_app_shell_v1/oracles.json").read_text(encoding="utf-8"))["scenarios"]


class A5Task002AdapterTests(unittest.TestCase):
    def _run_case(self, scenario_id: str):
        case = next(item for item in FIXTURE["cases"] if item["scenario_id"] == scenario_id)
        system = a5_testing_adapter.create_system(case)
        before = system.layer_snapshot()
        actual = system.run_case(case)
        after = system.layer_snapshot()
        expected = ORACLES[scenario_id]
        return actual, expected, before, after

    def test_all_cases_match_oracles(self) -> None:
        for scenario_id in ORACLES:
            with self.subTest(scenario_id=scenario_id):
                actual, expected, before, after = self._run_case(scenario_id)
                self.assertEqual(actual, expected["result"])
                for layer in expected["forbidden_mutations"]:
                    self.assertEqual(after.get(layer), before.get(layer), f"{scenario_id}: {layer} changed")

    def test_systems_are_isolated(self) -> None:
        case = next(item for item in FIXTURE["cases"] if item["scenario_id"] == "A5-004")
        first = a5_testing_adapter.create_system(case)
        second = a5_testing_adapter.create_system(case)
        first.run_case(case)
        self.assertEqual(first.layer_snapshot()["revisions"], "rev_011")
        self.assertEqual(second.layer_snapshot()["revisions"], "rev_010")

    def test_layer_snapshot_exposes_contract_layers(self) -> None:
        system = a5_testing_adapter.create_system(FIXTURE["cases"][0])
        snapshot = system.layer_snapshot()
        self.assertEqual(
            set(snapshot),
            {"canonical_objects", "revisions", "trust_closeness", "personality_judgments"},
        )

    def test_inject_failure_reaches_publish(self) -> None:
        case = next(item for item in FIXTURE["cases"] if item["scenario_id"] == "A5-004")
        system = a5_testing_adapter.create_system(case)
        system.inject_failure("l1.proposal.2")
        actual = system.run_case(case)
        confirm = actual["step_results"]["confirm"]
        self.assertEqual(confirm["publish_status"], "failed")
        self.assertIsNone(confirm["published_revision"])
        self.assertEqual(actual["data_revision"], "rev_010")

    def test_cli_receipts_and_history_on_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli_main(["--data-dir", tmp, "receipts"]), 0)
            self.assertEqual(cli_main(["--data-dir", tmp, "history"]), 0)

    def test_cli_guide_full_journey(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli_main(["--data-dir", tmp, "guide", "--yes"]), 0)
            self.assertEqual(cli_main(["--data-dir", tmp, "status"]), 0)
            self.assertEqual(cli_main(["--data-dir", tmp, "receipts"]), 0)
            self.assertEqual(cli_main(["--data-dir", tmp, "history"]), 0)


if __name__ == "__main__":
    unittest.main()
