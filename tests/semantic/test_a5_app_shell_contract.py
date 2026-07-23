from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/a5_app_shell_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/a5_app_shell_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_A5_ADAPTER"), "A5 adapter not configured")
class A5AppShellContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_A5_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_A5_ADAPTER is required")
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

    @scenario("A5-001")
    def test_a5_001_record_source(self) -> None: self.run_contract_case("A5-001")

    @scenario("A5-002")
    def test_a5_002_natural_language_review(self) -> None: self.run_contract_case("A5-002")

    @scenario("A5-003")
    def test_a5_003_impact_preview(self) -> None: self.run_contract_case("A5-003")

    @scenario("A5-004")
    def test_a5_004_confirm_publish(self) -> None: self.run_contract_case("A5-004")

    @scenario("A5-005")
    def test_a5_005_read_updated_views(self) -> None: self.run_contract_case("A5-005")

    @scenario("A5-006")
    def test_a5_006_receipt_and_history(self) -> None: self.run_contract_case("A5-006")

    @scenario("A5-007")
    def test_a5_007_revert_restores_views(self) -> None: self.run_contract_case("A5-007")

    @scenario("A5-008")
    def test_a5_008_journey_audit(self) -> None: self.run_contract_case("A5-008")