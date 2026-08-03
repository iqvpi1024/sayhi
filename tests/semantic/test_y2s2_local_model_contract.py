from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/y2s2_local_model_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/y2s2_local_model_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_Y2S2_ADAPTER"), "Y2S2 adapter not configured")
class Y2S2LocalModelContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_Y2S2_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_Y2S2_ADAPTER is required")
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

    @scenario("Y2S2-001")
    def test_y2s2_001_fixture_proposes_three_unconfirmed(self) -> None: self.run_contract_case("Y2S2-001")

    @scenario("Y2S2-002")
    def test_y2s2_002_envelope_fields_and_determinism(self) -> None: self.run_contract_case("Y2S2-002")

    @scenario("Y2S2-003")
    def test_y2s2_003_malformed_outputs_fail_closed(self) -> None: self.run_contract_case("Y2S2-003")

    @scenario("Y2S2-004")
    def test_y2s2_004_injection_source_and_escalation_fields(self) -> None: self.run_contract_case("Y2S2-004")

    @scenario("Y2S2-005")
    def test_y2s2_005_canonical_digest_and_revision_unchanged(self) -> None: self.run_contract_case("Y2S2-005")

    @scenario("Y2S2-006")
    def test_y2s2_006_red_line_compartments_local_only(self) -> None: self.run_contract_case("Y2S2-006")

    @scenario("Y2S2-007")
    def test_y2s2_007_local_http_stub_and_non_loopback_rejected(self) -> None: self.run_contract_case("Y2S2-007")

    @scenario("Y2S2-008")
    def test_y2s2_008_version_registry_rollback(self) -> None: self.run_contract_case("Y2S2-008")

    @scenario("Y2S2-009")
    def test_y2s2_009_user_confirmation_proposes_changeset_only(self) -> None: self.run_contract_case("Y2S2-009")

    @scenario("Y2S2-010")
    def test_y2s2_010_determinism_profile_fail_closed(self) -> None: self.run_contract_case("Y2S2-010")