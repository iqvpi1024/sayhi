from __future__ import annotations

from typing import Any, Protocol


class B6ShadowMigrationSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...


class B6ShadowMigrationAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> B6ShadowMigrationSystem: ...
