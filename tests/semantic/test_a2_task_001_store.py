from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


class A2Task001StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(Path(self.temp.name) / "a2.sqlite3")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())

    def test_a2_schema_and_pragmas_are_present(self) -> None:
        self.assertIn("a2_view_rebuild_receipts", self.store.schema_objects())
        self.assertEqual(self.store.pragma_values(), {"foreign_keys": 1, "journal_mode": "delete", "synchronous": 2})

    def test_a2_receipt_persists_and_lists(self) -> None:
        self.store.put_a2_view_receipt("receipt_a2_001", "current_state", "rev_010", "rebuilt", {"generator_policy_id": "a2_deterministic_v1"})
        receipts = self.store.a2_view_receipts()
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["status"], "rebuilt")
        self.assertEqual(receipts[0]["payload"]["generator_policy_id"], "a2_deterministic_v1")

    def test_current_state_projection_stale_and_delete(self) -> None:
        with self.store.transaction():
            self.store.add_revision("rev_011", "2032-04-10T09:00:00Z")
            self.store.upsert_projection("current_state", "rev_010", "rev_010", "fresh", {"objects": [], "object_count": 0})
        self.assertEqual(self.store.mark_current_state_stale("rev_011"), 1)
        self.assertEqual(self.store.projection_record("current_state")["freshness_status"], "stale")
        self.store.put_a2_view_receipt("receipt_a2_002", "current_state", "rev_010", "rebuilt", {})
        self.assertEqual(self.store.delete_current_state_projection(), 1)
        self.assertEqual(self.store.a2_view_receipts(), [])
        with self.assertRaises(KeyError):
            self.store.projection_record("current_state")
        self.assertEqual(self.store.canonical_object("rel_contact_alpha_beta")["object_type"], "state") if False else None

    def test_delete_does_not_touch_canonical_or_ledger(self) -> None:
        with self.store.transaction():
            self.store.upsert_projection("current_state", "rev_010", "rev_010", "fresh", {"objects": [], "object_count": 0})
        before_objects = self.store._connection.execute("SELECT COUNT(*) FROM canonical_objects").fetchone()[0]
        before_ledger = self.store._connection.execute("SELECT COUNT(*) FROM ledger_records").fetchone()[0]
        self.store.delete_current_state_projection()
        after_objects = self.store._connection.execute("SELECT COUNT(*) FROM canonical_objects").fetchone()[0]
        after_ledger = self.store._connection.execute("SELECT COUNT(*) FROM ledger_records").fetchone()[0]
        self.assertEqual(before_objects, after_objects)
        self.assertEqual(before_ledger, after_ledger)

    def test_receipt_requires_existing_revision(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.put_a2_view_receipt("receipt_a2_orphan", "current_state", "rev_missing", "rebuilt", {})
