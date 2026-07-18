"""Outcome object and Calibration for MVP-C C1."""

from __future__ import annotations

import copy
from typing import Any, Mapping

JsonObject = dict[str, Any]


class OutcomeService:
    """Create and read Outcome objects without writing Canonical directly."""

    def __init__(self, store: Any, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now

    def create(
        self,
        outcome_id: str,
        decision_ref: str,
        result: str,
        side_effects: list[str],
    ) -> JsonObject:
        """Create an Outcome object linked to a Decision."""
        decision = self._store.canonical_object_or_none(decision_ref)
        if decision is None or decision.get("object_type") != "decision":
            raise ValueError("invalid_decision_ref")
        outcome = {
            "outcome_id": outcome_id,
            "object_type": "outcome",
            "schema_version": "noetide.semantic.v1",
            "object_revision": "rev_001",
            "owner_ref": "person_alpha",
            "created_at": self._now,
            "created_by": "user",
            "sensitivity": "private",
            "compartments": ["personal"],
            "subject_refs": ["person_alpha"],
            "recorder_ref": "person_alpha",
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "decision_ref": decision_ref,
            "result": result,
            "side_effects": side_effects,
            "recorded_at": self._now,
            "evidence_refs": [],
            "evidence_status": "missing",
        }
        return outcome


class CalibrationService:
    """Compare predicted outcomes with actual outcomes."""

    def __init__(self, now: str) -> None:
        self._now = now

    def calibrate(self, decision: JsonObject, outcome: JsonObject) -> JsonObject:
        """Compare prediction vs actual and return calibration result."""
        predicted = decision.get("predicted_outcome")
        actual = outcome.get("result")

        if predicted is None:
            calibration_status = "no_prediction"
        elif predicted == actual:
            calibration_status = "accurate"
        else:
            calibration_status = "inaccurate"

        return {
            "calibration_id": f"calibration_{decision['decision_id']}",
            "decision_ref": decision["decision_id"],
            "outcome_ref": outcome["outcome_id"],
            "predicted": predicted,
            "actual": actual,
            "calibration_status": calibration_status,
            "calibrated_at": self._now,
        }

    def calibration_score(self, calibrations: list[JsonObject]) -> float:
        """Calculate overall calibration score from multiple calibrations."""
        if not calibrations:
            return 0.0

        accurate_count = sum(
            1 for c in calibrations if c["calibration_status"] == "accurate"
        )
        with_prediction_count = sum(
            1 for c in calibrations if c["calibration_status"] != "no_prediction"
        )

        if with_prediction_count == 0:
            return 0.0

        return accurate_count / with_prediction_count
