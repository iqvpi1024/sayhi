"""B6-TASK-001/002 narrow tests: shadow migration + disambiguation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.disambiguation import process_batches, propagate_merge, scan_candidates
from noetide_micro.reconciliation import expected_projection_payload, DEEP_PARTITIONS
from noetide_micro.shadow_migration import (
    inject_shadow_deviation,
    reconcile_shadow,
    run_shadow_migration,
    shadow_history_integrity,
)
from noetide_micro.store import SemanticStore


CLOCK = "2032-06-01T09:00:00Z"
VIEW_NAMES = {
    "person_card": "proj_b6_card_001",
    "relationship_timeline": "proj_b6_timeline_001",
    "current_state": "proj_b6_current_001",
}
ENTITIES = [
    {"entity_id": f"synthetic_person_{key}_0{i}", "name_key": f"synthetic_name_{key}"}
    for key in ("alpha", "beta", "gamma", "delta")
    for i in (1, 2, 3)
]


def build_source_store(directory: str) -> Path:
    path = Path(directory) / "b6_original.sqlite3"
    store = SemanticStore(path)
    store.add_revision("rev_020", CLOCK, "seed")
    store.add_revision("rev_021", CLOCK)
    objects = [
        ("state_b6_contact_001", {"rev_020": {"contact_frequency": "weekly"}, "rev_021": {"contact_frequency": "daily"}}),
        ("state_b6_static_001", {"rev_020": {"residence_city": "synthetic_city_b"}, "rev_021": {"residence_city": "synthetic_city_b"}}),
    ]
    for object_id, revisions in objects:
        store.add_canonical_object(
            object_id,
            {"object_type": "state", "object_revision": "rev_021", "fields": revisions["rev_021"]},
        )
        for revision, fields in revisions.items():
            store.put_ledger_record(
                f"snapshot:{object_id}:{revision}",
                "revision_snapshot",
                {"object_id": object_id, "revision": revision, "fields": fields},
            )
    for partition in DEEP_PARTITIONS:
        store.upsert_projection(
            VIEW_NAMES[partition], "rev_021", "rev_021", "fresh",
            expected_projection_payload(store, partition),
        )
    store.close()
    return path


class ShadowMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.source_path = build_source_store(self._tmp.name)
        self.shadow_path = Path(self._tmp.name) / "b6_shadow.sqlite3"

    def _original_digest(self) -> str:
        store = SemanticStore(self.source_path)
        try:
            return store.canonical_layer_digest()
        finally:
            store.close()

    def test_clean_migration_reconciled_and_original_untouched(self) -> None:
        before = self._original_digest()
        result = run_shadow_migration(self.source_path, self.shadow_path, CLOCK)
        self.assertEqual(result["status"], "reconciled")
        self.assertEqual(
            result["deep_result"],
            {"person_card": "match", "relationship_timeline": "match", "current_state": "match"},
        )
        self.assertEqual(self._original_digest(), before)

    def test_transform_counts_deterministic(self) -> None:
        result = run_shadow_migration(self.source_path, self.shadow_path, CLOCK)
        self.assertEqual(result["transform_log"], {"fields_renamed": 2})
        shadow = SemanticStore(self.shadow_path)
        try:
            payload = shadow.canonical_object("state_b6_contact_001")
            self.assertIn("contact_frequency_v2", payload["fields"])
            self.assertNotIn("contact_frequency", payload["fields"])
        finally:
            shadow.close()

    def test_fault_injection_discards_shadow_without_partial_write(self) -> None:
        before = self._original_digest()
        result = run_shadow_migration(
            self.source_path, self.shadow_path, CLOCK, fault_injection={"at_batch": 2}
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["fault_batch"], 2)
        self.assertEqual(result["shadow_state"], "discarded")
        self.assertFalse(self.shadow_path.exists())
        self.assertEqual(self._original_digest(), before)

    def test_deviation_reported_mismatch_not_repaired(self) -> None:
        run_shadow_migration(self.source_path, self.shadow_path, CLOCK)
        inject_shadow_deviation(self.shadow_path, "person_card", "contact_frequency_v2", "weekly")
        report = reconcile_shadow(self.shadow_path)
        self.assertEqual(report["deep_result"]["person_card"], "mismatch")
        self.assertEqual(report["deep_result"]["current_state"], "match")
        self.assertIn("person_card", report["mismatch_details"])
        shadow = SemanticStore(self.shadow_path)
        try:
            payload = shadow.projection_record("proj_b6_card_001")["payload"]
            self.assertEqual(payload["objects"]["state_b6_contact_001"]["contact_frequency_v2"], "weekly")
        finally:
            shadow.close()

    def test_history_carried_intact(self) -> None:
        run_shadow_migration(self.source_path, self.shadow_path, CLOCK)
        integrity = shadow_history_integrity(self.source_path, self.shadow_path)
        self.assertTrue(integrity["revisions_carried"])
        self.assertTrue(integrity["snapshots_carried"])
        self.assertTrue(integrity["undo_history_intact"])


class DisambiguationTests(unittest.TestCase):
    def test_candidate_pairs_deterministic_no_auto_merge(self) -> None:
        result = scan_candidates(ENTITIES)
        self.assertEqual(result["candidate_pairs"], 12)
        self.assertEqual(result["auto_merges"], 0)
        self.assertTrue(result["all_candidates_proposed"])
        again = scan_candidates(list(reversed(ENTITIES)))
        self.assertEqual(result["candidate_pairs"], again["candidate_pairs"])
        self.assertEqual(
            [c["candidate_id"] for c in result["candidates"]],
            [c["candidate_id"] for c in again["candidates"]],
        )

    def test_merge_propagation_counts(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = SemanticStore(Path(tmp.name) / "b6_merge.sqlite3")
        self.addCleanup(store.close)
        links = [
            {"link_id": "link_b6_001", "from_object": "state_b6_contact_001", "to_entity": "synthetic_person_alpha_01"},
            {"link_id": "link_b6_002", "from_object": "state_b6_static_001", "to_entity": "synthetic_person_alpha_01"},
            {"link_id": "link_b6_003", "from_object": "state_b6_static_001", "to_entity": "synthetic_person_alpha_02"},
        ]
        for link in links:
            store.put_ledger_record(link["link_id"], "reference_link", link)
        instruction = {"merge_id": "merge_b6_001", "source_entity_ref": "synthetic_person_alpha_01", "target_entity_ref": "synthetic_person_alpha_02", "confirmed": True}
        result = propagate_merge(store, instruction, CLOCK)
        self.assertEqual(result["propagated_references"], 2)
        self.assertTrue(result["history_preserved"])
        self.assertTrue(result["unaffected_entities_intact"])
        remaining = [r for r in store.ledger_records_of_type("reference_link") if r["to_entity"] == "synthetic_person_alpha_01"]
        self.assertEqual(remaining, [])

    def test_unconfirmed_merge_rejected(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = SemanticStore(Path(tmp.name) / "b6_merge2.sqlite3")
        self.addCleanup(store.close)
        with self.assertRaises(ValueError):
            propagate_merge(store, {"merge_id": "m", "source_entity_ref": "a", "target_entity_ref": "b", "confirmed": False}, CLOCK)

    def test_batch_counts_reproducible(self) -> None:
        result = process_batches(list(range(12)), 5)
        self.assertEqual(result["batches"], 3)
        self.assertEqual(result["processed"], 12)
        self.assertTrue(result["counts_reproducible"])
        self.assertEqual(process_batches(list(range(12)), 5), result)


if __name__ == "__main__":
    unittest.main()
