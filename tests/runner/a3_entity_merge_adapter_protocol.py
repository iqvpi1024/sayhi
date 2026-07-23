from __future__ import annotations

from typing import Any, Protocol


class A3EntityMergeSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...

    def inject_failure(self, failure_point: str) -> None: ...


class A3EntityMergeAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> A3EntityMergeSystem: ...
