"""B1 Candidate Review integration tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from noetide_micro.candidate_aggregator import CandidateAggregator, CandidateEnvelope
from noetide_micro.review_budget import ReviewBudget, ReviewBudgetService


FIXTURE_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "micro_relationship_v1" / "fixture.json"


class B1CandidateReviewTests(unittest.TestCase):
    """Integration tests for B1 Candidate Review."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_b1_001_aggregate_multiple_sources_same_semantic(self) -> None:
        """Multiple sources proposing same semantic change should aggregate."""
        agg = CandidateAggregator()

        c1 = CandidateEnvelope(
            candidate_id="c1",
            candidate_kind="state",
            source_refs=[{"source_id": "chat_001"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="medium",
            review_priority="high",
            value_factors={
                "target_ref": "state_contact_001",
                "goal_impact": 0.8,
                "change_scope": 0.5,
                "urgency": 0.9,
                "uncertainty": 0.2,
                "historical_acceptance": 0.7,
            },
            confirmation_policy="single_confirmation",
        )

        c2 = CandidateEnvelope(
            candidate_id="c2",
            candidate_kind="state",
            source_refs=[{"source_id": "diary_001"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="low",
            review_priority="normal",
            value_factors={
                "target_ref": "state_contact_001",
                "goal_impact": 0.5,
                "change_scope": 0.5,
                "urgency": 0.3,
                "uncertainty": 0.4,
                "historical_acceptance": 0.6,
            },
            confirmation_policy="single_confirmation",
        )

        agg.add_candidate(c1)
        result = agg.add_candidate(c2)

        # Should merge into single candidate
        self.assertEqual(len(agg.list_candidates()), 1)
        self.assertEqual(result.candidate_id, "c1")
        self.assertEqual(len(result.source_refs), 2)
        self.assertEqual(result.value_factors.get("duplicate_count", 0), 1)

    def test_b1_002_different_semantics_not_merged(self) -> None:
        """Different semantic candidates should not be merged."""
        agg = CandidateAggregator()

        c1 = CandidateEnvelope(
            candidate_id="c1",
            candidate_kind="state",
            source_refs=[{"source_id": "src1"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="medium",
            review_priority="high",
            value_factors={"target_ref": "state_contact_001"},
            confirmation_policy="single_confirmation",
        )

        c2 = CandidateEnvelope(
            candidate_id="c2",
            candidate_kind="state",
            source_refs=[{"source_id": "src2"}],
            proposed_value="low_frequency",
            valid_time_candidate=None,
            risk_level="low",
            review_priority="normal",
            value_factors={"target_ref": "state_contact_001"},
            confirmation_policy="posthoc_revertible",
        )

        agg.add_candidate(c1)
        agg.add_candidate(c2)

        self.assertEqual(len(agg.list_candidates()), 2)

    def test_b1_003_review_budget_limits_session(self) -> None:
        """Review Budget should limit candidates per session."""
        agg = CandidateAggregator()

        for i in range(5):
            c = CandidateEnvelope(
                candidate_id=f"c{i}",
                candidate_kind="state",
                source_refs=[{"source_id": f"src{i}"}],
                proposed_value=f"value_{i}",
                valid_time_candidate=None,
                risk_level="medium",
                review_priority="normal",
                value_factors={
                    "target_ref": "state_contact_001",
                    "goal_impact": 0.5 + i * 0.1,
                    "change_scope": 0.5,
                    "urgency": 0.5,
                    "uncertainty": 0.3,
                    "historical_acceptance": 0.5,
                },
                confirmation_policy="single_confirmation",
            )
            agg.add_candidate(c)

        budget = ReviewBudget(max_items_per_session=3)
        service = ReviewBudgetService(budget)
        items = agg.list_review_items()
        selected = service.filter_candidates(items)

        self.assertEqual(len(selected), 3)
        self.assertEqual(service.get_budget_status()["session_count"], 3)
        self.assertEqual(len(service.get_suppressed()), 2)

    def test_b1_004_value_score_sorting(self) -> None:
        """Candidates should be sorted by value score descending."""
        agg = CandidateAggregator()

        c1 = CandidateEnvelope(
            candidate_id="low_value",
            candidate_kind="state",
            source_refs=[{"source_id": "src1"}],
            proposed_value="low_frequency",
            valid_time_candidate=None,
            risk_level="low",
            review_priority="low",
            value_factors={
                "target_ref": "state_contact_001",
                "goal_impact": 0.1,
                "change_scope": 0.2,
                "urgency": 0.1,
                "uncertainty": 0.8,
                "historical_acceptance": 0.2,
            },
            confirmation_policy="posthoc_revertible",
        )

        c2 = CandidateEnvelope(
            candidate_id="high_value",
            candidate_kind="state",
            source_refs=[{"source_id": "src2"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="medium",
            review_priority="high",
            value_factors={
                "target_ref": "state_contact_001",
                "goal_impact": 0.9,
                "change_scope": 0.8,
                "urgency": 0.9,
                "uncertainty": 0.1,
                "historical_acceptance": 0.8,
            },
            confirmation_policy="single_confirmation",
        )

        agg.add_candidate(c1)
        agg.add_candidate(c2)

        items = agg.list_review_items()
        self.assertEqual(items[0]["candidate_id"], "high_value")
        self.assertEqual(items[1]["candidate_id"], "low_value")
        self.assertGreater(items[0]["value_score"], items[1]["value_score"])

    def test_b1_005_risk_level_maximum(self) -> None:
        """Merged candidate should take maximum risk level."""
        agg = CandidateAggregator()

        c1 = CandidateEnvelope(
            candidate_id="c1",
            candidate_kind="state",
            source_refs=[{"source_id": "src1"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="low",
            review_priority="normal",
            value_factors={"target_ref": "state_contact_001"},
            confirmation_policy="single_confirmation",
        )

        c2 = CandidateEnvelope(
            candidate_id="c2",
            candidate_kind="state",
            source_refs=[{"source_id": "src2"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="high",
            review_priority="normal",
            value_factors={"target_ref": "state_contact_001"},
            confirmation_policy="single_confirmation",
        )

        agg.add_candidate(c1)
        result = agg.add_candidate(c2)

        self.assertEqual(result.risk_level, "high")

    def test_b1_006_confirmation_policy_stricter(self) -> None:
        """Merged candidate should take stricter confirmation policy."""
        agg = CandidateAggregator()

        c1 = CandidateEnvelope(
            candidate_id="c1",
            candidate_kind="state",
            source_refs=[{"source_id": "src1"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="medium",
            review_priority="normal",
            value_factors={"target_ref": "state_contact_001"},
            confirmation_policy="single_confirmation",
        )

        c2 = CandidateEnvelope(
            candidate_id="c2",
            candidate_kind="state",
            source_refs=[{"source_id": "src2"}],
            proposed_value="no_contact",
            valid_time_candidate=None,
            risk_level="medium",
            review_priority="normal",
            value_factors={"target_ref": "state_contact_001"},
            confirmation_policy="double_confirmation",
        )

        agg.add_candidate(c1)
        result = agg.add_candidate(c2)

        self.assertEqual(result.confirmation_policy, "double_confirmation")

    def test_b1_007_high_risk_automatic_forbidden(self) -> None:
        """High risk personal semantics should not be automatically published."""
        agg = CandidateAggregator()

        c1 = CandidateEnvelope(
            candidate_id="c1",
            candidate_kind="assertion",
            source_refs=[{"source_id": "src1"}],
            proposed_value="synthetic_trust_baseline",
            valid_time_candidate=None,
            risk_level="high",
            review_priority="high",
            value_factors={"target_ref": "assertion_trust_001"},
            confirmation_policy="automatic_forbidden",
        )

        agg.add_candidate(c1)
        items = agg.list_review_items()

        self.assertEqual(items[0]["confirmation_policy"], "automatic_forbidden")

    def test_b1_008_budget_stop_low_value_generation(self) -> None:
        """Budget should stop low value generation when backlog is high."""
        budget = ReviewBudget(high_value_backlog_threshold=5)
        service = ReviewBudgetService(budget)

        self.assertTrue(service.should_stop_low_value_generation(5))
        self.assertFalse(service.should_stop_low_value_generation(4))


if __name__ == "__main__":
    unittest.main()
