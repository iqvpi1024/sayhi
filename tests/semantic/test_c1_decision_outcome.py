"""C1 Decision-Outcome integration tests."""

from __future__ import annotations

import unittest

from noetide_micro.decision import DecisionService
from noetide_micro.outcome import OutcomeService, CalibrationService
from noetide_micro.scenario import ScenarioService


class C1DecisionOutcomeTests(unittest.TestCase):
    """Integration tests for C1 Decision-Outcome."""

    def setUp(self) -> None:
        self.now = "2031-10-15T02:00:00Z"
        self.decision_svc = DecisionService(None, {}, self.now)
        self.outcome_svc = OutcomeService(None, {}, self.now)
        self.calibration_svc = CalibrationService()
        self.scenario_svc = ScenarioService(None, {}, self.now)

    def test_c1_001_create_decision(self) -> None:
        """Decision can be created with question and options."""
        decision = self.decision_svc.create(
            decision_id="decision_001",
            question="Should I change jobs?",
            options=["stay", "leave"],
            constraints=["financial stability"],
            assumptions=["market stable"],
        )
        self.assertEqual(decision["decision_id"], "decision_001")
        self.assertEqual(decision["status"], "open")
        self.assertEqual(decision["question"], "Should I change jobs?")
        self.assertEqual(len(decision["options"]), 2)
        self.assertIsNone(decision["choice"])

    def test_c1_002_decide_updates_status(self) -> None:
        """Deciding updates status and records choice."""
        decision = self.decision_svc.create(
            decision_id="decision_001",
            question="Should I change jobs?",
            options=["stay", "leave"],
            constraints=[],
            assumptions=[],
        )
        decided = self.decision_svc.decide(decision, "leave")
        self.assertEqual(decided["status"], "decided")
        self.assertEqual(decided["choice"], "leave")
        self.assertEqual(decided["review_status"], "confirmed")

    def test_c1_003_decide_must_be_valid_option(self) -> None:
        """Decision choice must be one of the options."""
        decision = self.decision_svc.create(
            decision_id="decision_001",
            question="Should I change jobs?",
            options=["stay", "leave"],
            constraints=[],
            assumptions=[],
        )
        with self.assertRaises(ValueError):
            self.decision_svc.decide(decision, "maybe")

    def test_c1_004_create_outcome(self) -> None:
        """Outcome can be created and linked to Decision."""
        outcome = self.outcome_svc.create(
            outcome_id="outcome_001",
            decision_ref="decision_001",
            result="better salary",
            side_effects=["longer commute"],
        )
        self.assertEqual(outcome["outcome_id"], "outcome_001")
        self.assertEqual(outcome["decision_ref"], "decision_001")
        self.assertEqual(outcome["result"], "better salary")

    def test_c1_005_calibration_accurate(self) -> None:
        """Calibration shows accurate when prediction matches actual."""
        decision = self.decision_svc.create(
            "decision_001", "Q?", ["a", "b"], [], []
        )
        decision = self.decision_svc.set_predicted_outcome(decision, "success")
        outcome = self.outcome_svc.create("outcome_001", "decision_001", "success", [])
        calibration = self.calibration_svc.calibrate(decision, outcome)
        self.assertEqual(calibration["calibration_status"], "accurate")

    def test_c1_006_calibration_inaccurate(self) -> None:
        """Calibration shows inaccurate when prediction differs."""
        decision = self.decision_svc.create(
            "decision_001", "Q?", ["a", "b"], [], []
        )
        decision = self.decision_svc.set_predicted_outcome(decision, "success")
        outcome = self.outcome_svc.create("outcome_001", "decision_001", "failure", [])
        calibration = self.calibration_svc.calibrate(decision, outcome)
        self.assertEqual(calibration["calibration_status"], "inaccurate")

    def test_c1_007_calibration_no_prediction(self) -> None:
        """Calibration shows no_prediction when no prediction was made."""
        decision = self.decision_svc.create(
            "decision_001", "Q?", ["a", "b"], [], []
        )
        outcome = self.outcome_svc.create("outcome_001", "decision_001", "success", [])
        calibration = self.calibration_svc.calibrate(decision, outcome)
        self.assertEqual(calibration["calibration_status"], "no_prediction")

    def test_c1_008_scenario_stays_predicted(self) -> None:
        """Scenario remains predicted type, not observed."""
        scenario = self.scenario_svc.create(
            "scen_001", "decision_001", "baseline", ["stable"], "moderate raise"
        )
        self.assertEqual(scenario["assertion_kind"], "predicted")
        self.assertEqual(scenario["review_status"], "unconfirmed")

    def test_c1_009_scenario_comparison(self) -> None:
        """Scenario comparison shows divergence."""
        baseline = self.scenario_svc.create("scen_001", "decision_001", "baseline", [], "moderate")
        optimistic = self.scenario_svc.create("scen_002", "decision_001", "optimistic", [], "large")
        pessimistic = self.scenario_svc.create("scen_003", "decision_001", "pessimistic", [], "small")
        comparison = self.scenario_svc.compare_scenarios([baseline, optimistic, pessimistic])
        self.assertTrue(comparison["divergence"])
        self.assertEqual(len(comparison["results"]), 3)

    def test_c1_010_calibration_score(self) -> None:
        """Calibration score calculates correctly."""
        calibrations = [
            {"calibration_status": "accurate"},
            {"calibration_status": "accurate"},
            {"calibration_status": "inaccurate"},
        ]
        score = self.calibration_svc.calibration_score(calibrations)
        self.assertAlmostEqual(score, 2.0 / 3.0)

    def test_c1_011_close_decision(self) -> None:
        """Closed decision cannot be decided again."""
        decision = self.decision_svc.create(
            "decision_001", "Q?", ["a", "b"], [], []
        )
        decided = self.decision_svc.decide(decision, "a")
        closed = self.decision_svc.close(decided)
        self.assertEqual(closed["status"], "closed")


if __name__ == "__main__":
    unittest.main()
