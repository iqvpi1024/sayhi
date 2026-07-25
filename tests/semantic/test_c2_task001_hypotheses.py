"""C2-TASK-001 narrow tests: hypothesis lifecycle module semantics."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from noetide_micro.hypotheses import (
    TRANSITION_RECORD_TYPE,
    attach_evidence,
    attempt_upgrade_to_fact,
    create_hypothesis,
    present_hypothesis,
    transition_status,
)
from noetide_micro.store import SemanticStore


CLOCK = "2026-07-26T00:00:00+00:00"
SPEC = {
    "hypothesis_id": "HYP-SYN-T1-001",
    "statement": "Synthetic hypothesis: the user may tend to avoid conflict.",
    "hypothesis_kind": "pattern",
    "valid_scope": "synthetic conflict conversations",
    "subject_ref": "ENT-SYN-T1-SELF",
}


def _seed_source(store: SemanticStore, source_id: str, text: str) -> None:
    store.append_source(
        {
            "source_id": source_id,
            "append_receipt_id": f"receipt_{source_id}",
            "source_kind": "synthetic_diary",
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "text": text,
            "synthetic": True,
        },
        {"receipt_id": f"receipt_{source_id}", "source_id": source_id, "status": "stored", "actor": "c2_task001_seed"},
    )


def build_store(directory: str) -> SemanticStore:
    store = SemanticStore(Path(directory) / "c2_task001.sqlite3")
    store.add_revision("rev_c2_task001_seed", CLOCK, "seed")
    for index in range(1, 4):
        _seed_source(store, f"SRC-SYN-T1-{index:03d}", f"synthetic text {index}")
    return store


def _create(store: SemanticStore, confirmed: bool = True):
    return create_hypothesis(
        store,
        SPEC,
        [
            {"source_id": "SRC-SYN-T1-001", "locator": "entry#1", "stance": "supports"},
            {"source_id": "SRC-SYN-T1-002", "locator": "entry#2", "stance": "supports"},
        ],
        confirmed=confirmed,
        at=CLOCK,
    )


class HypothesisLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = build_store(self._tmp.name)
        self.addCleanup(self.store.close)

    def test_create_confirmed_active_revision_one(self) -> None:
        result = _create(self.store)
        self.assertEqual(result["outcome"], "applied")
        view = present_hypothesis(self.store, "HYP-SYN-T1-001")
        self.assertEqual(view["status"], "active")
        self.assertEqual(view["display_tone"], "exploratory")
        self.assertFalse(view["is_fact"])
        self.assertTrue(view["derived_only"])
        self.assertEqual(view["evidence_for"], 2)
        payload = self.store.canonical_object("HYP-SYN-T1-001")
        self.assertEqual(payload["object_revision"], 1)
        self.assertEqual(payload["object_type"], "hypothesis")
        self.assertEqual(payload["revision_history"], [])

    def test_create_unconfirmed_rejected_no_write(self) -> None:
        result = _create(self.store, confirmed=False)
        self.assertEqual(result["outcome"], "rejected")
        self.assertEqual(result["reason"], "confirmation_required")
        self.assertIsNone(self.store.canonical_object_or_none("HYP-SYN-T1-001"))

    def test_attach_support_keeps_status_and_appends_history(self) -> None:
        _create(self.store)
        result = attach_evidence(self.store, "HYP-SYN-T1-001", {"source_id": "SRC-SYN-T1-003", "locator": "entry#3", "stance": "supports"}, confirmed=True, at=CLOCK)
        self.assertEqual(result["outcome"], "applied")
        payload = self.store.canonical_object("HYP-SYN-T1-001")
        self.assertEqual(payload["status"], "active")
        self.assertEqual(payload["object_revision"], 2)
        self.assertEqual(len(payload["evidence_for"]), 3)
        self.assertEqual(len(payload["revision_history"]), 1)
        self.assertEqual(payload["revision_history"][0]["status"], "active")

    def test_counter_evidence_never_auto_transitions(self) -> None:
        _create(self.store)
        attach_evidence(self.store, "HYP-SYN-T1-001", {"source_id": "SRC-SYN-T1-003", "locator": "entry#3", "stance": "contradicts"}, confirmed=True, at=CLOCK)
        payload = self.store.canonical_object("HYP-SYN-T1-001")
        self.assertEqual(payload["status"], "active")
        self.assertEqual(len(payload["evidence_against"]), 1)

    def test_attach_unconfirmed_or_illegal_rejected_zero_writes(self) -> None:
        _create(self.store)
        before = self.store.canonical_object_digest("HYP-SYN-T1-001")
        unconfirmed = attach_evidence(self.store, "HYP-SYN-T1-001", {"source_id": "SRC-SYN-T1-003", "locator": "entry#3", "stance": "supports"}, confirmed=False, at=CLOCK)
        missing = attach_evidence(self.store, "HYP-SYN-T1-001", {"source_id": "SRC-SYN-T1-MISSING", "locator": "entry#9", "stance": "supports"}, confirmed=True, at=CLOCK)
        derived = attach_evidence(self.store, "HYP-SYN-T1-001", {"source_id": "DERIVED:projection:proj_x", "locator": "row#1", "stance": "supports"}, confirmed=True, at=CLOCK)
        self.assertEqual(unconfirmed["reason"], "confirmation_required")
        self.assertEqual(missing["reason"], "evidence_source_missing")
        self.assertEqual(derived["reason"], "derived_view_is_not_evidence")
        self.assertEqual(self.store.canonical_object_digest("HYP-SYN-T1-001"), before)

    def test_confirmed_transition_history_and_tone(self) -> None:
        _create(self.store)
        attach_evidence(self.store, "HYP-SYN-T1-001", {"source_id": "SRC-SYN-T1-003", "locator": "entry#3", "stance": "contradicts"}, confirmed=True, at=CLOCK)
        result = transition_status(self.store, "HYP-SYN-T1-001", "challenged", "synthetic counter-evidence", confirmed=True, at=CLOCK)
        self.assertEqual(result["outcome"], "applied")
        view = present_hypothesis(self.store, "HYP-SYN-T1-001")
        self.assertEqual(view["status"], "challenged")
        self.assertEqual(view["display_tone"], "tentative")
        payload = self.store.canonical_object("HYP-SYN-T1-001")
        self.assertEqual(payload["object_revision"], 3)
        self.assertEqual([entry["status"] for entry in payload["revision_history"]], ["active", "active"])
        receipts = [r for r in self.store.ledger_records_of_type(TRANSITION_RECORD_TYPE) if r["hypothesis_id"] == "HYP-SYN-T1-001"]
        self.assertEqual(len([r for r in receipts if r["kind"] == "transition"]), 1)

    def test_transition_unconfirmed_or_unknown_rejected(self) -> None:
        _create(self.store)
        before = self.store.canonical_object_digest("HYP-SYN-T1-001")
        unconfirmed = transition_status(self.store, "HYP-SYN-T1-001", "challenged", "x", confirmed=False, at=CLOCK)
        unknown = transition_status(self.store, "HYP-SYN-T1-001", "verified", "x", confirmed=True, at=CLOCK)
        missing = transition_status(self.store, "HYP-SYN-T1-UNKNOWN", "retired", "x", confirmed=True, at=CLOCK)
        self.assertEqual(unconfirmed["reason"], "confirmation_required")
        self.assertEqual(unknown["reason"], "status_unknown")
        self.assertEqual(missing["reason"], "hypothesis_missing")
        self.assertEqual(self.store.canonical_object_digest("HYP-SYN-T1-001"), before)

    def test_correction_retire_restore_append_only(self) -> None:
        _create(self.store)
        transition_status(self.store, "HYP-SYN-T1-001", "weakened", "counter evidence", confirmed=True, at=CLOCK)
        transition_status(self.store, "HYP-SYN-T1-001", "active", "user correction", confirmed=True, at=CLOCK)
        transition_status(self.store, "HYP-SYN-T1-001", "retired", "user retired", confirmed=True, at=CLOCK)
        transition_status(self.store, "HYP-SYN-T1-001", "active", "user restore", confirmed=True, at=CLOCK)
        payload = self.store.canonical_object("HYP-SYN-T1-001")
        self.assertEqual(payload["status"], "active")
        self.assertEqual(payload["object_revision"], 5)
        self.assertEqual([entry["status"] for entry in payload["revision_history"]], ["active", "weakened", "active", "retired"])
        view = present_hypothesis(self.store, "HYP-SYN-T1-001")
        self.assertEqual(view["display_tone"], "exploratory")

    def test_upgrade_to_fact_always_rejected_zero_writes(self) -> None:
        _create(self.store)
        before = self.store.canonical_object_digest("HYP-SYN-T1-001")
        result = attempt_upgrade_to_fact(self.store, "HYP-SYN-T1-001")
        self.assertEqual(result["outcome"], "rejected")
        self.assertEqual(result["writes"], 0)
        self.assertEqual(self.store.canonical_object_digest("HYP-SYN-T1-001"), before)


if __name__ == "__main__":
    unittest.main()
