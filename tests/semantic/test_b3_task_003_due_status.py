from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.commitments import CommitmentChangeSetService
from noetide_micro.due_status import DueStatusService, compute_due_status
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


NOW = "2032-03-10T09:00:00Z"
DUE = "2032-03-12T09:00:00Z"


class B3Task003DueStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(Path(self.temp.name) / "b3.sqlite3")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            self.store.add_revision("rev_020", NOW, "seed")
            self.store.add_canonical_object("person_gamma", {"object_id": "person_gamma", "object_type": "entity", "object_revision": "rev_020", "synthetic": True})
        self.store.append_source(
            {"source_id": "src_b3_stmt_001", "append_receipt_id": "receipt_src_b3_stmt_001", "source_kind": "synthetic_text", "content_hash": "hash_b3_stmt_001", "synthetic": True, "synthetic_profile_id": "b3_commitment_v1"},
            {"receipt_id": "receipt_src_b3_stmt_001", "source_id": "src_b3_stmt_001", "status": "stored"},
        )
        service = CommitmentChangeSetService(self.store, NOW)
        proposal = service.propose({
            "commitment_id": "commitment_b3_001", "commitment_kind": "synthetic_obligation",
            "responsible_ref": "person_gamma",
            "statement_locator": {"source_id": "src_b3_stmt_001", "locator": {"scheme": "synthetic", "start": 0, "end": 1}},
            "due_time": DUE, "valid_time": {"start": NOW, "end": None}, "synthetic_profile_id": "b3_commitment_v1",
        })
        service.approve(proposal["changeset_id"], "person_gamma")
        service.publish(proposal["changeset_id"])
        self.due = DueStatusService(self.store, NOW)

    def _canonical_snapshot(self):
        return sorted(
            (row[0], row[1])
            for row in self.store._connection.execute("SELECT object_id, object_revision FROM canonical_objects ORDER BY object_id")
        )

    def test_due_status_is_deterministic_at_fixed_clocks(self) -> None:
        record = self.store.commitment_record("commitment_b3_001")
        self.assertEqual(compute_due_status(record, "2032-03-10T09:00:00Z"), "upcoming")
        self.assertEqual(compute_due_status(record, "2032-03-12T09:00:00Z"), "due")
        self.assertEqual(compute_due_status(record, "2032-03-14T09:00:00Z"), "overdue")
        result = self.due.project("due_b3_001", "commitment_b3_001", "2032-03-10T09:00:00Z")
        self.assertEqual(result["status"], "fresh")
        self.assertEqual(result["data_revision"], "rev_021")
        read = self.due.read("due_b3_001", "2032-03-12T09:00:00Z")
        self.assertEqual(read["due_status"], "due")

    def test_rebuild_is_equivalent_after_delete(self) -> None:
        self.due.project("due_b3_001", "commitment_b3_001", "2032-03-10T09:00:00Z")
        before = self.store.due_status_projection("due_b3_001")["payload"]
        self.assertEqual(self.store.delete_due_status_projections(), 1)
        self.due.project("due_b3_001", "commitment_b3_001", "2032-03-10T09:00:00Z")
        after = self.store.due_status_projection("due_b3_001")["payload"]
        self.assertEqual(before, after)
        self.assertEqual(self.store.canonical_object("commitment_b3_001")["object_type"], "commitment")

    def test_injected_failure_keeps_canonical_readable(self) -> None:
        self.due.project("due_b3_001", "commitment_b3_001", "2032-03-10T09:00:00Z")
        self.due.inject_rebuild_failure()
        result = self.due.rebuild("due_b3_001", "2032-03-10T09:00:00Z")
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["reason_code"], "due_projection_rebuild_failed")
        self.assertTrue(result["canonical_readable"])
        self.assertEqual(self.store.due_status_projection("due_b3_001")["freshness_status"], "unavailable")
        receipts = self.store.due_rebuild_receipts()
        self.assertTrue(any(receipt["status"] == "failed" for receipt in receipts))
        self.assertEqual(self.store.current_revision(), "rev_021")

    def test_projection_never_writes_canonical_and_is_not_evidence(self) -> None:
        snapshot = self._canonical_snapshot()
        self.due.project("due_b3_001", "commitment_b3_001", "2032-03-10T09:00:00Z")
        self.due.rebuild("due_b3_001", "2032-03-14T09:00:00Z")
        self.assertEqual(snapshot, self._canonical_snapshot())
        rejected = self.due.reject_derived_evidence("due_b3_001")
        self.assertEqual(rejected, {"status": "rejected", "reason_code": "derived_evidence_forbidden"})
        self.assertEqual(snapshot, self._canonical_snapshot())
