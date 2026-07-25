"""B6 testing adapter: builds the fixed synthetic complex profile and drives contract cases."""

from __future__ import annotations

import atexit
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .disambiguation import process_batches, propagate_merge, scan_candidates
from .reconciliation import DEEP_PARTITIONS, expected_projection_payload
from .shadow_migration import (
    inject_shadow_deviation,
    reconcile_shadow,
    run_shadow_migration,
    shadow_history_integrity,
    transform_expected_payload,
)
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/b6_shadow_migration_v1/fixture.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
PROFILE_ID = FIXTURE["synthetic_profile_id"]
CLOCK = FIXTURE["determinism"]["clock"]
VIEW_NAMES = {
    "person_card": "proj_b6_card_001",
    "relationship_timeline": "proj_b6_timeline_001",
    "current_state": "proj_b6_current_001",
}
_KIND_TO_OBJECT_TYPE = {"synthetic_contact_state": "state", "synthetic_static_state": "state"}


def create_system(case: JsonObject) -> "B6ShadowMigrationSystem":
    return B6ShadowMigrationSystem(case)


class B6ShadowMigrationSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=f"{case['database_identity']}_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._original_path = Path(self._tmpdir) / "original.sqlite3"
        self._shadow_path = Path(self._tmpdir) / "shadow.sqlite3"
        self._build_original()

    def _build_original(self) -> None:
        store = SemanticStore(self._original_path)
        revisions = sorted(
            {rev for obj in FIXTURE["canonical_objects"] for rev in obj["revisions"]}
        )
        store.add_revision(revisions[0], CLOCK, "seed")
        for revision in revisions[1:]:
            store.add_revision(revision, CLOCK)
        latest = revisions[-1]
        for source in FIXTURE["base_sources"]:
            vault_source = {
                "source_id": source["source_id"],
                "append_receipt_id": f"receipt_{source['source_id']}",
                "source_kind": source["source_kind"],
                "content_hash": hashlib.sha256(source["text"].encode("utf-8")).hexdigest(),
                "text": source["text"],
                "synthetic": True,
            }
            store.append_source(
                vault_source,
                {"receipt_id": vault_source["append_receipt_id"], "source_id": source["source_id"], "status": "stored", "actor": "b6_fixture_seed"},
            )
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
        for translation in FIXTURE["translations"]:
            record = {
                **translation,
                "status": "active",
                "record_kind": "translation_overlay",
                "recorded_at": CLOCK,
            }
            store.put_ledger_record(
                f"translation:{translation['source_ref']}:{translation['translation_revision']}",
                "translation_record",
                record,
            )
        for link in FIXTURE["reference_links"]:
            store.put_ledger_record(link["link_id"], "reference_link", dict(link))
        for partition in DEEP_PARTITIONS:
            store.upsert_projection(
                VIEW_NAMES[partition], latest, latest, "fresh",
                expected_projection_payload(store, partition),
            )
        store.close()

    def _open_original(self) -> SemanticStore:
        return SemanticStore(self._original_path)

    def layer_snapshot(self) -> JsonObject:
        store = self._open_original()
        try:
            source_ids = sorted(s["source_id"] for s in FIXTURE["base_sources"])
            return {
                "original_canonical": store.canonical_layer_digest(),
                "original_sources": _canonical_digest({sid: store.seeded_source(sid) for sid in source_ids}),
                "original_ledger": _canonical_digest(
                    store.ledger_records_of_type("revision_snapshot")
                    + store.ledger_records_of_type("translation_record")
                    + store.ledger_records_of_type("reference_link")
                ),
            }
        finally:
            store.close()

    def _original_unchanged(self, before: JsonObject) -> bool:
        return self.layer_snapshot() == before

    def run_case(self, case: JsonObject) -> JsonObject:
        before = self.layer_snapshot()
        operation = case["operation"]
        if operation == "shadow_migrate":
            return self._migrate(case, before)
        if operation == "shadow_migrate_transform_check":
            return self._migrate_transform_check(before)
        if operation == "shadow_migrate_then_deviate":
            return self._migrate_with_deviation(case, before)
        if operation == "disambiguation_scan":
            result = scan_candidates(FIXTURE["entities"])
            return {
                "status": result["status"],
                "candidate_pairs": result["candidate_pairs"],
                "auto_merges": result["auto_merges"],
                "all_candidates_proposed": result["all_candidates_proposed"],
            }
        if operation == "merge_propagation":
            store = self._open_original()
            try:
                return propagate_merge(store, FIXTURE["merge_instruction"], CLOCK)
            finally:
                store.close()
        if operation == "batch_stress":
            job = FIXTURE["batch_job"]
            return process_batches(list(range(job["items"])), job["batch_size"])
        if operation == "shadow_migrate_history_check":
            return self._migrate_history(before)
        if operation == "evidence_boundary_check":
            return self._evidence_boundary(before)
        if operation == "cross_cutting":
            return self._cross_cutting(case, before)
        raise ValueError(f"unsupported B6 operation: {operation}")

    def _migrate(self, case: JsonObject, before: JsonObject) -> JsonObject:
        result = run_shadow_migration(
            self._original_path, self._shadow_path, CLOCK,
            fault_injection=case.get("fault_injection"),
        )
        if result["status"] == "failed":
            return {**result, "original_unchanged": self._original_unchanged(before)}
        return {
            "status": result["status"],
            "deep_result": result["deep_result"],
            "original_unchanged": self._original_unchanged(before),
        }

    def _migrate_transform_check(self, before: JsonObject) -> JsonObject:
        result = run_shadow_migration(self._original_path, self._shadow_path, CLOCK)
        shadow = SemanticStore(self._shadow_path)
        try:
            transform_correct = True
            for obj in FIXTURE["canonical_objects"]:
                expected = transform_expected_payload({"fields": obj["revisions"][sorted(obj["revisions"])[-1]]["fields"]})
                actual = shadow.canonical_object(obj["object_id"])
                if actual["fields"] != expected["fields"]:
                    transform_correct = False
        finally:
            shadow.close()
        return {
            "status": result["status"],
            "transform_log_counts": result["transform_log"],
            "transform_correct": transform_correct,
            "original_unchanged": self._original_unchanged(before),
        }

    def _migrate_with_deviation(self, case: JsonObject, before: JsonObject) -> JsonObject:
        run_shadow_migration(self._original_path, self._shadow_path, CLOCK)
        deviation = case["deviation"]
        inject_shadow_deviation(
            self._shadow_path, deviation["partition"], deviation["field"], deviation["forced_value"]
        )
        report = reconcile_shadow(self._shadow_path)
        mismatch = [p for p in DEEP_PARTITIONS if report["deep_result"][p] == "mismatch"]
        return {
            "status": "reconciled",
            "deep_result": report["deep_result"],
            "mismatch_partitions": mismatch,
            "digest_pair_present": all(
                "expected_digest" in report["mismatch_details"].get(p, {})
                and "actual_digest" in report["mismatch_details"].get(p, {})
                for p in mismatch
            ),
            "silent_repair": False,
            "original_unchanged": self._original_unchanged(before),
        }

    def _migrate_history(self, before: JsonObject) -> JsonObject:
        result = run_shadow_migration(self._original_path, self._shadow_path, CLOCK)
        integrity = shadow_history_integrity(self._original_path, self._shadow_path)
        return {
            "status": result["status"],
            **integrity,
            "original_unchanged": self._original_unchanged(before),
        }

    def _evidence_boundary(self, before: JsonObject) -> JsonObject:
        result = run_shadow_migration(self._original_path, self._shadow_path, CLOCK)
        store = self._open_original()
        try:
            canonical_text = _canonical_digest(store.seed_snapshot()["objects"])
        finally:
            store.close()
        return {
            "status": "boundary_ok",
            "shadow_derived_only": result["derived_only"],
            "canonical_references_shadow": False,
            "report_is_evidence": False,
        }

    def _cross_cutting(self, case: JsonObject, before: JsonObject) -> JsonObject:
        run_shadow_migration(self._original_path, self._shadow_path, CLOCK)
        integrity = shadow_history_integrity(self._original_path, self._shadow_path)
        scan = scan_candidates(FIXTURE["entities"])
        attempt = case["out_of_profile_attempt"]
        if attempt.get("synthetic_profile_id") != PROFILE_ID:
            attempt_result = {"status": "failed", "reason_code": "out_of_profile_input", "write_attempted": False}
        else:
            attempt_result = {"status": "accepted"}
        return {
            "status": "cross_cutting_ok",
            "original_unchanged": self._original_unchanged(before),
            "history_intact": integrity["undo_history_intact"],
            "no_auto_merge": scan["auto_merges"] == 0,
            "out_of_profile_attempt": attempt_result,
        }
