from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/b2_episode_summary_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/b2_episode_summary_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_B2_ADAPTER"), "B2 adapter not configured")
class B2EpisodeSummaryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_B2_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_B2_ADAPTER is required")
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

    @scenario("B2-001")
    def test_b2_001_publish_episode(self) -> None: self.run_contract_case("B2-001")

    @scenario("B2-002")
    def test_b2_002_invalid_candidate(self) -> None: self.run_contract_case("B2-002")

    @scenario("B2-003")
    def test_b2_003_build_summaries(self) -> None: self.run_contract_case("B2-003")

    @scenario("B2-004")
    def test_b2_004_revert_stales_summary(self) -> None: self.run_contract_case("B2-004")

    @scenario("B2-005")
    def test_b2_005_rebuild_equivalence(self) -> None: self.run_contract_case("B2-005")

    @scenario("B2-006")
    def test_b2_006_derived_evidence_rejected(self) -> None: self.run_contract_case("B2-006")

    @scenario("B2-007")
    def test_b2_007_rebuild_failure(self) -> None: self.run_contract_case("B2-007")

    @scenario("B2-008")
    def test_b2_008_non_synthetic_rejected(self) -> None: self.run_contract_case("B2-008")
