from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/a4_access_policy_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/a4_access_policy_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_A4_ADAPTER"), "A4 adapter not configured")
class A4AccessPolicyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_A4_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_A4_ADAPTER is required")
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

    @scenario("A4-001")
    def test_a4_001_allow_all_fields(self) -> None: self.run_contract_case("A4-001")

    @scenario("A4-002")
    def test_a4_002_field_redaction(self) -> None: self.run_contract_case("A4-002")

    @scenario("A4-003")
    def test_a4_003_strictest_intersection(self) -> None: self.run_contract_case("A4-003")

    @scenario("A4-004")
    def test_a4_004_grant_invalid(self) -> None: self.run_contract_case("A4-004")

    @scenario("A4-005")
    def test_a4_005_fail_closed_set(self) -> None: self.run_contract_case("A4-005")

    @scenario("A4-006")
    def test_a4_006_sealed_excluded(self) -> None: self.run_contract_case("A4-006")

    @scenario("A4-007")
    def test_a4_007_zero_write(self) -> None: self.run_contract_case("A4-007")

    @scenario("A4-008")
    def test_a4_008_view_bypass_and_shape(self) -> None: self.run_contract_case("A4-008")
