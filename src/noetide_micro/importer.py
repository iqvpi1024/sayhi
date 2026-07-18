"""Durable synthetic-only Source import for the Release Candidate."""

from __future__ import annotations

import hashlib
import sqlite3
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]


class SyntheticImporter:
    """Append an explicitly declared synthetic Source without semantic inference."""

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now

    def import_text(
        self, text: str, source_id: str, declared_subject_refs: list[str], *, synthetic: bool
    ) -> JsonObject:
        if not synthetic:
            return self._rejected(source_id, "synthetic_declaration_required")
        if not source_id or not isinstance(text, str) or not isinstance(declared_subject_refs, list):
            return self._rejected(source_id, "invalid_request")
        if len(set(declared_subject_refs)) != len(declared_subject_refs):
            return self._rejected(source_id, "duplicate_subject_ref")
        for subject_ref in declared_subject_refs:
            if not isinstance(subject_ref, str) or self._store.canonical_object_or_none(subject_ref) is None:
                return self._rejected(source_id, "invalid_subject_ref")

        payload = text.encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        existing = self._store.seeded_source(source_id)
        if existing is not None:
            if existing.get("content_hash") == digest and existing.get("source_system") == "synthetic_importer_v1":
                return self._receipt(source_id, "duplicate", digest, len(payload), None)
            return self._rejected(source_id, "idempotency_mismatch")

        source = {
            "source_id": source_id,
            "append_receipt_id": f"receipt_{source_id}",
            "source_kind": "synthetic_text",
            "source_system": "synthetic_importer_v1",
            "inline_content": text,
            "content_hash": digest,
            "byte_length": len(payload),
            "source_created_at": "unknown",
            "ingested_at": self._now,
            "language": "unknown",
            "source_timezone": "unknown",
            "locator_scheme": "text_utf8_byte_range_v1",
            "locator": {"start_byte": 0, "end_byte_exclusive": len(payload)},
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared" if declared_subject_refs else "provisional",
            "owner_ref": "synthetic_owner_001",
            "subject_refs": declared_subject_refs,
            "recorder_ref": "synthetic_owner_001",
            "sensitivity": "private",
            "compartments": ["personal"],
            "third_party_present": "unknown" if not declared_subject_refs else True,
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
        }
        receipt = self._receipt(source_id, "stored", digest, len(payload), None)
        try:
            self._store.append_source(source, receipt)
        except sqlite3.Error:
            return self._rejected(source_id, "storage_failure")
        return receipt

    def _receipt(self, source_id: str, status: str, digest: str, byte_length: int, failure: str | None) -> JsonObject:
        return {
            "receipt_id": f"receipt_{source_id}", "source_id": source_id, "status": status,
            "hash_algorithm": "sha256", "content_hash": digest, "byte_length": byte_length,
            "media_type": "text/plain; charset=utf-8", "ingested_at": self._now,
            "locator_scheme": "text_utf8_byte_range_v1", "coverage_raw_status": "absent",
            "policy_profile_ref": "owner_intake_private_v1", "policy_resolution_status": "declared",
            "effective_policy": {"sensitivity": "private", "compartments": ["personal"]},
            "failure": failure, "actor": "synthetic_importer_v1",
        }

    def _rejected(self, source_id: str, failure: str) -> JsonObject:
        return self._receipt(source_id, "rejected", "", 0, failure)
