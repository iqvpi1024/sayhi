from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.c1 import C1ChangeSetService
from noetide_micro.decision import DecisionService
from noetide_micro.outcome import OutcomeService
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


class C1ChangeSetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=SemanticStore(Path(self.temp.name)/"c1.sqlite3");self.addCleanup(self.store.close);self.store.seed_rev_010(demo_fixture())
        self.writer=C1ChangeSetService(self.store,"2031-10-15T02:00:00Z")

    def test_decision_and_outcome_publish_through_changesets(self):
        decision=DecisionService(self.store,{},"2031-10-15T02:00:00Z").create("decision_synthetic","question",["a"],[],[],"a")
        decision=self.writer.publish(decision,"person_alpha")
        outcome=OutcomeService(self.store,{},"2031-10-15T02:00:00Z").create("outcome_synthetic",decision["decision_id"],"actual",[])
        outcome=self.writer.publish(outcome,"person_alpha")
        self.assertEqual(self.store.canonical_object(outcome["outcome_id"])["object_type"],"outcome")
        self.assertIsNotNone(self.store.ledger_record("changeset_c1_decision_synthetic"))
        self.assertIsNotNone(self.store.ledger_record("changeset_c1_outcome_synthetic"))

    def test_duplicate_or_invalid_outcome_fails_without_revision(self):
        before=self.store.current_revision()
        self.assertRaises(ValueError,self.writer.publish,{"object_type":"outcome","outcome_id":"outcome_bad","decision_ref":"missing"},"person_alpha")
        self.assertEqual(self.store.current_revision(),before)
