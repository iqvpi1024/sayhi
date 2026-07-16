"""Test-only adapter factory for the approved Micro runner contract."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .candidate import ContactCandidateBuilder
from .changesets import ChangeSetService
from .intake import IntakeService
from .queries import CanonicalQueries
from .store import SemanticStore
from .views import CoreViewReader


JsonObject = dict[str, Any]
_WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class FixedClock:
    """The fixture controls business time; the runtime never reads wall time."""

    value: str

    def now(self) -> str:
        return self.value


class Task002MicroSystem:
    """Protocol-shaped bootstrap only; later tasks provide business behavior."""

    def __init__(self, fixture: Mapping[str, Any], data_root: Path) -> None:
        self.fixture = copy.deepcopy(dict(fixture))
        self.clock = FixedClock(str(self.fixture["determinism"]["clock"]))
        self.data_root = data_root
        self._failure_points: set[str] = set()
        self._database_path = data_root / "micro.sqlite3"
        store = SemanticStore(self._database_path)
        try:
            store.seed_rev_010(self.fixture)
        finally:
            store.close()

    @property
    def store(self) -> SemanticStore:
        """Compatibility handle for narrow tests; callers must close it."""
        return SemanticStore(self._database_path)

    def _with_store(self, callback: Any) -> Any:
        store = SemanticStore(self._database_path)
        try:
            return callback(store)
        finally:
            store.close()

    def intake(self, request: Mapping[str, Any]) -> JsonObject:
        return self._with_store(lambda store: IntakeService(store, self.fixture).append(request))

    def get_source(self, source_id: str) -> JsonObject:
        def read(store: SemanticStore) -> JsonObject:
            source = store.seeded_source(source_id)
            if source is None:
                raise KeyError(source_id)
            return source

        return self._with_store(read)

    def canonical_snapshot(self) -> JsonObject:
        return self._with_store(lambda store: store.seed_snapshot())

    def propose_contact_changeset(self, source_id: str) -> JsonObject:
        return self._with_store(
            lambda store: ContactCandidateBuilder(store, self.fixture, self.clock.now()).propose(source_id)
        )

    def preview_changeset(self, changeset_id: str) -> JsonObject:
        return self._with_store(
            lambda store: ContactCandidateBuilder(store, self.fixture, self.clock.now()).preview(changeset_id)
        )

    def approve_changeset(self, changeset_id: str, actor: str) -> JsonObject:
        return self._with_store(
            lambda store: ContactCandidateBuilder(store, self.fixture, self.clock.now()).approve(changeset_id, actor)
        )

    def publish_changeset(self, changeset_id: str, idempotency_key: str) -> JsonObject:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).publish(
                changeset_id, idempotency_key, self._failure_points
            )
        )

    def get_changeset(self, changeset_id: str) -> JsonObject:
        return self._with_store(
            lambda store: ContactCandidateBuilder(store, self.fixture, self.clock.now()).get(changeset_id)
        )

    def get_publish_attempts(self, changeset_id: str) -> Sequence[JsonObject]:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).attempts(changeset_id)
        )

    def get_receipt(self, receipt_id: str) -> JsonObject:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).receipt(receipt_id)
        )

    def read_core_view(self, view_name: str, session_id: str) -> JsonObject:
        return self._with_store(
            lambda store: CoreViewReader(store, self.fixture).read(view_name, session_id)
        )

    def query_relationship_contact(self, at: str) -> JsonObject:
        return self._with_store(
            lambda store: CanonicalQueries(store, self.fixture).relationship_contact(at)
        )

    def revert_changeset(self, changeset_id: str, idempotency_key: str) -> JsonObject:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).revert(
                changeset_id, idempotency_key
            )
        )

    def list_audit_events(self, changeset_id: str) -> Sequence[JsonObject]:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).audit_events(changeset_id)
        )

    def inject_failure(self, failure_point: str) -> None:
        self._failure_points.add(failure_point)

    def reconcile_views(self) -> JsonObject:
        return self._with_store(lambda store: CoreViewReader(store, self.fixture).reconcile())

    def advance_revision_for_test(self) -> JsonObject:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).advance_for_test()
        )

    def propose_retry(self, changeset_id: str) -> JsonObject:
        return self._with_store(
            lambda store: ChangeSetService(store, self.fixture, self.clock.now()).propose_retry(changeset_id)
        )

    @staticmethod
    def _not_implemented(method: str) -> JsonObject:
        raise NotImplementedError(f"{method} is not implemented before its approved task")


def create_system(fixture: Mapping[str, Any], data_root: Path) -> Task002MicroSystem:
    """Create a deterministic, repository-contained test system."""
    resolved_root = data_root.resolve()
    if _WORKSPACE_ROOT not in resolved_root.parents:
        raise ValueError("data_root must be inside the repository workspace")
    if not fixture.get("synthetic") or fixture.get("external_data_used"):
        raise ValueError("Micro adapter accepts approved synthetic fixtures only")
    if not data_root.exists() or not data_root.is_dir():
        raise ValueError("caller must create the per-run data_root")
    return Task002MicroSystem(fixture, resolved_root)
