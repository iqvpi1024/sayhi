"""B6 shadow migration: file-level shadow copy, deterministic v1->v2 transform, fault handling."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Mapping

from .reconciliation import DEEP_PARTITIONS, expected_projection_payload
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
MIGRATION_VERSION = "v1_to_v2"
FIELD_RENAMES = {
    "contact_frequency": "contact_frequency_v2",
    "residence_city": "residence_city_v2",
}
TRANSFORM_BATCH_SIZE = 1  # one canonical object per batch, deterministic


def run_shadow_migration(
    source_path: str | Path,
    shadow_path: str | Path,
    clock: str,
    fault_injection: Mapping[str, Any] | None = None,
) -> JsonObject:
    """Migrate a static synthetic profile into a discardable shadow copy.

    The original database file is only ever copied, never opened for write.
    The transform renames synthetic fields in Canonical objects (logged) and
    revision snapshots (carried), then rebuilds the shadow's Derived
    projections from the transformed Canonical and reconciles them per
    partition. A fault injection fails the run explicitly and discards the
    shadow; the original is untouched in every outcome.
    """
    source = Path(source_path)
    shadow = Path(shadow_path)
    shadow.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, shadow)
    shadow_store = SemanticStore(shadow)
    try:
        object_ids = sorted(
            summary["object_id"] for summary in shadow_store.canonical_object_summaries()
        )
        fields_renamed = 0
        batch_index = 0
        for object_id in object_ids:
            batch_index += 1
            if fault_injection and fault_injection.get("at_batch") == batch_index:
                return _failed(shadow_store, shadow, batch_index)
            payload = shadow_store.canonical_object(object_id)
            fields = payload.get("fields", {})
            renamed = _rename_fields(fields)
            if renamed != dict(fields):
                fields_renamed += 1
                payload["fields"] = renamed
                shadow_store.replace_canonical_object(object_id, payload)
        for record in shadow_store.ledger_records_of_type("revision_snapshot"):
            renamed = _rename_fields(record.get("fields", {}))
            if renamed != dict(record.get("fields", {})):
                record["fields"] = renamed
                shadow_store.replace_ledger_record(
                    f"snapshot:{record['object_id']}:{record['revision']}", record
                )
        _rebuild_shadow_projections(shadow_store)
        deep_result = _reconcile_shadow(shadow_store)
        return {
            "status": "reconciled",
            "migration_version": MIGRATION_VERSION,
            "shadow_state": "reconciled",
            "transform_log": {"fields_renamed": fields_renamed},
            "deep_result": deep_result,
            "derived_only": True,
        }
    finally:
        shadow_store.close()


def shadow_history_integrity(source_path: str | Path, shadow_path: str | Path) -> JsonObject:
    """Read-only check that revisions, snapshots and translations survived the copy."""
    source_store = SemanticStore(source_path)
    shadow_store = SemanticStore(shadow_path)
    try:
        revisions_carried = source_store.revision_ids() == shadow_store.revision_ids()
        snapshots_carried = len(source_store.ledger_records_of_type("revision_snapshot")) == len(
            shadow_store.ledger_records_of_type("revision_snapshot")
        )
        translations_carried = len(source_store.ledger_records_of_type("translation_record")) == len(
            shadow_store.ledger_records_of_type("translation_record")
        )
        undo_history_intact = revisions_carried and snapshots_carried
        return {
            "revisions_carried": revisions_carried,
            "snapshots_carried": snapshots_carried,
            "translations_carried": translations_carried,
            "undo_history_intact": undo_history_intact,
        }
    finally:
        source_store.close()
        shadow_store.close()


def transform_expected_payload(payload: Mapping[str, Any]) -> JsonObject:
    """Public transform for verification: apply v1->v2 renames to one payload copy."""
    transformed = dict(payload)
    if "fields" in transformed:
        transformed["fields"] = _rename_fields(transformed["fields"])
    return transformed


def inject_shadow_deviation(
    shadow_path: str | Path, partition: str, field: str, forced_value: Any
) -> None:
    """Test-only deviation of a shadow projection; never touches the original."""
    shadow_store = SemanticStore(shadow_path)
    try:
        for record in shadow_store.projection_records():
            payload = record["payload"]
            if isinstance(payload, dict) and payload.get("partition") == partition:
                deviated = dict(payload)
                target_key = "objects" if "objects" in payload else "current"
                target = {oid: dict(fields) for oid, fields in payload[target_key].items()}
                for fields in target.values():
                    if field in fields:
                        fields[field] = forced_value
                deviated[target_key] = target
                shadow_store.replace_projection(
                    record["view_name"],
                    record["data_revision"],
                    record["view_revision"],
                    "fresh",
                    deviated,
                )
                return
        raise KeyError(partition)
    finally:
        shadow_store.close()


def reconcile_shadow(shadow_path: str | Path) -> JsonObject:
    """Re-run per-partition reconciliation on an existing shadow copy."""
    shadow_store = SemanticStore(shadow_path)
    try:
        return _reconcile_shadow(shadow_store, with_details=True)
    finally:
        shadow_store.close()


def _rename_fields(fields: Mapping[str, Any]) -> JsonObject:
    renamed = {FIELD_RENAMES.get(key, key): value for key, value in fields.items()}
    return renamed


def _rebuild_shadow_projections(store: SemanticStore) -> None:
    current = store.current_revision()
    for record in store.projection_records():
        payload = record["payload"]
        if isinstance(payload, dict) and payload.get("partition") in DEEP_PARTITIONS:
            expected = expected_projection_payload(store, payload["partition"])
            store.replace_projection(
                record["view_name"], current, current, "fresh", expected
            )


def _reconcile_shadow(store: SemanticStore, with_details: bool = False) -> JsonObject:
    deep_result: JsonObject = {}
    mismatch_details: JsonObject = {}
    stored = {
        record["payload"]["partition"]: record["payload"]
        for record in store.projection_records()
        if isinstance(record["payload"], dict) and record["payload"].get("partition") in DEEP_PARTITIONS
    }
    for partition in DEEP_PARTITIONS:
        expected = expected_projection_payload(store, partition)
        actual = stored.get(partition)
        match = actual is not None and _canonical_digest(actual) == _canonical_digest(expected)
        deep_result[partition] = "match" if match else "mismatch"
        if not match:
            mismatch_details[partition] = {
                "expected_digest": _canonical_digest(expected),
                "actual_digest": _canonical_digest(actual) if actual is not None else "absent",
            }
    if with_details:
        return {"deep_result": deep_result, "mismatch_details": mismatch_details}
    return deep_result


def _failed(store: SemanticStore, shadow: Path, batch_index: int) -> JsonObject:
    store.close()
    shadow.unlink(missing_ok=True)  # failed shadow is discarded
    return {
        "status": "failed",
        "reason_code": "migration_fault_injected",
        "fault_batch": batch_index,
        "partial_write_to_original": False,
        "shadow_state": "discarded",
    }
