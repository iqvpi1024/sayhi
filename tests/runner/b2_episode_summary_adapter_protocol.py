from __future__ import annotations

from typing import Any, Protocol


class B2EpisodeSummarySystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...

    def inject_failure(self, failure_point: str) -> None: ...


class B2EpisodeSummaryAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> B2EpisodeSummarySystem: ...
