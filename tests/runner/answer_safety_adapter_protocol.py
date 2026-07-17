from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable

JsonObject = dict[str, Any]


@runtime_checkable
class AnswerSafetySystem(Protocol):
    """Test-only port required by the materialized Answer Safety suite."""

    def evaluate(self, query_id: str) -> JsonObject: ...

    def layer_snapshot(self) -> JsonObject:
        """Return revision plus Source/Canonical/Ledger/Projection count and digest."""
        ...

    def inject_failure(self, failure_point: str) -> None: ...


class AnswerSafetyAdapterModule(Protocol):
    def create_system(
        self,
        fixture: Mapping[str, Any],
        scenario_id: str,
        data_root: Path,
    ) -> AnswerSafetySystem: ...
