"""B4-TASK-003 narrow tests: query-time semantic diff, derived-only."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.semantic_diff import compute_diff
from noetide_micro.store import SemanticStore


CLOCK = "2032-04-01T09:00:00Z"


def build_store(directory: str) -> SemanticStore:
    store = SemanticStore(Path(directory) / "b4_task003.sqlite3")
    store.add_revision("rev_010", CLOCK, "seed")
    store.add_revision("rev_011", CLOCK)
    store.add_revision("rev_012", CLOCK)
    snapshots = [
        ("state_contact_001", "rev_010", {"contact_frequency": "weekly", "channel": "text"}),
        ("state_contact_001", "rev_011", {"contact_frequency": "daily", "channel": "text"}),
        ("state_static_001", "rev_010", {"residence_city": "synthetic_city_a"}),
        ("state_static_001", "rev_012", {"residence_city": "synthetic_city_a"}),
        ("hyp_contact_001", "rev_011", {"likelihood": "low"}),
        ("hyp_contact_001", "rev_012", {"likelihood": "medium"}),
    ]
    for object_id, revision, fields in snapshots:
        store.put_ledger_record(
            f"snapshot:{object_id}:{revision}",
            "revision_snapshot",
            {"object_id": object_id, "revision": revision, "fields": fields},
        )
    return store


class SemanticDiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = build_store(self._tmp.name)
        self.addCleanup(self.store.close)

    def test_modify_field_level_before_after(self) -> None:
        diff = compute_diff(self.store, "state_contact_001", "rev_010", "rev_011")
        self.assertEqual(diff["change_type"], "modify")
        self.assertEqual(
            diff["field_diffs"],
            [{"field_path": "contact_frequency", "before": "weekly", "after": "daily"}],
        )
        self.assertTrue(diff["derived_only"])

    def test_hypothesis_change_presentable(self) -> None:
        diff = compute_diff(self.store, "hyp_contact_001", "rev_011", "rev_012")
        self.assertEqual(diff["change_type"], "modify")
        self.assertEqual(diff["field_diffs"], [{"field_path": "likelihood", "before": "low", "after": "medium"}])

    def test_no_change(self) -> None:
        diff = compute_diff(self.store, "state_static_001", "rev_010", "rev_012")
        self.assertEqual(diff["change_type"], "no_change")
        self.assertEqual(diff["field_diffs"], [])

    def test_create_when_object_appears_after_base(self) -> None:
        diff = compute_diff(self.store, "hyp_contact_001", "rev_010", "rev_012")
        self.assertEqual(diff["change_type"], "create")
        self.assertEqual(diff["field_diffs"], [{"field_path": "likelihood", "before": None, "after": "medium"}])

    def test_missing_target_revision_rejected(self) -> None:
        with self.assertRaises(KeyError):
            compute_diff(self.store, "state_contact_001", "rev_010", "rev_099")

    def test_unknown_object_rejected(self) -> None:
        with self.assertRaises(KeyError):
            compute_diff(self.store, "missing_object_001", "rev_010", "rev_011")

    def test_diff_never_writes(self) -> None:
        before = (
            self.store.canonical_layer_digest(),
            len(self.store.ledger_records_of_type("revision_snapshot")),
            len(self.store.ledger_records_of_type("semantic_diff")),
        )
        compute_diff(self.store, "state_contact_001", "rev_010", "rev_011")
        compute_diff(self.store, "hyp_contact_001", "rev_011", "rev_012")
        after = (
            self.store.canonical_layer_digest(),
            len(self.store.ledger_records_of_type("revision_snapshot")),
            len(self.store.ledger_records_of_type("semantic_diff")),
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
