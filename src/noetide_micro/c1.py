"""Narrow ChangeSet-backed C1 persistence for synthetic Decision and Outcome."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]


class C1ChangeSetService:
    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now

    def publish(self, payload: Mapping[str, Any], actor: str) -> JsonObject:
        object_type = payload.get("object_type")
        object_id = payload.get("decision_id") or payload.get("outcome_id") or payload.get("assertion_id")
        if object_type not in {"decision", "outcome", "assertion"} or not isinstance(object_id, str) or not actor:
            raise ValueError("invalid_c1_payload")
        if self._store.canonical_object_or_none(object_id) is not None:
            raise ValueError("c1_object_already_exists")
        if object_type == "outcome":
            decision = self._store.canonical_object_or_none(payload.get("decision_ref", ""))
            if decision is None or decision.get("object_type") != "decision":
                raise ValueError("invalid_decision_ref")
        before = self._store.current_revision()
        revision = f"rev_c1_{object_id}"
        published = copy.deepcopy(dict(payload))
        published["object_revision"] = revision
        published["recorded_at"] = self._now
        changeset = {"changeset_id": f"changeset_c1_{object_id}", "schema_version": "noetide.changeset.v1", "base_revision": before, "actor": actor, "requested_at": self._now, "proposals": [{"proposal_id": f"proposal_c1_{object_id}", "operation": "add", "target_ref": {"object_type": object_type, "object_id": object_id}, "before_digest": "absent", "after_value": published}], "confirmation_policy": "single_confirmation", "status": "published", "published_revision": revision, "reversibility": "reversible"}
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            self._store.add_canonical_object(object_id, published)
            self._store.put_ledger_record(changeset["changeset_id"], "changeset", changeset, revision)
        return published

    def _changeset_sequence(self, object_id: str) -> int:
        """Count published changesets targeting one object (publish included)."""
        count = 0
        for record in self._store.ledger_records_of_type("changeset"):
            for proposal in record.get("proposals", []):
                if proposal.get("target_ref", {}).get("object_id") == object_id:
                    count += 1
                    break
        return count

    def publish_revision(self, object_id: str, payload: Mapping[str, Any], actor: str, operation: str = "correct") -> JsonObject:
        """Persist a state transition of an existing C1 object as a NEW revision.

        Add-only philosophy: the previous revision, its changeset and the
        payload ``revision_history`` are never rewritten; the transition only
        appends a new canonical_revisions row and a new changeset ledger row.
        """
        existing = self._store.canonical_object_or_none(object_id)
        if existing is None:
            raise ValueError("c1_object_missing")
        if not actor:
            raise ValueError("invalid_c1_payload")
        object_type = existing.get("object_type")
        if object_type not in {"decision", "outcome", "assertion"}:
            raise ValueError("invalid_c1_payload")
        sequence = self._changeset_sequence(object_id) + 1
        before = self._store.current_revision()
        revision = f"rev_c1_{object_id}_r{sequence:03d}"
        published = copy.deepcopy(dict(payload))
        published["object_revision"] = revision
        published["recorded_at"] = self._now
        changeset = {"changeset_id": f"changeset_c1_{object_id}_r{sequence:03d}", "schema_version": "noetide.changeset.v1", "base_revision": before, "actor": actor, "requested_at": self._now, "proposals": [{"proposal_id": f"proposal_c1_{object_id}_r{sequence:03d}", "operation": operation, "target_ref": {"object_type": object_type, "object_id": object_id}, "before_digest": _canonical_digest(existing), "after_value": published}], "confirmation_policy": "single_confirmation", "status": "published", "published_revision": revision, "reversibility": "reversible"}
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            self._store.replace_canonical_object(object_id, published)
            self._store.put_ledger_record(changeset["changeset_id"], "changeset", changeset, revision)
        return published
