from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/b5_multilingual_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/b5_multilingual_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_B5_ADAPTER"), "B5 adapter not configured")
class B5MultilingualContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_B5_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_B5_ADAPTER is required")
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

    @scenario("B5-001")
    def test_b5_001_append_bilingual_pair(self) -> None: self.run_contract_case("B5-001")

    @scenario("B5-002")
    def test_b5_002_original_and_evidence_resolution(self) -> None: self.run_contract_case("B5-002")

    @scenario("B5-003")
    def test_b5_003_bilingual_view_paired(self) -> None: self.run_contract_case("B5-003")

    @scenario("B5-004")
    def test_b5_004_overwrite_original_rejected(self) -> None: self.run_contract_case("B5-004")

    @scenario("B5-005")
    def test_b5_005_translation_unavailable(self) -> None: self.run_contract_case("B5-005")

    @scenario("B5-006")
    def test_b5_006_translation_revision_history(self) -> None: self.run_contract_case("B5-006")

    @scenario("B5-007")
    def test_b5_007_orphan_translation_reported(self) -> None: self.run_contract_case("B5-007")

    @scenario("B5-008")
    def test_b5_008_cross_cutting_fail_closed(self) -> None: self.run_contract_case("B5-008")
