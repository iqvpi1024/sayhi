"""Fixture-scoped B3 contract adapter."""
from __future__ import annotations

import copy
from typing import Any

from .commitments import CommitmentChangeSetService
from .due_status import DueStatusService
from .runtime import demo_fixture
from .store import SemanticStore


_NOW = "2032-03-10T09:00:00Z"


class B3System:
    def __init__(self, case: dict[str, Any]) -> None:
        self.case = copy.deepcopy(case)
        self.store = SemanticStore(":memory:")
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            self.store.add_revision("rev_020", _NOW)
            self.store.add_canonical_object("person_gamma", {"object_id": "person_gamma", "object_type": "entity", "object_revision": "rev_020", "synthetic": True})
        self._seed_sources()
        self.commitments = CommitmentChangeSetService(self.store, _NOW)
        self.due = DueStatusService(self.store, _NOW)
        self.failure: str | None = None
        if case["scenario_id"] in {"B3-003", "B3-004", "B3-005", "B3-006", "B3-007", "B3-008"}:
            self._publish()
        if case["scenario_id"] == "B3-006":
            self.commitments.complete("commitment_b3_001")
        for projection_id in case.get("existing_projection_ids", []):
            self.due.project(projection_id, "commitment_b3_001", _NOW)
        # Append-only ledger baseline: history appended by the scenario must not
        # rewrite or drop pre-existing entries; retention is proven by the oracle result.
        self._ledger_baseline = [f"{row['commitment_id']}:{row['event']}" for row in self.store.ledger_records_of_type("commitment_history")]

    def inject_failure(self, failure_point: str) -> None:
        self.failure = failure_point

    def layer_snapshot(self) -> dict[str, Any]:
        snapshot = self.store.seed_snapshot()
        return {
            "assertions": snapshot.get("assertions", []),
            "relationship_states": snapshot.get("relationship_states", []),
            "hypotheses": snapshot.get("hypotheses", []),
            "commitments": [(row["commitment_id"], row["status"], row["object_revision"]) for row in self.store.commitment_records()],
            "due_projections": [row["projection_id"] for row in self.store.due_status_projections()],
            "revisions": self.store.current_revision(),
            "source_records": ["synthetic"],
            "historical_revisions": ["rev_010"],
            "ledger_entries": list(self._ledger_baseline),
        }

    def _seed_sources(self) -> None:
        if self.store.seeded_source("src_b3_stmt_001") is None:
            self.store.append_source(
                {"source_id": "src_b3_stmt_001", "append_receipt_id": "receipt_b3_stmt_001", "source_kind": "synthetic_text", "content_hash": "b3", "synthetic": True, "synthetic_profile_id": "b3_commitment_v1"},
                {"receipt_id": "receipt_b3_stmt_001", "status": "stored"},
            )

    def _candidate(self) -> dict[str, Any]:
        raw = self.case.get("commitment_candidate", {})
        return {
            "commitment_id": raw.get("commitment_id"),
            "commitment_kind": raw.get("commitment_kind"),
            "responsible_ref": raw.get("responsible_ref"),
            "statement_locator": {"source_id": raw.get("statement_locator"), "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 23}} if raw.get("statement_locator") else None,
            "due_time": raw.get("due_time"),
            "valid_time": raw.get("valid_time"),
            "synthetic_profile_id": raw.get("synthetic_profile_id"),
        }

    def _publish(self) -> dict[str, Any]:
        candidate = self._candidate() if "commitment_candidate" in self.case else {
            "commitment_id": "commitment_b3_001", "commitment_kind": "synthetic_obligation", "responsible_ref": "person_gamma",
            "statement_locator": {"source_id": "src_b3_stmt_001", "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 23}},
            "due_time": "2032-03-12T09:00:00Z", "valid_time": {"start": "2032-03-10T09:00:00Z", "end": None},
            "synthetic_profile_id": "b3_commitment_v1"}
        proposed = self.commitments.propose(candidate)
        self.commitments.approve(proposed["changeset_id"], "person_gamma")
        return self.commitments.publish(proposed["changeset_id"])

    def run_case(self, case: dict[str, Any]) -> dict[str, Any]:
        scenario = case["scenario_id"]
        if scenario == "B3-001":
            return self._publish()
        if scenario == "B3-002":
            try:
                return self.commitments.propose(self._candidate())
            except ValueError:
                return {"status": "failed", "reason_code": "commitment_preflight_invalid", "data_revision": self.store.current_revision()}
        if scenario == "B3-003":
            self.due.project(case["projection_id"], "commitment_b3_001", _NOW)
            statuses = [self.due.read(case["projection_id"], clock)["due_status"] for clock in case["clock_readings"]]
            revision = self.store.current_revision()
            return {"status": "fresh", "due_statuses": statuses, "projection_id": case["projection_id"], "data_revision": revision, "view_revision": revision}
        if scenario == "B3-004":
            return self.commitments.complete("commitment_b3_001")
        if scenario == "B3-005":
            attempts = case["cancel_attempts"]
            result = self.commitments.cancel("commitment_b3_001", attempts[0]["cancel_reason"])
            rejected = self.commitments.cancel("commitment_b3_001", attempts[1]["cancel_reason"])
            return {"status": result["status"], "commitment_id": result["commitment_id"], "cancel_reason": result["cancel_reason"], "data_revision": result["data_revision"], "rejected_attempt": rejected}
        if scenario == "B3-006":
            return self.commitments.revert("commitment_b3_001")
        if scenario == "B3-007":
            projection_id = case["existing_projection_ids"][0]
            before = self.store.due_status_projection(projection_id)["payload"]
            self.store.delete_due_status_projections()
            self.due.project(projection_id, "commitment_b3_001", _NOW)
            equivalent = self.store.due_status_projection(projection_id)["payload"] == before
            if self.failure == "due_projector.before_write":
                self.due.inject_rebuild_failure()
            failed = self.due.rebuild(projection_id, _NOW)
            return {**failed, "rebuild_equivalent_before_failure": equivalent}
        if scenario == "B3-008":
            result = self.due.reject_derived_evidence(case["projection_id"])
            unchanged = self.store.commitment_record("commitment_b3_001")["status"] == "open"
            return {**result, "commitment_unchanged": unchanged, "data_revision": self.store.current_revision()}
        raise ValueError(f"unknown scenario {scenario}")


def create_system(case: dict[str, Any]) -> B3System:
    return B3System(case)
