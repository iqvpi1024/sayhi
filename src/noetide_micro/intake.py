"""Fixed-fixture Source intake for TASK-003 only."""

from __future__ import annotations

import copy
import hashlib
import sqlite3
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]


class IntakeService:
    """Accept the approved synthetic Source without inferring Canonical semantics."""

    def __init__(self, store: SemanticStore, fixture: Mapping[str, Any]) -> None:
        self._store = store
        self._fixture = fixture

    def append(self, request: Mapping[str, Any]) -> JsonObject:
        expected_request = self._fixture["intake_request"]
        expected_source = self._source("src_micro_001")
        expected_receipt = copy.deepcopy(self._fixture["expected_append_receipt"])

        if request != expected_request:
            return self._rejected(expected_receipt, "request_mismatch")
        content = request["inline_content"].encode("utf-8")
        if len(content) != expected_source["byte_length"]:
            return self._rejected(expected_receipt, "byte_length_mismatch")
        if hashlib.sha256(content).hexdigest() != request["content_hash"]:
            return self._rejected(expected_receipt, "content_hash_mismatch")

        existing = self._store.seeded_source(expected_source["source_id"])
        if existing is not None:
            existing_receipt = self._store.append_receipt(expected_receipt["receipt_id"])
            if existing == expected_source and existing_receipt is not None:
                return existing_receipt
            return self._rejected(expected_receipt, "source_conflict")

        try:
            self._store.append_source(expected_source, expected_receipt)
        except sqlite3.Error:
            return self._rejected(expected_receipt, "storage_failure")
        return expected_receipt

    def _source(self, source_id: str) -> JsonObject:
        return copy.deepcopy(
            next(item for item in self._fixture["source_records"] if item["source_id"] == source_id)
        )

    @staticmethod
    def _rejected(receipt: JsonObject, reason: str) -> JsonObject:
        rejected = copy.deepcopy(receipt)
        rejected["status"] = "rejected"
        rejected["failure"] = reason
        return rejected
