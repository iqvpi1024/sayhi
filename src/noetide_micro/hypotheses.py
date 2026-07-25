"""C2 hypothesis lifecycle: confirmed-only canonical writes, evidence lists, status transitions.

Contract: SPEC-C2-HYPOTHESIS-001. ADR: ADR-0014.
No automatic transitions exist in this module; every write requires confirmed=True.
"""

from __future__ import annotations

from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]

STATUSES = ("active", "challenged", "weakened", "retired")
DISPLAY_TONES = {"active": "exploratory", "challenged": "tentative", "weakened": "tentative", "retired": "archived"}
EVIDENCE_STANCES = ("supports", "contradicts", "contextual")
HYPOTHESIS_KINDS = ("pattern", "causal", "personality", "future")
TRANSITION_RECORD_TYPE = "hypothesis_transition"
DERIVED_SOURCE_PREFIX = "DERIVED:"


def _rejected(reason: str) -> JsonObject:
    return {"outcome": "rejected", "reason": reason, "writes": 0}


def _revision_id(hypothesis_id: str, object_revision: int) -> str:
    return f"rev_{hypothesis_id}_{object_revision:03d}"


def _receipt_id(hypothesis_id: str, sequence: int) -> str:
    return f"receipt_{hypothesis_id}_{sequence:04d}"


def _next_sequence(store: SemanticStore, hypothesis_id: str) -> int:
    records = store.ledger_records_of_type(TRANSITION_RECORD_TYPE)
    return sum(1 for record in records if record.get("hypothesis_id") == hypothesis_id) + 1


def _validate_evidence_ref(store: SemanticStore, hypothesis_id: str, ref: Mapping[str, Any]) -> str | None:
    source_id = str(ref.get("source_id", ""))
    if source_id.startswith(DERIVED_SOURCE_PREFIX):
        return "derived_view_is_not_evidence"
    if store.seeded_source(source_id) is None:
        return "evidence_source_missing"
    if ref.get("stance") not in EVIDENCE_STANCES:
        return "evidence_stance_unknown"
    if not ref.get("locator"):
        return "evidence_locator_missing"
    return None


def _evidence_rows(hypothesis_id: str, refs: list[JsonObject]) -> list[JsonObject]:
    return [
        {"source_id": ref["source_id"], "locator": ref["locator"], "stance": ref["stance"], "claim_ref": hypothesis_id}
        for ref in refs
    ]


def _write_receipt(store: SemanticStore, hypothesis_id: str, kind: str, payload: JsonObject, at: str, revision_id: str) -> None:
    sequence = _next_sequence(store, hypothesis_id)
    store.put_ledger_record(
        _receipt_id(hypothesis_id, sequence),
        TRANSITION_RECORD_TYPE,
        {"hypothesis_id": hypothesis_id, "kind": kind, "at": at, "confirmed_by": "synthetic_user", **payload},
        revision_id=revision_id,
    )


def create_hypothesis(
    store: SemanticStore,
    spec: Mapping[str, Any],
    evidence: list[Mapping[str, Any]],
    *,
    confirmed: bool,
    at: str,
) -> JsonObject:
    """Create a hypothesis as active with object_revision=1; confirmed ChangeSet only."""
    if not confirmed:
        return _rejected("confirmation_required")
    hypothesis_id = str(spec.get("hypothesis_id", ""))
    if not hypothesis_id:
        return _rejected("hypothesis_id_missing")
    if store.canonical_object_or_none(hypothesis_id) is not None:
        return _rejected("hypothesis_exists")
    if spec.get("hypothesis_kind") not in HYPOTHESIS_KINDS:
        return _rejected("hypothesis_kind_unknown")
    if not spec.get("statement") or not spec.get("valid_scope"):
        return _rejected("statement_or_scope_missing")
    refs = [dict(ref) for ref in evidence]
    for ref in refs:
        problem = _validate_evidence_ref(store, hypothesis_id, ref)
        if problem:
            return _rejected(problem)
    payload: JsonObject = {
        "object_type": "hypothesis",
        "object_revision": 1,
        "hypothesis_id": hypothesis_id,
        "statement": spec["statement"],
        "hypothesis_kind": spec["hypothesis_kind"],
        "valid_scope": spec["valid_scope"],
        "subject_ref": spec.get("subject_ref"),
        "status": "active",
        "evidence_for": [ref for ref in refs if ref["stance"] == "supports"],
        "evidence_against": [ref for ref in refs if ref["stance"] == "contradicts"],
        "evidence_contextual": [ref for ref in refs if ref["stance"] == "contextual"],
        "revision_history": [],
        "created_at": at,
    }
    revision_id = _revision_id(hypothesis_id, 1)
    with store.transaction():
        store.add_revision(revision_id, at)
        store.add_canonical_object(hypothesis_id, payload)
        store.replace_evidence_refs(hypothesis_id, _evidence_rows(hypothesis_id, refs))
        _write_receipt(store, hypothesis_id, "create", {"from_status": None, "to_status": "active", "object_revision": 1}, at, revision_id)
    return {"outcome": "applied", "hypothesis_id": hypothesis_id, "status": "active", "object_revision": 1}


