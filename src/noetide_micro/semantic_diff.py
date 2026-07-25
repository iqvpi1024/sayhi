"""B4 Semantic Diff: query-time derived field-level diff; never persisted, never evidence."""

from __future__ import annotations

from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
SNAPSHOT_RECORD_TYPE = "revision_snapshot"


def compute_diff(
    store: SemanticStore, object_ref: str, base_revision: str, target_revision: str
) -> JsonObject:
    """Derive a field-level SemanticDiff between two revision snapshots.

    The result exists only in caller memory: nothing is written, cached or
    recorded, so a diff can never become Canonical evidence. A missing target
    snapshot (or unknown object) is rejected explicitly; an object that exists
    but has no snapshot at the base revision is reported as ``create``.
    """
    snapshots = {
        record["revision"]: record["fields"]
        for record in store.ledger_records_of_type(SNAPSHOT_RECORD_TYPE)
        if record.get("object_id") == object_ref
    }
    if target_revision not in snapshots:
        raise KeyError(f"no snapshot for {object_ref} at {target_revision}")
    if base_revision in snapshots:
        before: Mapping[str, Any] | None = snapshots[base_revision]
    elif snapshots:
        before = None  # object exists but was created after the base revision
    else:
        raise KeyError(f"unknown object {object_ref}")
    after = snapshots[target_revision]
    field_diffs = _field_diffs(before if before is not None else {}, after, prefix="")
    if before is None:
        change_type = "create"
    else:
        change_type = "modify" if field_diffs else "no_change"
    return {
        "diff_id": f"diff_{object_ref}_{base_revision}_{target_revision}",
        "object_ref": object_ref,
        "base_revision": base_revision,
        "target_revision": target_revision,
        "change_type": change_type,
        "field_diffs": field_diffs,
        "derived_only": True,
    }


def _field_diffs(
    before: Mapping[str, Any], after: Mapping[str, Any], prefix: str
) -> list[JsonObject]:
    diffs: list[JsonObject] = []
    for key in sorted(set(before) | set(after)):
        path = f"{prefix}{key}"
        in_before, in_after = key in before, key in after
        before_value = before.get(key)
        after_value = after.get(key)
        if in_before and in_after and before_value == after_value:
            continue
        if isinstance(before_value, dict) and isinstance(after_value, dict):
            diffs.extend(_field_diffs(before_value, after_value, prefix=f"{path}."))
            continue
        diffs.append(
            {
                "field_path": path,
                "before": before_value if in_before else None,
                "after": after_value if in_after else None,
            }
        )
    return diffs
