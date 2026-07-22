"""Fixed deterministic B3 Derived due-status projection behavior."""

from __future__ import annotations

from typing import Any

from .store import SemanticStore


_POLICY = "b3_deterministic_v1"


class DerivedEvidenceForbidden(PermissionError):
    """Derived due-status can never be used as evidence or a ChangeSet trigger."""


def compute_due_status(commitment: dict[str, Any], clock: str) -> str:
    """Deterministic due-status from Canonical Commitment and a fixed clock only."""
    if commitment["status"] != "open":
        return "closed"
    if clock < commitment["due_time"]:
        return "upcoming"
    if clock == commitment["due_time"]:
        return "due"
    return "overdue"


class DueStatusService:
    """Builds B3 Derived due projections without exposing them as evidence."""

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now
        self._fail_next_rebuild = False
        self._receipt_index = 0

    def project(self, projection_id: str, commitment_id: str, clock: str) -> dict[str, Any]:
        commitment = self._store.commitment_record(commitment_id)
        status = compute_due_status(commitment, clock)
        revision = self._store.current_revision()
        dependencies = {"commitment_refs": [commitment_id], "statement_source_id": commitment["statement_source_id"], "data_revision": revision}
        payload = {"commitment_id": commitment_id, "due_status": status, "clock_instant": clock}
        with self._store.transaction():
            self._store.replace_due_status_projection(
                projection_id, commitment_id, revision, revision, "fresh", status, clock,
                {**payload, "dependency_set": dependencies}, self._now, _POLICY,
            )
            self._store.put_due_rebuild_receipt(
                self._receipt_id(projection_id, revision, "rebuilt"), projection_id, revision, "rebuilt",
                {"generator_policy_id": _POLICY, "dependency_set": dependencies},
            )
        return {"status": "fresh", "projection_id": projection_id, "due_status": status, "data_revision": revision, "view_revision": revision}

    def read(self, projection_id: str, clock: str) -> dict[str, Any]:
        projection = self._store.due_status_projection(projection_id)
        commitment = self._store.commitment_record(projection["commitment_id"])
        status = compute_due_status(commitment, clock)
        current = self._store.current_revision()
        if projection["view_revision"] != current or projection["freshness_status"] != "fresh":
            return {"status": projection["freshness_status"], "projection_id": projection_id, "due_status": None, "data_revision": current, "view_revision": projection["view_revision"]}
        return {"status": "fresh", "projection_id": projection_id, "due_status": status, "data_revision": current, "view_revision": projection["view_revision"]}

    def rebuild(self, projection_id: str, clock: str) -> dict[str, Any]:
        projection = self._store.due_status_projection(projection_id)
        commitment_id = projection["commitment_id"]
        commitment = self._store.commitment_record(commitment_id)
        status = compute_due_status(commitment, clock)
        revision = self._store.current_revision()
        if self._fail_next_rebuild:
            self._fail_next_rebuild = False
            with self._store.transaction():
                self._store.replace_due_status_projection(
                    projection_id, commitment_id, revision, projection["view_revision"], "unavailable",
                    status, clock, {"commitment_id": commitment_id, "due_status": status, "clock_instant": clock},
                    self._now, _POLICY,
                )
                self._store.put_due_rebuild_receipt(
                    self._receipt_id(projection_id, revision, "failed"), projection_id, revision, "failed",
                    {"reason_code": "due_projection_rebuild_failed"},
                )
            canonical_readable = self._store.commitment_record(commitment_id)["commitment_id"] == commitment_id
            return {"status": "unavailable", "reason_code": "due_projection_rebuild_failed", "canonical_readable": canonical_readable, "data_revision": revision}
        dependencies = {"commitment_refs": [commitment_id], "statement_source_id": commitment["statement_source_id"], "data_revision": revision}
        with self._store.transaction():
            self._store.replace_due_status_projection(
                projection_id, commitment_id, revision, revision, "fresh", status, clock,
                {"commitment_id": commitment_id, "due_status": status, "clock_instant": clock, "dependency_set": dependencies},
                self._now, _POLICY,
            )
            self._store.put_due_rebuild_receipt(
                self._receipt_id(projection_id, revision, "rebuilt"), projection_id, revision, "rebuilt",
                {"generator_policy_id": _POLICY, "dependency_set": dependencies},
            )
        return {"status": "fresh", "projection_id": projection_id, "due_status": status, "data_revision": revision, "view_revision": revision}

    def reject_derived_evidence(self, value: Any) -> dict[str, str]:
        if isinstance(value, str) and value.startswith("due_b3_"):
            return {"status": "rejected", "reason_code": "derived_evidence_forbidden"}
        raise ValueError("direct_source_locator_required")

    def inject_rebuild_failure(self) -> None:
        self._fail_next_rebuild = True

    def _receipt_id(self, projection_id: str, revision: str, status: str) -> str:
        self._receipt_index += 1
        return f"due_receipt_{projection_id}_{revision}_{status}_{self._receipt_index:03d}"
