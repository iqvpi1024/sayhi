"""B4-TASK-001 narrow tests: incremental reconciliation detection only."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.reconciliation import revision_consistency, run_reconciliation
from noetide_micro.store import SemanticStore


CLOCK = "2032-04-01T09:00:00Z"


def build_store(directory: str) -> SemanticStore:
    store = SemanticStore(Path(directory) / "b4_task001.sqlite3")
    store.add_revision("rev_010", CLOCK, "seed")
    store.add_revision("rev_011", CLOCK)
    store.add_revision("rev_012", CLOCK)
    store.add_canonical_object(
        "state_contact_001",
        {"object_type": "state", "object_revision": "rev_012", "state_id": "state_contact_001", "contact_frequency": "daily"},
    )
    for view_name in ("proj_b4_card_001", "proj_b4_timeline_001", "proj_b4_current_001"):
        store.upsert_projection(view_name, "rev_012", "rev_012", "fresh", {"partition": view_name})
    return store


class IncrementalReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = build_store(self._tmp.name)
        self.addCleanup(self.store.close)

    def test_clean_profile_reports_zero_findings(self) -> None:
        report = run_reconciliation(self.store, "incremental", CLOCK)
        self.assertEqual(report["mode"], "incremental")
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["summary"]["finding_count"], 0)
        self.assertFalse(report["summary"]["auto_repair_attempted"])
        self.assertTrue(revision_consistency(self.store))

    def test_failure_queue_detected(self) -> None:
        self.store.put_a2_view_receipt("fq_b4_001", "proj_b4_card_001", "rev_012", "failed", {"reason_code": "synthetic_projection_write_failed"})
        report = run_reconciliation(self.store, "incremental", CLOCK)
        self.assertEqual(len(report["findings"]), 1)
        finding = report["findings"][0]
        self.assertEqual(finding["kind"], "failure_queue")
        self.assertEqual(finding["subject_ref"], "fq_b4_001")
        self.assertEqual(finding["disposition"], "quarantined_reported")

    def test_stale_view_detected(self) -> None:
        self.store.replace_projection("proj_b4_card_001", "rev_012", "rev_011", "fresh", {"partition": "proj_b4_card_001"})
        report = run_reconciliation(self.store, "incremental", CLOCK)
        self.assertEqual([f["kind"] for f in report["findings"]], ["stale_view"])
        self.assertEqual(report["findings"][0]["subject_ref"], "proj_b4_card_001")
        self.assertFalse(revision_consistency(self.store))

    def test_orphan_reference_detected(self) -> None:
        self.store.upsert_projection(
            "proj_b4_orphan_001", "rev_012", "rev_012", "fresh",
            {"derived_id": "der_b4_001", "referenced_object_id": "missing_object_001"},
        )
        report = run_reconciliation(self.store, "incremental", CLOCK)
        self.assertEqual([f["kind"] for f in report["findings"]], ["orphan_reference"])
        self.assertEqual(report["findings"][0]["subject_ref"], "der_b4_001")

    def test_unconsumed_changeset_detected(self) -> None:
        self.store.put_ledger_record("cs_b4_001", "changeset", {"changeset_id": "cs_b4_001", "status": "approved"})
        report = run_reconciliation(self.store, "incremental", CLOCK)
        self.assertEqual([f["kind"] for f in report["findings"]], ["unconsumed_changeset"])
        self.assertEqual(report["findings"][0]["subject_ref"], "cs_b4_001")

    def test_reconciliation_never_writes(self) -> None:
        before = (self.store.canonical_layer_digest(), self.store.seed_snapshot()["projections"])
        self.store.put_a2_view_receipt("fq_b4_001", "proj_b4_card_001", "rev_012", "failed", {})
        self.store.put_ledger_record("cs_b4_001", "changeset", {"changeset_id": "cs_b4_001", "status": "proposed"})
        run_reconciliation(self.store, "incremental", CLOCK)
        after = (self.store.canonical_layer_digest(), self.store.seed_snapshot()["projections"])
        self.assertEqual(before, after)

    def test_unsupported_mode_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_reconciliation(self.store, "weekly", CLOCK)


if __name__ == "__main__":
    unittest.main()
