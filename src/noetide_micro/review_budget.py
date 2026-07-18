"""Review Budget and notification throttling for Shiling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

JsonObject = dict[str, Any]


@dataclass
class ReviewBudget:
    """Controls how often and how many candidates are presented to the user."""

    max_items_per_session: int = 3
    target_minutes_per_week: float = 5.0
    high_value_backlog_threshold: int = 10
    suppression_decay_days: int = 7


class ReviewBudgetService:
    """Enforces review budget without changing evidence or canonical state."""

    def __init__(self, budget: ReviewBudget | None = None) -> None:
        self._budget = budget or ReviewBudget()
        self._session_count: int = 0
        self._suppressed: dict[str, str] = {}  # candidate_id -> reason

    def filter_candidates(self, candidates: list[JsonObject]) -> list[JsonObject]:
        """Return candidates that fit within budget."""
        if not candidates:
            return []

        # Sort by value score descending
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.get("value_score", 0.0),
            reverse=True,
        )

        # Budget exhausted
        if self._session_count >= self._budget.max_items_per_session:
            return []

        # Take top N within budget
        available = self._budget.max_items_per_session - self._session_count
        selected = sorted_candidates[:available]
        self._session_count += len(selected)

        # Mark remaining as suppressed
        for c in sorted_candidates[available:]:
            self._suppressed[c["candidate_id"]] = "budget_exhausted"

        return selected

    def get_suppressed(self) -> dict[str, str]:
        return dict(self._suppressed)

    def reset_session(self) -> None:
        self._session_count = 0

    def get_budget_status(self) -> JsonObject:
        return {
            "max_items_per_session": self._budget.max_items_per_session,
            "target_minutes_per_week": self._budget.target_minutes_per_week,
            "high_value_backlog_threshold": self._budget.high_value_backlog_threshold,
            "session_count": self._session_count,
            "remaining": max(0, self._budget.max_items_per_session - self._session_count),
            "suppressed_count": len(self._suppressed),
        }

    def should_stop_low_value_generation(self, high_value_backlog: int) -> bool:
        """Return True if high value backlog exceeds threshold."""
        return high_value_backlog >= self._budget.high_value_backlog_threshold
