from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/c5_pack_backup_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/c5_pack_backup_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_C5_ADAPTER"), "C5 adapter not configured")
class C5PackContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_C5_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_C5_ADAPTER is required")
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

    @scenario("C5-001")
    def test_c5_001_markdown_pack_export_complete(self) -> None: self.run_contract_case("C5-001")

    @scenario("C5-002")
    def test_c5_002_render_deterministic_readable(self) -> None: self.run_contract_case("C5-002")

    @scenario("C5-003")
    def test_c5_003_verify_then_tamper_rejected(self) -> None: self.run_contract_case("C5-003")

    @scenario("C5-004")
    def test_c5_004_unknown_and_missing_files_rejected(self) -> None: self.run_contract_case("C5-004")

    @scenario("C5-005")
    def test_c5_005_backup_ciphertext_receipt(self) -> None: self.run_contract_case("C5-005")

    @scenario("C5-006")
    def test_c5_006_restore_correct_key_byte_identical(self) -> None: self.run_contract_case("C5-006")

    @scenario("C5-007")
    def test_c5_007_restore_wrong_key_rejected(self) -> None: self.run_contract_case("C5-007")

    @scenario("C5-008")
    def test_c5_008_deletion_receipt_eight_components(self) -> None: self.run_contract_case("C5-008")

    @scenario("C5-009")
    def test_c5_009_partial_failure_honest(self) -> None: self.run_contract_case("C5-009")

    @scenario("C5-010")
    def test_c5_010_cross_cutting_readonly_fail_closed(self) -> None: self.run_contract_case("C5-010")
