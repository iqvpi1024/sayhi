from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/y2s4_cloud_model_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/y2s4_cloud_model_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_Y2S4_ADAPTER"), "Y2S4 adapter not configured")
class Y2S4CloudModelContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_Y2S4_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_Y2S4_ADAPTER is required")
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

    @scenario("Y2S4-001")
    def test_y2s4_001_default_closed(self) -> None: self.run_contract_case("Y2S4-001")

    @scenario("Y2S4-002")
    def test_y2s4_002_explicit_grant_proposes(self) -> None: self.run_contract_case("Y2S4-002")

    @scenario("Y2S4-003")
    def test_y2s4_003_red_line_fail_closed(self) -> None: self.run_contract_case("Y2S4-003")

    @scenario("Y2S4-004")
    def test_y2s4_004_purpose_mismatch(self) -> None: self.run_contract_case("Y2S4-004")

    @scenario("Y2S4-005")
    def test_y2s4_005_scope_mismatch(self) -> None: self.run_contract_case("Y2S4-005")

    @scenario("Y2S4-006")
    def test_y2s4_006_expiry_and_revocation(self) -> None: self.run_contract_case("Y2S4-006")

    @scenario("Y2S4-007")
    def test_y2s4_007_preview_required(self) -> None: self.run_contract_case("Y2S4-007")

    @scenario("Y2S4-008")
    def test_y2s4_008_failures_are_audited(self) -> None: self.run_contract_case("Y2S4-008")

    @scenario("Y2S4-009")
    def test_y2s4_009_audit_and_version_rollback(self) -> None: self.run_contract_case("Y2S4-009")

    @scenario("Y2S4-010")
    def test_y2s4_010_determinism_stdlib_and_synthetic(self) -> None: self.run_contract_case("Y2S4-010")
