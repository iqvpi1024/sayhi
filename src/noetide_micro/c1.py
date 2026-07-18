"""Narrow ChangeSet-backed C1 persistence for synthetic Decision and Outcome."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from .store import SemanticStore


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
