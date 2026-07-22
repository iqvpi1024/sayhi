from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/a2_current_state_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/a2_current_state_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_A2_ADAPTER"), "A2 adapter not configured")
class A2CurrentStateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_A2_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_A2_ADAPTER is required")
        self.adapter = importlib.import_module(module_name)
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.oracles = json.loads(ORACLES.read_text(encoding="utf-8"))["scenarios"]

    def run_contract_case(self, scenario_id: str) -> None:
        case = next(item for item in self.fixture["cases"] if item["scenario_id"] == scenario_id)
        system = self.adapter.create_system(case)
        before = system.layer_snapshot()
        if "failure_point" in case:
            system.inject_failure(case["failure_point"])
        actual = system.run_case(case)
        after = system.layer_snapshot()
        expected = self.oracles[scenario_id]
        self.assertEqual(actual, expected["result"])
        for layer in expected["forbidden_mutations"]:
            self.assertEqual(after.get(layer), before.get(layer), f"{scenario_id}: {layer} changed")

    @scenario("A2-001")
    def test_a2_001_publish_current_state(self) -> None: self.run_contract_case("A2-001")

    @scenario("A2-002")
    def test_a2_002_invalid_candidate_fail_closed(self) -> None: self.run_contract_case("A2-002")

    @scenario("A2-003")
    def test_a2_003_due_status_deterministic(self) -> None: self.run_contract_case("A2-003")

    @scenario("A2-004")
    def test_a2_004_complete_current_state(self) -> None: self.run_contract_case("A2-004")

    @scenario("A2-005")
    def test_a2_005_cancel_requires_reason(self) -> None: self.run_contract_case("A2-005")

    @scenario("A2-006")
    def test_a2_006_compensation_revert(self) -> None: self.run_contract_case("A2-006")

    @scenario("A2-007")
    def test_a2_007_projection_rebuild_failure(self) -> None: self.run_contract_case("A2-007")

    @scenario("A2-008")
    def test_a2_008_derived_misuse_rejected(self) -> None: self.run_contract_case("A2-008")
