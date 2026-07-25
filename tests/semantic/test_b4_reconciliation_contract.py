from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/b4_reconciliation_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/b4_reconciliation_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_B4_ADAPTER"), "B4 adapter not configured")
class B4ReconciliationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_B4_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_B4_ADAPTER is required")
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

    @scenario("B4-001")
    def test_b4_001_clean_incremental_no_findings(self) -> None: self.run_contract_case("B4-001")

    @scenario("B4-002")
    def test_b4_002_failure_queue_detected(self) -> None: self.run_contract_case("B4-002")

    @scenario("B4-003")
    def test_b4_003_stale_view_detected(self) -> None: self.run_contract_case("B4-003")

    @scenario("B4-004")
    def test_b4_004_orphan_reference_detected(self) -> None: self.run_contract_case("B4-004")

    @scenario("B4-005")
    def test_b4_005_unconsumed_changeset_detected(self) -> None: self.run_contract_case("B4-005")

    @scenario("B4-006")
    def test_b4_006_deep_reconcile_match(self) -> None: self.run_contract_case("B4-006")

    @scenario("B4-007")
    def test_b4_007_deep_reconcile_mismatch_no_repair(self) -> None: self.run_contract_case("B4-007")

    @scenario("B4-008")
    def test_b4_008_semantic_diff_modify(self) -> None: self.run_contract_case("B4-008")

    @scenario("B4-009")
    def test_b4_009_semantic_diff_hypothesis_and_no_change(self) -> None: self.run_contract_case("B4-009")

    @scenario("B4-010")
    def test_b4_010_cross_cutting_fail_closed(self) -> None: self.run_contract_case("B4-010")
