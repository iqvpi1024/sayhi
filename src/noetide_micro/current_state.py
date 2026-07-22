"""Fixed deterministic A2 current_state Core View projection behavior."""

from __future__ import annotations

from typing import Any

from .store import SemanticStore


_VIEW = "current_state"
_POLICY = "a2_deterministic_v1"
_PROFILE = "a2_current_state_v1"
_ALLOWED_TYPES = {"entity", "relationship", "state", "assertion"}


def current_objects(store: SemanticStore, clock: str) -> list[dict[str, Any]]:
    """Pure current-validity selection from Canonical objects and a fixed clock."""
    objects: list[dict[str, Any]] = []
    for row in store.canonical_object_summaries():
        if row["object_type"] not in _ALLOWED_TYPES:
            continue
        valid_time = row["payload"].get("valid_time")
        if not isinstance(valid_time, dict):
            continue
        start = valid_time.get("start")
        end = valid_time.get("end")
        if not isinstance(start, str) or start > clock:
            continue
        if end is not None and end <= clock:
            continue
        objects.append({
            "object_id": row["object_id"],
            "object_type": row["object_type"],
            "object_revision": row["object_revision"],
            "valid_time": {"start": start, "end": end},
        })
    return objects


class CurrentStateService:
    """Builds the third Core View as a Derived projection; it never produces evidence."""

    def __init__(self, store: SemanticStore, now: str, clock: str, synthetic_profile_id: str = _PROFILE) -> None:
        self._store = store
        self._now = now
        self._clock = clock
        self._profile = synthetic_profile_id
        self._fail_next_rebuild = False
        self._receipt_index = 0

    def build(self) -> dict[str, Any]:
        if self._profile != _PROFILE:
            return {"status": "failed", "reason_code": "a2_preflight_invalid", "projection_absent": True, "data_revision": self._store.current_revision()}
        revision = self._store.current_revision()
        objects = current_objects(self._store, self._clock)
        payload = {"objects": objects, "object_count": len(objects)}
        with self._store.transaction():
            self._store.upsert_projection(_VIEW, revision, revision, "fresh", payload)
            self._store.put_a2_view_receipt(
                self._receipt_id(revision, "rebuilt"), _VIEW, revision, "rebuilt",
                {"generator_policy_id": _POLICY, "clock": self._clock, "object_count": len(objects)},
            )
        return {
            "status": "fresh", "view_name": _VIEW,
            "object_ids": [item["object_id"] for item in objects], "object_count": len(objects),
            "data_revision": revision, "view_revision": revision,
        }

    def read(self, view_name: str = _VIEW) -> dict[str, Any]:
        if view_name != _VIEW:
            raise KeyError(view_name)
        record = self._store.projection_record(_VIEW)
        current = self._store.current_revision()
        if record["freshness_status"] == "fresh" and record["data_revision"] == current and record["view_revision"] == current:
            return {
                "status": "fresh",
                "object_ids": [item["object_id"] for item in record["payload"]["objects"]],
                "revisions_aligned": True,
                "data_revision": current, "view_revision": current,
            }
        freshness = record["freshness_status"]
        if freshness == "fresh":
            freshness = "stale"
        return {
            "status": freshness,
            "masquerades_as_current": False,
            "data_revision": current, "view_revision": record["view_revision"],
        }

    def rebuild(self) -> dict[str, Any]:
        record = self._store.projection_record(_VIEW)
        revision = self._store.current_revision()
        if self._fail_next_rebuild:
            self._fail_next_rebuild = False
            with self._store.transaction():
                self._store.upsert_projection(_VIEW, revision, record["view_revision"], "unavailable", record["payload"])
                self._store.put_a2_view_receipt(
                    self._receipt_id(revision, "failed"), _VIEW, revision, "failed",
                    {"reason_code": "a2_rebuild_failed"},
                )
            canonical_readable = len(self._store.canonical_object_summaries()) > 0
            return {"status": "unavailable", "reason_code": "a2_rebuild_failed", "canonical_readable": canonical_readable, "data_revision": revision}
        return self.build()

    def equivalent_payload(self) -> dict[str, Any]:
        """Direct Canonical recomputation used to prove rebuild equivalence."""
        objects = current_objects(self._store, self._clock)
        return {"objects": objects, "object_count": len(objects)}

    def reject_derived_evidence(self, value: Any) -> dict[str, str]:
        if isinstance(value, str) and value.startswith("current_state"):
            return {"status": "rejected", "reason_code": "derived_evidence_forbidden"}
        raise ValueError("direct_source_locator_required")

    def inject_rebuild_failure(self) -> None:
        self._fail_next_rebuild = True

    def _receipt_id(self, revision: str, status: str) -> str:
        self._receipt_index += 1
        return f"a2_receipt_{revision}_{status}_{self._receipt_index:03d}"
