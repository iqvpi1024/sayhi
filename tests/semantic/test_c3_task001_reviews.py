"""Narrow C3-TASK-001 checks for the reviews module (Derived reports and comparisons)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from noetide_micro import reviews
from noetide_micro.store import SemanticStore


CLOCK = "2026-07-26T00:00:00+00:00"
W1 = ("weekly", "2026-07-06", "2026-07-13")
W2 = ("weekly", "2026-07-13", "2026-07-20")


def seed(store: SemanticStore) -> None:
    store.add_revision("rev_c3_task001", CLOCK, "seed")
    for oid, day in [("EP1", "2026-07-06"), ("EP2", "2026-07-08"), ("EP3", "2026-07-13")]:
        store.add_canonical_object(oid, {"object_type": "episode", "object_revision": "rev_c3_task001", "occurred_on": day})
    store.add_canonical_object("CM1", {"object_type": "commitment", "object_revision": "rev_c3_task001",
                                       "status": "completed", "completed_at": "2026-07-07", "due_at": "2026-07-08"})
    store.add_canonical_object("HP1", {"object_type": "hypothesis", "object_revision": "rev_c3_task001", "status": "active"})


class ReviewsTask001Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="c3_task001_")
        self.addCleanup(shutil.rmtree, self._tmpdir, True)
        self.store = SemanticStore(Path(self._tmpdir) / "c3.sqlite3")
        seed(self.store)

    def test_half_open_window_attribution(self) -> None:
        result = reviews.generate_review(self.store, *W1, generated_at=CLOCK)
        self.assertEqual(result["outcome"], "generated")
        metrics = result["report"]["metrics"]
        self.assertEqual(metrics["episodes"], 2)
        self.assertEqual(metrics["days_recorded"], 2)
        self.assertEqual(metrics["commitments_closed_on_time"], 1)
        self.assertEqual(metrics["hypothesis_status_counts"]["active"], 1)

    def test_stale_after_canonical_change_and_rebuild_keeps_history(self) -> None:
        reviews.generate_review(self.store, *W1, generated_at=CLOCK)
        self.store.add_canonical_object("EP4", {"object_type": "episode", "object_revision": "rev_c3_task001", "occurred_on": "2026-07-09"})
        presented = reviews.present_review(self.store, *W1)
        self.assertEqual(presented["freshness"], "stale")
        self.assertEqual(presented["report"]["metrics"]["episodes"], 2)
        rebuilt = reviews.rebuild_review(self.store, *W1, generated_at=CLOCK)
        self.assertEqual(rebuilt["report"]["view_revision"], 2)
        self.assertEqual(rebuilt["report"]["metrics"]["episodes"], 3)
        presented = reviews.present_review(self.store, *W1)
        self.assertEqual(presented["freshness"], "fresh")
        self.assertEqual(presented["version_chain"], [1, 2])
        v1 = [r for r in self.store.ledger_records_of_type(reviews.REVIEW_RECORD_TYPE) if r["view_revision"] == 1]
        self.assertEqual(len(v1), 1)
        self.assertEqual(v1[0]["metrics"]["episodes"], 2)

    def test_delete_and_rebuild_equivalent(self) -> None:
        first = reviews.generate_review(self.store, *W1, generated_at=CLOCK)["report"]["metrics"]
        deleted = reviews.delete_review(self.store, *W1)
        self.assertEqual(deleted["outcome"], "deleted")
        rebuilt = reviews.rebuild_review(self.store, *W1, generated_at=CLOCK)["report"]
        self.assertEqual(rebuilt["metrics"], first)
        self.assertEqual(rebuilt["view_revision"], 1)

    def test_illegal_comparisons_rejected_without_writes(self) -> None:
        before = len(self.store.ledger_records_of_type(reviews.COMPARISON_RECORD_TYPE))
        bad_set = reviews.compare_phases(
            self.store, {"review_kind": "weekly", "window_start": W1[1], "window_end": W1[2]},
            {"review_kind": "weekly", "window_start": W2[1], "window_end": W2[2]}, "other_metrics_v9", CLOCK)
        self.assertEqual(bad_set["outcome"], "rejected")
        bad_kind = reviews.compare_phases(
            self.store, {"review_kind": "weekly", "window_start": W1[1], "window_end": W1[2]},
            {"review_kind": "monthly", "window_start": "2026-07-01", "window_end": "2026-08-01"}, reviews.METRIC_SET_ID, CLOCK)
        self.assertEqual(bad_kind["outcome"], "rejected")
        inverted = reviews.compare_phases(
            self.store, {"review_kind": "weekly", "window_start": "2026-07-13", "window_end": "2026-07-06"},
            {"review_kind": "weekly", "window_start": W2[1], "window_end": W2[2]}, reviews.METRIC_SET_ID, CLOCK)
        self.assertEqual(inverted["outcome"], "rejected")
        self.assertEqual(len(self.store.ledger_records_of_type(reviews.COMPARISON_RECORD_TYPE)), before)

    def test_signed_deltas(self) -> None:
        result = reviews.compare_phases(
            self.store, {"review_kind": "weekly", "window_start": W1[1], "window_end": W1[2]},
            {"review_kind": "weekly", "window_start": W2[1], "window_end": W2[2]}, reviews.METRIC_SET_ID, CLOCK)
        self.assertEqual(result["outcome"], "generated")
        self.assertEqual(result["comparison"]["deltas"]["episodes"], -1)
        self.assertTrue(result["comparison"]["derived_only"])


if __name__ == "__main__":
    unittest.main()
