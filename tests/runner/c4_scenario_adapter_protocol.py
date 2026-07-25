from __future__ import annotations

from typing import Any, Protocol


class C4ScenarioSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...


class C4ScenarioAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> C4ScenarioSystem: ...