def attach_evidence(
    store: SemanticStore,
    hypothesis_id: str,
    ref: Mapping[str, Any],
    *,
    confirmed: bool,
    at: str,
) -> JsonObject:
    """Attach one evidence ref; never changes status (no automatic transitions)."""
    if not confirmed:
        return _rejected("confirmation_required")
    payload = store.canonical_object_or_none(hypothesis_id)
    if payload is None or payload.get("object_type") != "hypothesis":
        return _rejected("hypothesis_missing")
    problem = _validate_evidence_ref(store, hypothesis_id, ref)
    if problem:
        return _rejected(problem)
    new_ref = {"source_id": ref["source_id"], "locator": ref["locator"], "stance": ref["stance"]}
    updated = dict(payload)
    old_revision = int(payload["object_revision"])
    new_revision = old_revision + 1
    history = list(payload.get("revision_history", []))
    history.append({"object_revision": old_revision, "status": payload["status"], "at": at, "change": "attach_evidence"})
    updated["revision_history"] = history
    updated["object_revision"] = new_revision
    key = {"supports": "evidence_for", "contradicts": "evidence_against", "contextual": "evidence_contextual"}[new_ref["stance"]]
    updated[key] = list(payload.get(key, [])) + [new_ref]
    all_refs = updated["evidence_for"] + updated["evidence_against"] + updated["evidence_contextual"]
    revision_id = _revision_id(hypothesis_id, new_revision)
    with store.transaction():
        store.add_revision(revision_id, at)
        store.replace_canonical_object(hypothesis_id, updated)
        store.replace_evidence_refs(hypothesis_id, _evidence_rows(hypothesis_id, all_refs))
        _write_receipt(store, hypothesis_id, "attach_evidence", {"stance": new_ref["stance"], "status": payload["status"], "object_revision": new_revision}, at, revision_id)
    return {"outcome": "applied", "hypothesis_id": hypothesis_id, "status": payload["status"], "object_revision": new_revision}


def transition_status(
    store: SemanticStore,
    hypothesis_id: str,
    to_status: str,
    reason: str,
    *,
    confirmed: bool,
    at: str,
) -> JsonObject:
    """User-confirmed status transition; append-only history, ledger receipt, no deletions."""
    if not confirmed:
        return _rejected("confirmation_required")
    payload = store.canonical_object_or_none(hypothesis_id)
    if payload is None or payload.get("object_type") != "hypothesis":
        return _rejected("hypothesis_missing")
    if to_status not in STATUSES:
        return _rejected("status_unknown")
    if not reason:
        return _rejected("reason_missing")
    updated = dict(payload)
    old_revision = int(payload["object_revision"])
    new_revision = old_revision + 1
    history = list(payload.get("revision_history", []))
    history.append({"object_revision": old_revision, "status": payload["status"], "at": at, "change": "transition", "to_status": to_status, "reason": reason})
    updated["revision_history"] = history
    updated["object_revision"] = new_revision
    updated["status"] = to_status
    revision_id = _revision_id(hypothesis_id, new_revision)
    with store.transaction():
        store.add_revision(revision_id, at)
        store.replace_canonical_object(hypothesis_id, updated)
        _write_receipt(store, hypothesis_id, "transition", {"from_status": payload["status"], "to_status": to_status, "reason": reason, "object_revision": new_revision}, at, revision_id)
    return {"outcome": "applied", "hypothesis_id": hypothesis_id, "status": to_status, "object_revision": new_revision}


def present_hypothesis(store: SemanticStore, hypothesis_id: str) -> JsonObject:
    """Derived presentation view; never a fact, never evidence."""
    payload = store.canonical_object_or_none(hypothesis_id)
    if payload is None or payload.get("object_type") != "hypothesis":
        return {"outcome": "rejected", "reason": "hypothesis_missing"}
    status = payload["status"]
    return {
        "hypothesis_id": hypothesis_id,
        "statement": payload["statement"],
        "status": status,
        "display_tone": DISPLAY_TONES[status],
        "is_fact": False,
        "derived_only": True,
        "evidence_for": len(payload.get("evidence_for", [])),
        "evidence_against": len(payload.get("evidence_against", [])),
    }


def attempt_upgrade_to_fact(store: SemanticStore, hypothesis_id: str) -> JsonObject:
    """Hypothesis never upgrades to Fact/Assertion; always rejected with zero writes."""
    return _rejected("hypothesis_cannot_upgrade_to_fact")
