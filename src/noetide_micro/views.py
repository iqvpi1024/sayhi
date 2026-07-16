"""L2 projection and safe-read behavior for the two Micro Core Views."""

from __future__ import annotations

from typing import Any, Mapping

from .queries import CanonicalQueries
from .store import SemanticStore


JsonObject = dict[str, Any]
VIEW_NAMES = ("person_card", "relationship_timeline")


class CoreViewProjector:
    """Projects committed Canonical data; it never produces evidence."""

    def __init__(self, store: SemanticStore, fixture: Mapping[str, Any]) -> None:
        self._store = store
        self._fixture = fixture

    def project(self, revision: str, failure_points: set[str]) -> list[JsonObject]:
        if revision != self._store.current_revision():
            raise RuntimeError("Views may only project the current committed revision")
        results: list[JsonObject] = []
        for view_name in VIEW_NAMES:
            if f"projection.{view_name}" in failure_points:
                existing = self._store.projection_record(view_name)
                self._store.replace_projection(
                    view_name,
                    revision,
                    existing["view_revision"],
                    "updating",
                    existing["payload"],
                )
                results.append({"target": view_name, "result": "failed"})
                continue
            payload = self._payload(view_name)
            self._store.replace_projection(view_name, revision, revision, "fresh", payload)
            results.append({"target": view_name, "result": "passed"})
        return results

    def _payload(self, view_name: str) -> JsonObject:
        current = CanonicalQueries(self._store, self._fixture).relationship_contact(
            self._fixture["determinism"]["clock"]
        )
        if view_name == "person_card":
            return {"contact_state": current["value"]}
        snapshot = self._store.seed_snapshot()["objects"]
        history = [
            {"state_id": item["state_id"], "value": item["value"], "valid_time": item["valid_time"]}
            for item in snapshot.values()
            if item.get("object_type") == "state"
            and item.get("state_kind") == "relationship.contact"
        ]
        history.sort(key=lambda item: item["valid_time"]["start"]["value"])
        return {"current_contact_state": current["value"], "history": history}


class CoreViewReader:
    """Returns a fresh view or a Canonical fallback without exposing stale payload as current."""

    def __init__(self, store: SemanticStore, fixture: Mapping[str, Any]) -> None:
        self._store = store
        self._fixture = fixture

    def read(self, view_name: str, session_id: str) -> JsonObject:
        if view_name not in VIEW_NAMES:
            raise KeyError(view_name)
        record = self._store.projection_record(view_name)
        current_revision = self._store.current_revision()
        if (
            record["freshness_status"] == "fresh"
            and record["data_revision"] == current_revision
            and record["view_revision"] == current_revision
        ):
            return record
        canonical = CanonicalQueries(self._store, self._fixture).relationship_contact(
            self._fixture["determinism"]["clock"]
        )
        payload = (
            {"contact_state": canonical["value"]}
            if view_name == "person_card"
            else {"current_contact_state": canonical["value"], "history": []}
        )
        return {
            "data_revision": current_revision,
            "view_revision": record["view_revision"],
            "freshness_status": record["freshness_status"],
            "payload": payload,
            "source": "canonical_fallback",
        }

    def reconcile(self) -> JsonObject:
        results = CoreViewProjector(self._store, self._fixture).project(
            self._store.current_revision(), set()
        )
        return {"data_revision": self._store.current_revision(), "view_results": results}
