from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.c1 import C1ChangeSetService
from noetide_micro.decision import DecisionService
from noetide_micro.outcome import OutcomeService
from noetide_micro.runtime import demo_fixture
from noetide_micro.scenario import ScenarioService
from noetide_micro.store import SemanticStore

def scenario(identifier):
 def decorate(method): method._noetide_scenario_id=identifier; return method
 return decorate


class C1ChangeSetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=SemanticStore(Path(self.temp.name)/"c1.sqlite3");self.addCleanup(self.store.close);self.store.seed_rev_010(demo_fixture())
        self.writer=C1ChangeSetService(self.store,"2031-10-15T02:00:00Z")

    @scenario("C1-005")
    def test_decision_and_outcome_publish_through_changesets(self):
        decision=DecisionService(self.store,{},"2031-10-15T02:00:00Z").create("decision_synthetic","question",["a"],[],[],"a")
        decision=self.writer.publish(decision,"person_alpha")
        outcome=OutcomeService(self.store,{},"2031-10-15T02:00:00Z").create("outcome_synthetic",decision["decision_id"],"actual",[])
        outcome=self.writer.publish(outcome,"person_alpha")
        self.assertEqual(self.store.canonical_object(outcome["outcome_id"])["object_type"],"outcome")
        self.assertIsNotNone(self.store.ledger_record("changeset_c1_decision_synthetic"))
        self.assertIsNotNone(self.store.ledger_record("changeset_c1_outcome_synthetic"))

    @scenario("C1-006")
    def test_duplicate_or_invalid_outcome_fails_without_revision(self):
        before=self.store.current_revision()
        self.assertRaises(ValueError,self.writer.publish,{"object_type":"outcome","outcome_id":"outcome_bad","decision_ref":"missing"},"person_alpha")
        self.assertEqual(self.store.current_revision(),before)

    @scenario("C1-007")
    def test_predicted_scenario_publishes_as_assertion(self):
        scenario=ScenarioService(self.store,{},"2031-10-15T02:00:00Z").create("scenario_synthetic","decision_synthetic","baseline",["assumption"],"projection")
        published=self.writer.publish(scenario,"person_alpha")
        self.assertEqual(self.store.canonical_object(published["assertion_id"])["assertion_kind"],"predicted")

    def test_persisted_decide_appends_revision_and_changeset(self):
        svc=DecisionService(self.store,{},"2031-10-15T02:00:00Z")
        decision=svc.create("decision_persisted","question",["a","b"],[],[])
        published=self.writer.publish(decision,"person_alpha")
        before_revisions=set(self.store.revision_ids())
        updated=svc.decide_persisted("decision_persisted","a","person_alpha")
        self.assertEqual(updated["status"],"decided")
        self.assertEqual(updated["object_revision"],"rev_c1_decision_persisted_r002")
        self.assertEqual(self.store.canonical_object("decision_persisted")["status"],"decided")
        self.assertEqual(set(self.store.revision_ids())-before_revisions,{"rev_c1_decision_persisted_r002"})
        changeset=self.store.ledger_record("changeset_c1_decision_persisted_r002")
        self.assertIsNotNone(changeset)
        self.assertEqual(changeset["published_revision"],"rev_c1_decision_persisted_r002")
        self.assertIsNotNone(self.store.ledger_record("changeset_c1_decision_persisted"))
        history=updated["revision_history"]
        self.assertEqual(len(history),1)
        self.assertEqual(history[0]["status"],"open")
        self.assertEqual(history[0]["object_revision"],published["object_revision"])

    def test_persisted_close_and_predicted_outcome_chain(self):
        svc=DecisionService(self.store,{},"2031-10-15T02:00:00Z")
        self.writer.publish(svc.create("decision_chain","question",["a","b"],[],[]),"person_alpha")
        svc.decide_persisted("decision_chain","a","person_alpha")
        closed=svc.close_persisted("decision_chain","person_alpha")
        self.assertEqual(closed["status"],"closed")
        self.assertEqual(closed["object_revision"],"rev_c1_decision_chain_r003")
        predicted=svc.set_predicted_outcome_persisted("decision_chain","success","person_alpha")
        self.assertEqual(predicted["predicted_outcome"],"success")
        self.assertEqual(predicted["object_revision"],"rev_c1_decision_chain_r004")
        self.assertEqual([h["change"] for h in predicted["revision_history"]],["decide","close","set_predicted_outcome"])
        with self.assertRaises(RuntimeError):
            svc.decide_persisted("decision_chain","b","person_alpha")

    def test_persisted_transition_requires_published_object_and_preserves_revision_on_failure(self):
        svc=DecisionService(self.store,{},"2031-10-15T02:00:00Z")
        before=self.store.current_revision()
        with self.assertRaises(ValueError):
            svc.decide_persisted("decision_missing","a","person_alpha")
        self.assertEqual(self.store.current_revision(),before)
        self.writer.publish(svc.create("decision_guard","question",["a"],[],[]),"person_alpha")
        with self.assertRaises(ValueError):
            svc.decide_persisted("decision_guard","not_an_option","person_alpha")
        self.assertEqual(self.store.canonical_object("decision_guard")["status"],"open")
