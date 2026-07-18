"""Scenario planning for MVP-C C1."""

from __future__ import annotations

import copy
from typing import Any, Mapping

JsonObject = dict[str, Any]


class ScenarioService:
    """Create scenario projections that remain predicted/fictional."""

    def __init__(self, store: Any, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now

    def create(
        self,
        scenario_id: str,
        decision_ref: str,
        scenario_kind: str,
        assumptions: list[str],
        projected_result: str,
    ) -> JsonObject:
        """Create a scenario that stays predicted/fictional.

        scenario_kind: baseline | optimistic | pessimistic
        """
        if scenario_kind not in {"baseline", "optimistic", "pessimistic"}:
            raise ValueError("scenario_kind must be baseline, optimistic, or pessimistic")

        scenario = {
            "assertion_id": scenario_id,
            "object_type": "assertion",
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
            "scenario_kind": scenario_kind,
            "assertion_kind": "predicted",
            "assumptions": assumptions,
            "projected_result": projected_result,
            "evidence_refs": [],
            "evidence_status": "missing",
            "review_status": "unconfirmed",
        }
        return scenario

    def compare_scenarios(self, scenarios: list[JsonObject]) -> JsonObject:
        """Compare multiple scenarios and return differences."""
        if len(scenarios) < 2:
            raise ValueError("need at least 2 scenarios to compare")

        kinds = {s["scenario_kind"] for s in scenarios}
        results = {s["scenario_kind"]: s["projected_result"] for s in scenarios}

        return {
            "comparison_id": "comparison_001",
            "scenarios": [s["assertion_id"] for s in scenarios],
            "kinds": list(kinds),
            "results": results,
            "divergence": len(set(results.values())) > 1,
            "compared_at": self._now,
        }
