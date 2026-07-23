from __future__ import annotations

import importlib
import json
import os
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/a3_entity_merge_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/a3_entity_merge_v1/oracles.json"


def scenario(identifier: str):
    def decorate(function):
        function._noetide_scenario_id = identifier
        return function
    return decorate


@unittest.skipUnless(os.environ.get("NOETIDE_A3_ADAPTER"), "A3 adapter not configured")
class A3EntityMergeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        module_name = os.environ.get("NOETIDE_A3_ADAPTER")
        if not module_name:
            self.fail("NOETIDE_A3_ADAPTER is required")
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

    @scenario("A3-001")
    def test_a3_001_merge_publish(self) -> None: self.run_contract_case("A3-001")

    @scenario("A3-002")
    def test_a3_002_invalid_merge_fail_closed(self) -> None: self.run_contract_case("A3-002")

    @scenario("A3-003")
    def test_a3_003_history_and_views_after_merge(self) -> None: self.run_contract_case("A3-003")

    @scenario("A3-004")
    def test_a3_004_merge_failure_atomic(self) -> None: self.run_contract_case("A3-004")

    @scenario("A3-005")
    def test_a3_005_split_restores_references(self) -> None: self.run_contract_case("A3-005")

    @scenario("A3-006")
    def test_a3_006_audit_chain_append_only(self) -> None: self.run_contract_case("A3-006")

    @scenario("A3-007")
    def test_a3_007_protected_layers_unchanged(self) -> None: self.run_contract_case("A3-007")

    @scenario("A3-008")
    def test_a3_008_invalid_split_fail_closed(self) -> None: self.run_contract_case("A3-008")
