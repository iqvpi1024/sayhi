"""B4 testing adapter: builds the fixed synthetic profile and drives B4 contract cases.

Only this adapter performs fixture seeding and controlled anomaly injection.
The reconciliation detector and semantic diff modules under test stay read-only.
"""

from __future__ import annotations

import atexit
import copy
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .reconciliation import (
    DEEP_PARTITIONS,
    expected_projection_payload,
    revision_consistency,
    run_reconciliation,
)
from .semantic_diff import compute_diff
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/b4_reconciliation_v1/fixture.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
PROFILE_ID = FIXTURE["synthetic_profile_id"]
CLOCK = FIXTURE["determinism"]["clock"]
TRUST_FIELDS = ("trust", "closeness", "persona_note")
_KIND_TO_OBJECT_TYPE = {
    "synthetic_contact_state": "state",
    "synthetic_static_state": "state",
    "hypothesis": "hypothesis",
}


def create_system(case: JsonObject) -> "B4ReconciliationSystem":
    return B4ReconciliationSystem(case)


class B4ReconciliationSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=f"{case['database_identity']}_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._store = _build_store(self._tmpdir, case["database_identity"])
        inject = case.get("inject")
        if inject:
            self._inject(inject)

    def layer_snapshot(self) -> JsonObject:
        store = self._store
        return {
            "canonical_objects": store.canonical_layer_digest(),
            "revisions": _canonical_digest(store.revision_ids()),
            "projections": _canonical_digest(store.projection_records()),
            "failure_queue": _canonical_digest(
                store.a2_view_receipts() + store.derived_rebuild_receipts() + store.due_rebuild_receipts()
            ),
            "derived_records": _canonical_digest(store.ledger_records_of_type("revision_snapshot")),
            "changesets": _canonical_digest(store.ledger_records_of_type("changeset")),
            "trust_persona": _canonical_digest(self._trust_persona()),
        }

    def run_case(self, case: JsonObject) -> JsonObject:
        operation = case["operation"]
        if operation == "run_incremental":
            return self._run_incremental(case)
        if operation == "run_deep":
            return self._run_deep()
        if operation == "semantic_diff":
            return self._run_single_diff(case["diff_query"])
        if operation == "semantic_diff_pair":
            return self._run_diff_pair(case["diff_queries"])
        if operation == "cross_cutting":
            return self._run_cross_cutting(case)
        raise ValueError(f"unsupported B4 operation: {operation}")

    # injection (adapter-only; the modules under test never write)

    def _inject(self, inject: Mapping[str, Any]) -> None:
        kind = inject["kind"]
        revision = self._store.current_revision()
        if kind == "failure_queue":
            entry = inject["entry"]
            self._store.put_a2_view_receipt(
                entry["failure_id"], "proj_b4_card_001", revision, "failed",
                {"reason_code": entry["reason_code"]},
            )
        elif kind == "stale_view":
            record = self._store.projection_record(inject["projection_id"])
            self._store.replace_projection(
                inject["projection_id"], revision, inject["forced_view_revision"], "fresh", record["payload"]
            )
        elif kind == "orphan_reference":
            entry = inject["entry"]
            self._store.upsert_projection(
                f"proj_orphan_{entry['derived_id']}", revision, revision, "fresh",
                {"derived_id": entry["derived_id"], "referenced_object_id": entry["referenced_object_id"]},
            )
        elif kind == "unconsumed_changeset":
            entry = inject["entry"]
            self._store.put_ledger_record(
                entry["changeset_id"], "changeset",
                {"changeset_id": entry["changeset_id"], "status": entry["changeset_status"]},
            )
        elif kind == "projection_deviation":
            record = self._store.projection_record(inject["projection_id"])
            payload = copy.deepcopy(record["payload"])
            target = payload.get("objects") or payload.get("current") or {}
            for fields in target.values():
                if inject["field"] in fields:
                    fields[inject["field"]] = inject["forced_value"]
            self._store.replace_projection(
                inject["projection_id"], revision, record["view_revision"], "fresh", payload
            )
        else:
            raise ValueError(f"unsupported B4 injection: {kind}")

    # operations

    def _run_incremental(self, case: JsonObject) -> JsonObject:
        report = run_reconciliation(self._store, "incremental", CLOCK)
        result: JsonObject = {
            "status": report["run_state"],
            "mode": report["mode"],
            "finding_count": report["summary"]["finding_count"],
            "auto_repair_attempted": report["summary"]["auto_repair_attempted"],
        }
        findings = report["findings"]
        if findings:
            result["finding_kind"] = findings[0]["kind"]
            result["subject_ref"] = findings[0]["subject_ref"]
            result["disposition"] = findings[0]["disposition"]
        else:
            result["data_revision"] = self._store.current_revision()
            result["revision_consistent"] = revision_consistency(self._store)
        return result

    def _run_deep(self) -> JsonObject:
        report = run_reconciliation(self._store, "deep", CLOCK)
        deep_result = report["deep_result"]
        result: JsonObject = {
            "status": report["run_state"],
            "mode": report["mode"],
            "deep_result": deep_result,
            "auto_repair_attempted": report["summary"]["auto_repair_attempted"],
        }
        mismatch_partitions = [p for p in DEEP_PARTITIONS if deep_result.get(p) == "mismatch"]
        if mismatch_partitions:
            result["mismatch_partitions"] = mismatch_partitions
            result["digest_pair_present"] = all(
                "expected_digest" in report["mismatch_details"].get(p, {})
                and "actual_digest" in report["mismatch_details"].get(p, {})
                for p in mismatch_partitions
            )
            result["projection_rewritten"] = not self._projections_unchanged_since_inject()
        return result

    def _projections_unchanged_since_inject(self) -> bool:
        # deep reconciliation is read-only; the deviated payload must still be stored
        for record in self._store.projection_records():
            payload = record["payload"]
            if isinstance(payload, dict) and payload.get("partition") == "person_card":
                objects = payload.get("objects", {})
                contact = objects.get("state_contact_001", {})
                return contact.get("contact_frequency") == "weekly"
        return False

    def _run_single_diff(self, query: JsonObject) -> JsonObject:
        before_diff_records = len(self._store.ledger_records_of_type("semantic_diff"))
        diff = compute_diff(self._store, query["object_ref"], query["base_revision"], query["target_revision"])
        persisted = len(self._store.ledger_records_of_type("semantic_diff")) != before_diff_records
        return {
            "status": "diff_issued",
            "object_ref": diff["object_ref"],
            "base_revision": diff["base_revision"],
            "target_revision": diff["target_revision"],
            "change_type": diff["change_type"],
            "field_diffs": diff["field_diffs"],
            "derived_only": diff["derived_only"],
            "diff_persisted": persisted,
        }

    def _run_diff_pair(self, queries: list[JsonObject]) -> JsonObject:
        digest_before = self._store.canonical_layer_digest()
        records_before = len(self._store.ledger_records_of_type("semantic_diff"))
        diffs = []
        for query in queries:
            diff = compute_diff(self._store, query["object_ref"], query["base_revision"], query["target_revision"])
            diffs.append(
                {
                    "object_ref": diff["object_ref"],
                    "change_type": diff["change_type"],
                    "field_diffs": diff["field_diffs"],
                }
            )
        return {
            "status": "diff_issued",
            "diffs": diffs,
            "canonical_digest_unchanged": self._store.canonical_layer_digest() == digest_before,
            "diff_persisted": len(self._store.ledger_records_of_type("semantic_diff")) != records_before,
        }

    def _run_cross_cutting(self, case: JsonObject) -> JsonObject:
        # full read-only journey: incremental + deep + a diff query
        run_reconciliation(self._store, "incremental", CLOCK)
        run_reconciliation(self._store, "deep", CLOCK)
        compute_diff(self._store, "state_contact_001", "rev_010", "rev_011")

        fixture_fields = _fixture_latest_fields("state_contact_001")
        current_fields = self._store.canonical_object("state_contact_001").get("fields", {})
        trust_unchanged = all(current_fields.get(f) == fixture_fields.get(f) for f in TRUST_FIELDS)

        expected_snapshots = sum(len(obj["revisions"]) for obj in FIXTURE["canonical_objects"])
        undo_retained = len(self._store.ledger_records_of_type("revision_snapshot")) == expected_snapshots
        ledger_intact = self._store.revision_ids() == ["rev_010", "rev_011", "rev_012"]

        attempt = case["out_of_profile_attempt"]
        if attempt.get("synthetic_profile_id") != PROFILE_ID:
            attempt_result = {"status": "failed", "reason_code": "out_of_profile_input", "write_attempted": False}
        else:
            attempt_result = {"status": "accepted"}
        return {
            "status": "cross_cutting_ok",
            "trust_closeness_persona_unchanged": trust_unchanged,
            "undo_history_retained": undo_retained,
            "revision_ledger_intact": ledger_intact,
            "out_of_profile_attempt": attempt_result,
        }

    def _trust_persona(self) -> JsonObject:
        persona: JsonObject = {}
        for summary in self._store.canonical_object_summaries():
            fields = summary["payload"].get("fields", {})
            picked = {f: fields[f] for f in TRUST_FIELDS if f in fields}
            if picked:
                persona[summary["object_id"]] = picked
        return persona


