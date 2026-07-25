from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/c3_review_calibration_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/c3_review_calibration_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_C3_ADAPTER"), "C3 adapter not configured")
class C3ReviewContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_C3_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_C3_ADAPTER is required")
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

    @scenario("C3-001")
    def test_c3_001_weekly_review_deterministic(self) -> None: self.run_contract_case("C3-001")

    @scenario("C3-002")
    def test_c3_002_monthly_yearly_window_boundaries(self) -> None: self.run_contract_case("C3-002")

    @scenario("C3-003")
    def test_c3_003_canonical_change_marks_stale(self) -> None: self.run_contract_case("C3-003")

    @scenario("C3-004")
    def test_c3_004_rebuild_new_version_history_kept(self) -> None: self.run_contract_case("C3-004")

    @scenario("C3-005")
    def test_c3_005_delete_rebuild_equivalent(self) -> None: self.run_contract_case("C3-005")

    @scenario("C3-006")
    def test_c3_006_phase_comparison_signed_deltas(self) -> None: self.run_contract_case("C3-006")

    @scenario("C3-007")
    def test_c3_007_metric_set_mismatch_rejected(self) -> None: self.run_contract_case("C3-007")

    @scenario("C3-008")
    def test_c3_008_illegal_window_rejected(self) -> None: self.run_contract_case("C3-008")

    @scenario("C3-009")
    def test_c3_009_derived_not_fact_evidence(self) -> None: self.run_contract_case("C3-009")

    @scenario("C3-010")
    def test_c3_010_cross_cutting_fail_closed(self) -> None: self.run_contract_case("C3-010")
