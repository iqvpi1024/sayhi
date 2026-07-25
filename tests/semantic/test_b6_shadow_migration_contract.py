from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/b6_shadow_migration_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/b6_shadow_migration_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_B6_ADAPTER"), "B6 adapter not configured")
class B6ShadowMigrationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_B6_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_B6_ADAPTER is required")
        self.adapter = importlib.import_module(module_name)
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.oracles = json.loads(ORACLES.read_text(encoding="utf-8"))["scenarios"]

    def run_contract_case(self, scenario_id: str) -> None:
        case = next(item for item in self.fixture["cases"] if item["scenario_id"] == scenario_id)
        system = self.adapter.create_system(case)
        before = system.layer_snapshot()
        actual = system.run_case(case)
        after = system.layer_snapshot()
        expected = self.oracles[scenario_id]
        self.assertEqual(actual, expected["result"])
        for layer in expected["forbidden_mutations"]:
            self.assertEqual(after.get(layer), before.get(layer), f"{scenario_id}: {layer} changed")

    @scenario("B6-001")
    def test_b6_001_shadow_migrate_reconciled(self) -> None: self.run_contract_case("B6-001")

    @scenario("B6-002")
    def test_b6_002_transform_counts_deterministic(self) -> None: self.run_contract_case("B6-002")

    @scenario("B6-003")
    def test_b6_003_migration_fault_no_partial_write(self) -> None: self.run_contract_case("B6-003")

    @scenario("B6-004")
    def test_b6_004_shadow_deviation_mismatch_reported(self) -> None: self.run_contract_case("B6-004")

    @scenario("B6-005")
    def test_b6_005_disambiguation_candidates_deterministic(self) -> None: self.run_contract_case("B6-005")

    @scenario("B6-006")
    def test_b6_006_merge_propagation_counts(self) -> None: self.run_contract_case("B6-006")

    @scenario("B6-007")
    def test_b6_007_batch_stress_reproducible(self) -> None: self.run_contract_case("B6-007")

    @scenario("B6-008")
    def test_b6_008_history_carried_intact(self) -> None: self.run_contract_case("B6-008")

    @scenario("B6-009")
    def test_b6_009_shadow_not_evidence(self) -> None: self.run_contract_case("B6-009")

    @scenario("B6-010")
    def test_b6_010_cross_cutting_fail_closed(self) -> None: self.run_contract_case("B6-010")
