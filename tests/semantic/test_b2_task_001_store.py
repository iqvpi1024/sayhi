from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


class B2Task001StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SemanticStore(Path(self.temp.name) / "b2.sqlite3")
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())

    def _add_episode(self) -> None:
        payload = {"object_id": "episode_b2_storage_001", "object_type": "episode", "object_revision": "rev_b2_020"}
        with self.store.transaction():
            self.store.add_revision("rev_b2_020", "2032-02-20T09:00:00Z")
            self.store.add_canonical_object("episode_b2_storage_001", payload)
            self.store.put_episode_record(
                "episode_b2_storage_001", "rev_b2_020", "synthetic_relationship_event",
                "2032-02-18T00:00:00Z", "2032-02-19T00:00:00Z", "2032-02-20T09:00:00Z",
                "b2_episode_summary_v1",
                [{"source_id": "src_history_001", "locator": {"scheme": "synthetic", "start": 0, "end": 1}}],
            )

    def test_b2_schema_and_pragmas_are_present(self) -> None:
        self.assertTrue({"episodes", "episode_source_refs", "summary_projections", "derived_rebuild_receipts"}.issubset(self.store.schema_objects()))
        self.assertEqual(self.store.pragma_values(), {"foreign_keys": 1, "journal_mode": "delete", "synchronous": 2})

    def test_episode_requires_canonical_episode_and_direct_source(self) -> None:
        with self.assertRaises(KeyError):
            self.store.put_episode_record("missing", "rev_010", "synthetic_relationship_event", "a", "b", "c", "b2_episode_summary_v1", [{"source_id": "src_history_001", "locator": {}}])
        self._add_episode()
        episode = self.store.episode_record("episode_b2_storage_001")
        self.assertEqual(episode["object_revision"], "rev_b2_020")
        self.assertEqual(episode["source_refs"][0]["source_id"], "src_history_001")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction():
                self.store.put_episode_record("episode_b2_storage_001", "rev_b2_020", "synthetic_relationship_event", "a", "b", "c", "b2_episode_summary_v1", [{"source_id": "src_missing", "locator": {}}])

    def test_derived_summary_delete_does_not_touch_canonical(self) -> None:
        self._add_episode()
        self.store.put_summary_projection(
            "summary_b2_storage_001", "day_summary", "rev_b2_020", "rev_b2_020", "fresh",
            {"episode_refs": ["episode_b2_storage_001"], "data_revision": "rev_b2_020"},
            {"summary_text": "synthetic derived summary"}, "2032-02-20T09:00:00Z", "b2_deterministic_v1",
        )
        self.assertEqual(self.store.summary_projection("summary_b2_storage_001")["freshness_status"], "fresh")
        self.assertEqual(self.store.delete_summary_projections(), 1)
        self.assertEqual(self.store.canonical_object("episode_b2_storage_001")["object_type"], "episode")
        with self.assertRaises(KeyError):
            self.store.summary_projection("summary_b2_storage_001")
