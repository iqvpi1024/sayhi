from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/c4_scenario_action_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/c4_scenario_action_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_C4_ADAPTER"), "C4 adapter not configured")
class C4ScenarioContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_C4_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_C4_ADAPTER is required")
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

    @scenario("C4-001")
    def test_c4_001_confirmed_create_trio_deterministic_feasibility(self) -> None: self.run_contract_case("C4-001")

    @scenario("C4-002")
    def test_c4_002_unconfirmed_create_rejected(self) -> None: self.run_contract_case("C4-002")

    @scenario("C4-003")
    def test_c4_003_upgrade_to_observed_rejected(self) -> None: self.run_contract_case("C4-003")

    @scenario("C4-004")
    def test_c4_004_confirmed_select_decision_unchanged(self) -> None: self.run_contract_case("C4-004")

    @scenario("C4-005")
    def test_c4_005_confirmed_follow_ups_open(self) -> None: self.run_contract_case("C4-005")

    @scenario("C4-006")
    def test_c4_006_confirmed_complete_revision_history(self) -> None: self.run_contract_case("C4-006")

    @scenario("C4-007")
    def test_c4_007_missed_derived_view(self) -> None: self.run_contract_case("C4-007")

    @scenario("C4-008")
    def test_c4_008_feasibility_deterministic(self) -> None: self.run_contract_case("C4-008")

    @scenario("C4-009")
    def test_c4_009_presentation_not_fact_no_advice(self) -> None: self.run_contract_case("C4-009")

    @scenario("C4-010")
    def test_c4_010_cross_cutting_fail_closed(self) -> None: self.run_contract_case("C4-010")
