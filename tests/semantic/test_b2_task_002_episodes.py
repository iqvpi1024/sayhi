from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from noetide_micro.episodes import EpisodeChangeSetService
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


class B2Task002EpisodeTests(unittest.TestCase):
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
        self.service = EpisodeChangeSetService(self.store, "2032-02-20T09:00:00Z")
        self.candidate = {
            "episode_id": "episode_b2_001",
            "episode_kind": "synthetic_relationship_event",
            "participant_refs": ["person_alpha", "person_beta"],
            "valid_time": {"start": "2032-02-18T00:00:00Z", "end": "2032-02-19T00:00:00Z"},
            "source_refs": [{"source_id": "src_b2_event_001", "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 23}}],
            "synthetic_profile_id": "b2_episode_summary_v1",
        }

    def test_publish_is_changeset_backed_and_preserves_protected_objects(self) -> None:
        protected = copy.deepcopy(self.store.seed_snapshot()["objects"])
        proposed = self.service.propose(self.candidate)
        self.assertEqual(proposed["status"], "proposed")
        self.assertIsNone(self.store.canonical_object_or_none("episode_b2_001"))
        self.service.approve(proposed["changeset_id"], "person_alpha")
        published = self.service.publish(proposed["changeset_id"])
        self.assertEqual(published, {"status": "published", "episode_id": "episode_b2_001", "data_revision": "rev_021"})
        self.assertEqual(self.store.canonical_object("episode_b2_001")["object_type"], "episode")
        self.assertEqual(self.store.episode_record("episode_b2_001")["source_refs"][0]["source_id"], "src_b2_event_001")
        self.assertTrue(all(self.store.canonical_object(key) == value for key, value in protected.items()))

    def test_invalid_candidate_does_not_write_canonical_or_revision(self) -> None:
        invalid = copy.deepcopy(self.candidate)
        invalid["source_refs"] = []
        before = self.store.current_revision()
        with self.assertRaisesRegex(ValueError, "episode_reference_invalid"):
            self.service.propose(invalid)
        self.assertEqual(self.store.current_revision(), before)
        self.assertIsNone(self.store.canonical_object_or_none("episode_b2_001"))

    def test_profile_mismatch_does_not_write_source_episode_or_revision(self) -> None:
        invalid = copy.deepcopy(self.candidate)
        invalid["synthetic_profile_id"] = "unapproved_profile"
        before_revision = self.store.current_revision()
        before_source = self.store.seeded_source("src_b2_event_001")
        with self.assertRaisesRegex(ValueError, "synthetic_input_required"):
            self.service.propose(invalid)
        self.assertEqual(self.store.current_revision(), before_revision)
        self.assertEqual(self.store.seeded_source("src_b2_event_001"), before_source)
        self.assertIsNone(self.store.canonical_object_or_none("episode_b2_001"))
        self.assertIsNone(self.store.ledger_record("changeset_b2_episode_b2_001"))

    def test_unknown_candidate_field_is_rejected_without_writes(self) -> None:
        invalid = copy.deepcopy(self.candidate)
        invalid["unapproved_field"] = "must_not_be_ignored"
        before_revision = self.store.current_revision()
        with self.assertRaisesRegex(ValueError, "fixture_profile_mismatch"):
            self.service.propose(invalid)
        self.assertEqual(self.store.current_revision(), before_revision)
        self.assertIsNone(self.store.canonical_object_or_none("episode_b2_001"))
        self.assertIsNone(self.store.ledger_record("changeset_b2_episode_b2_001"))

    def test_revert_uses_compensation_revision_and_keeps_ledger_history(self) -> None:
        proposed = self.service.propose(self.candidate)
        self.service.approve(proposed["changeset_id"], "person_alpha")
        self.service.publish(proposed["changeset_id"])
        reverted = self.service.revert(proposed["changeset_id"])
        self.assertEqual(reverted, {"status": "reverted", "episode_id": "episode_b2_001", "data_revision": "rev_022"})
        self.assertIsNone(self.store.canonical_object_or_none("episode_b2_001"))
        self.assertEqual(self.store.ledger_record(proposed["changeset_id"])["status"], "reverted")
        self.assertIsNotNone(self.store.ledger_record("changeset_b2_compensation_episode_b2_001"))
