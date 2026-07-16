"""Allowlisted contact ChangeSet proposal for the single Micro fixture."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
CHANGESET_ID = "changeset_micro_001"
TRANSITION_AT = "2031-09-01T00:00:00+08:00"


class ContactCandidateBuilder:
    """Build and review exactly one fixture-scoped contact proposal."""

    def __init__(self, store: SemanticStore, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now

    def propose(self, source_id: str) -> JsonObject:
        if source_id != "src_micro_001" or self._store.seeded_source(source_id) is None:
            raise KeyError(source_id)
        existing = self._store.ledger_record(CHANGESET_ID)
        if existing is not None:
            return existing
        snapshot = self._store.seed_snapshot()
        if snapshot["data_revision"] != "rev_010":
            raise RuntimeError("fixture candidate can only be proposed at rev_010")
        old_state = snapshot["objects"]["state_contact_001"]
        trigger = {
            "source_id": source_id,
            "locator": {
                "scheme": "text_utf8_byte_range_v1",
                "start_byte": 0,
                "end_byte_exclusive": 58,
            },
        }
        next_state = copy.deepcopy(old_state)
        next_state.update(
            {
                "state_id": "state_contact_002",
                "object_revision": "rev_011",
                "created_at": self._now,
                "created_by": "shiling",
                "value": "no_contact",
                "valid_time": _unbounded_interval(TRANSITION_AT),
                "recorded_at": self._now,
                "recorded_by": "user",
                "evidence_refs": [
                    {
                        "source_id": source_id,
                        "locator": trigger["locator"],
                        "stance": "supports",
                        "claim_ref": "state_contact_002",
                    }
                ],
                "evidence_status": "present",
                "review_status": "confirmed",
            }
        )
        end_value = copy.deepcopy(old_state)
        end_value["object_revision"] = "rev_011"
        end_value["recorded_at"] = self._now
        end_value["recorded_by"] = "user"
        end_value["valid_time"] = copy.deepcopy(old_state["valid_time"])
        end_value["valid_time"]["end"] = _known_boundary(TRANSITION_AT)

        proposal = {
            "changeset_id": CHANGESET_ID,
            "base_revision": "rev_010",
            "actor": "shiling",
            "trigger_sources": [trigger],
            "proposals": [
                {
                    "proposal_id": "proposal_contact_end_001",
                    "operation": "end",
                    "target_ref": {"object_type": "state", "object_id": "state_contact_001"},
                    "before_digest": _digest(old_state),
                    "after_value": end_value,
                    "valid_time": end_value["valid_time"],
                    "evidence_refs": old_state["evidence_refs"],
                },
                {
                    "proposal_id": "proposal_contact_add_001",
                    "operation": "add",
                    "target_ref": {"object_type": "state", "object_id": "state_contact_002"},
                    "before_digest": "absent",
                    "after_value": next_state,
                    "valid_time": next_state["valid_time"],
                    "evidence_refs": next_state["evidence_refs"],
                },
            ],
            "impact_set": {
                "canonical_targets": ["state_contact_001", "state_contact_002"],
                "derived_views": ["person_card", "relationship_timeline"],
            },
            "protected_paths": [
                "relationship.origin",
                "state[relationship.role].value",
                "assertion[relationship.trust].value",
                "assertion[relationship.closeness].value",
                "hypothesis[relationship.personality]",
            ],
            "risk_level": "medium",
            "confirmation_policy": "single_confirmation",
            "status": "proposed",
            "published_revision": None,
            "receipt_id": None,
        }
        self._store.put_ledger_record(CHANGESET_ID, "changeset", proposal)
        return proposal

    def preview(self, changeset_id: str) -> JsonObject:
        changeset = self._required(changeset_id)
        return copy.deepcopy(changeset)

    def approve(self, changeset_id: str, actor: str) -> JsonObject:
        changeset = self._required(changeset_id)
        if actor != "person_alpha":
            raise PermissionError("only the synthetic owner may approve this ChangeSet")
        if changeset["status"] == "approved":
            return changeset
        if changeset["status"] != "proposed":
            raise RuntimeError("only a proposed ChangeSet may be approved")
        approved = copy.deepcopy(changeset)
        approved["status"] = "approved"
        approved["approval"] = {"actor": actor, "recorded_at": self._now}
        self._store.replace_ledger_record(changeset_id, approved)
        return approved

    def get(self, changeset_id: str) -> JsonObject:
        return self._required(changeset_id)

    def _required(self, changeset_id: str) -> JsonObject:
        if changeset_id != CHANGESET_ID:
            raise KeyError(changeset_id)
        item = self._store.ledger_record(changeset_id)
        if item is None:
            raise KeyError(changeset_id)
        return item


def _digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _known_boundary(value: str) -> JsonObject:
    return {
        "boundary_kind": "known",
        "value": value,
        "precision": "instant",
        "certainty": "exact",
        "timezone": "Asia/Shanghai",
        "resolution_status": "confirmed",
    }


def _unbounded_interval(start: str) -> JsonObject:
    return {
        "kind": "interval",
        "start": _known_boundary(start),
        "end": {
            "boundary_kind": "unbounded",
            "value": None,
            "precision": "unknown",
            "certainty": "unknown",
            "timezone": "not_applicable",
            "resolution_status": "confirmed",
        },
        "bounds": "[)",
    }
