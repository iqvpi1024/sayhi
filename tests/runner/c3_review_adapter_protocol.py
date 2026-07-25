from __future__ import annotations

from typing import Any, Protocol


class C3ReviewSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...


class C3ReviewAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> C3ReviewSystem: ...
