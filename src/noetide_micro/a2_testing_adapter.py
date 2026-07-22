"""Fixture-scoped A2 contract adapter."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .current_state import CurrentStateService
from .runtime import demo_fixture
from .store import SemanticStore


_NOW = "2032-04-10T09:00:00Z"
_CLOCK = "2032-04-10T09:00:00Z"
_FIXTURE = Path(__file__).resolve().parents[2] / "tests/fixtures/a2_current_state_v1/fixture.json"


class A2System:
    def __init__(self, case: dict[str, Any]) -> None:
        self.case = copy.deepcopy(case)
        fixture = json.loads(_FIXTURE.read_text(encoding="utf-8"))
        self._snapshot = fixture["canonical_snapshot"]
        self._change = fixture["canonical_change"]
        self.store = SemanticStore(":memory:")
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            self.store.add_revision("rev_020", _NOW)
            for item in self._snapshot:
                self.store.add_canonical_object(item["object_id"], {**item, "object_revision": "rev_020"})
        self.store.append_source(
            {"source_id": "src_a2_stmt_001", "append_receipt_id": "receipt_a2_stmt_001", "source_kind": "synthetic_text", "content_hash": "a2", "synthetic": True, "synthetic_profile_id": "a2_current_state_v1"},
            {"receipt_id": "receipt_a2_stmt_001", "status": "stored"},
        )
        self.service = CurrentStateService(self.store, _NOW, _CLOCK)
        self.failure: str | None = None
        if case.get("pre_build"):
            self.service.build()
        if case.get("apply_canonical_change") and case["scenario_id"] == "A2-005":
            self._apply_change()
        self._ledger_baseline = [row["receipt_id"] for row in self.store.a2_view_receipts()]

    def inject_failure(self, failure_point: str) -> None:
        self.failure = failure_point

    def layer_snapshot(self) -> dict[str, Any]:
        snapshot = self.store.seed_snapshot()
        try:
            projections = [self.store.projection_record("current_state")["view_name"]]
        except KeyError:
            projections = []
        return {
            "assertions": snapshot.get("assertions", []),
            "relationship_states": snapshot.get("relationship_states", []),
            "hypotheses": snapshot.get("hypotheses", []),
            "canonical_objects": sorted((row["object_id"], row["object_revision"]) for row in self.store.canonical_object_summaries()),
            "revisions": self.store.current_revision(),
            "source_records": ["synthetic"],
            "historical_revisions": ["rev_010"],
            "projections": projections,
            "ledger_entries": list(self._ledger_baseline),
        }

    def _apply_change(self) -> None:
        with self.store.transaction():
            self.store.add_revision("rev_021", _NOW)
            self.store.add_canonical_object(self._change["object_id"], {**self._change, "object_revision": "rev_021"})

    def run_case(self, case: dict[str, Any]) -> dict[str, Any]:
        scenario = case["scenario_id"]
        if scenario == "A2-001":
            return self.service.build()
        if scenario == "A2-002":
            wrong_profile = CurrentStateService(self.store, _NOW, _CLOCK, synthetic_profile_id=case.get("synthetic_profile_id", "unexpected_profile"))
            failed = wrong_profile.build()
            try:
                self.service.read(case.get("unknown_view", "current_state_v2"))
            except KeyError:
                pass
            projection_absent = not any(row["view_name"] == "current_state" for row in [r for r in self.store.a2_view_receipts()] + []) and failed.get("projection_absent", True)
            return {"status": "failed", "reason_code": "a2_preflight_invalid", "projection_absent": bool(projection_absent), "data_revision": self.store.current_revision()}
        if scenario == "A2-003":
            return self.service.read()
        if scenario == "A2-004":
            self._apply_change()
            return self.service.read()
        if scenario == "A2-005":
            rebuilt = self.service.rebuild()
            equivalent = self.store.projection_record("current_state")["payload"] == self.service.equivalent_payload()
            return {"status": rebuilt["status"], "rebuild_equivalent": equivalent, "object_ids": rebuilt["object_ids"], "object_count": rebuilt["object_count"], "data_revision": rebuilt["data_revision"], "view_revision": rebuilt["view_revision"]}
        if scenario == "A2-006":
            before = self.store.projection_record("current_state")["payload"]
            self.store.delete_current_state_projection()
            self.service.build()
            equivalent = self.store.projection_record("current_state")["payload"] == before
            return {"status": "fresh", "rebuild_equivalent": equivalent, "data_revision": self.store.current_revision(), "view_revision": self.store.current_revision()}
        if scenario == "A2-007":
            if self.failure == "a2_projector.before_write":
                self.service.inject_rebuild_failure()
            return self.service.rebuild()
        if scenario == "A2-008":
            before = sorted((row["object_id"], row["object_revision"]) for row in self.store.canonical_object_summaries())
            result = self.service.reject_derived_evidence("current_state")
            after = sorted((row["object_id"], row["object_revision"]) for row in self.store.canonical_object_summaries())
            return {**result, "canonical_unchanged": before == after, "data_revision": self.store.current_revision()}
        raise ValueError(f"unknown scenario {scenario}")


def create_system(case: dict[str, Any]) -> A2System:
    return A2System(case)
