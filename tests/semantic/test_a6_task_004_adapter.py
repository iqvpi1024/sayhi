"""Narrow tests for A6-TASK-004 testing adapter (protocol shape only, synthetic)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from noetide_micro import a6_testing_adapter as adapter


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "tests/fixtures/a6_hardening_v1/fixture.json").read_text(encoding="utf-8")
)


def case(scenario_id: str) -> dict:
    return next(item for item in FIXTURE["cases"] if item["scenario_id"] == scenario_id)


class A6Task004AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = adapter.create_system(FIXTURE)

    def test_create_system_rejects_non_synthetic_fixture(self) -> None:
        bad = {**FIXTURE, "synthetic": False}
        with self.assertRaises(ValueError):
            adapter.create_system(bad)
        leaked = {**FIXTURE, "external_data_used": True}
        with self.assertRaises(ValueError):
            adapter.create_system(leaked)

    def test_layer_snapshot_shape(self) -> None:
        snapshot = self.system.layer_snapshot()
        self.assertEqual(
            sorted(snapshot), ["canonical", "closeness", "history", "personality", "trust"]
        )
        self.assertTrue(all(isinstance(value, str) for value in snapshot.values()))

    def test_first_scenarios_chain_and_snapshot_stability(self) -> None:
        before = self.system.layer_snapshot()
        result = self.system.run_scenario(case("A6-001"))
        self.assertEqual(
            result,
            {"source_appended": True, "receipt_issued": True, "canonical_revision_unchanged": True},
        )
        after = self.system.layer_snapshot()
        for layer in ("canonical", "trust", "closeness", "personality"):
            self.assertEqual(after[layer], before[layer])

    def test_injected_failure_required_for_rollback_scenario(self) -> None:
        with self.assertRaises(RuntimeError):
            self.system.run_scenario(case("A6-016"))
        self.system.inject_failure("mid_publish")
        result = self.system.run_scenario(case("A6-016"))
        self.assertEqual(
            result,
            {"rolled_back": True, "canonical_revision_unchanged": True, "failure_reported": True},
        )

    def test_sandbox_scenarios_do_not_touch_shared_state(self) -> None:
        before = self.system.layer_snapshot()
        clean = self.system.run_scenario(case("A6-013"))
        self.assertEqual(
            clean,
            {"exit_code": 0, "data_dir_created_at_declared_path": True, "preflight_smoke_passed": True},
        )
        self.system.inject_failure("corrupt_db_file")
        corrupt = self.system.run_scenario(case("A6-014"))
        self.assertTrue(corrupt["exit_code_nonzero"])
        self.assertTrue(corrupt["original_file_untouched"])
        self.assertFalse(corrupt["silent_repair_attempted"])
        after = self.system.layer_snapshot()
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
