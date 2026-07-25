"""B4 read-only reconciliation detector: findings are quarantined + reported, never repaired."""

from __future__ import annotations

from typing import Any

from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
PROFILE_ID = "b4_reconciliation_v1"
DEEP_PARTITIONS = ("person_card", "relationship_timeline", "current_state")
INCREMENTAL_KINDS = ("failure_queue", "stale_view", "orphan_reference", "unconsumed_changeset")
UNCONSUMED_CHANGESET_STATUSES = ("proposed", "approved")


def run_reconciliation(store: SemanticStore, mode: str, clock: str) -> JsonObject:
    """Run a read-only reconciliation scan and return a ReconciliationReport.

    Run state machine: ``requested -> scanning -> report_issued``. The detector
    only reads Canonical, L2 projections and the revision ledger. It never
    writes, repairs or rewrites projections; every finding is quarantined and
    reported with disposition ``quarantined_reported``. A failed scan returns an
    explicit unavailable report shell instead of an empty "no findings" report.
    """
    if mode not in ("incremental", "deep"):
        raise ValueError(f"unsupported reconciliation mode: {mode}")
    try:
        if mode == "incremental":
            findings = _incremental_findings(store)
            deep_result: JsonObject | None = None
            mismatch_details: JsonObject = {}
        else:
            findings = []
            deep_result, mismatch_details = _deep_compare(store)
    except Exception as exc:  # unavailable shell, never a silent empty report
        return {
            "report_id": f"report_{mode}_{clock}",
            "profile_id": PROFILE_ID,
            "mode": mode,
            "generated_at": clock,
            "run_state": "unavailable",
            "unavailable_reason": f"{type(exc).__name__}: {exc}",
            "findings": [],
            "deep_result": None,
            "mismatch_details": {},
            "summary": {"finding_count": 0, "quarantined": True, "auto_repair_attempted": False},
        }
    return {
        "report_id": f"report_{mode}_{clock}",
        "profile_id": PROFILE_ID,
        "mode": mode,
        "generated_at": clock,
        "run_state": "report_issued",
        "findings": findings,
        "deep_result": deep_result,
        "mismatch_details": mismatch_details,
        "summary": {
            "finding_count": len(findings),
            "quarantined": True,
            "auto_repair_attempted": False,
        },
    }


def expected_projection_payload(store: SemanticStore, partition: str) -> JsonObject:
    """Derive the expected Derived projection payload for one deep partition.

    Deterministic and Canonical-only: the same derivation seeds the synthetic
    profile projections and rebuilds expectations during deep reconciliation,
    so a stored projection matches exactly when nothing deviated.
    """
    if partition not in DEEP_PARTITIONS:
        raise ValueError(f"unknown deep partition: {partition}")
    snapshot = store.seed_snapshot()
    objects = snapshot["objects"]
    current = snapshot["data_revision"]
    fields_at_current = {
        object_id: payload.get("fields", {})
        for object_id, payload in sorted(objects.items())
    }
    if partition == "person_card":
        return {"partition": partition, "data_revision": current, "objects": fields_at_current}
    if partition == "current_state":
        return {"partition": partition, "data_revision": current, "current": fields_at_current}
    history = [
        {
            "object_id": record["object_id"],
            "revision": record["revision"],
            "fields": record["fields"],
        }
        for record in store.ledger_records_of_type("revision_snapshot")
    ]
    history.sort(key=lambda item: (item["object_id"], item["revision"]))
    return {"partition": partition, "data_revision": current, "history": history}


def _deep_compare(store: SemanticStore) -> tuple[JsonObject, JsonObject]:
    """Rebuild each partition from Canonical and compare digests; never rewrite."""
    stored_by_partition: dict[str, JsonObject] = {}
    for record in store.projection_records():
        payload = record["payload"]
        if isinstance(payload, dict) and payload.get("partition") in DEEP_PARTITIONS:
            stored_by_partition[payload["partition"]] = payload
    deep_result: JsonObject = {}
    mismatch_details: JsonObject = {}
    for partition in DEEP_PARTITIONS:
        expected = expected_projection_payload(store, partition)
        actual = stored_by_partition.get(partition)
        expected_digest = _canonical_digest(expected)
        actual_digest = _canonical_digest(actual) if actual is not None else "absent"
        if actual is not None and actual_digest == expected_digest:
            deep_result[partition] = "match"
        else:
            deep_result[partition] = "mismatch"
            mismatch_details[partition] = {
                "expected_digest": expected_digest,
                "actual_digest": actual_digest,
            }
    return deep_result, mismatch_details


def revision_consistency(store: SemanticStore) -> bool:
    """Read-only L1/L2 revision consistency check used after controlled writes."""
    current = store.current_revision()
    for record in store.projection_records():
        if record["freshness_status"] != "fresh":
            return False
        if record["view_revision"] != current or record["data_revision"] != current:
            return False
    return True


def _incremental_findings(store: SemanticStore) -> list[JsonObject]:
    findings: list[JsonObject] = []
    findings.extend(_failure_queue_findings(store))
    findings.extend(_stale_view_findings(store))
    findings.extend(_orphan_reference_findings(store))
    findings.extend(_unconsumed_changeset_findings(store))
    return findings


def _failure_queue_findings(store: SemanticStore) -> list[JsonObject]:
    receipts: list[JsonObject] = []
    receipts.extend(store.a2_view_receipts())
    receipts.extend(store.derived_rebuild_receipts())
    receipts.extend(store.due_rebuild_receipts())
    return [
        _finding("failure_queue", receipt["receipt_id"], "projection rebuild recorded as failed")
        for receipt in receipts
        if receipt["status"] == "failed"
    ]


def _stale_view_findings(store: SemanticStore) -> list[JsonObject]:
    current = store.current_revision()
    findings: list[JsonObject] = []
    for record in store.projection_records():
        if record["view_revision"] != current or record["freshness_status"] != "fresh":
            findings.append(
                _finding(
                    "stale_view",
                    record["view_name"],
                    f"view_revision={record['view_revision']} freshness={record['freshness_status']} current={current}",
                )
            )
    return findings


def _orphan_reference_findings(store: SemanticStore) -> list[JsonObject]:
    known = {summary["object_id"] for summary in store.canonical_object_summaries()}
    findings: list[JsonObject] = []
    for record in store.projection_records():
        payload = record["payload"]
        if not isinstance(payload, dict):
            continue
        referenced = payload.get("referenced_object_id")
        if isinstance(referenced, str) and referenced not in known:
            derived_id = payload.get("derived_id")
            subject = derived_id if isinstance(derived_id, str) and derived_id else record["view_name"]
            findings.append(
                _finding("orphan_reference", subject, f"referenced object {referenced} is absent from Canonical")
            )
    return findings


def _unconsumed_changeset_findings(store: SemanticStore) -> list[JsonObject]:
    findings: list[JsonObject] = []
    for payload in store.ledger_records_of_type("changeset"):
        if payload.get("status") in UNCONSUMED_CHANGESET_STATUSES:
            changeset_id = payload.get("changeset_id", "unknown_changeset")
            findings.append(
                _finding("unconsumed_changeset", changeset_id, f"changeset status {payload.get('status')} was never published")
            )
    return findings


def _finding(kind: str, subject_ref: str, detail: str) -> JsonObject:
    return {
        "finding_id": f"finding_{kind}_{subject_ref}",
        "kind": kind,
        "subject_ref": subject_ref,
        "detail": detail,
        "disposition": "quarantined_reported",
    }
