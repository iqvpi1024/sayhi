from __future__ import annotations

import unittest

from noetide_micro.review_budget import ReviewBudgetService


def scenario(identifier: str):
    def decorate(method):
        method._noetide_scenario_id = identifier
        return method
    return decorate


class B1BudgetTests(unittest.TestCase):
    @scenario("B1-001")
    def test_critical_candidate_is_never_suppressed_by_budget(self) -> None:
        service = ReviewBudgetService()
        ordinary = {"candidate_id": "cand_ordinary", "review_priority": "normal", "risk_level": "low", "value_score": 9}
        critical = {"candidate_id": "cand_critical", "review_priority": "critical", "risk_level": "critical", "value_score": 0}
        service.filter_candidates([ordinary, ordinary | {"candidate_id": "cand_ordinary_2"}, ordinary | {"candidate_id": "cand_ordinary_3"}])
        selected = service.filter_candidates([critical, ordinary | {"candidate_id": "cand_ordinary_4"}])
        self.assertEqual([item["candidate_id"] for item in selected], ["cand_critical"])
        self.assertNotIn("cand_critical", service.get_suppressed())

    @scenario("B1-002")
    def test_budget_suppression_does_not_remove_candidate_payload(self) -> None:
        service = ReviewBudgetService()
        candidates = [{"candidate_id": f"cand_{index}", "review_priority": "normal", "risk_level": "low", "value_score": 10 - index, "source_refs": [{"source_id": "src_synthetic"}]} for index in range(4)]
        service.filter_candidates(candidates)
        self.assertEqual(service.get_suppressed()["cand_3"], "budget_exhausted")
        self.assertEqual(candidates[3]["source_refs"], [{"source_id": "src_synthetic"}])
