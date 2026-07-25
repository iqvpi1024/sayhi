"""C3 review reports and phase comparisons: deterministic Derived metrics over the Canonical layer."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
REVIEW_RECORD_TYPE = "review_report"
COMPARISON_RECORD_TYPE = "phase_comparison"
METRIC_SET_ID = "review_metrics_v1"
METRIC_KEYS = (
    "days_recorded",
    "episodes",
    "commitments_completed",
    "commitments_cancelled",
    "commitments_closed_on_time",
    "decisions_reviewed",
)
HYPOTHESIS_STATUSES = ("active", "challenged", "weakened", "retired")
WINDOW_LENGTHS = {"weekly": 7}


def _parse_day(value: str) -> date:
    return date.fromisoformat(value)


def _window_days(kind: str, start: str, end: str) -> int:
    return (_parse_day(end) - _parse_day(start)).days


def _validate_window(kind: str, start: str, end: str) -> str | None:
    """Returns a rejection reason, or None when the window is legal."""
    if kind not in ("weekly", "monthly", "yearly"):
        return "unknown review_kind"
    try:
        days = _window_days(kind, start, end)
    except ValueError:
        return "invalid window dates"
    if days <= 0:
        return "inverted or empty window"
    expected = WINDOW_LENGTHS.get(kind)
    if expected is not None and days != expected:
        return "window length mismatch"
    return None


def _objects_by_type(store: SemanticStore) -> dict[str, dict[str, JsonObject]]:
    grouped: dict[str, dict[str, JsonObject]] = {}
    for item in store.canonical_object_summaries():
        grouped.setdefault(item["payload"]["object_type"], {})[item["object_id"]] = item["payload"]
    return grouped


def _window_inputs(store: SemanticStore, start: str, end: str) -> JsonObject:
    """Collects the Canonical objects that feed the metrics for one window."""
    lo, hi = _parse_day(start), _parse_day(end)
    grouped = _objects_by_type(store)

    def in_window(value: str | None) -> bool:
        if value is None:
            return False
        try:
            day = _parse_day(value)
        except ValueError:
            return False
        return lo <= day < hi

    episodes = {oid: p for oid, p in grouped.get("episode", {}).items() if in_window(p.get("occurred_on"))}
    commitments = {
        oid: p
        for oid, p in grouped.get("commitment", {}).items()
        if in_window(p.get("completed_at")) or in_window(p.get("cancelled_at"))
    }
    decisions = {oid: p for oid, p in grouped.get("decision", {}).items() if in_window(p.get("reviewed_at"))}
    hypotheses = dict(grouped.get("hypothesis", {}))
    return {"episodes": episodes, "commitments": commitments, "decisions": decisions, "hypotheses": hypotheses}


def _window_input_digest(store: SemanticStore, start: str, end: str) -> str:
    return _canonical_digest(_window_inputs(store, start, end))


def _compute_metrics(inputs: JsonObject) -> JsonObject:
    episodes = inputs["episodes"]
    commitments = inputs["commitments"]
    decisions = inputs["decisions"]
    hypotheses = inputs["hypotheses"]
    days = {p["occurred_on"] for p in episodes.values()}
    completed = [p for p in commitments.values() if p.get("status") == "completed" and p.get("completed_at")]
    cancelled = [p for p in commitments.values() if p.get("status") == "cancelled" and p.get("cancelled_at")]
    on_time = [p for p in completed if p.get("due_at") and p["completed_at"] <= p["due_at"]]
    counts = {status: 0 for status in HYPOTHESIS_STATUSES}
    for payload in hypotheses.values():
        status = payload.get("status")
        if status in counts:
            counts[status] += 1
    return {
        "days_recorded": len(days),
        "episodes": len(episodes),
        "commitments_completed": len(completed),
        "commitments_cancelled": len(cancelled),
        "commitments_closed_on_time": len(on_time),
        "decisions_reviewed": len(decisions),
        "hypothesis_status_counts": counts,
    }


def _reports_for_window(store: SemanticStore, kind: str, start: str, end: str) -> list[JsonObject]:
    records = [
        r
        for r in store.ledger_records_of_type(REVIEW_RECORD_TYPE)
        if r["review_kind"] == kind and r["window_start"] == start and r["window_end"] == end
    ]
    return sorted(records, key=lambda r: r["view_revision"])


def generate_review(store: SemanticStore, kind: str, start: str, end: str, generated_at: str) -> JsonObject:
    """Appends a new ReviewReport version for the window; never writes the Canonical layer."""
    problem = _validate_window(kind, start, end)
    if problem is not None:
        return {"outcome": "rejected", "reason": problem}
    inputs = _window_inputs(store, start, end)
    existing = _reports_for_window(store, kind, start, end)
    view_revision = (existing[-1]["view_revision"] + 1) if existing else 1
    record_id = f"review:{kind}:{start}:{end}:v{view_revision}"
    payload: JsonObject = {
        "review_id": record_id,
        "review_kind": kind,
        "window_start": start,
        "window_end": end,
        "metric_set_id": METRIC_SET_ID,
        "metrics": _compute_metrics(inputs),
        "view_revision": view_revision,
        "source_digest": _canonical_digest(inputs),
        "generated_at": generated_at,
        "derived_only": True,
    }
    store.put_ledger_record(record_id, REVIEW_RECORD_TYPE, payload)
    return {"outcome": "generated", "report": payload}


def present_review(store: SemanticStore, kind: str, start: str, end: str) -> JsonObject:
    """Read-only view of the latest report version with freshness computed from window inputs."""
    existing = _reports_for_window(store, kind, start, end)
    if not existing:
        return {"outcome": "not_found"}
    latest = existing[-1]
    current_digest = _window_input_digest(store, start, end)
    return {
        "outcome": "presented",
        "report": latest,
        "freshness": "fresh" if current_digest == latest["source_digest"] else "stale",
        "version_chain": [r["view_revision"] for r in existing],
        "derived_only": True,
    }


def rebuild_review(store: SemanticStore, kind: str, start: str, end: str, generated_at: str) -> JsonObject:
    """Appends a new version for the window; prior versions stay untouched."""
    return generate_review(store, kind, start, end, generated_at)


def delete_review(store: SemanticStore, kind: str, start: str, end: str) -> JsonObject:
    """Deletes the latest report version for the window; Derived-only, no Canonical effect."""
    existing = _reports_for_window(store, kind, start, end)
    if not existing:
        return {"outcome": "not_found"}
    latest = existing[-1]
    store.delete_ledger_record(latest["review_id"])
    return {"outcome": "deleted", "review_id": latest["review_id"], "deleted_metrics": latest["metrics"]}


def compare_phases(
    store: SemanticStore,
    window_a: Mapping[str, str],
    window_b: Mapping[str, str],
    metric_set_id: str,
    generated_at: str,
) -> JsonObject:
    """Appends a PhaseComparison with per-metric signed deltas (window_b - window_a)."""
    if metric_set_id != METRIC_SET_ID:
        return {"outcome": "rejected", "reason": "metric set mismatch"}
    kind_a, kind_b = window_a.get("review_kind"), window_b.get("review_kind")
    start_a, end_a = window_a.get("window_start"), window_a.get("window_end")
    start_b, end_b = window_b.get("window_start"), window_b.get("window_end")
    if kind_a != kind_b:
        return {"outcome": "rejected", "reason": "review_kind mismatch"}
    for kind, start, end in ((kind_a, start_a, end_a), (kind_b, start_b, end_b)):
        if not isinstance(kind, str) or not isinstance(start, str) or not isinstance(end, str):
            return {"outcome": "rejected", "reason": "invalid window shape"}
        problem = _validate_window(kind, start, end)
        if problem is not None:
            return {"outcome": "rejected", "reason": problem}
    if _window_days(kind_a, start_a, end_a) != _window_days(kind_b, start_b, end_b):
        return {"outcome": "rejected", "reason": "window length mismatch"}
    metrics_a = _compute_metrics(_window_inputs(store, start_a, end_a))
    metrics_b = _compute_metrics(_window_inputs(store, start_b, end_b))
    deltas: JsonObject = {key: metrics_b[key] - metrics_a[key] for key in METRIC_KEYS}
    deltas["hypothesis_status_counts"] = {
        status: metrics_b["hypothesis_status_counts"][status] - metrics_a["hypothesis_status_counts"][status]
        for status in HYPOTHESIS_STATUSES
    }
    comparison_id = f"comparison:{kind_a}:{start_a}:{end_a}:vs:{start_b}:{end_b}"
    payload: JsonObject = {
        "comparison_id": comparison_id,
        "metric_set_id": metric_set_id,
        "window_a": {"review_kind": kind_a, "window_start": start_a, "window_end": end_a},
        "window_b": {"review_kind": kind_b, "window_start": start_b, "window_end": end_b},
        "deltas": deltas,
        "generated_at": generated_at,
        "derived_only": True,
    }
    store.put_ledger_record(comparison_id, COMPARISON_RECORD_TYPE, payload)
    return {"outcome": "generated", "comparison": payload}
