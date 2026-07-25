from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/c2_hypothesis_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/c2_hypothesis_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_C2_ADAPTER"), "C2 adapter not configured")
class C2HypothesisContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_C2_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_C2_ADAPTER is required")
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

    @scenario("C2-001")
    def test_c2_001_confirmed_create_active(self) -> None: self.run_contract_case("C2-001")

    @scenario("C2-002")
    def test_c2_002_attach_support_status_kept(self) -> None: self.run_contract_case("C2-002")

    @scenario("C2-003")
    def test_c2_003_counter_evidence_no_auto_transition(self) -> None: self.run_contract_case("C2-003")

    @scenario("C2-004")
    def test_c2_004_confirmed_transition_challenged(self) -> None: self.run_contract_case("C2-004")

    @scenario("C2-005")
    def test_c2_005_confirmed_transition_weakened(self) -> None: self.run_contract_case("C2-005")

    @scenario("C2-006")
    def test_c2_006_presentation_tentative_fact_isolated(self) -> None: self.run_contract_case("C2-006")

    @scenario("C2-007")
    def test_c2_007_upgrade_to_fact_rejected(self) -> None: self.run_contract_case("C2-007")

    @scenario("C2-008")
    def test_c2_008_correction_retire_restore_history(self) -> None: self.run_contract_case("C2-008")

    @scenario("C2-009")
    def test_c2_009_unconfirmed_operations_rejected(self) -> None: self.run_contract_case("C2-009")

    @scenario("C2-010")
    def test_c2_010_cross_cutting_fail_closed(self) -> None: self.run_contract_case("C2-010")
