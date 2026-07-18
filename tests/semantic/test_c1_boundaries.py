from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.decision import DecisionService
from noetide_micro.outcome import OutcomeService
from noetide_micro.runtime import demo_fixture
from noetide_micro.scenario import ScenarioService
from noetide_micro.store import SemanticStore

def scenario(identifier):
 def decorate(method): method._noetide_scenario_id=identifier; return method
 return decorate


class C1BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=SemanticStore(Path(self.temp.name)/"c1.sqlite3");self.addCleanup(self.store.close);self.store.seed_rev_010(demo_fixture())
        self.decision=DecisionService(self.store,{},"2031-10-15T02:00:00Z")

    @scenario("C1-001")
    def test_initial_choice_must_be_an_option(self):
        self.assertRaises(ValueError,self.decision.create,"decision_synthetic","question",["a"],[],[],"b")

    @scenario("C1-002")
    def test_outcome_requires_existing_decision(self):
        self.assertRaises(ValueError,OutcomeService(self.store,{},"2031-10-15T02:00:00Z").create,"outcome_synthetic","missing","actual",[])

    @scenario("C1-003")
    def test_scenario_is_predicted_assertion_not_new_object_type(self):
        scenario=ScenarioService(self.store,{},"2031-10-15T02:00:00Z").create("scenario_synthetic","decision_synthetic","baseline",["assumption"],"projection")
        self.assertEqual((scenario["object_type"],scenario["assertion_kind"]),("assertion","predicted"))

    @scenario("C1-004")
    def test_calibration_does_not_modify_decision_or_outcome(self):
        decision=self.decision.create("decision_synthetic","question",["a"],[],[],"a")
        decision["predicted_outcome"]="expected"
        outcome={"outcome_id":"outcome_synthetic","result":"actual"}
        from noetide_micro.outcome import CalibrationService
        before=(decision.copy(),outcome.copy())
        result=CalibrationService("2031-10-15T02:00:00Z").calibrate(decision,outcome)
        self.assertEqual(result["calibrated_at"],"2031-10-15T02:00:00Z")
        self.assertEqual((decision,outcome),before)
