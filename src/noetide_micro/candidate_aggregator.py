"""Candidate aggregation, deduplication and value scoring for Shiling."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import json
from typing import Any, Mapping

JsonObject = dict[str, Any]


@dataclass(frozen=True)
class CandidateKey:
    """Stable key for candidate deduplication by semantic content."""

    candidate_kind: str
    target_ref: str
    proposed_value: str


@dataclass
class CandidateEnvelope:
    """A semantic candidate before it becomes a ChangeSet proposal."""

    candidate_id: str
    candidate_kind: str
    source_refs: list[JsonObject]
    proposed_value: Any
    valid_time_candidate: JsonObject | None
    risk_level: str
    review_priority: str
    value_factors: JsonObject
    confirmation_policy: str
    status: str = "candidate"
    changeset_ref: str | None = None
    expires_at: str | None = None
    model_or_rule_version: str = "synthetic_rule_v1"
    assertion_kind: str | None = None
    target_ref: JsonObject | None = None


class CandidateAggregator:
    """Aggregate candidates from multiple sources without writing Canonical."""

    def __init__(self) -> None:
        self._candidates: dict[str, CandidateEnvelope] = {}
        self._groups: dict[CandidateKey, str] = {}  # key -> candidate_id

    def add_candidate(self, candidate: CandidateEnvelope) -> CandidateEnvelope:
        """Add a candidate; if duplicate exists, merge sources and update score."""
        key = self._make_key(candidate)

        # Check for existing duplicate by semantic content
        existing_id = self._groups.get(key)
        if existing_id is not None:
            existing = self._candidates[existing_id]
            merged = self._merge_candidates(existing, candidate)
            self._candidates[existing_id] = merged
            return merged

        # New candidate
        self._candidates[candidate.candidate_id] = candidate
        self._groups[key] = candidate.candidate_id
        return candidate

    def get_candidate(self, candidate_id: str) -> CandidateEnvelope | None:
        return self._candidates.get(candidate_id)

    def list_candidates(self) -> list[CandidateEnvelope]:
        return list(self._candidates.values())

    def list_review_items(self) -> list[JsonObject]:
        """Return candidates sorted by value score descending."""
        items = []
        for candidate in sorted(
            self._candidates.values(),
            key=lambda c: self._compute_value_score(c),
            reverse=True,
        ):
            items.append({
                "candidate_id": candidate.candidate_id,
                "candidate_kind": candidate.candidate_kind,
                "proposed_value": candidate.proposed_value,
                "risk_level": candidate.risk_level,
                "review_priority": candidate.review_priority,
                "value_score": self._compute_value_score(candidate),
                "value_factors": candidate.value_factors,
                "confirmation_policy": candidate.confirmation_policy,
                "status": candidate.status,
                "source_count": len(candidate.source_refs),
            })
        return items

    def _make_key(self, candidate: CandidateEnvelope) -> CandidateKey:
        return CandidateKey(
            candidate_kind=candidate.candidate_kind,
            target_ref=json.dumps(candidate.target_ref or candidate.value_factors.get("target_ref", "unknown"), sort_keys=True, separators=(",", ":")),
            proposed_value=json.dumps(candidate.proposed_value, sort_keys=True, separators=(",", ":")),
        )

    def _merge_candidates(
        self, existing: CandidateEnvelope, new: CandidateEnvelope
    ) -> CandidateEnvelope:
        merged_sources = copy.deepcopy(existing.source_refs)
        for ref in new.source_refs:
            if not any(r.get("source_id") == ref.get("source_id") for r in merged_sources):
                merged_sources.append(ref)

        merged_factors = copy.deepcopy(existing.value_factors)
        merged_factors["duplicate_count"] = merged_factors.get("duplicate_count", 0) + 1
        merged_factors["latest_source_time"] = new.value_factors.get("source_time", "unknown")

        return CandidateEnvelope(
            candidate_id=existing.candidate_id,
            candidate_kind=existing.candidate_kind,
            source_refs=merged_sources,
            proposed_value=existing.proposed_value,
            valid_time_candidate=existing.valid_time_candidate or new.valid_time_candidate,
            risk_level=_max_risk(existing.risk_level, new.risk_level),
            review_priority=_max_priority(existing.review_priority, new.review_priority),
            value_factors=merged_factors,
            confirmation_policy=_stricter_policy(existing.confirmation_policy, new.confirmation_policy),
            status=existing.status,
            changeset_ref=existing.changeset_ref or new.changeset_ref,
            expires_at=new.expires_at or existing.expires_at,
        )

    def _compute_value_score(self, candidate: CandidateEnvelope) -> float:
        factors = candidate.value_factors
        score = 0.0

        # Impact on goals/commitments
        score += factors.get("goal_impact", 0.0) * 3.0

        # Change scope
        score += factors.get("change_scope", 0.0) * 2.0

        # Risk (inverse)
        risk_scores = {"low": 1.0, "medium": 0.5, "high": 0.2, "critical": 0.0}
        score += risk_scores.get(candidate.risk_level, 0.5) * 2.0

        # Urgency
        score += factors.get("urgency", 0.0) * 1.5

        # Uncertainty (inverse)
        score += (1.0 - factors.get("uncertainty", 0.5)) * 1.0

        # Historical acceptance rate
        score += factors.get("historical_acceptance", 0.5) * 0.5

        # Penalize duplicates (already merged, so this is residual)
        duplicate_count = factors.get("duplicate_count", 0)
        score -= duplicate_count * 0.3

        return max(0.0, score)


def _order_index(order: list[str], value: str) -> int:
    """fail-closed:未知值按最严格档(末位之后)处理,而不是抛 ValueError。"""
    try:
        return order.index(value)
    except ValueError:
        return len(order)


def _max_risk(a: str, b: str) -> str:
    order = ["low", "medium", "high", "critical"]
    return a if _order_index(order, a) >= _order_index(order, b) else b


def _max_priority(a: str, b: str) -> str:
    order = ["low", "normal", "high", "critical"]
    return a if _order_index(order, a) >= _order_index(order, b) else b


def _stricter_policy(a: str, b: str) -> str:
    order = ["automatic", "posthoc_revertible", "single_confirmation", "double_confirmation", "automatic_forbidden"]
    return a if _order_index(order, a) >= _order_index(order, b) else b
