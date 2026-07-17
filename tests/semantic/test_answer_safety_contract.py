from __future__ import annotations

import copy
import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/answer_safety_v1/fixture.json"
ORACLE_PATH = ROOT / "tests/fixtures/answer_safety_v1/oracles.json"
RUN_ROOT = ROOT / "tmp/answer-safety-runs"


def scenario(scenario_id: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(method: Callable[..., Any]) -> Callable[..., Any]:
        setattr(method, "_noetide_scenario_id", scenario_id)
        return method

    return decorate


class AnswerSafetyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.oracles = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
        adapter_name = os.environ.get("NOETIDE_ANSWER_ADAPTER")
        if not adapter_name:
            raise RuntimeError("NOETIDE_ANSWER_ADAPTER is required")
        cls.adapter = importlib.import_module(adapter_name)
        if not callable(getattr(cls.adapter, "create_system", None)):
            raise TypeError(
                f"{adapter_name} must expose create_system(fixture, scenario_id, data_root)"
            )

    def setUp(self) -> None:
        RUN_ROOT.mkdir(parents=True, exist_ok=True)
        self._temp = tempfile.TemporaryDirectory(
            prefix="noetide-answer-safety-", dir=RUN_ROOT
        )
        self.addCleanup(self._temp.cleanup)

    def _case(self, scenario_id: str, fixture: Mapping[str, Any] | None = None) -> dict[str, Any]:
        source = fixture or self.fixture
        return next(
            item for item in source["cases"] if item["scenario_id"] == scenario_id
        )

    def _create_system(
        self,
        scenario_id: str,
        name: str = "primary",
        fixture: Mapping[str, Any] | None = None,
    ) -> Any:
        data_root = Path(self._temp.name) / name
        data_root.mkdir(parents=True, exist_ok=False)
        return self.adapter.create_system(
            copy.deepcopy(fixture or self.fixture), scenario_id, data_root
        )

    def _expected_layer_snapshot(
        self, scenario_id: str, fixture: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        case = self._case(scenario_id, fixture)
        initial = case["initial_state"]
        digests = case["expected_initial_layer_digests"]
        return {
            "data_revision": initial["data_revision"],
            "source": {"count": len(initial["source_records"]), "digest": digests["source"]},
            "canonical": {
                "count": len(initial["canonical_objects"]),
                "digest": digests["canonical"],
            },
            "ledger": {"count": len(initial["ledger_records"]), "digest": digests["ledger"]},
            "projection": {
                "count": len(initial["projection_rows"]),
                "digest": digests["projection"],
            },
        }

    def _assert_exact_case(self, scenario_id: str, system: Any | None = None) -> dict[str, Any]:
        target = system or self._create_system(scenario_id)
        expected_snapshot = self._expected_layer_snapshot(scenario_id)
        self.assertEqual(target.layer_snapshot(), expected_snapshot)
        actual: dict[str, Any] = {}
        expected_answers = self.oracles["scenarios"][scenario_id]["expected_answers"]
        for query_id, expected in expected_answers.items():
            answer = target.evaluate(query_id)
            self.assertEqual(answer, expected)
            actual[query_id] = answer
        self.assertEqual(target.layer_snapshot(), expected_snapshot)
        return actual

    @scenario("AS-001")
    def test_as_001_viewpoint_scope(self) -> None:
        answers = self._assert_exact_case("AS-001")
        self.assertEqual(answers["as001_viewpoint"]["verification_scope"], "viewpoint")

    @scenario("AS-002")
    def test_as_002_statement_and_world_claim_separated(self) -> None:
        answers = self._assert_exact_case("AS-002")
        self.assertEqual(answers["as002_statement_occurrence"]["answer_status"], "verified")
        self.assertEqual(answers["as002_world_claim"]["answer_status"], "unknown")

    @scenario("AS-003")
    def test_as_003_unconfirmed_candidate_is_not_evidence(self) -> None:
        answers = self._assert_exact_case("AS-003")
        self.assertEqual(answers["as003_unconfirmed"]["evidence_refs"], [])

    @scenario("AS-004")
    def test_as_004_conflict_is_parallel_and_order_independent(self) -> None:
        primary = self._assert_exact_case("AS-004")
        reversed_fixture = copy.deepcopy(self.fixture)
        case = self._case("AS-004", reversed_fixture)
        case["initial_state"]["source_records"].reverse()
        case["initial_state"]["canonical_objects"].reverse()
        reversed_system = self._create_system(
            "AS-004", name="reversed", fixture=reversed_fixture
        )
        self.assertEqual(
            reversed_system.layer_snapshot(),
            self._expected_layer_snapshot("AS-004", reversed_fixture),
        )
        reversed_answer = reversed_system.evaluate("as004_disputed")
        self.assertEqual(reversed_answer, primary["as004_disputed"])
        self.assertEqual(
            reversed_system.layer_snapshot(),
            self._expected_layer_snapshot("AS-004", reversed_fixture),
        )

    @scenario("AS-005")
    def test_as_005_not_covered_variants(self) -> None:
        answers = self._assert_exact_case("AS-005")
        self.assertEqual(answers["as005_outside_coverage"]["answer_status"], "not_covered")
        self.assertEqual(answers["as005_unknown_continuity"]["answer_status"], "not_covered")

    @scenario("AS-006")
    def test_as_006_current_stale_historical_not_stale(self) -> None:
        answers = self._assert_exact_case("AS-006")
        self.assertEqual(answers["as006_current_stale"]["answer_status"], "stale")
        self.assertEqual(answers["as006_historical_not_stale"]["answer_status"], "verified")

    @scenario("AS-007")
    def test_as_007_coverage_sufficient_unknown(self) -> None:
        answers = self._assert_exact_case("AS-007")
        self.assertEqual(answers["as007_unknown"]["answer_value"], None)

    @scenario("AS-008")
    def test_as_008_derived_evidence_forbidden(self) -> None:
        answers = self._assert_exact_case("AS-008")
        answer = answers["as008_derived_forbidden"]
        self.assertEqual(answer["evidence_refs"], [])
        self.assertIn("derived_evidence_forbidden", answer["reason_codes"])

    @scenario("AS-009")
    def test_as_009_fictional_isolated(self) -> None:
        before = self._expected_layer_snapshot("AS-009")
        system = self._create_system("AS-009")
        answers = self._assert_exact_case("AS-009", system)
        self.assertEqual(answers["as009_fictional_isolated"]["answer_status"], "unknown")
        self.assertEqual(system.layer_snapshot(), before)

    @scenario("AS-010")
    def test_as_010_deterministic_read_only_replay(self) -> None:
        system = self._create_system("AS-010")
        expected_snapshot = self._expected_layer_snapshot("AS-010")
        self.assertEqual(system.layer_snapshot(), expected_snapshot)
        first = system.evaluate("as010_replay")
        middle = system.layer_snapshot()
        second = system.evaluate("as010_replay")
        self.assertEqual(first, self.oracles["scenarios"]["AS-010"]["expected_answers"]["as010_replay"])
        self.assertEqual(second, first)
        self.assertEqual(middle, expected_snapshot)
        self.assertEqual(system.layer_snapshot(), expected_snapshot)

    @scenario("AS-011")
    def test_as_011_result_write_failure_cannot_publish_pass(self) -> None:
        from tests.runner.run_answer_safety_suite import (
            ResultArtifactWriteError,
            write_result_artifact,
        )

        output = Path(self._temp.name) / "result.json"
        payload = {"run_result": "passed", "suite_passed": True, "synthetic": True}
        with self.assertRaises(ResultArtifactWriteError) as caught:
            write_result_artifact(
                output,
                payload,
                failure_point="result.output.before_atomic_replace",
            )
        self.assertFalse(output.exists())
        self.assertEqual(
            caught.exception.failure_record["reason_code"],
            "result_artifact_write_failed",
        )

        existing = Path(self._temp.name) / "existing.json"
        existing.write_text("historical-result\n", encoding="utf-8", newline="\n")
        with self.assertRaises(FileExistsError):
            write_result_artifact(existing, payload)
        self.assertEqual(existing.read_text(encoding="utf-8"), "historical-result\n")
