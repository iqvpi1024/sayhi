"""Production-facing local runtime for the approved synthetic Micro demo."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from .candidate import ContactCandidateBuilder
from .changesets import ChangeSetService
from .intake import IntakeService
from .queries import CanonicalQueries
from .store import SemanticStore
from .views import CoreViewReader


JsonObject = dict[str, Any]
_CLOCK = "2031-10-15T02:00:00Z"
_TEXT = "We no longer keep daily contact after the transition date."


def demo_fixture() -> JsonObject:
    """Return the package-owned, explicitly synthetic Micro demo fixture."""
    source_hash = hashlib.sha256(_TEXT.encode("utf-8")).hexdigest()
    locator = {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": len(_TEXT.encode("utf-8"))}
    history = {
        "source_id": "src_history_001", "append_receipt_id": "receipt_history_001",
        "source_kind": "synthetic_text", "content_hash": hashlib.sha256(b"historical active contact").hexdigest(),
        "inline_content": "historical active contact", "byte_length": 25,
    }
    source = {
        "source_id": "src_micro_001", "append_receipt_id": "receipt_source_micro_001",
        "source_kind": "synthetic_text", "content_hash": source_hash, "inline_content": _TEXT,
        "byte_length": len(_TEXT.encode("utf-8")), "locator": locator,
    }
    active = {
        "state_id": "state_contact_001", "object_type": "state", "object_revision": "rev_010",
        "state_kind": "relationship.contact", "subject_ref": "rel_alpha_beta", "value": "active",
        "created_at": _CLOCK, "created_by": "fixture_seed", "recorded_at": _CLOCK, "recorded_by": "fixture_seed",
        "valid_time": {"kind": "interval", "start": {"boundary_kind": "known", "value": "2030-01-01T00:00:00+00:00"}, "end": {"boundary_kind": "unbounded", "value": None}, "bounds": "[)"},
        "evidence_refs": [{"source_id": "src_history_001", "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 25}, "stance": "supports", "claim_ref": "state_contact_001"}],
    }
    relationship = {"relationship_id": "rel_alpha_beta", "object_type": "relationship", "object_revision": "rev_010", "participant_refs": ["person_alpha", "person_beta"], "origin": "synthetic_project_peer"}
    people = [
        {"entity_id": "person_alpha", "object_type": "entity", "object_revision": "rev_010", "entity_kind": "person", "canonical_label": "Synthetic Alpha"},
        {"entity_id": "person_beta", "object_type": "entity", "object_revision": "rev_010", "entity_kind": "person", "canonical_label": "Synthetic Beta"},
    ]
    return {
        "fixture_id": "micro_relationship_v1", "synthetic": True,
        "determinism": {"clock": _CLOCK}, "source_records": [history, source],
        "intake_request": {"source_id": "src_micro_001", "inline_content": _TEXT, "content_hash": source_hash, "byte_length": len(_TEXT.encode("utf-8"))},
        "expected_append_receipt": {"receipt_id": "receipt_source_micro_001", "source_id": "src_micro_001", "status": "stored"},
        "protected_semantics": {"object_ids": []},
        "initial_state": {"data_revision": "rev_010", "canonical_objects": [*people, relationship, active], "core_views": {"person_card": {"data_revision": "rev_010", "view_revision": "rev_010", "freshness_status": "fresh", "contact_state": "active"}, "relationship_timeline": {"data_revision": "rev_010", "view_revision": "rev_010", "freshness_status": "fresh", "current_contact_state": "active", "history": [{"state_id": "state_contact_001", "value": "active", "valid_time": active["valid_time"]}]}}},
    }


class LocalMicroRuntime:
    """A local runtime with no dependency on test adapters or test fixtures."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.fixture = demo_fixture()
        self._failures: set[str] = set()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._store = SemanticStore(self.data_dir / "noetide.sqlite3")
        self._store.seed_rev_010(self.fixture)

    def close(self) -> None:
        self._store.close()

    def intake(self) -> JsonObject:
        return IntakeService(self._store, self.fixture).append(self.fixture["intake_request"])

    def propose(self, source_id: str) -> JsonObject:
        return ContactCandidateBuilder(self._store, self.fixture, _CLOCK).propose(source_id)

    def approve(self, changeset_id: str, actor: str) -> JsonObject:
        return ContactCandidateBuilder(self._store, self.fixture, _CLOCK).approve(changeset_id, actor)

    def publish(self, changeset_id: str, idempotency_key: str) -> JsonObject:
        return ChangeSetService(self._store, self.fixture, _CLOCK).publish(changeset_id, idempotency_key, self._failures)

    def revert(self, changeset_id: str, idempotency_key: str) -> JsonObject:
        return ChangeSetService(self._store, self.fixture, _CLOCK).revert(changeset_id, idempotency_key)

    def view(self, name: str) -> JsonObject:
        return CoreViewReader(self._store, self.fixture).read(name, "local_cli")

    def changeset(self, changeset_id: str) -> JsonObject | None:
        return self._store.ledger_record(changeset_id)

    def revision(self) -> str:
        return self._store.current_revision()

    def source(self, source_id: str) -> JsonObject | None:
        return self._store.seeded_source(source_id)


def open_runtime(data_dir: str | Path) -> LocalMicroRuntime:
    return LocalMicroRuntime(Path(data_dir))
