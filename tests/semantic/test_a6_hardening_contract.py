from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/a6_hardening_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/a6_hardening_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_A6_ADAPTER"), "A6 adapter not configured")
class A6HardeningContractTests(unittest.TestCase):
    """A6-001..021 execute in fixed order on one shared reference-profile system
    (SPEC-A6-HARDENING-001 rule 2). This module must be executed as a whole;
    running a single test in isolation breaks the sequential-state contract."""

    @classmethod
    def setUpClass(cls) -> None:
        module_name = os.environ.get("NOETIDE_A6_ADAPTER")
        if not module_name:
            raise RuntimeError("NOETIDE_A6_ADAPTER is required")
        cls.adapter = importlib.import_module(module_name)
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.oracles = json.loads(ORACLES.read_text(encoding="utf-8"))["scenarios"]
        cls.shared_system = cls.adapter.create_system(cls.fixture)

    def run_contract_case(self, scenario_id: str) -> None:
        case = next(item for item in self.fixture["cases"] if item["scenario_id"] == scenario_id)
        system = self.adapter.create_system(self.fixture) if case.get("isolation") == "sandbox" else self.shared_system
        before = system.layer_snapshot()
        if "failure_point" in case:
            system.inject_failure(case["failure_point"])
        actual = system.run_scenario(case)
        after = system.layer_snapshot()
        expected = self.oracles[scenario_id]
        self.assertEqual(actual, expected["result"])
        for layer in expected["forbidden_mutations"]:
            self.assertEqual(after.get(layer), before.get(layer), f"{scenario_id}: {layer} changed")

    @scenario("A6-001")
    def test_a6_001_source_append_receipt(self) -> None: self.run_contract_case("A6-001")

    @scenario("A6-002")
    def test_a6_002_candidate_not_fact(self) -> None: self.run_contract_case("A6-002")

    @scenario("A6-003")
    def test_a6_003_changeset_only_writes(self) -> None: self.run_contract_case("A6-003")

    @scenario("A6-004")
    def test_a6_004_review_preview_publish(self) -> None: self.run_contract_case("A6-004")

    @scenario("A6-005")
    def test_a6_005_core_views_updated(self) -> None: self.run_contract_case("A6-005")

    @scenario("A6-006")
    def test_a6_006_receipt_history_revert(self) -> None: self.run_contract_case("A6-006")

    @scenario("A6-007")
    def test_a6_007_six_state_answers(self) -> None: self.run_contract_case("A6-007")

    @scenario("A6-008")
    def test_a6_008_bitemporal_history(self) -> None: self.run_contract_case("A6-008")

    @scenario("A6-009")
    def test_a6_009_conflict_side_by_side(self) -> None: self.run_contract_case("A6-009")

    @scenario("A6-010")
    def test_a6_010_merge_split(self) -> None: self.run_contract_case("A6-010")

    @scenario("A6-011")
    def test_a6_011_access_fail_closed(self) -> None: self.run_contract_case("A6-011")

    @scenario("A6-012")
    def test_a6_012_cross_cutting_final(self) -> None: self.run_contract_case("A6-012")

    @scenario("A6-013")
    def test_a6_013_clean_start(self) -> None: self.run_contract_case("A6-013")

    @scenario("A6-014")
    def test_a6_014_startup_db_corrupt(self) -> None: self.run_contract_case("A6-014")

    @scenario("A6-015")
    def test_a6_015_data_dir_unwritable(self) -> None: self.run_contract_case("A6-015")

    @scenario("A6-016")
    def test_a6_016_publish_failure_rollback(self) -> None: self.run_contract_case("A6-016")

    @scenario("A6-017")
    def test_a6_017_view_unavailable_fallback(self) -> None: self.run_contract_case("A6-017")

    @scenario("A6-018")
    def test_a6_018_data_paths_separation(self) -> None: self.run_contract_case("A6-018")

    @scenario("A6-019")
    def test_a6_019_backup_export(self) -> None: self.run_contract_case("A6-019")

    @scenario("A6-020")
    def test_a6_020_uninstall_semantics(self) -> None: self.run_contract_case("A6-020")

    @scenario("A6-021")
    def test_a6_021_slo_observations(self) -> None: self.run_contract_case("A6-021")
