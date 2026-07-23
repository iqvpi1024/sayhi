from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.access_policy import build_policy_context, evaluate_case_requests
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/a4_access_policy_v1/fixture.json").read_text(encoding="utf-8"))
ORACLES = json.loads((ROOT / "tests/fixtures/a4_access_policy_v1/oracles.json").read_text(encoding="utf-8"))["scenarios"]


class A4Task002AccessPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(str(Path(self._tmp.name) / "a4_task_002.sqlite"))
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            for labeled in FIXTURE["policy_labeled_objects"]:
                payload = {
                    "object_type": labeled["object_type"],
                    "object_revision": "rev_010",
                    "entity_id" if labeled["object_type"] == "entity" else "assertion_id": labeled["object_id"],
                    "sensitivity": labeled["sensitivity"],
                    "compartments": labeled["compartments"],
                    **labeled["fields"],
                }
                self.store.add_canonical_object(labeled["object_id"], payload)
        labels = {item["object_id"]: item for item in self.store.policy_labeled_objects()}
        self.context = build_policy_context(
            callers=FIXTURE["callers"],
            known_purposes=FIXTURE["known_purposes"],
            known_compartments=FIXTURE["known_compartments"],
            compartment_policies=FIXTURE["compartment_policies"],
            grants=FIXTURE["grants"],
            object_labels=labels,
        )

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def _case(self, scenario_id: str):
        return next(item for item in FIXTURE["cases"] if item["scenario_id"] == scenario_id)

    def _assert_scenario(self, scenario_id: str) -> None:
        expected = ORACLES[scenario_id]["result"]["results"]
        actual = evaluate_case_requests(self._case(scenario_id)["requests"], self.context)
        self.assertEqual(actual, expected)

    def test_a4_001_allow_all_fields(self) -> None:
        self._assert_scenario("A4-001")

    def test_a4_002_field_redaction(self) -> None:
        self._assert_scenario("A4-002")

    def test_a4_003_strictest_intersection_and_conflict(self) -> None:
        self._assert_scenario("A4-003")

    def test_a4_004_grant_invalid(self) -> None:
        self._assert_scenario("A4-004")

    def test_a4_005_fail_closed_set(self) -> None:
        self._assert_scenario("A4-005")

    def test_a4_006_sealed_excluded(self) -> None:
        self._assert_scenario("A4-006")

    def test_a4_007_evaluation_is_zero_write(self) -> None:
        before = self.store.canonical_layer_digest()
        for scenario_id in ("A4-001", "A4-002", "A4-003", "A4-004", "A4-005", "A4-006"):
            evaluate_case_requests(self._case(scenario_id)["requests"], self.context)
        self.assertEqual(self.store.canonical_layer_digest(), before)
        self.assertEqual(self.store.current_revision(), "rev_010")

    def test_a4_008_deny_shape_echoes_requested_fields_only(self) -> None:
        for scenario_id in ("A4-002", "A4-006"):
            decisions = evaluate_case_requests(self._case(scenario_id)["requests"], self.context)
            for request, decision in zip(self._case(scenario_id)["requests"], decisions):
                self.assertEqual(set(decision), {"decision", "allowed_fields", "denied_fields", "reason_code"})
                for field in decision["denied_fields"]:
                    self.assertIn(field, request["field_paths"])
        direct = evaluate_case_requests(self._case("A4-002")["requests"], self.context)
        via_view = evaluate_case_requests(self._case("A4-002")["requests"], self.context)
        self.assertEqual(direct, via_view)


if __name__ == "__main__":
    unittest.main()