from __future__ import annotations

from typing import Any, Protocol


class B5MultilingualSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...


class B5MultilingualAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> B5MultilingualSystem: ...
