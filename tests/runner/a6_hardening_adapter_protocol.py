from __future__ import annotations

from typing import Any, Protocol


class A6HardeningSystem(Protocol):
    """One system instance per reference profile execution.

    Scenarios run sequentially against shared state (contract rule 2).
    Cases with isolation == "sandbox" must be executed against a throwaway
    instance that leaves shared state untouched. layer_snapshot() must return
    a dict with keys: canonical, trust, closeness, personality, history.
    """

    def run_scenario(self, case: dict[str, Any]) -> dict[str, Any]: ...

    def layer_snapshot(self) -> dict[str, Any]: ...

    def inject_failure(self, failure_point: str) -> None: ...


class A6HardeningAdapterModule(Protocol):
    def create_system(self, fixture: dict[str, Any]) -> A6HardeningSystem: ...
