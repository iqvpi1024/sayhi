from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/y2s3_local_web_ui_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/y2s3_local_web_ui_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_Y2S3_ADAPTER"), "Y2S3 adapter not configured")
class Y2S3LocalWebUiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_Y2S3_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_Y2S3_ADAPTER is required")
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

    @scenario("Y2S3-001")
    def test_y2s3_001_home_and_local_audit(self) -> None: self.run_contract_case("Y2S3-001")

    @scenario("Y2S3-002")
    def test_y2s3_002_record_appends_source_only(self) -> None: self.run_contract_case("Y2S3-002")

    @scenario("Y2S3-003")
    def test_y2s3_003_review_presentation_is_derived(self) -> None: self.run_contract_case("Y2S3-003")

    @scenario("Y2S3-004")
    def test_y2s3_004_confirm_publishes_changeset(self) -> None: self.run_contract_case("Y2S3-004")

    @scenario("Y2S3-005")
    def test_y2s3_005_views_reflect_published_state(self) -> None: self.run_contract_case("Y2S3-005")

    @scenario("Y2S3-006")
    def test_y2s3_006_history_labels_come_from_ledger(self) -> None: self.run_contract_case("Y2S3-006")

    @scenario("Y2S3-007")
    def test_y2s3_007_revert_restores_views_and_keeps_history(self) -> None: self.run_contract_case("Y2S3-007")

    @scenario("Y2S3-008")
    def test_y2s3_008_export_read_only_and_backup_path_controlled(self) -> None: self.run_contract_case("Y2S3-008")

    @scenario("Y2S3-009")
    def test_y2s3_009_rejections_fail_closed(self) -> None: self.run_contract_case("Y2S3-009")

    @scenario("Y2S3-010")
    def test_y2s3_010_determinism_stdlib_and_synthetic(self) -> None: self.run_contract_case("Y2S3-010")