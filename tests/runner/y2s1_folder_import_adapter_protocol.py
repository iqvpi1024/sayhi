from __future__ import annotations

from typing import Any, Protocol


class Y2S1FolderImportSystem(Protocol):
    def run_case(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...


class Y2S1FolderImportAdapterModule(Protocol):
    def create_system(self, case: dict[str, Any]) -> Y2S1FolderImportSystem: ...
