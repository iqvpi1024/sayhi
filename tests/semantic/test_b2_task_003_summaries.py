from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from noetide_micro.episodes import EpisodeChangeSetService
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore
from noetide_micro.summaries import EpisodeSummaryService


class B2Task003SummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SemanticStore(Path(self.temp.name) / "b2.sqlite3")
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())
        self.store.append_source(
            {"source_id": "src_b2_event_001", "append_receipt_id": "receipt_b2_event_001", "source_kind": "synthetic_text", "content_hash": "synthetic_hash_b2_001", "payload": "synthetic episode event", "synthetic": True, "synthetic_profile_id": "b2_episode_summary_v1"},
            {"receipt_id": "receipt_b2_event_001", "status": "stored"},
        )
        self.episodes = EpisodeChangeSetService(self.store, "2032-02-20T09:00:00Z")
        self.summaries = EpisodeSummaryService(self.store, "2032-02-20T09:00:00Z")
        self.candidate = {
            "episode_id": "episode_b2_001", "episode_kind": "synthetic_relationship_event",
            "participant_refs": ["person_alpha", "person_beta"],
            "valid_time": {"start": "2032-02-18T00:00:00Z", "end": "2032-02-19T00:00:00Z"},
            "source_refs": [{"source_id": "src_b2_event_001", "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 23}}],
            "synthetic_profile_id": "b2_episode_summary_v1",
        }
        proposed = self.episodes.propose(self.candidate)
        self.episodes.approve(proposed["changeset_id"], "person_alpha")
        self.episodes.publish(proposed["changeset_id"])
        self.changeset_id = proposed["changeset_id"]

    def test_builds_fresh_day_and_phase_projections_from_direct_dependencies(self) -> None:
        result = self.summaries.build_for_episode("episode_b2_001")
        self.assertEqual(result, {"status": "fresh", "projection_ids": ["summary_b2_day_001", "summary_b2_phase_001"], "data_revision": "rev_021", "view_revision": "rev_021"})
        phase = self.store.summary_projection("summary_b2_phase_001")
        self.assertEqual(phase["freshness_status"], "fresh")
        self.assertEqual(phase["dependency_set"]["episode_refs"], ["episode_b2_001"])
        self.assertEqual(phase["dependency_set"]["source_refs"][0]["source_id"], "src_b2_event_001")
        self.assertNotIn("evidence_refs", phase["payload"])

    def test_revert_marks_stale_then_rebuild_excludes_removed_episode(self) -> None:
        self.summaries.build_for_episode("episode_b2_001")
        self.episodes.revert(self.changeset_id)
        stale = self.summaries.read("summary_b2_day_001")
        self.assertEqual(stale["status"], "stale")
        rebuilt = self.summaries.rebuild_existing()
        self.assertEqual(rebuilt, {"status": "fresh", "data_revision": "rev_022"})
        self.assertEqual(self.store.summary_projection("summary_b2_day_001")["dependency_set"]["episode_refs"], [])

    def test_delete_and_rebuild_uses_canonical_episode_not_old_derived_payload(self) -> None:
        self.summaries.build_for_episode("episode_b2_001")
        expected = copy.deepcopy(self.store.summary_projection("summary_b2_day_001")["payload"])
        self.assertEqual(self.store.delete_summary_projections(), 2)
        self.summaries.build_for_episode("episode_b2_001")
        self.assertEqual(self.store.summary_projection("summary_b2_day_001")["payload"], expected)
        self.assertEqual(self.store.canonical_object("episode_b2_001")["object_type"], "episode")

    def test_derived_evidence_is_rejected_and_rebuild_failure_keeps_canonical_readable(self) -> None:
        self.summaries.build_for_episode("episode_b2_001")
        self.assertEqual(self.summaries.reject_derived_evidence("summary_b2_day_001"), {"status": "rejected", "reason_code": "derived_evidence_forbidden"})
        self.summaries.inject_rebuild_failure()
        self.assertEqual(self.summaries.rebuild_existing(), {"status": "unavailable", "reason_code": "summary_rebuild_failed", "data_revision": "rev_021"})
        self.assertEqual(self.store.canonical_object("episode_b2_001")["object_type"], "episode")
        self.assertEqual(self.store.summary_projection("summary_b2_day_001")["freshness_status"], "unavailable")
        self.assertTrue(any(receipt["status"] == "failed" for receipt in self.store.derived_rebuild_receipts()))
