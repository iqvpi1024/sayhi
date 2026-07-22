from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/b3_commitment_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/b3_commitment_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_B3_ADAPTER"), "B3 adapter not configured")
class B3CommitmentContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_B3_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_B3_ADAPTER is required")
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

    @scenario("B3-001")
    def test_b3_001_publish_commitment(self) -> None: self.run_contract_case("B3-001")

    @scenario("B3-002")
    def test_b3_002_invalid_candidate_fail_closed(self) -> None: self.run_contract_case("B3-002")

    @scenario("B3-003")
    def test_b3_003_due_status_deterministic(self) -> None: self.run_contract_case("B3-003")

    @scenario("B3-004")
    def test_b3_004_complete_commitment(self) -> None: self.run_contract_case("B3-004")

    @scenario("B3-005")
    def test_b3_005_cancel_requires_reason(self) -> None: self.run_contract_case("B3-005")

    @scenario("B3-006")
    def test_b3_006_compensation_revert(self) -> None: self.run_contract_case("B3-006")

    @scenario("B3-007")
    def test_b3_007_projection_rebuild_failure(self) -> None: self.run_contract_case("B3-007")

    @scenario("B3-008")
    def test_b3_008_derived_misuse_rejected(self) -> None: self.run_contract_case("B3-008")
