"""Fixture-scoped A5 contract adapter (SPEC-A5-APP-SHELL-001 v0.2).

Each system is an isolated in-memory synthetic app-shell journey. The shell
only calls already-verified core capabilities (intake / candidate / changesets
/ views); presentation output is request-time Derived and never persisted.
"""

from __future__ import annotations

import copy
import json
from typing import Any

from .app_shell import render_impact_preview, render_review, shell_write_scan
from .candidate import ContactCandidateBuilder
from .changesets import ChangeSetService
from .intake import IntakeService
from .runtime import demo_fixture
from .store import SemanticStore
from .views import CoreViewReader


JsonObject = dict[str, Any]

_SOURCE_ID = "src_micro_001"
_CHANGESET_ID = "changeset_micro_001"
_RELATIONSHIP_ID = "rel_alpha_beta"
_APPROVE_ACTOR = "person_alpha"
_PUBLISH_KEY = "a5_publish_001"
_REVERT_KEY = "a5_revert_001"
_PUBLISH_RECEIPT_ID = "receipt_publish_001"
_SESSION = "a5_shell"
_VIEW_NAMES = ("person_card", "relationship_timeline")
_PROTECTED_STATE_KINDS = ("trust", "closeness")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class A5System:
    """One isolated synthetic app-shell journey bound to a single fixture case."""

    def __init__(self, case: JsonObject) -> None:
        self.case = copy.deepcopy(case)
        self.fixture = demo_fixture()
        self.clock = str(self.fixture["determinism"]["clock"])
        self.store = SemanticStore(":memory:")
        self.store.seed_rev_010(self.fixture)
        self._failures: set[str] = set()
        self._publish_effect: JsonObject | None = None

    def layer_snapshot(self) -> JsonObject:
        objects = self.store.seed_snapshot()["objects"]
        trust_closeness = {
            oid: payload
            for oid, payload in sorted(objects.items())
            if payload.get("state_kind") in _PROTECTED_STATE_KINDS
        }
        personality = {
            oid: payload
            for oid, payload in sorted(objects.items())
            if payload.get("object_type") == "hypothesis"
        }
        return {
            "canonical_objects": _canonical(objects),
            "revisions": self.store.current_revision(),
            "trust_closeness": _canonical(trust_closeness),
            "personality_judgments": _canonical(personality),
        }

    def inject_failure(self, failure_point: str) -> None:
        self._failures.add(failure_point)

    def run_case(self, case: JsonObject) -> JsonObject:
        steps = case["steps"]
        journey_start = self.layer_snapshot()
        objects_before = self.store.seed_snapshot()["objects"]
        step_results: JsonObject = {}
        proposal: JsonObject | None = None
        for index, step in enumerate(steps):
            if step == "record":
                step_results["record"] = self._step_record()
            elif step == "propose":
                proposal, step_results["propose"] = self._step_propose()
            elif step == "review":
                step_results["review"] = self._step_review(proposal)
            elif step == "preview":
                step_results["preview"] = render_impact_preview(proposal)
            elif step == "confirm":
                step_results["confirm"] = self._step_confirm(objects_before)
            elif step == "read_view":
                step_results["read_view"] = self._step_read_view(reverted="revert" in steps[:index])
            elif step == "receipt":
                step_results["receipt"] = self._step_receipt()
            elif step == "history":
                step_results["history"] = self._step_history()
            elif step == "revert":
                step_results["revert"] = self._step_revert()
            elif step == "audit":
                step_results["audit"] = self._step_audit(journey_start, step_results.get("preview"))
            else:
                raise KeyError(f"unknown A5 journey step: {step}")
        return {
            "status": "journey_step_completed",
            "step_results": step_results,
            "data_revision": self.store.current_revision(),
        }

    # -- journey steps -------------------------------------------------

    def _step_record(self) -> JsonObject:
        receipt = IntakeService(self.store, self.fixture).append(self.fixture["intake_request"])
        return {
            "source_id": receipt["source_id"],
            "receipt_id": receipt["receipt_id"],
            "store_status": receipt["status"],
        }

    def _step_propose(self) -> tuple[JsonObject, JsonObject]:
        proposal = ContactCandidateBuilder(self.store, self.fixture, self.clock).propose(_SOURCE_ID)
        return proposal, {"changeset_id": proposal["changeset_id"], "status": proposal["status"]}

    def _step_review(self, proposal: JsonObject) -> JsonObject:
        relationship = self.store.canonical_object(_RELATIONSHIP_ID)
        labels = [
            self.store.canonical_object(ref)["canonical_label"]
            for ref in relationship["participant_refs"]
        ]
        return render_review(proposal, labels)

    def _step_confirm(self, objects_before: JsonObject) -> JsonObject:
        builder = ContactCandidateBuilder(self.store, self.fixture, self.clock)
        builder.approve(_CHANGESET_ID, _APPROVE_ACTOR)
        receipt = ChangeSetService(self.store, self.fixture, self.clock).publish(
            _CHANGESET_ID, _PUBLISH_KEY, self._failures
        )
        objects_after = self.store.seed_snapshot()["objects"]
        self._publish_effect = {
            "will_create": sorted(oid for oid in objects_after if oid not in objects_before),
            "will_modify": sorted(
                oid
                for oid in objects_after
                if oid in objects_before and objects_after[oid] != objects_before[oid]
            ),
            "views_affected": sorted(
                name
                for name in _VIEW_NAMES
                if self.store.projection_record(name)["data_revision"] == receipt["published_revision"]
            ),
        }
        return {
            "publish_status": receipt["status"],
            "published_revision": receipt["published_revision"],
            "receipt_id": receipt["receipt_id"],
        }

    def _step_read_view(self, reverted: bool) -> JsonObject:
        reader = CoreViewReader(self.store, self.fixture)
        card = reader.read("person_card", _SESSION)
        timeline = reader.read("relationship_timeline", _SESSION)
        card_result: JsonObject = {
            "freshness_status": card["freshness_status"],
            "data_revision": card["data_revision"],
        }
        current_value = card["payload"]["contact_state"]
        if reverted:
            card_result["contact_state"] = current_value
        else:
            card_result["contains_new_state"] = current_value == self._published_new_value()
        timeline_result = {
            "freshness_status": timeline["freshness_status"],
            "data_revision": timeline["data_revision"],
            "history_count": len(timeline["payload"]["history"]),
        }
        return {"person_card": card_result, "relationship_timeline": timeline_result}

    def _published_new_value(self) -> Any:
        changeset = self.store.ledger_record(_CHANGESET_ID)
        if changeset is None:
            return None
        return next(
            (
                proposal["after_value"]["value"]
                for proposal in changeset["proposals"]
                if proposal["operation"] == "add"
            ),
            None,
        )

    def _step_receipt(self) -> JsonObject:
        receipt = ChangeSetService(self.store, self.fixture, self.clock).receipt(_PUBLISH_RECEIPT_ID)
        return {"receipt_id": receipt["receipt_id"], "published_revision": receipt["published_revision"]}

    def _step_history(self) -> JsonObject:
        changesets = self.store.ledger_records_of_type("changeset")
        receipts = self.store.ledger_records_of_type("receipt")
        events = self.store.ledger_records_of_type("audit_event")
        return {
            "changeset_ids": [item["changeset_id"] for item in changesets],
            "receipt_ids": [item["receipt_id"] for item in receipts],
            "audit_events": [item["event_type"] for item in events],
        }

    def _step_revert(self) -> JsonObject:
        receipt = ChangeSetService(self.store, self.fixture, self.clock).revert(
            _CHANGESET_ID, _REVERT_KEY
        )
        return {
            "receipt_id": receipt["receipt_id"],
            "compensation_revision": receipt["compensation_revision"],
        }

    def _step_audit(self, journey_start: JsonObject, preview: JsonObject | None) -> JsonObject:
        current = self.layer_snapshot()
        effect = self._publish_effect or {"will_create": [], "will_modify": [], "views_affected": []}
        preview_matches = (
            preview is not None
            and set(preview["will_create"]) == set(effect["will_create"])
            and set(preview["will_modify"]) == set(effect["will_modify"])
            and set(preview["views_affected"]) == set(effect["views_affected"])
        )
        _, forbidden = shell_write_scan()
        return {
            "preview_matches_publish": preview_matches,
            "zero_bypass": forbidden == [],
            "trust_closeness_unchanged": current["trust_closeness"] == journey_start["trust_closeness"],
            "personality_unchanged": current["personality_judgments"] == journey_start["personality_judgments"],
        }


def create_system(case: JsonObject) -> A5System:
    return A5System(case)
