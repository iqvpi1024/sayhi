"""B4-TASK-002 narrow tests: deep reconciliation rebuild-compare per partition."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from noetide_micro.reconciliation import (
    DEEP_PARTITIONS,
    expected_projection_payload,
    run_reconciliation,
)
from noetide_micro.store import SemanticStore


CLOCK = "2032-04-01T09:00:00Z"
OBJECT_REVISIONS = {
    "state_contact_001": {
        "rev_010": {"contact_frequency": "weekly"},
        "rev_011": {"contact_frequency": "daily"},
        "rev_012": {"contact_frequency": "daily"},
    },
    "state_static_001": {
        "rev_010": {"residence_city": "synthetic_city_a"},
        "rev_011": {"residence_city": "synthetic_city_a"},
        "rev_012": {"residence_city": "synthetic_city_a"},
    },
}
VIEW_NAMES = {
    "person_card": "proj_b4_card_001",
    "relationship_timeline": "proj_b4_timeline_001",
    "current_state": "proj_b4_current_001",
}


def build_store(directory: str) -> SemanticStore:
    store = SemanticStore(Path(directory) / "b4_task002.sqlite3")
    store.add_revision("rev_010", CLOCK, "seed")
    store.add_revision("rev_011", CLOCK)
    store.add_revision("rev_012", CLOCK)
    for object_id, revisions in OBJECT_REVISIONS.items():
        store.add_canonical_object(
            object_id,
            {"object_type": "state", "object_revision": "rev_012", "fields": revisions["rev_012"]},
        )
        for revision, fields in revisions.items():
            store.put_ledger_record(
                f"snapshot:{object_id}:{revision}",
                "revision_snapshot",
                {"object_id": object_id, "revision": revision, "fields": fields},
            )
    for partition in DEEP_PARTITIONS:
        payload = expected_projection_payload(store, partition)
        store.upsert_projection(VIEW_NAMES[partition], "rev_012", "rev_012", "fresh", payload)
    return store


class DeepReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = build_store(self._tmp.name)
        self.addCleanup(self.store.close)

    def test_clean_profile_deep_match_all_partitions(self) -> None:
        report = run_reconciliation(self.store, "deep", CLOCK)
        self.assertEqual(report["run_state"], "report_issued")
        self.assertEqual(
            report["deep_result"],
            {"person_card": "match", "relationship_timeline": "match", "current_state": "match"},
        )
        self.assertEqual(report["mismatch_details"], {})

    def test_deviation_detected_with_digest_pair_and_no_rewrite(self) -> None:
        record = self.store.projection_record("proj_b4_card_001")
        before = copy.deepcopy(record)
        deviated = copy.deepcopy(record["payload"])
        deviated["objects"]["state_contact_001"]["contact_frequency"] = "weekly"
        self.store.replace_projection("proj_b4_card_001", "rev_012", "rev_012", "fresh", deviated)
        report = run_reconciliation(self.store, "deep", CLOCK)
        self.assertEqual(report["deep_result"]["person_card"], "mismatch")
        self.assertEqual(report["deep_result"]["relationship_timeline"], "match")
        self.assertEqual(report["deep_result"]["current_state"], "match")
        pair = report["mismatch_details"]["person_card"]
        self.assertIn("expected_digest", pair)
        self.assertIn("actual_digest", pair)
        self.assertNotEqual(pair["expected_digest"], pair["actual_digest"])
        after = self.store.projection_record("proj_b4_card_001")
        self.assertEqual(after["payload"], deviated)
        self.assertEqual(after["view_revision"], before["view_revision"])

    def test_missing_partition_projection_reported_mismatch_not_repaired(self) -> None:
        self.store.replace_projection("proj_b4_current_001", "rev_012", "rev_012", "fresh", {"partition": None})
        report = run_reconciliation(self.store, "deep", CLOCK)
        self.assertEqual(report["deep_result"]["current_state"], "mismatch")
        self.assertEqual(report["mismatch_details"]["current_state"]["actual_digest"], "absent")

    def test_unavailable_shell_on_scan_failure(self) -> None:
        empty = SemanticStore(Path(self._tmp.name) / "b4_empty.sqlite3")
        empty.close()  # closed connection makes the read-only scan genuinely fail
        report = run_reconciliation(empty, "deep", CLOCK)
        self.assertEqual(report["run_state"], "unavailable")
        self.assertTrue(report["unavailable_reason"])
        self.assertEqual(report["findings"], [])
        self.assertFalse(report["summary"]["auto_repair_attempted"])


if __name__ == "__main__":
    unittest.main()
