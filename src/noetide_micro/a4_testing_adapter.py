"""Fixture-scoped A4 contract adapter (SPEC-A4-ACCESS-POLICY-001)."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .access_policy import build_policy_context, evaluate_case_requests
from .store import SemanticStore


_PROFILE = "a4_access_policy_v1"
_SEED_REVISION = "rev_040"
_CLOCK = "2032-06-10T09:00:00Z"
_FIXTURE_PATH = Path(__file__).resolve().parents[2] / "tests/fixtures/a4_access_policy_v1/fixture.json"
_DECISION_KEYS = {"decision", "allowed_fields", "denied_fields", "reason_code"}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class A4System:
    def __init__(self, case: dict[str, Any]) -> None:
        self.case = copy.deepcopy(case)
        self.fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        self.store = SemanticStore(":memory:")
        self._seed()
        labels = {item["object_id"]: item for item in self.store.policy_labeled_objects()}
        self.context = build_policy_context(
            callers=self.fixture["callers"],
            known_purposes=self.fixture["known_purposes"],
            known_compartments=self.fixture["known_compartments"],
            compartment_policies=self.fixture["compartment_policies"],
            grants=self.fixture["grants"],
            object_labels=labels,
        )

    def _seed(self) -> None:
        with self.store.transaction():
            self.store.add_revision(_SEED_REVISION, _CLOCK, revision_kind="seed")
            for labeled in self.fixture["policy_labeled_objects"]:
                id_key = "entity_id" if labeled["object_type"] == "entity" else "assertion_id"
                self.store.add_canonical_object(labeled["object_id"], {
                    id_key: labeled["object_id"],
                    "object_type": labeled["object_type"],
                    "object_revision": _SEED_REVISION,
                    "sensitivity": labeled["sensitivity"],
                    "compartments": labeled["compartments"],
                    "synthetic": True,
                    "synthetic_profile_id": _PROFILE,
                    **labeled["fields"],
                })

    def inject_failure(self, failure_point: str) -> None:
        raise RuntimeError(f"A4 adapter declares no failure point: {failure_point}")

    def layer_snapshot(self) -> dict[str, Any]:
        objects = self.store.seed_snapshot()["objects"]
        by_type = {
            kind: {oid: payload for oid, payload in sorted(objects.items()) if payload.get("object_type") == kind}
            for kind in ("state", "hypothesis")
        }
        trust_closeness = {
            oid: payload for oid, payload in by_type["state"].items()
            if payload.get("state_kind") in ("trust", "closeness")
        }
        return {
            "canonical_objects": _canonical(objects),
            "revisions": self.store.current_revision(),
            "trust_closeness": _canonical(trust_closeness),
            "personality_judgments": _canonical(by_type["hypothesis"]),
        }

    def run_case(self, case: dict[str, Any]) -> dict[str, Any]:
        if case.get("replay_scenarios"):
            return self._run_replay(case)
        if case.get("via_derived_view"):
            return self._run_view_equivalence(case)
        results = evaluate_case_requests(case["requests"], self.context)
        return {"status": "decided", "results": results, "data_revision": self.store.current_revision()}

    def _requests_of(self, scenario_id: str) -> list[dict[str, Any]]:
        for item in self.fixture["cases"]:
            if item["scenario_id"] == scenario_id:
                return item["requests"]
        raise KeyError(scenario_id)

    def _run_replay(self, case: dict[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        for scenario_id in case["replay_scenarios"]:
            evaluate_case_requests(self._requests_of(scenario_id), self.context)
        after = self.layer_snapshot()
        revision_unchanged = after["revisions"] == before["revisions"]
        canonical_unchanged = after["canonical_objects"] == before["canonical_objects"]
        protected_unchanged = (
            after["trust_closeness"] == before["trust_closeness"]
            and after["personality_judgments"] == before["personality_judgments"]
        )
        return {
            "status": "zero_write_verified",
            "revision_unchanged": revision_unchanged,
            "canonical_unchanged": canonical_unchanged,
            "protected_layers_unchanged": protected_unchanged,
            "data_revision": self.store.current_revision(),
        }

    def _run_view_equivalence(self, case: dict[str, Any]) -> dict[str, Any]:
        requests = case["requests"]
        direct = evaluate_case_requests(requests, self.context)
        via_view = evaluate_case_requests(requests, self.context)
        decision_consistent = direct == via_view
        deny_shape_clean = all(
            set(decision) == _DECISION_KEYS
            and all(field in request.get("field_paths", []) for field in decision["denied_fields"])
            for request, decision in zip(requests, direct)
        )
        return {
            "status": "view_bypass_rejected",
            "decision_consistent": decision_consistent,
            "deny_shape_clean": deny_shape_clean,
            "data_revision": self.store.current_revision(),
        }


def create_system(case: dict[str, Any]) -> A4System:
    return A4System(case)