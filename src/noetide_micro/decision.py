"""Decision object for MVP-C C1."""

from __future__ import annotations

import copy
from typing import Any, Mapping

JsonObject = dict[str, Any]


class DecisionService:
    """Create and read Decision objects without writing Canonical directly."""

    def __init__(self, store: Any, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now

    def create(
        self,
        decision_id: str,
        question: str,
        options: list[str],
        constraints: list[str],
        assumptions: list[str],
        choice: str | None = None,
    ) -> JsonObject:
        """Create a Decision object. If choice is provided, status is 'decided'."""
        decision = {
            "decision_id": decision_id,
            "object_type": "decision",
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
            "question": question,
            "options": options,
            "constraints": constraints,
            "assumptions": assumptions,
            "choice": choice,
            "status": "decided" if choice else "open",
            "evidence_refs": [],
            "evidence_status": "missing",
            "review_status": "confirmed" if choice else "unconfirmed",
            "predicted_outcome": None,
            "actual_outcome_ref": None,
        }
        return decision

    def decide(self, decision: JsonObject, choice: str) -> JsonObject:
        """Record a choice for an open Decision."""
        if decision["status"] != "open":
            raise RuntimeError("only an open Decision may be decided")
        if choice not in decision["options"]:
            raise ValueError("choice must be one of the options")
        updated = copy.deepcopy(decision)
        updated["choice"] = choice
        updated["status"] = "decided"
        updated["review_status"] = "confirmed"
        updated["object_revision"] = "rev_002"
        return updated

    def close(self, decision: JsonObject) -> JsonObject:
        """Close a decided Decision."""
        if decision["status"] != "decided":
            raise RuntimeError("only a decided Decision may be closed")
        updated = copy.deepcopy(decision)
        updated["status"] = "closed"
        updated["object_revision"] = "rev_003"
        return updated

    def set_predicted_outcome(self, decision: JsonObject, predicted: str) -> JsonObject:
        """Set a predicted outcome without writing it as actual."""
        updated = copy.deepcopy(decision)
        updated["predicted_outcome"] = predicted
        return updated
