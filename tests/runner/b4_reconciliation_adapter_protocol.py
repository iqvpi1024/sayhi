from __future__ import annotations

from typing import Any, Protocol


class B4ReconciliationSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...


class B4ReconciliationAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> B4ReconciliationSystem: ...
