from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.b1 import CandidateReviewService
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


def scenario(identifier: str):
    def decorate(method):
        method._noetide_scenario_id = identifier
        return method
    return decorate


def candidate(candidate_id: str = "cand_synthetic_001"):
    return {"candidate_id": candidate_id, "candidate_kind": "state", "source_refs": [{"source_id": "src_history_001"}], "proposed_value": "no_contact", "target_ref": {"object_type": "state", "object_id": "state_contact_001"}, "model_or_rule_version": "synthetic_rule_v1", "risk_level": "medium", "review_priority": "normal", "confirmation_policy": "single_confirmation"}


class B1PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SemanticStore(Path(self.temp.name) / "b1.sqlite3")
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())
        self.service = CandidateReviewService(self.store, "2031-10-15T02:00:00Z")

    @scenario("B1-003")
    def test_submit_is_ledger_only_and_idempotent(self):
        before = self.store.seed_snapshot()
        self.service.submit(candidate())
        self.assertEqual(self.service.submit(candidate())["candidate_id"], "cand_synthetic_001")
        self.assertEqual(self.store.seed_snapshot(), before)

    @scenario("B1-004")
    def test_collision_and_automatic_candidate_fail_closed(self):
        self.service.submit(candidate())
        self.assertRaises(ValueError, self.service.submit, candidate() | {"proposed_value": "active"})
        self.assertRaises(ValueError, self.service.submit, candidate("cand_auto") | {"confirmation_policy": "automatic"})

    @scenario("B1-005")
    def test_review_writes_audit_event_without_canonical_write(self):
        self.service.submit(candidate())
        before = self.store.seed_snapshot()
        self.assertEqual(self.service.review("cand_synthetic_001", "later", "person_alpha")["status"], "deferred")
        self.assertEqual(self.store.seed_snapshot(), before)
        self.assertEqual(self.store.ledger_records_of_type("candidate_review_event")[0]["action"], "later")
