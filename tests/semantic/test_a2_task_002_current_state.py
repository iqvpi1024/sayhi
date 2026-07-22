from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.current_state import CurrentStateService, current_objects
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


NOW = "2032-04-10T09:00:00Z"
CLOCK = "2032-04-10T09:00:00Z"

SNAPSHOT = [
    {"object_id": "person_delta", "object_type": "entity", "valid_time": {"start": "2032-01-01T00:00:00Z", "end": None}},
    {"object_id": "person_epsilon", "object_type": "entity", "valid_time": {"start": "2032-01-01T00:00:00Z", "end": None}},
    {"object_id": "relationship_a2_001", "object_type": "relationship", "valid_time": {"start": "2032-02-01T00:00:00Z", "end": None}},
    {"object_id": "state_a2_contact_current", "object_type": "state", "valid_time": {"start": "2032-04-01T00:00:00Z", "end": None}},
    {"object_id": "state_a2_contact_history", "object_type": "state", "valid_time": {"start": "2032-03-01T00:00:00Z", "end": "2032-04-01T00:00:00Z"}},
    {"object_id": "assertion_a2_001", "object_type": "assertion", "valid_time": {"start": "2032-04-02T00:00:00Z", "end": None}},
]
CURRENT_IDS = ["assertion_a2_001", "person_delta", "person_epsilon", "relationship_a2_001", "state_a2_contact_current"]


class A2Task002CurrentStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(Path(self.temp.name) / "a2.sqlite3")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            self.store.add_revision("rev_020", NOW, "seed")
            for item in SNAPSHOT:
                self.store.add_canonical_object(item["object_id"], {**item, "object_revision": "rev_020"})
        self.service = CurrentStateService(self.store, NOW, CLOCK)

    def _canonical_snapshot(self):
        return sorted((row["object_id"], row["object_revision"]) for row in self.store.canonical_object_summaries())

    def test_build_fresh_view_excludes_history(self) -> None:
        result = self.service.build()
        self.assertEqual(result["status"], "fresh")
        self.assertEqual(result["object_ids"], CURRENT_IDS)
        self.assertEqual(result["object_count"], 5)
        self.assertEqual(result["data_revision"], "rev_020")
        ids = [item["object_id"] for item in current_objects(self.store, CLOCK)]
        self.assertNotIn("state_a2_contact_history", ids)

    def test_read_fresh_then_stale_after_canonical_change(self) -> None:
        self.service.build()
        fresh = self.service.read()
        self.assertEqual(fresh["status"], "fresh")
        self.assertTrue(fresh["revisions_aligned"])
        with self.store.transaction():
            self.store.add_revision("rev_021", NOW)
            self.store.add_canonical_object("state_a2_contact_new", {"object_id": "state_a2_contact_new", "object_type": "state", "object_revision": "rev_021", "valid_time": {"start": "2032-04-09T00:00:00Z", "end": None}})
        stale = self.service.read()
        self.assertEqual(stale["status"], "stale")
        self.assertFalse(stale["masquerades_as_current"])
        self.assertEqual(stale["view_revision"], "rev_020")

    def test_rebuild_after_stale_is_fresh_and_equivalent(self) -> None:
        self.service.build()
        with self.store.transaction():
            self.store.add_revision("rev_021", NOW)
            self.store.add_canonical_object("state_a2_contact_new", {"object_id": "state_a2_contact_new", "object_type": "state", "object_revision": "rev_021", "valid_time": {"start": "2032-04-09T00:00:00Z", "end": None}})
        rebuilt = self.service.rebuild()
        self.assertEqual(rebuilt["status"], "fresh")
        self.assertEqual(rebuilt["data_revision"], "rev_021")
        self.assertEqual(rebuilt["object_count"], 6)
        self.assertEqual(self.store.projection_record("current_state")["payload"], self.service.equivalent_payload())
        self.assertEqual(self.store.current_revision(), "rev_021")

    def test_delete_and_rebuild_equivalent(self) -> None:
        self.service.build()
        before = self.store.projection_record("current_state")["payload"]
        self.assertEqual(self.store.delete_current_state_projection(), 1)
        self.service.build()
        after = self.store.projection_record("current_state")["payload"]
        self.assertEqual(before, after)

    def test_injected_failure_unavailable_and_canonical_readable(self) -> None:
        self.service.build()
        self.service.inject_rebuild_failure()
        result = self.service.rebuild()
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["reason_code"], "a2_rebuild_failed")
        self.assertTrue(result["canonical_readable"])
        self.assertEqual(self.store.projection_record("current_state")["freshness_status"], "unavailable")
        self.assertTrue(any(receipt["status"] == "failed" for receipt in self.store.a2_view_receipts()))
        self.assertEqual(self.store.current_revision(), "rev_020")

    def test_projection_never_writes_canonical_and_is_not_evidence(self) -> None:
        snapshot = self._canonical_snapshot()
        self.service.build()
        self.service.rebuild()
        self.assertEqual(snapshot, self._canonical_snapshot())
        self.assertEqual(self.service.reject_derived_evidence("current_state"), {"status": "rejected", "reason_code": "derived_evidence_forbidden"})
        self.assertEqual(snapshot, self._canonical_snapshot())
        wrong = CurrentStateService(self.store, NOW, CLOCK, synthetic_profile_id="unexpected_profile")
        self.assertEqual(wrong.build()["reason_code"], "a2_preflight_invalid")
