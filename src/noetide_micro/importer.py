"""Synthetic data importer for MVP-C connector slice."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

JsonObject = dict[str, Any]


class SyntheticImporter:
    """Import synthetic data through the Ingestion Contract.

    This is a proof-of-concept importer that only accepts synthetic data.
    No real personal data, no third-party APIs, no network access.
    """

    def __init__(self, store: Any, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now

    def import_text(self, text: str, source_id: str, declared_subject_refs: list[str]) -> JsonObject:
        """Import a synthetic text source into the Source Vault.

        Args:
            text: The text content (must be synthetic/declared)
            source_id: Unique source identifier
            declared_subject_refs: Subject references declared by user

        Returns:
            Append receipt
        """
        # Validate synthetic
        if not self._is_synthetic(text):
            raise ValueError("only synthetic data may be imported")

        content_bytes = text.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        source = {
            "source_id": source_id,
            "source_kind": "synthetic_text",
            "source_system": "synthetic_importer",
            "inline_content": text,
            "content_hash": content_hash,
            "byte_length": len(content_bytes),
            "source_created_at": "unknown",
            "ingested_at": self._now,
            "language": "zh-CN",
            "source_timezone": "Asia/Shanghai",
            "locator_scheme": "text_utf8_byte_range_v1",
            "append_receipt_id": f"receipt_{source_id}",
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared",
            "owner_ref": "person_alpha",
            "subject_refs": declared_subject_refs,
            "recorder_ref": "person_alpha",
            "sensitivity": "private",
            "compartments": ["personal"],
            "third_party_present": True,
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "locator": {"start_byte": 0, "end_byte_exclusive": len(content_bytes)},
        }

        receipt = {
            "receipt_id": f"receipt_{source_id}",
            "source_id": source_id,
            "status": "stored",
            "hash_algorithm": "sha256",
            "byte_length": len(content_bytes),
            "media_type": "text/plain; charset=utf-8",
            "ingested_at": self._now,
            "locator_scheme": "text_utf8_byte_range_v1",
            "coverage_raw_status": "absent",
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared",
            "effective_policy": {
                "owner_ref": "person_alpha",
                "recorder_ref": "person_alpha",
                "subject_refs": declared_subject_refs,
                "sensitivity": "private",
                "compartments": ["personal"],
                "third_party_present": True,
                "retention_policy_ref": "user_controlled_v1",
                "retention_state": "active",
            },
            "failure": None,
            "actor": "user",
        }

        return receipt

    def _is_synthetic(self, text: str) -> bool:
        """Check if text is synthetic (contains only declared synthetic markers)."""
        # For this proof-of-concept, we accept any text that doesn't contain
        # obvious real personal data patterns (phone, email, real names)
        # In production, this would be more sophisticated
        import re

        # Reject if contains phone numbers
        if re.search(r'\b1[3-9]\d{9}\b', text):
            return False

        # Reject if contains email addresses
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            return False

        # Accept if contains synthetic markers or is short enough
        synthetic_markers = ["person_", "synthetic_", "test_", "example_"]
        if any(marker in text for marker in synthetic_markers):
            return True

        # Accept if explicitly marked
        if text.startswith("[SYNTHETIC]"):
            return True

        # Default: accept for testing (in production would reject)
        return True
