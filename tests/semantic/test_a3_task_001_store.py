from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


PRE_MERGE_REFS = [
    {"ref_kind": "relationship_party", "object_id": "relationship_a3_001", "field": "party_ref", "old_value": "person_delta"},
    {"ref_kind": "state_subject", "object_id": "state_a3_001", "field": "subject_ref", "old_value": "person_delta"},
    {"ref_kind": "assertion_subject", "object_id": "assertion_a3_001", "field": "subject_ref", "old_value": "person_delta"},
]


class A3Task001StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(Path(self.temp.name) / "a3.sqlite3")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())

    def _put_merge(self) -> None:
        self.store.put_merge_record(
            "merge_a3_001", "person_delta", "person_epsilon", PRE_MERGE_REFS,
            "rev_010", "2032-05-10T09:00:00Z", "a3_entity_merge_v1",
        )

    def test_a3_schema_and_pragmas_are_present(self) -> None:
        objects = self.store.schema_objects()
        self.assertIn("merge_records", objects)
        self.assertIn("split_records", objects)
        self.assertEqual(self.store.pragma_values(), {"foreign_keys": 1, "journal_mode": "delete", "synchronous": 2})

    def test_merge_record_persists_and_round_trips(self) -> None:
        self._put_merge()
        record = self.store.merge_record("merge_a3_001")
        self.assertEqual(record["source_entity_ref"], "person_delta")
        self.assertEqual(record["target_entity_ref"], "person_epsilon")
        self.assertEqual(record["pre_merge_references"], PRE_MERGE_REFS)
        self.assertEqual(record["published_revision"], "rev_010")
        self.assertEqual(record["synthetic_profile_id"], "a3_entity_merge_v1")
        self.assertEqual(len(self.store.merge_records()), 1)

    def test_merge_record_is_append_only_and_immutable(self) -> None:
        self._put_merge()
        with self.assertRaises(sqlite3.IntegrityError):
            self._put_merge()
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.put_merge_record(
                "merge_a3_001", "person_delta", "person_zeta", [],
                "rev_010", "2032-05-10T09:00:00Z", "a3_entity_merge_v1",
            )
        record = self.store.merge_record("merge_a3_001")
        self.assertEqual(record["target_entity_ref"], "person_epsilon")
        self.assertEqual(record["pre_merge_references"], PRE_MERGE_REFS)

    def test_split_record_requires_existing_merge_and_revision(self) -> None:
        self._put_merge()
        with self.assertRaises(ValueError):
            self.store.put_split_record("split_a3_001", "merge_unknown", "rev_010", "2032-05-11T09:00:00Z")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.put_split_record("split_a3_001", "merge_a3_001", "rev_missing", "2032-05-11T09:00:00Z")
        self.store.put_split_record("split_a3_001", "merge_a3_001", "rev_010", "2032-05-11T09:00:00Z")
        record = self.store.split_record_for_merge("merge_a3_001")
        self.assertEqual(record["split_id"], "split_a3_001")
        self.assertEqual(record["published_revision"], "rev_010")
        self.assertIsNone(self.store.split_record_for_merge("merge_unknown"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.put_split_record("split_a3_001", "merge_a3_001", "rev_010", "2032-05-11T09:00:00Z")

    def test_merge_record_requires_existing_revision_and_valid_refs(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.put_merge_record(
                "merge_a3_orphan", "person_delta", "person_epsilon", [],
                "rev_missing", "2032-05-10T09:00:00Z", "a3_entity_merge_v1",
            )
        with self.assertRaises(ValueError):
            self.store.put_merge_record(
                "merge_a3_self", "person_delta", "person_delta", [],
                "rev_010", "2032-05-10T09:00:00Z", "a3_entity_merge_v1",
            )
        self.assertEqual(self.store.merge_records(), [])
