"""C4 scenario trio and action follow-ups: predicted scenarios with deterministic feasibility and confirmed-only writes."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .store import SemanticStore


JsonObject = dict[str, Any]
SELECTION_RECORD_TYPE = "scenario_selection"
FOLLOWUP_TRANSITION_RECORD_TYPE = "follow_up_transition"
SCENARIO_KINDS = ("baseline", "optimistic", "pessimistic")


def evaluate_feasibility(constraints: Mapping[str, Sequence[str]]) -> str:
    """Deterministic pure function over declared constraints (C4-INV-003)."""
    if constraints.get("hard_blockers"):
        return "infeasible"
    if constraints.get("soft_constraints"):
        return "constrained"
    return "feasible"


def _scenario_objects(store: SemanticStore) -> dict[str, JsonObject]:
    return {
        item["object_id"]: item["payload"]
        for item in store.canonical_object_summaries()
        if item["payload"].get("object_type") == "assertion" and item["payload"].get("scenario_kind") in SCENARIO_KINDS
    }


def _follow_up_objects(store: SemanticStore) -> dict[str, JsonObject]:
    return {
        item["object_id"]: item["payload"]
        for item in store.canonical_object_summaries()
        if item["payload"].get("object_type") == "commitment" and item["payload"].get("scenario_ref")
    }


def create_scenario_set(
    store: SemanticStore,
    decision_ref: str,
    specs: Mapping[str, Mapping[str, Any]],
    confirmed: bool,
    at: str,
) -> JsonObject:
    """Creates the baseline/optimistic/pessimistic trio as predicted assertions (confirmed-only)."""
    if not confirmed:
        return {"outcome": "rejected", "reason": "unconfirmed"}
    decision = store.canonical_object_or_none(decision_ref)
    if decision is None or decision.get("object_type") != "decision":
        return {"outcome": "rejected", "reason": "decision_ref not found"}
    created: dict[str, JsonObject] = {}
    for kind in SCENARIO_KINDS:
        spec = specs.get(kind)
        if spec is None:
            return {"outcome": "rejected", "reason": f"missing spec for {kind}"}
        scenario_id = f"SCN-{decision_ref}-{kind}"
        payload: JsonObject = {
            "object_type": "assertion",
            "object_revision": 1,
            "assertion_kind": "predicted",
            "scenario_kind": kind,
            "decision_ref": decision_ref,
            "assumptions": list(spec["assumptions"]),
            "projected_result": spec["projected_result"],
            "feasibility_constraints": {
                "hard_blockers": list(spec["hard_blockers"]),
                "soft_constraints": list(spec["soft_constraints"]),
            },
            "feasibility_status": evaluate_feasibility(spec),
            "created_at": at,
            "synthetic": True,
        }
        store.add_canonical_object(scenario_id, payload)
        created[kind] = payload
    return {"outcome": "applied", "scenarios": created}


def select_scenario(store: SemanticStore, scenario_id: str, confirmed: bool, at: str, confirmed_by: str = "user") -> JsonObject:
    """Appends a selection receipt; never modifies the scenario/decision (C4-INV-005)."""
    if not confirmed:
        return {"outcome": "rejected", "reason": "unconfirmed"}
    scenario = store.canonical_object_or_none(scenario_id)
    if scenario is None or scenario.get("assertion_kind") != "predicted" or scenario.get("scenario_kind") not in SCENARIO_KINDS:
        return {"outcome": "rejected", "reason": "scenario not found"}
    record_id = f"selection:{scenario_id}"
    store.put_ledger_record(record_id, SELECTION_RECORD_TYPE, {
        "record_id": record_id,
        "scenario_id": scenario_id,
        "decision_ref": scenario["decision_ref"],
        "confirmed_by": confirmed_by,
        "at": at,
    })
    return {"outcome": "applied", "scenario_id": scenario_id}


def _selected(store: SemanticStore, scenario_id: str) -> bool:
    return any(r["scenario_id"] == scenario_id for r in store.ledger_records_of_type(SELECTION_RECORD_TYPE))


def create_follow_ups(
    store: SemanticStore,
    scenario_id: str,
    actions: Sequence[Mapping[str, str]],
    confirmed: bool,
    at: str,
) -> JsonObject:
    """Creates follow-up commitment objects for a selected scenario (confirmed-only)."""
    if not confirmed:
        return {"outcome": "rejected", "reason": "unconfirmed"}
    scenario = store.canonical_object_or_none(scenario_id)
    if scenario is None or scenario.get("scenario_kind") not in SCENARIO_KINDS:
        return {"outcome": "rejected", "reason": "scenario not found"}
    if not _selected(store, scenario_id):
        return {"outcome": "rejected", "reason": "scenario not selected"}
    created: list[JsonObject] = []
    for action in actions:
        payload: JsonObject = {
            "object_type": "commitment",
            "object_revision": 1,
            "follow_up_id": action["follow_up_id"],
            "scenario_ref": scenario_id,
            "decision_ref": scenario["decision_ref"],
            "title": action["title"],
            "due_date": action["due_date"],
            "status": "open",
            "revision_history": [],
            "created_at": at,
            "synthetic": True,
        }
        store.add_canonical_object(action["follow_up_id"], payload)
        created.append(payload)
    return {"outcome": "applied", "follow_ups": created}


def complete_follow_up(store: SemanticStore, follow_up_id: str, confirmed: bool, at: str) -> JsonObject:
    """Marks one follow-up done with a new revision and an append-only receipt (confirmed-only)."""
    if not confirmed:
        return {"outcome": "rejected", "reason": "unconfirmed"}
    payload = store.canonical_object_or_none(follow_up_id)
    if payload is None or payload.get("object_type") != "commitment" or not payload.get("scenario_ref"):
        return {"outcome": "rejected", "reason": "follow_up not found"}
    if payload["status"] != "open":
        return {"outcome": "rejected", "reason": "follow_up not open"}
    updated = dict(payload)
    updated["revision_history"] = list(payload["revision_history"]) + [
        {"status": payload["status"], "object_revision": payload["object_revision"], "at": at}
    ]
    updated["status"] = "done"
    updated["object_revision"] = payload["object_revision"] + 1
    updated["completed_at"] = at
    store.replace_canonical_object(follow_up_id, updated)
    record_id = f"followup-transition:{follow_up_id}:r{updated['object_revision']}"
    store.put_ledger_record(record_id, FOLLOWUP_TRANSITION_RECORD_TYPE, {
        "record_id": record_id,
        "follow_up_id": follow_up_id,
        "from_status": "open",
        "to_status": "done",
        "at": at,
    })
    return {"outcome": "applied", "follow_up": updated}


def follow_up_view(store: SemanticStore, scenario_id: str, clock_date: str) -> JsonObject:
    """Derived deterministic view: done stays done; open past due_date is missed (C4-INV-006). Zero writes."""
    items = []
    for follow_up_id, payload in sorted(_follow_up_objects(store).items()):
        if payload["scenario_ref"] != scenario_id:
            continue
        if payload["status"] == "done":
            view_status = "done"
        elif payload["due_date"] < clock_date:
            view_status = "missed"
        else:
            view_status = "open"
        items.append({
            "follow_up_id": follow_up_id,
            "title": payload["title"],
            "due_date": payload["due_date"],
            "view_status": view_status,
        })
    return {"outcome": "presented", "scenario_id": scenario_id, "items": items, "derived_only": True}


def present_scenario(store: SemanticStore, scenario_id: str) -> JsonObject:
    """Derived presentation: never a fact, never professional advice (C4-INV-001/004)."""
    payload = store.canonical_object_or_none(scenario_id)
    if payload is None or payload.get("scenario_kind") not in SCENARIO_KINDS:
        return {"outcome": "not_found"}
    return {
        "outcome": "presented",
        "scenario_id": scenario_id,
        "scenario_kind": payload["scenario_kind"],
        "feasibility_status": payload["feasibility_status"],
        "assertion_kind": payload["assertion_kind"],
        "is_fact": False,
        "not_professional_advice": True,
        "derived_only": True,
    }


def attempt_mark_observed(store: SemanticStore, scenario_id: str) -> JsonObject:
    """Scenarios never become observed facts; always rejected with zero writes (C4-INV-001)."""
    return {"outcome": "rejected", "reason": "scenarios remain predicted"}
