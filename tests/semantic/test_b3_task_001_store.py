from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


class B3Task001StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SemanticStore(Path(self.temp.name) / "b3.sqlite3")
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())

    def _add_commitment(self, status: str = "open", cancel_reason: str | None = None) -> None:
        payload = {"object_id": "commitment_b3_storage_001", "object_type": "commitment", "object_revision": "rev_b3_020"}
        with self.store.transaction():
            self.store.add_revision("rev_b3_020", "2032-03-10T09:00:00Z")
            self.store.add_canonical_object("commitment_b3_storage_001", payload)
            self.store.put_commitment_record(
                "commitment_b3_storage_001", "rev_b3_020", "synthetic_obligation", "person_gamma",
                "src_history_001", {"scheme": "synthetic", "start": 0, "end": 1},
                "2032-03-12T09:00:00Z", "2032-03-10T09:00:00Z", None, "2032-03-10T09:00:00Z",
                status, cancel_reason, "user_confirmed", "b3_commitment_v1",
            )

    def test_b3_schema_and_pragmas_are_present(self) -> None:
        self.assertTrue({"commitments", "due_status_projections", "due_rebuild_receipts"}.issubset(self.store.schema_objects()))
        self.assertEqual(self.store.pragma_values(), {"foreign_keys": 1, "journal_mode": "delete", "synchronous": 2})

    def test_commitment_requires_canonical_commitment_and_direct_source(self) -> None:
        with self.assertRaises(KeyError):
            self.store.put_commitment_record(
                "missing", "rev_010", "synthetic_obligation", "person_gamma",
                "src_history_001", {}, "2032-03-12T09:00:00Z", "2032-03-10T09:00:00Z", None,
                "2032-03-10T09:00:00Z", "open", None, "user_confirmed", "b3_commitment_v1",
            )
        self._add_commitment()
        commitment = self.store.commitment_record("commitment_b3_storage_001")
        self.assertEqual(commitment["status"], "open")
        self.assertEqual(commitment["statement_source_id"], "src_history_001")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction():
                self.store.put_commitment_record(
                    "commitment_b3_storage_001", "rev_b3_020", "synthetic_obligation", "person_gamma",
                    "src_missing", {}, "2032-03-12T09:00:00Z", "2032-03-10T09:00:00Z", None,
                    "2032-03-10T09:00:00Z", "open", None, "user_confirmed", "b3_commitment_v1",
                )

    def test_cancelled_commitment_requires_reason(self) -> None:
        with self.assertRaises(ValueError):
            self._add_commitment(status="cancelled", cancel_reason=None)
        with self.assertRaises(ValueError):
            with self.store.transaction():
                self.store.add_revision("rev_b3_021", "2032-03-11T09:00:00Z")
                self.store.add_canonical_object("commitment_b3_storage_002", {"object_id": "commitment_b3_storage_002", "object_type": "commitment", "object_revision": "rev_b3_021"})
                self.store.put_commitment_record(
                    "commitment_b3_storage_002", "rev_b3_021", "synthetic_obligation", "person_gamma",
                    "src_history_001", {}, "2032-03-12T09:00:00Z", "2032-03-10T09:00:00Z", None,
                    "2032-03-10T09:00:00Z", "open", None, "user_confirmed", "b3_commitment_v1",
                )
                self.store.update_commitment_status("commitment_b3_storage_002", "rev_b3_021", "cancelled")
        self._add_commitment()
        with self.store.transaction():
            self.store.add_revision("rev_b3_022", "2032-03-11T09:00:00Z")
            self.store.update_commitment_status("commitment_b3_storage_001", "rev_b3_022", "cancelled", "synthetic plan changed")
        self.assertEqual(self.store.commitment_record("commitment_b3_storage_001")["cancel_reason"], "synthetic plan changed")

    def test_derived_due_projection_delete_does_not_touch_canonical(self) -> None:
        self._add_commitment()
        self.store.put_due_status_projection(
            "due_b3_storage_001", "commitment_b3_storage_001", "rev_b3_020", "rev_b3_020", "fresh",
            "upcoming", "2032-03-10T09:00:00Z", {"due_status": "upcoming"}, "2032-03-10T09:00:00Z", "b3_deterministic_v1",
        )
        self.assertEqual(self.store.due_status_projection("due_b3_storage_001")["due_status"], "upcoming")
        self.assertEqual(self.store.delete_due_status_projections(), 1)
        self.assertEqual(self.store.canonical_object("commitment_b3_storage_001")["object_type"], "commitment")
        with self.assertRaises(KeyError):
            self.store.due_status_projection("due_b3_storage_001")

    def test_due_projection_requires_commitment_foreign_key(self) -> None:
        self._add_commitment()
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.put_due_status_projection(
                "due_b3_orphan", "commitment_missing", "rev_b3_020", "rev_b3_020", "fresh",
                "upcoming", "2032-03-10T09:00:00Z", {}, "2032-03-10T09:00:00Z", "b3_deterministic_v1",
            )
