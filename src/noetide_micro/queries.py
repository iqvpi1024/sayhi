"""Canonical-only relationship contact queries for TASK-006."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]


class CanonicalQueries:
    """Reads State records directly and never uses a Projection as evidence."""

    def __init__(self, store: SemanticStore, fixture: Mapping[str, Any]) -> None:
        self._store = store
        self._fixture = fixture

    def relationship_contact(self, at: str) -> JsonObject:
        instant = _parse_time(at)
        candidates = [
            item
            for item in self._store.seed_snapshot()["objects"].values()
            if item.get("object_type") == "state"
            and item.get("state_kind") == "relationship.contact"
            and item.get("subject_ref") == "rel_alpha_beta"
            and _contains(item["valid_time"], instant)
        ]
        if len(candidates) != 1:
            raise RuntimeError("canonical contact query must resolve exactly one State")
        return candidates[0]

    def protected_snapshot(self) -> JsonObject:
        objects = self._store.seed_snapshot()["objects"]
        protected_ids = self._fixture["protected_semantics"]["object_ids"]
        return {
            object_id: {
                "object_revision": objects[object_id]["object_revision"],
                "digest": _digest(objects[object_id]),
            }
            for object_id in protected_ids
        }


def _contains(valid_time: Mapping[str, Any], instant: datetime) -> bool:
    if valid_time.get("kind") != "interval" or valid_time.get("bounds") != "[)":
        return False
    start = valid_time["start"]
    end = valid_time["end"]
    if start["boundary_kind"] != "known":
        return False
    if instant < _parse_time(start["value"]):
        return False
    if end["boundary_kind"] == "unbounded":
        return True
    if end["boundary_kind"] != "known":
        return False
    return instant < _parse_time(end["value"])


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _digest(value: Mapping[str, Any]) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
