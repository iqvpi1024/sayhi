from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.commitments import CommitmentChangeSetService
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


NOW = "2032-03-10T09:00:00Z"


def candidate(commitment_id: str = "commitment_b3_001", **overrides):
    base = {
        "commitment_id": commitment_id,
        "commitment_kind": "synthetic_obligation",
        "responsible_ref": "person_gamma",
        "statement_locator": {"source_id": "src_b3_stmt_001", "locator": {"scheme": "synthetic", "start": 0, "end": 1}},
        "due_time": "2032-03-12T09:00:00Z",
        "valid_time": {"start": "2032-03-10T09:00:00Z", "end": None},
        "synthetic_profile_id": "b3_commitment_v1",
    }
    base.update(overrides)
    return base


class B3Task002CommitmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(Path(self.temp.name) / "b3.sqlite3")
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            self.store.add_revision("rev_020", NOW, "seed")
            self.store.add_canonical_object("person_gamma", {"object_id": "person_gamma", "object_type": "entity", "object_revision": "rev_020", "synthetic": True})
        self.store.append_source(
            {"source_id": "src_b3_stmt_001", "append_receipt_id": "receipt_src_b3_stmt_001", "source_kind": "synthetic_text", "content_hash": "hash_b3_stmt_001", "synthetic": True, "synthetic_profile_id": "b3_commitment_v1"},
            {"receipt_id": "receipt_src_b3_stmt_001", "source_id": "src_b3_stmt_001", "status": "stored"},
        )
        self.service = CommitmentChangeSetService(self.store, NOW)

    def _publish(self, cid: str = "commitment_b3_001"):
        proposal = self.service.propose(candidate(cid))
        self.service.approve(proposal["changeset_id"], "person_gamma")
        return self.service.publish(proposal["changeset_id"])

    def _snapshot_layers(self):
        objects = {
            "commitments": self.store.commitment_records(),
            "non_commitment_canonical": sorted(
                (row[0], row[1])
                for row in self.store._connection.execute(
                    "SELECT object_id, object_revision FROM canonical_objects WHERE object_type != 'commitment' ORDER BY object_id"
                )
            ),
            "due_projections": self.store.due_status_projections(),
            "current_revision": self.store.current_revision(),
        }
        return objects

    def test_publish_valid_candidate(self) -> None:
        result = self._publish()
        self.assertEqual(result, {
            "status": "published", "commitment_id": "commitment_b3_001", "commitment_status": "open",
            "review_status": "user_confirmed", "statement_locator": "src_b3_stmt_001", "data_revision": "rev_021",
        })
        record = self.store.commitment_record("commitment_b3_001")
        self.assertEqual(record["status"], "open")
        self.assertEqual(record["review_status"], "user_confirmed")
        self.assertEqual(record["statement_source_id"], "src_b3_stmt_001")

    def test_invalid_candidate_fail_closed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.service.propose(candidate(synthetic_profile_id="unexpected_profile"))
        self.assertEqual(str(ctx.exception), "synthetic_input_required")
        with self.assertRaises(ValueError) as ctx2:
            self.service.propose(candidate(statement_locator=None))
        self.assertEqual(str(ctx2.exception), "commitment_reference_invalid")
        self.assertEqual(self.store.current_revision(), "rev_020")
        self.assertIsNone(self.store.canonical_object_or_none("commitment_b3_001"))
        self.assertEqual(self.store.commitment_records(), [])

    def test_complete_commitment_stales_projection(self) -> None:
        self._publish()
        self.store.put_due_status_projection(
            "due_b3_001", "commitment_b3_001", "rev_021", "rev_021", "fresh",
            "upcoming", NOW, {"due_status": "upcoming"}, NOW, "b3_deterministic_v1",
        )
        result = self.service.complete("commitment_b3_001")
        self.assertEqual(result, {"status": "completed", "commitment_id": "commitment_b3_001", "data_revision": "rev_022", "due_projection_status": "stale"})
        self.assertEqual(self.store.commitment_record("commitment_b3_001")["status"], "completed")
        self.assertEqual(self.store.due_status_projection("due_b3_001")["freshness_status"], "stale")

    def test_cancel_requires_reason(self) -> None:
        self._publish()
        rejected = self.service.cancel("commitment_b3_001", None)
        self.assertEqual(rejected, {"status": "failed", "reason_code": "cancel_reason_required", "data_revision": "rev_021"})
        self.assertEqual(self.store.commitment_record("commitment_b3_001")["status"], "open")
        result = self.service.cancel("commitment_b3_001", "synthetic plan changed")
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["cancel_reason"], "synthetic plan changed")
        self.assertEqual(result["data_revision"], "rev_022")
        self.assertEqual(self.store.commitment_record("commitment_b3_001")["cancel_reason"], "synthetic plan changed")

    def test_compensation_revert_restores_open_and_history(self) -> None:
        self._publish()
        self.service.complete("commitment_b3_001")
        result = self.service.revert("commitment_b3_001")
        self.assertEqual(result["status"], "open")
        self.assertEqual(result["data_revision"], "rev_023")
        self.assertEqual(result["history_retained"], ["published", "completed", "compensation_reverted"])
        self.assertEqual(self.store.commitment_record("commitment_b3_001")["status"], "open")
        changesets = self.store.ledger_records_of_type("changeset")
        self.assertTrue(any(cs.get("base_revision") == "rev_022" for cs in changesets))

    def test_terminal_commitment_cannot_be_completed_again(self) -> None:
        self._publish()
        self.service.complete("commitment_b3_001")
        with self.assertRaises(RuntimeError):
            self.service.complete("commitment_b3_001")
        with self.assertRaises(RuntimeError):
            self.service.cancel("commitment_b3_001", "synthetic reason")
        self.assertEqual(self.store.current_revision(), "rev_022")

    def test_lifecycle_does_not_touch_other_layers(self) -> None:
        before = self._snapshot_layers()
        self._publish()
        after_publish = self._snapshot_layers()
        self.assertEqual(before["non_commitment_canonical"], after_publish["non_commitment_canonical"])
        self.service.complete("commitment_b3_001")
        after_complete = self._snapshot_layers()
        self.assertEqual(before["non_commitment_canonical"], after_complete["non_commitment_canonical"])
        self.service.revert("commitment_b3_001")
        after_revert = self._snapshot_layers()
        self.assertEqual(before["non_commitment_canonical"], after_revert["non_commitment_canonical"])

    def test_publish_idempotent_replay_of_existing_proposal(self) -> None:
        proposal = self.service.propose(candidate())
        replay = self.service.propose(candidate())
        self.assertEqual(proposal, replay)
        self.service.approve(proposal["changeset_id"], "person_gamma")
        approved_again = self.service.approve(proposal["changeset_id"], "person_gamma")
        self.assertEqual(approved_again["status"], "approved")