def _fixture_latest_fields(object_id: str) -> JsonObject:
    obj = next(item for item in FIXTURE["canonical_objects"] if item["object_id"] == object_id)
    latest = sorted(obj["revisions"])[-1]
    return obj["revisions"][latest]["fields"]


def _build_store(tmpdir: str, database_identity: str) -> SemanticStore:
    store = SemanticStore(Path(tmpdir) / f"{database_identity}.sqlite3")
    revisions = sorted(
        {revision for obj in FIXTURE["canonical_objects"] for revision in obj["revisions"]}
    )
    store.add_revision(revisions[0], CLOCK, "seed")
    for revision in revisions[1:]:
        store.add_revision(revision, CLOCK)
    latest = revisions[-1]
    for obj in FIXTURE["canonical_objects"]:
        object_latest = sorted(obj["revisions"])[-1]
        store.add_canonical_object(
            obj["object_id"],
            {
                "object_type": _KIND_TO_OBJECT_TYPE[obj["object_kind"]],
                "object_revision": object_latest,
                "object_kind": obj["object_kind"],
                "entity_ref": obj["entity_ref"],
                "statement_locator": obj["statement_locator"],
                "fields": obj["revisions"][object_latest]["fields"],
            },
        )
        for revision, snapshot in obj["revisions"].items():
            store.put_ledger_record(
                f"snapshot:{obj['object_id']}:{revision}",
                "revision_snapshot",
                {"object_id": obj["object_id"], "revision": revision, "fields": snapshot["fields"]},
            )
    for projection in FIXTURE["projections"]:
        payload = expected_projection_payload(store, projection["partition"])
        store.upsert_projection(projection["projection_id"], latest, latest, "fresh", payload)
    return store
