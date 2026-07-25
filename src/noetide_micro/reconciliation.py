"""B4 read-only reconciliation detector: findings are quarantined + reported, never repaired."""

from __future__ import annotations

from typing import Any

from .store import SemanticStore


JsonObject = dict[str, Any]
PROFILE_ID = "b4_reconciliation_v1"
INCREMENTAL_KINDS = ("failure_queue", "stale_view", "orphan_reference", "unconsumed_changeset")
UNCONSUMED_CHANGESET_STATUSES = ("proposed", "approved")


def run_reconciliation(store: SemanticStore, mode: str, clock: str) -> JsonObject:
    """Run a read-only reconciliation scan and return a ReconciliationReport.

    The detector only reads Canonical, L2 projections and the revision ledger.
    It never writes, repairs or rewrites projections; every finding is
    quarantined and reported with disposition ``quarantined_reported``.
    """
    if mode != "incremental":
        raise ValueError("B4-TASK-001 implements incremental reconciliation only")
    findings = _incremental_findings(store)
    return {
        "report_id": f"report_{mode}_{clock}",
        "profile_id": PROFILE_ID,
        "mode": mode,
        "generated_at": clock,
        "findings": findings,
        "deep_result": None,
        "summary": {
            "finding_count": len(findings),
            "quarantined": True,
            "auto_repair_attempted": False,
        },
    }


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
