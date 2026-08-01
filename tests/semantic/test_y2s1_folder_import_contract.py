from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/y2s1_folder_import_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/y2s1_folder_import_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_Y2S1_ADAPTER"), "Y2S1 adapter not configured")
class Y2S1FolderImportContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_Y2S1_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_Y2S1_ADAPTER is required")
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

    @scenario("Y2S1-001")
    def test_y2s1_001_batch_import_three_files(self) -> None: self.run_contract_case("Y2S1-001")

    @scenario("Y2S1-002")
    def test_y2s1_002_source_fields_exact(self) -> None: self.run_contract_case("Y2S1-002")

    @scenario("Y2S1-003")
    def test_y2s1_003_duplicate_content_points_to_existing(self) -> None: self.run_contract_case("Y2S1-003")

    @scenario("Y2S1-004")
    def test_y2s1_004_rescan_zero_new_sources(self) -> None: self.run_contract_case("Y2S1-004")

    @scenario("Y2S1-005")
    def test_y2s1_005_non_whitelist_extensions_skipped(self) -> None: self.run_contract_case("Y2S1-005")

    @scenario("Y2S1-006")
    def test_y2s1_006_unsafe_paths_rejected_zero_writes(self) -> None: self.run_contract_case("Y2S1-006")

    @scenario("Y2S1-007")
    def test_y2s1_007_invalid_utf8_rejected_rest_ok(self) -> None: self.run_contract_case("Y2S1-007")

    @scenario("Y2S1-008")
    def test_y2s1_008_interrupted_import_rerun_converges(self) -> None: self.run_contract_case("Y2S1-008")

    @scenario("Y2S1-009")
    def test_y2s1_009_watch_poll_only_imports_new(self) -> None: self.run_contract_case("Y2S1-009")

    @scenario("Y2S1-010")
    def test_y2s1_010_canonical_guard_determinism_fail_closed(self) -> None: self.run_contract_case("Y2S1-010")
