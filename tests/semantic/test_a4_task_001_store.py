from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore



class A4Task001StoreHelpersTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self._tmp.name) / "a4_task_001.sqlite")
        self.store = SemanticStore(self.db_path)
        self.store.seed_rev_010(demo_fixture())
        self._labeled_payload = {
            "object_type": "entity",
            "object_revision": "rev_010",
            "entity_id": "a4_labeled_person",
            "sensitivity": "restricted",
            "compartments": ["personal", "health"],
            "owner_ref": "caller_owner",
            "label": "synthetic labeled object",
        }
        with self.store.transaction():
            self.store.add_canonical_object("a4_labeled_person", self._labeled_payload)

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def test_object_policy_labels_reads_s1_fields(self) -> None:
        labels = self.store.object_policy_labels("a4_labeled_person")
        self.assertIsNotNone(labels)
        self.assertEqual(labels["sensitivity"], "restricted")
        self.assertEqual(labels["compartments"], ["personal", "health"])
        self.assertEqual(labels["owner_ref"], "caller_owner")

    def test_object_policy_labels_unknown_object_returns_none(self) -> None:
        self.assertIsNone(self.store.object_policy_labels("a4_missing_object"))

    def test_policy_labeled_objects_only_lists_labeled(self) -> None:
        labeled = self.store.policy_labeled_objects()
        ids = [item["object_id"] for item in labeled]
        self.assertEqual(ids, ["a4_labeled_person"])
        self.assertEqual(labeled[0]["object_type"], "entity")

    def test_canonical_object_digest_is_deterministic(self) -> None:
        first = self.store.canonical_object_digest("a4_labeled_person")
        second = self.store.canonical_object_digest("a4_labeled_person")
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_canonical_layer_digest_unchanged_by_reads(self) -> None:
        before = self.store.canonical_layer_digest()
        self.store.object_policy_labels("a4_labeled_person")
        self.store.policy_labeled_objects()
        self.store.canonical_object_digest("a4_labeled_person")
        self.store.seed_snapshot()
        after = self.store.canonical_layer_digest()
        self.assertEqual(before, after)

    def test_canonical_layer_digest_changes_on_write(self) -> None:
        before = self.store.canonical_layer_digest()
        updated = dict(self._labeled_payload)
        updated["label"] = "synthetic labeled object v2"
        with self.store.transaction():
            self.store.replace_canonical_object("a4_labeled_person", updated)
        self.assertNotEqual(before, self.store.canonical_layer_digest())


if __name__ == "__main__":
    unittest.main()