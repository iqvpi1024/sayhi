"""Narrow C4-TASK-001 checks for the scenarios module."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from noetide_micro import scenarios
from noetide_micro.store import SemanticStore


CLOCK = "2026-07-26T00:00:00+00:00"
CLOCK_DATE = "2026-07-26"
SPECS = {
    "baseline": {"assumptions": ["a1"], "projected_result": "r1", "hard_blockers": [], "soft_constraints": ["s1"]},
    "optimistic": {"assumptions": ["a2"], "projected_result": "r2", "hard_blockers": [], "soft_constraints": []},
    "pessimistic": {"assumptions": ["a3"], "projected_result": "r3", "hard_blockers": ["h1"], "soft_constraints": ["s1"]},
}
ACTIONS = [
    {"follow_up_id": "FU1", "title": "t1", "due_date": "2026-07-20"},
    {"follow_up_id": "FU2", "title": "t2", "due_date": "2026-07-30"},
]


class ScenariosTask001Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="c4_task001_")
        self.addCleanup(shutil.rmtree, self._tmpdir, True)
        self.store = SemanticStore(Path(self._tmpdir) / "c4.sqlite3")
        self.store.add_revision("rev_c4_task001", CLOCK, "seed")
        self.store.add_canonical_object("DC1", {"object_type": "decision", "object_revision": "rev_c4_task001", "status": "decided"})

    def _create(self) -> dict:
        return scenarios.create_scenario_set(self.store, "DC1", SPECS, True, CLOCK)

    def test_create_trio_deterministic_feasibility(self) -> None:
        result = self._create()
        self.assertEqual(result["outcome"], "applied")
        self.assertEqual(result["scenarios"]["baseline"]["feasibility_status"], "constrained")
        self.assertEqual(result["scenarios"]["optimistic"]["feasibility_status"], "feasible")
        self.assertEqual(result["scenarios"]["pessimistic"]["feasibility_status"], "infeasible")
        self.assertTrue(all(p["assertion_kind"] == "predicted" for p in result["scenarios"].values()))

    def test_unconfirmed_and_missing_decision_rejected(self) -> None:
        self.assertEqual(scenarios.create_scenario_set(self.store, "DC1", SPECS, False, CLOCK)["outcome"], "rejected")
        self.assertEqual(scenarios.create_scenario_set(self.store, "DC-X", SPECS, True, CLOCK)["outcome"], "rejected")
        self.assertEqual(scenarios.create_scenario_set(self.store, "DC1", {"baseline": SPECS["baseline"]}, True, CLOCK)["outcome"], "rejected")

    def test_upgrade_rejected_and_presentation(self) -> None:
        self._create()
        sid = "SCN-DC1-baseline"
        self.assertEqual(scenarios.attempt_mark_observed(self.store, sid)["outcome"], "rejected")
        view = scenarios.present_scenario(self.store, sid)
        self.assertEqual(view["assertion_kind"], "predicted")
        self.assertFalse(view["is_fact"])
        self.assertTrue(view["not_professional_advice"])
        self.assertNotIn("advice", view)

    def test_select_and_follow_up_lifecycle(self) -> None:
        self._create()
        sid = "SCN-DC1-baseline"
        self.assertEqual(scenarios.create_follow_ups(self.store, sid, ACTIONS, True, CLOCK)["outcome"], "rejected")
        self.assertEqual(scenarios.select_scenario(self.store, sid, True, CLOCK)["outcome"], "applied")
        created = scenarios.create_follow_ups(self.store, sid, ACTIONS, True, CLOCK)
        self.assertEqual(created["outcome"], "applied")
        self.assertEqual(len(created["follow_ups"]), 2)
        done = scenarios.complete_follow_up(self.store, "FU2", True, CLOCK)
        self.assertEqual(done["outcome"], "applied")
        self.assertEqual(done["follow_up"]["status"], "done")
        self.assertEqual(done["follow_up"]["object_revision"], 2)
        self.assertEqual(len(done["follow_up"]["revision_history"]), 1)
        self.assertEqual(scenarios.complete_follow_up(self.store, "FU2", True, CLOCK)["outcome"], "rejected")
        view = scenarios.follow_up_view(self.store, sid, CLOCK_DATE)
        statuses = {i["follow_up_id"]: i["view_status"] for i in view["items"]}
        self.assertEqual(statuses, {"FU1": "missed", "FU2": "done"})
        self.assertEqual(self.store.canonical_object("FU1")["status"], "open")

    def test_unconfirmed_select_and_complete_rejected(self) -> None:
        self._create()
        sid = "SCN-DC1-baseline"
        self.assertEqual(scenarios.select_scenario(self.store, sid, False, CLOCK)["outcome"], "rejected")
        scenarios.select_scenario(self.store, sid, True, CLOCK)
        scenarios.create_follow_ups(self.store, sid, ACTIONS, True, CLOCK)
        self.assertEqual(scenarios.complete_follow_up(self.store, "FU1", False, CLOCK)["outcome"], "rejected")
        self.assertEqual(self.store.canonical_object("FU1")["status"], "open")


if __name__ == "__main__":
    unittest.main()
