"""Fixed synthetic Commitment ChangeSet behavior for B3."""

from __future__ import annotations

import copy
import re
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
_PROFILE = "b3_commitment_v1"
_RFC3339_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class CommitmentChangeSetService:
    """Publishes and transitions one fixture-scoped Commitment without using Derived due-status data."""

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now

    def propose(self, candidate: Mapping[str, Any]) -> JsonObject:
        self._validate_candidate(candidate)
        commitment_id = candidate["commitment_id"]
        changeset_id = f"changeset_b3_{commitment_id}"
        existing = self._store.ledger_record(changeset_id)
        if existing is not None:
            return existing
        proposal = {
            "changeset_id": changeset_id,
            "schema_version": "noetide.changeset.v1",
            "base_revision": self._store.current_revision(),
            "actor": "shiling",
            "requested_at": self._now,
            "confirmation_policy": "single_confirmation",
            "status": "proposed",
            "published_revision": None,
            "reversibility": "reversible",
            "proposals": [
                {
                    "proposal_id": f"proposal_b3_{commitment_id}",
                    "operation": "add",
                    "target_ref": {"object_type": "commitment", "object_id": commitment_id},
                    "before_digest": "absent",
                    "after_value": self._commitment_payload(candidate, "pending"),
                }
            ],
        }
        with self._store.transaction():
            self._store.put_ledger_record(changeset_id, "changeset", proposal)
        return proposal

    def approve(self, changeset_id: str, actor: str) -> JsonObject:
        changeset = self._required_changeset(changeset_id)
        if actor != "person_gamma":
            raise PermissionError("only the synthetic owner may approve a B3 Commitment")
        if changeset["status"] == "approved":
            return changeset
        if changeset["status"] != "proposed":
            raise RuntimeError("only a proposed Commitment ChangeSet may be approved")
        approved = copy.deepcopy(changeset)
        approved["status"] = "approved"
        approved["approval"] = {"actor": actor, "recorded_at": self._now}
        with self._store.transaction():
            self._store.replace_ledger_record(changeset_id, approved)
        return approved

    def publish(self, changeset_id: str) -> JsonObject:
        changeset = self._required_changeset(changeset_id)
        if changeset["status"] != "approved":
            raise RuntimeError("only an approved Commitment ChangeSet may publish")
        if changeset["base_revision"] != self._store.current_revision():
            return self._fail(changeset, "conflicted", "stale_base_revision")
        candidate = changeset["proposals"][0]["after_value"]
        commitment_id = candidate["commitment_id"]
        if self._store.canonical_object_or_none(commitment_id) is not None:
            return self._fail(changeset, "conflicted", "commitment_already_exists")
        revision = self._next_revision()
        published = copy.deepcopy(candidate)
        published["object_revision"] = revision
        published["recorded_at"] = self._now
        published["review_status"] = "user_confirmed"
        receipt = {
            "receipt_id": f"receipt_b3_{commitment_id}_publish",
            "changeset_id": changeset_id,
            "status": "published",
            "published_revision": revision,
        }
        completed = copy.deepcopy(changeset)
        completed.update({"status": "published", "published_revision": revision, "receipt_id": receipt["receipt_id"]})
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            self._store.mark_due_status_projections_stale(revision)
            self._store.add_canonical_object(commitment_id, published)
            self._store.replace_evidence_refs(commitment_id, published["evidence_refs"])
            self._store.put_commitment_record(
                commitment_id, revision, candidate["commitment_kind"], candidate["responsible_ref"],
                candidate["statement_locator"]["source_id"], candidate["statement_locator"]["locator"],
                candidate["due_time"], candidate["valid_time"]["start"], candidate["valid_time"]["end"],
                self._now, "open", None, "user_confirmed", candidate["synthetic_profile_id"],
            )
            self._store.replace_ledger_record(changeset_id, completed, revision)
            self._store.put_ledger_record(receipt["receipt_id"], "receipt", receipt, revision)
            self._store.put_ledger_record(
                f"history:{commitment_id}:published", "commitment_history",
                {"commitment_id": commitment_id, "event": "published", "revision": revision}, revision,
            )
            self._store.put_ledger_record(
                f"audit:{changeset_id}:published", "audit_event",
                {"changeset_id": changeset_id, "event_type": "published", "revision": revision}, revision,
            )
        return {
            "status": "published",
            "commitment_id": commitment_id,
            "commitment_status": "open",
            "review_status": "user_confirmed",
            "statement_locator": candidate["statement_locator"]["source_id"],
            "data_revision": revision,
        }

    def complete(self, commitment_id: str) -> JsonObject:
        return self._lifecycle(commitment_id, "completed", None, "commitment_completed")

    def cancel(self, commitment_id: str, cancel_reason: str | None) -> JsonObject:
        if not cancel_reason:
            return {"status": "failed", "reason_code": "cancel_reason_required", "data_revision": self._store.current_revision()}
        return self._lifecycle(commitment_id, "cancelled", cancel_reason, "commitment_cancelled")

    def revert(self, commitment_id: str) -> JsonObject:
        record = self._store.commitment_record(commitment_id)
        if record["status"] not in {"completed", "cancelled"}:
            raise RuntimeError("only a completed or cancelled Commitment may be compensation-reverted")
        revision = self._next_revision()
        changeset_id = f"changeset_b3_compensation_{commitment_id}_{revision}"
        receipt_id = f"receipt_b3_{commitment_id}_revert_{revision}"
        canonical = self._store.canonical_object(commitment_id)
        restored = copy.deepcopy(canonical)
        restored["object_revision"] = revision
        restored["lifecycle_status"] = "open"
        restored["cancel_reason"] = None
        compensation = {
            "changeset_id": changeset_id,
            "schema_version": "noetide.changeset.v1",
            "base_revision": self._store.current_revision(),
            "actor": "user",
            "requested_at": self._now,
            "confirmation_policy": "single_confirmation",
            "status": "published",
            "published_revision": revision,
            "reversibility": "reversible",
            "proposals": [
                {
                    "proposal_id": f"proposal_b3_compensation_{commitment_id}",
                    "operation": "replace",
                    "target_ref": {"object_type": "commitment", "object_id": commitment_id},
                    "after_value": restored,
                }
            ],
        }
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            self._store.mark_due_status_projections_stale(revision)
            self._store.replace_canonical_object(commitment_id, restored)
            self._store.update_commitment_status(commitment_id, revision, "open", None)
            self._store.put_ledger_record(changeset_id, "changeset", compensation, revision)
            self._store.put_ledger_record(receipt_id, "receipt", {"receipt_id": receipt_id, "changeset_id": changeset_id, "status": "published", "published_revision": revision}, revision)
            self._store.put_ledger_record(
                f"history:{commitment_id}:compensation_reverted:{revision}", "commitment_history",
                {"commitment_id": commitment_id, "event": "compensation_reverted", "revision": revision}, revision,
            )
            self._store.put_ledger_record(
                f"audit:{changeset_id}:published", "audit_event",
                {"changeset_id": changeset_id, "event_type": "published", "revision": revision}, revision,
            )
        return {
            "status": "open",
            "commitment_id": commitment_id,
            "data_revision": revision,
            "history_retained": self._history_events(commitment_id),
        }

    def _lifecycle(self, commitment_id: str, status: str, cancel_reason: str | None, event: str) -> JsonObject:
        record = self._store.commitment_record(commitment_id)
        if record["status"] != "open":
            raise RuntimeError("only an open Commitment may be completed or cancelled")
        revision = self._next_revision()
        changeset_id = f"changeset_b3_{event}_{commitment_id}"
        receipt_id = f"receipt_b3_{commitment_id}_{event}"
        canonical = self._store.canonical_object(commitment_id)
        transitioned = copy.deepcopy(canonical)
        transitioned["object_revision"] = revision
        transitioned["lifecycle_status"] = status
        transitioned["cancel_reason"] = cancel_reason
        changeset = {
            "changeset_id": changeset_id,
            "schema_version": "noetide.changeset.v1",
            "base_revision": self._store.current_revision(),
            "actor": "user",
            "requested_at": self._now,
            "confirmation_policy": "single_confirmation",
            "status": "published",
            "published_revision": revision,
            "reversibility": "reversible",
            "proposals": [
                {
                    "proposal_id": f"proposal_b3_{event}_{commitment_id}",
                    "operation": "replace",
                    "target_ref": {"object_type": "commitment", "object_id": commitment_id},
                    "after_value": transitioned,
                }
            ],
        }
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            self._store.mark_due_status_projections_stale(revision)
            self._store.replace_canonical_object(commitment_id, transitioned)
            self._store.update_commitment_status(commitment_id, revision, status, cancel_reason)
            self._store.put_ledger_record(changeset_id, "changeset", changeset, revision)
            self._store.put_ledger_record(receipt_id, "receipt", {"receipt_id": receipt_id, "changeset_id": changeset_id, "status": "published", "published_revision": revision}, revision)
            self._store.put_ledger_record(
                f"history:{commitment_id}:{event}", "commitment_history",
                {"commitment_id": commitment_id, "event": "completed" if status == "completed" else "cancelled", "revision": revision}, revision,
            )
            self._store.put_ledger_record(
                f"audit:{changeset_id}:published", "audit_event",
                {"changeset_id": changeset_id, "event_type": "published", "revision": revision}, revision,
            )
        result = {
            "status": status,
            "commitment_id": commitment_id,
            "data_revision": revision,
            "due_projection_status": "stale",
        }
        if status == "cancelled":
            result["cancel_reason"] = cancel_reason
        return result

    def _history_events(self, commitment_id: str) -> list[str]:
        events = [
            row["event"]
            for row in self._store.ledger_records_of_type("commitment_history")
            if row.get("commitment_id") == commitment_id
        ]
        return events

    def _next_revision(self) -> str:
        current = self._store.current_revision()
        prefix, _, digits = current.rpartition("_")
        if not digits.isdigit():
            raise RuntimeError("unexpected revision format")
        return f"{prefix}_{int(digits) + 1:03d}"

    def _fail(self, changeset: Mapping[str, Any], status: str, reason_code: str) -> JsonObject:
        failed = copy.deepcopy(changeset)
        failed.update({"status": status, "published_revision": None, "failure_reason": reason_code})
        with self._store.transaction():
            self._store.replace_ledger_record(changeset["changeset_id"], failed)
        return {"status": status, "reason_code": reason_code, "data_revision": self._store.current_revision()}

    def _required_changeset(self, changeset_id: str) -> JsonObject:
        changeset = self._store.ledger_record(changeset_id)
        if changeset is None or changeset.get("changeset_id") != changeset_id:
            raise KeyError(changeset_id)
        return changeset

    def _validate_candidate(self, candidate: Mapping[str, Any]) -> None:
        allowed_candidate_fields = {
            "commitment_id", "commitment_kind", "responsible_ref", "statement_locator",
            "due_time", "valid_time", "synthetic_profile_id",
        }
        if set(candidate) != allowed_candidate_fields:
            raise ValueError("fixture_profile_mismatch")
        if candidate.get("synthetic_profile_id") != _PROFILE:
            raise ValueError("synthetic_input_required")
        if candidate.get("commitment_kind") != "synthetic_obligation":
            raise ValueError("commitment_kind_invalid")
        if not isinstance(candidate.get("commitment_id"), str) or self._store.canonical_object_or_none(candidate["commitment_id"]) is not None:
            raise ValueError("commitment_id_invalid")
        responsible_ref = candidate.get("responsible_ref")
        statement_locator = candidate.get("statement_locator")
        due_time = candidate.get("due_time")
        valid_time = candidate.get("valid_time")
        if not isinstance(responsible_ref, str) or not isinstance(statement_locator, Mapping) or not isinstance(due_time, str) or not isinstance(valid_time, Mapping):
            raise ValueError("commitment_reference_invalid")
        if not _RFC3339_UTC.match(due_time):
            raise ValueError("commitment_reference_invalid")
        if set(valid_time) != {"start", "end"} or not isinstance(valid_time.get("start"), str) or (valid_time.get("end") is not None and not isinstance(valid_time.get("end"), str)):
            raise ValueError("commitment_reference_invalid")
        entity = self._store.canonical_object_or_none(responsible_ref)
        if entity is None or entity.get("object_type") != "entity":
            raise ValueError("commitment_reference_invalid")
        if set(statement_locator) != {"source_id", "locator"} or not isinstance(statement_locator.get("source_id"), str) or not isinstance(statement_locator.get("locator"), Mapping):
            raise ValueError("commitment_reference_invalid")
        source = self._store.seeded_source(statement_locator["source_id"])
        if source is None or source.get("synthetic") is not True or source.get("synthetic_profile_id") != _PROFILE:
            raise ValueError("commitment_reference_invalid")

    def _commitment_payload(self, candidate: Mapping[str, Any], revision: str) -> JsonObject:
        return {
            "commitment_id": candidate["commitment_id"],
            "object_type": "commitment",
            "schema_version": "noetide.semantic.v1",
            "object_revision": revision,
            "owner_ref": "person_gamma",
            "created_at": self._now,
            "created_by": "shiling",
            "sensitivity": "normal",
            "compartments": ["personal"],
            "subject_refs": [candidate["responsible_ref"]],
            "recorder_ref": "person_gamma",
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "commitment_kind": candidate["commitment_kind"],
            "responsible_ref": candidate["responsible_ref"],
            "statement_locator": dict(candidate["statement_locator"]),
            "due_time": candidate["due_time"],
            "valid_time": dict(candidate["valid_time"]),
            "recorded_at": self._now,
            "lifecycle_status": "open",
            "cancel_reason": None,
            "evidence_refs": [
                {
                    "source_id": candidate["statement_locator"]["source_id"],
                    "locator": dict(candidate["statement_locator"]["locator"]),
                    "stance": "supports",
                    "claim_ref": candidate["commitment_id"],
                }
            ],
            "evidence_status": "present",
            "review_status": "unreviewed",
            "synthetic_profile_id": candidate["synthetic_profile_id"],
        }
