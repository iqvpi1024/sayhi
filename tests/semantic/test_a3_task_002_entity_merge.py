from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.entity_merge import EntityMergeService
from noetide_micro.store import SemanticStore


NOW = "2032-05-10T09:00:00Z"
PROFILE = "a3_entity_merge_v1"
MERGE_CANDIDATE = {
    "operation": "merge",
    "source_entity_ref": "person_delta",
    "target_entity_ref": "person_epsilon",
    "reason": "synthetic duplicate identity confirmed by user",
    "synthetic_profile_id": PROFILE,
}


def _entity(entity_id: str) -> dict:
    return {
        "entity_id": entity_id,
        "object_type": "entity",
        "object_revision": "rev_030",
        "entity_kind": "person",
        "canonical_label": f"Synthetic {entity_id}",
        "identity_status": "active",
        "synthetic_profile_id": PROFILE,
    }


class A3Task002EntityMergeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(Path(self.temp.name) / "a3.sqlite3")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.store.close)
        with self.store.transaction():
            self.store.add_revision("rev_030", NOW, revision_kind="seed")
            for entity_id in ("person_delta", "person_epsilon", "person_zeta"):
                self.store.add_canonical_object(entity_id, _entity(entity_id))
            self.store.add_canonical_object("relationship_a3_001", {
                "relationship_id": "relationship_a3_001", "object_type": "relationship",
                "object_revision": "rev_030", "participant_refs": ["person_delta", "person_zeta"],
                "synthetic_profile_id": PROFILE,
            })
            self.store.add_canonical_object("relationship_a3_002", {
                "relationship_id": "relationship_a3_002", "object_type": "relationship",
                "object_revision": "rev_030", "participant_refs": ["person_epsilon", "person_zeta"],
                "synthetic_profile_id": PROFILE,
            })
            self.store.add_canonical_object("state_a3_001", {
                "state_id": "state_a3_001", "object_type": "state", "object_revision": "rev_030",
                "state_kind": "contact_state", "subject_ref": "person_delta",
                "synthetic_profile_id": PROFILE,
            })
            self.store.add_canonical_object("state_trust_a3", {
                "state_id": "state_trust_a3", "object_type": "state", "object_revision": "rev_030",
                "state_kind": "trust", "subject_ref": "person_delta", "value": 0.4,
                "synthetic_profile_id": PROFILE,
            })
            self.store.add_canonical_object("assertion_a3_001", {
                "assertion_id": "assertion_a3_001", "object_type": "assertion",
                "object_revision": "rev_030", "subject_ref": "person_delta",
                "synthetic_profile_id": PROFILE,
            })
            self.store.add_canonical_object("hypothesis_a3_001", {
                "hypothesis_id": "hypothesis_a3_001", "object_type": "hypothesis",
                "object_revision": "rev_030", "subject_ref": "person_delta",
                "content": "synthetic reserved personality hypothesis",
                "synthetic_profile_id": PROFILE,
            })
            for view in ("person_card", "relationship_timeline", "current_state"):
                self.store.upsert_projection(view, "rev_030", "rev_030", "fresh", {"objects": []})
        self.service = EntityMergeService(self.store, NOW)

    def test_merge_publish_success_and_protected_layers(self) -> None:
        result = self.service.publish_merge(MERGE_CANDIDATE)
        self.assertEqual(result["status"], "merge_published")
        self.assertEqual(result["source_identity_status"], "merged")
        self.assertEqual(result["merged_into"], "person_epsilon")
        self.assertEqual(result["redirected_references"], 3)
        self.assertTrue(result["merge_record_complete"])
        self.assertEqual(result["data_revision"], "rev_031")
        relationship = self.store.canonical_object("relationship_a3_001")
        self.assertEqual(relationship["participant_refs"], ["person_epsilon", "person_zeta"])
        self.assertEqual(relationship["object_revision"], "rev_031")
        untouched = self.store.canonical_object("relationship_a3_002")
        self.assertEqual(untouched["participant_refs"], ["person_epsilon", "person_zeta"])
        self.assertEqual(untouched["object_revision"], "rev_030")
        self.assertEqual(self.store.canonical_object("state_a3_001")["subject_ref"], "person_epsilon")
        self.assertEqual(self.store.canonical_object("assertion_a3_001")["subject_ref"], "person_epsilon")
        trust = self.store.canonical_object("state_trust_a3")
        self.assertEqual(trust["subject_ref"], "person_delta")
        self.assertEqual(trust["object_revision"], "rev_030")
        hypothesis = self.store.canonical_object("hypothesis_a3_001")
        self.assertEqual(hypothesis["subject_ref"], "person_delta")
        self.assertEqual(hypothesis["object_revision"], "rev_030")
        record = self.store.merge_record("merge_person_delta_person_epsilon")
        self.assertEqual(len(record["pre_merge_references"]), 3)
        self.assertEqual(self.service.core_view_statuses(), {
            "person_card": "stale", "relationship_timeline": "stale", "current_state": "stale",
        })

    def test_merge_preflight_fail_closed(self) -> None:
        attempts = [
            dict(MERGE_CANDIDATE, reason=None),
            dict(MERGE_CANDIDATE, target_entity_ref="person_delta"),
            dict(MERGE_CANDIDATE, synthetic_profile_id="unexpected_profile"),
            dict(MERGE_CANDIDATE, source_entity_ref="person_unknown"),
        ]
        codes = [self.service.publish_merge(attempt)["reason_code"] for attempt in attempts]
        self.assertEqual(codes, [
            "merge_reason_required", "merge_source_equals_target",
            "unexpected_synthetic_profile", "merge_entity_not_found",
        ])
        self.assertEqual(self.store.current_revision(), "rev_030")
        self.assertEqual(self.store.merge_records(), [])
        self.assertEqual(self.store.canonical_object("person_delta")["identity_status"], "active")

    def test_merge_mid_redirect_failure_is_atomic(self) -> None:
        self.service.inject_failure("entity_merge.mid_redirect")
        result = self.service.publish_merge(MERGE_CANDIDATE)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["reason_code"], "merge_redirect_failed")
        self.assertEqual(result["data_revision"], "rev_030")
        self.assertEqual(self.store.current_revision(), "rev_030")
        source = self.store.canonical_object("person_delta")
        self.assertEqual(source["identity_status"], "active")
        self.assertNotIn("merged_into", source)
        self.assertEqual(
            self.store.canonical_object("relationship_a3_001")["participant_refs"],
            ["person_delta", "person_zeta"],
        )
        self.assertEqual(self.store.canonical_object("state_a3_001")["subject_ref"], "person_delta")
        self.assertEqual(self.store.merge_records(), [])
        self.assertEqual(self.service.core_view_statuses(), {
            "person_card": "fresh", "relationship_timeline": "fresh", "current_state": "fresh",
        })

    def test_split_restores_references_and_audit(self) -> None:
        merge = self.service.publish_merge(MERGE_CANDIDATE)
        self.assertEqual(merge["status"], "merge_published")
        result = self.service.publish_split({
            "operation": "split",
            "merge_ref": "merge_person_delta_person_epsilon",
            "reason": "synthetic user requests split rollback",
        })
        self.assertEqual(result["status"], "split_published")
        self.assertEqual(result["source_identity_status"], "active")
        self.assertTrue(result["merged_into_cleared"])
        self.assertEqual(result["references_restored"], 3)
        self.assertTrue(result["field_equivalent_to_pre_merge"])
        self.assertEqual(result["data_revision"], "rev_032")
        relationship = self.store.canonical_object("relationship_a3_001")
        self.assertEqual(relationship["participant_refs"], ["person_delta", "person_zeta"])
        self.assertEqual(self.store.canonical_object("state_a3_001")["subject_ref"], "person_delta")
        self.assertEqual(self.store.canonical_object("assertion_a3_001")["subject_ref"], "person_delta")
        record = self.store.split_record_for_merge("merge_person_delta_person_epsilon")
        self.assertIsNotNone(record)
        self.assertEqual(record["published_revision"], "rev_032")
        self.assertEqual(len(self.store.merge_records()), 1)
        self.assertEqual(self.service.audit_events(), ["merge_published", "split_published"])
        self.assertEqual(self.service.core_view_statuses(), {
            "person_card": "stale", "relationship_timeline": "stale", "current_state": "stale",
        })

    def test_split_fail_closed(self) -> None:
        self.service.publish_merge(MERGE_CANDIDATE)
        self.service.publish_split({
            "operation": "split",
            "merge_ref": "merge_person_delta_person_epsilon",
            "reason": "synthetic user requests split rollback",
        })
        attempts = [
            {"operation": "split", "merge_ref": "merge_unknown", "reason": "unknown merge ref"},
            {"operation": "split", "merge_ref": "merge_person_delta_person_epsilon", "reason": "repeated split"},
            {"operation": "split", "merge_ref": None, "reason": "missing merge ref"},
        ]
        codes = [self.service.publish_split(attempt)["reason_code"] for attempt in attempts]
        self.assertEqual(codes, ["merge_ref_not_found", "merge_already_split", "merge_ref_required"])
        self.assertEqual(self.store.current_revision(), "rev_032")
        self.assertEqual(len(self.store.split_records()), 1)
        fresh_merge = self.service.publish_split({
            "operation": "split",
            "merge_ref": "merge_person_delta_person_epsilon",
            "reason": "still closed",
        })
        self.assertEqual(fresh_merge["reason_code"], "merge_already_split")
