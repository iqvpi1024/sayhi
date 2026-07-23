"""A5 app shell presentation layer: pure functions, read-only, never persisted.

Implements SPEC-A5-APP-SHELL-001 v0.2: natural-language review items and
impact previews derived from a proposed ChangeSet. Presentation output is
request-time Derived: it is never written to Canonical, Ledger or any
projection, and never becomes evidence.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping


JsonObject = dict[str, Any]

PRESENTATION_REVISION = "a5_shell_v1"

# Store write-method names the presentation layer must never call. The static
# scan asserts none of these appear as attribute calls in this module's source.
FORBIDDEN_WRITE_METHODS = frozenset(
    {
        "add_canonical_object",
        "replace_canonical_object",
        "delete_canonical_object",
        "replace_evidence_refs",
        "add_revision",
        "replace_projection",
        "upsert_projection",
        "mark_summary_projections_stale",
        "mark_current_state_stale",
        "mark_all_projections_stale",
        "delete_current_state_projection",
        "delete_summary_projections",
        "put_ledger_record",
        "replace_ledger_record",
        "append_source",
        "put_episode_record",
        "delete_episode_record",
        "put_summary_projection",
        "replace_summary_projection",
        "put_derived_rebuild_receipt",
        "put_commitment_record",
        "update_commitment_status",
        "put_due_status_projection",
        "replace_due_status_projection",
        "put_due_rebuild_receipt",
        "delete_due_status_projections",
        "put_a2_view_receipt",
        "put_merge_record",
        "put_split_record",
        "seed_rev_010",
        "seed_answer_safety_fixture",
    }
)

_WRITE_CALL = re.compile(r"\.([a-z_][a-z0-9_]*)\s*\(")


def render_review(changeset: Mapping[str, Any], participant_labels: list[str]) -> JsonObject:
    """Render one natural-language review item from a proposed ChangeSet."""
    proposals = changeset["proposals"]
    added = next(p for p in proposals if p["operation"] == "add")
    ended = next(p for p in proposals if p["operation"] == "end")
    old_value = ended["after_value"]["value"]
    new_value = added["after_value"]["value"]
    start = added["after_value"]["valid_time"]["start"]["value"]
    if len(participant_labels) != 2:
        raise ValueError("A5 review rendering requires exactly two participant labels")
    summary = (
        f"识灵建议：{participant_labels[0]} 与 {participant_labels[1]} 的联系状态从 "
        f"{old_value} 改为 {new_value}，自 {start} 起生效。"
    )
    citations = [trigger["source_id"] for trigger in changeset.get("trigger_sources", [])]
    return {
        "candidate_ref": changeset["changeset_id"],
        "summary_text": summary,
        "evidence_citations": citations,
        "presentation_revision": PRESENTATION_REVISION,
    }


def render_impact_preview(changeset: Mapping[str, Any]) -> JsonObject:
    """Render the impact preview (object sets + view sets) for a ChangeSet."""
    proposals = changeset["proposals"]
    will_create = [p["target_ref"]["object_id"] for p in proposals if p["operation"] == "add"]
    will_modify = [p["target_ref"]["object_id"] for p in proposals if p["operation"] in ("end", "correct", "update")]
    views_affected = list(changeset["impact_set"]["derived_views"])
    impact_text = (
        f"确认后将新增 {len(will_create)} 条联系状态记录并结束 {len(will_modify)} 条历史记录；"
        f"受影响视图：{'、'.join(views_affected)}。"
    )
    return {
        "will_create": will_create,
        "will_modify": will_modify,
        "views_affected": views_affected,
        "impact_text": impact_text,
        "presentation_revision": PRESENTATION_REVISION,
    }


def shell_write_scan(module_path: str | Path | None = None) -> tuple[list[str], list[str]]:
    """Static zero-bypass scan of the presentation layer source.

    Returns (allowed_calls, forbidden_calls): attribute-call names found in
    this module that are presentation helpers vs forbidden store writes.
    """
    path = Path(module_path) if module_path else Path(__file__).resolve()
    source = path.read_text(encoding="utf-8")
    called = sorted(set(_WRITE_CALL.findall(source)))
    forbidden = [name for name in called if name in FORBIDDEN_WRITE_METHODS]
    allowed = [name for name in called if name not in FORBIDDEN_WRITE_METHODS]
    return allowed, forbidden