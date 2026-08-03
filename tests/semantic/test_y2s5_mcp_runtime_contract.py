from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/y2s5_mcp_runtime_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/y2s5_mcp_runtime_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_Y2S5_ADAPTER"), "Y2S5 adapter not configured")
class Y2S5McpRuntimeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_Y2S5_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_Y2S5_ADAPTER is required")
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

    @scenario("Y2S5-001")
    def test_y2s5_001_authorized_read(self) -> None: self.run_contract_case("Y2S5-001")

    @scenario("Y2S5-002")
    def test_y2s5_002_denied_read(self) -> None: self.run_contract_case("Y2S5-002")

    @scenario("Y2S5-003")
    def test_y2s5_003_redacted_and_sealed(self) -> None: self.run_contract_case("Y2S5-003")

    @scenario("Y2S5-004")
    def test_y2s5_004_propose_only(self) -> None: self.run_contract_case("Y2S5-004")

    @scenario("Y2S5-005")
    def test_y2s5_005_record_source(self) -> None: self.run_contract_case("Y2S5-005")

    @scenario("Y2S5-006")
    def test_y2s5_006_idempotency_and_conflict(self) -> None: self.run_contract_case("Y2S5-006")

    @scenario("Y2S5-007")
    def test_y2s5_007_revision_precondition(self) -> None: self.run_contract_case("Y2S5-007")

    @scenario("Y2S5-008")
    def test_y2s5_008_irreversible_denied(self) -> None: self.run_contract_case("Y2S5-008")

    @scenario("Y2S5-009")
    def test_y2s5_009_failure_policy_large_file(self) -> None: self.run_contract_case("Y2S5-009")

    @scenario("Y2S5-010")
    def test_y2s5_010_determinism_stdlib_loopback(self) -> None: self.run_contract_case("Y2S5-010")
