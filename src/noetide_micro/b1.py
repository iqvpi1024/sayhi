"""Persisted B1 Candidate Review with no Canonical write path."""

from __future__ import annotations

import copy
import json
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
_ACTIONS = {"later", "reject", "never_ask"}


def _stable(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class CandidateReviewService:
    """Stores candidates and review audit events without publishing semantics."""

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now

    def submit(self, candidate: Mapping[str, Any]) -> JsonObject:
        required = {"candidate_id", "candidate_kind", "source_refs", "proposed_value", "target_ref", "model_or_rule_version", "risk_level", "review_priority", "confirmation_policy"}
        if not required.issubset(candidate) or candidate.get("confirmation_policy") == "automatic":
            raise ValueError("invalid_or_automatic_candidate")
        if candidate.get("risk_level") not in {"low", "medium", "high", "critical"}:
            raise ValueError("invalid_risk_level")
        if candidate.get("review_priority") not in {"low", "normal", "high", "critical"}:
            raise ValueError("invalid_review_priority")
        for reference in candidate["source_refs"]:
            if not isinstance(reference, Mapping) or not isinstance(reference.get("source_id"), str) or self._store.seeded_source(reference["source_id"]) is None:
                raise ValueError("invalid_source_ref")
        record_id = "candidate:" + candidate["candidate_id"]
        existing = self._store.ledger_record(record_id)
        normalized = copy.deepcopy(dict(candidate))
        normalized.setdefault("status", "candidate")
        normalized.setdefault("changeset_ref", None)
        normalized["recorded_at"] = self._now
        if existing is not None:
            if _stable({key: value for key, value in existing.items() if key != "recorded_at"}) != _stable({key: value for key, value in normalized.items() if key != "recorded_at"}):
                raise ValueError("candidate_id_collision")
            return existing
        self._store.put_ledger_record(record_id, "candidate", normalized)
        return normalized

    def review(self, candidate_id: str, action: str, actor: str) -> JsonObject:
        if action not in _ACTIONS or not actor:
            raise ValueError("invalid_review_action")
        record_id = "candidate:" + candidate_id
        candidate = self._store.ledger_record(record_id)
        if candidate is None:
            raise KeyError(candidate_id)
        updated = copy.deepcopy(candidate)
        updated["status"] = {"later": "deferred", "reject": "rejected", "never_ask": "suppressed"}[action]
        updated["last_review_action"] = action
        updated["reviewed_at"] = self._now
        self._store.replace_ledger_record(record_id, updated)
        event = {"event_id": f"candidate_review:{candidate_id}:{self._now}:{action}", "candidate_id": candidate_id, "action": action, "actor": actor, "recorded_at": self._now}
        self._store.put_ledger_record(event["event_id"], "candidate_review_event", event)
        return updated

    def list_candidates(self) -> list[JsonObject]:
        return self._store.ledger_records_of_type("candidate")
