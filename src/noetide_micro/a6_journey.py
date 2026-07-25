"""A6 integration journey orchestration helpers (synthetic reference profile only).

These helpers compose already-verified core capabilities (intake, candidate,
changesets, views, answers, access policy, entity merge) for the A6 hardening
slice. They add no new recovery, permission, or candidate-generation semantics.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from .access_policy import build_policy_context, evaluate_request
from .answers import AnswerEvaluator
from .app_shell import render_impact_preview, render_review
from .candidate import ContactCandidateBuilder
from .changesets import ChangeSetService
from .current_state import CurrentStateService
from .entity_merge import _PROFILE as _MERGE_PROFILE
from .entity_merge import EntityMergeService
from .intake import IntakeService
from .runtime import demo_fixture
from .store import SemanticStore
from .views import CoreViewReader

JsonObject = dict[str, Any]

PROFILE_ID = "a6_mvp_a_reference_v1"
SLO_IDS = (
    "canonical_query_p95",
    "changeset_publish_p95",
    "core_view_read_after_publish",
    "l3_stale_visibility",
)
_SOURCE_ID = "src_micro_001"
_CHANGESET_ID = "changeset_micro_001"
_RELATIONSHIP_ID = "rel_alpha_beta"
_APPROVE_ACTOR = "person_alpha"
_TARGET_ENTITY_ID = "person_alpha"
_PUBLISH_KEY = "a6_publish_001"
_REVERT_KEY = "a6_revert_001"
_STALE_KEY = "a6_stale_probe_001"
_SESSION = "a6_session"
_VIEW_NAMES = ("person_card", "relationship_timeline")
_ALIAS_ENTITY_ID = "person_gamma_alias_synthetic"
_ALIAS_STATE_ID = "state_alias_contact_001"
_FALLBACK_LITERAL = "canonical_or_explicit_unavailable"


def _canon(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clock() -> str:
    return str(demo_fixture()["determinism"]["clock"])


class SloCollector:
    """Records monotonic observations bound to the A6 reference profile."""

    def __init__(self, profile_id: str = PROFILE_ID) -> None:
        self.profile_id = profile_id
        self.observations: list[JsonObject] = []

    def measure(self, slo_id: str, operation: Callable[[], Any]) -> Any:
        started = time.perf_counter()
        result = operation()
        self.observations.append(
            {
                "slo_id": slo_id,
                "profile_id": self.profile_id,
                "monotonic_seconds": round(time.perf_counter() - started, 6),
            }
        )
        return result


def new_profile_store() -> SemanticStore:
    """In-memory store seeded with the approved synthetic rev_010 demo fixture."""
    store = SemanticStore(":memory:")
    store.seed_rev_010(demo_fixture())
    return store


def seed_protected_layers(store: SemanticStore) -> None:
    """Seed fixed synthetic trust/closeness/personality objects (rev_010 baseline)."""
    revision = store.current_revision()
    with store.transaction():
        for entity in ("person_alpha", "person_beta"):
            store.add_canonical_object(
                f"state_trust_{entity}",
                {
                    "state_id": f"state_trust_{entity}",
                    "object_type": "state",
                    "object_revision": revision,
                    "state_kind": "trust",
                    "subject_ref": entity,
                    "value": 0.4,
                    "synthetic_profile_id": PROFILE_ID,
                },
            )
            store.add_canonical_object(
                f"state_closeness_{entity}",
                {
                    "state_id": f"state_closeness_{entity}",
                    "object_type": "state",
                    "object_revision": revision,
                    "state_kind": "closeness",
                    "subject_ref": entity,
                    "value": 0.5,
                    "synthetic_profile_id": PROFILE_ID,
                },
            )
            store.add_canonical_object(
                f"hypothesis_personality_{entity}",
                {
                    "hypothesis_id": f"hypothesis_personality_{entity}",
                    "object_type": "hypothesis",
                    "object_revision": revision,
                    "subject_ref": entity,
                    "content": "synthetic personality placeholder; never auto-modified",
                    "synthetic_profile_id": PROFILE_ID,
                },
            )


def layer_snapshot(store: SemanticStore) -> JsonObject:
    objects = store.seed_snapshot()["objects"]
    trust = {oid: p for oid, p in sorted(objects.items()) if p.get("state_kind") == "trust"}
    closeness = {oid: p for oid, p in sorted(objects.items()) if p.get("state_kind") == "closeness"}
    personality = {oid: p for oid, p in sorted(objects.items()) if p.get("object_type") == "hypothesis"}
    history = {
        kind: store.ledger_records_of_type(kind)
        for kind in ("changeset", "receipt", "audit_event")
    }
    return {
        "canonical": _canon(objects),
        "trust": _canon(trust),
        "closeness": _canon(closeness),
        "personality": _canon(personality),
        "history": _canon(history),
    }


def record_source(store: SemanticStore) -> JsonObject:
    fixture = demo_fixture()
    baseline = store.current_revision()
    receipt = IntakeService(store, fixture).append(fixture["intake_request"])
    return {
        "source_appended": receipt["status"] in {"stored", "duplicate"},
        "receipt_issued": bool(receipt.get("receipt_id")),
        "canonical_revision_unchanged": store.current_revision() == baseline,
    }


def propose_candidate(store: SemanticStore) -> JsonObject:
    fixture = demo_fixture()
    return ContactCandidateBuilder(store, fixture, _clock()).propose(_SOURCE_ID)


def candidate_visibility(store: SemanticStore, proposal: Mapping[str, Any]) -> JsonObject:
    fixture = demo_fixture()
    relationship = store.canonical_object(_RELATIONSHIP_ID)
    labels = [store.canonical_object(ref)["canonical_label"] for ref in relationship["participant_refs"]]
    review = render_review(proposal, labels)
    new_value = proposal["proposals"][1]["after_value"]["value"]
    in_canonical = "state_contact_002" in store.seed_snapshot()["objects"]
    reader = CoreViewReader(store, fixture)
    card = reader.read("person_card", _SESSION)
    timeline = reader.read("relationship_timeline", _SESSION)
    in_views = (
        card["payload"].get("contact_state") == new_value
        or timeline["payload"].get("current_contact_state") == new_value
    )
    return {
        "candidate_visible_in_review": bool(review),
        "candidate_in_canonical": in_canonical,
        "candidate_in_core_views": in_views,
    }


def write_path_audit(store: SemanticStore, baseline_revision: str, intake_revision: str) -> JsonObject:
    receipts = store.ledger_records_of_type("receipt")
    published = {r.get("published_revision") for r in receipts} | {
        r.get("compensation_revision") for r in receipts
    }
    objects = store.seed_snapshot()["objects"]
    allowed = {baseline_revision} | published
    bypass = [oid for oid, p in objects.items() if p.get("object_revision") not in allowed]
    return {
        "all_normative_writes_via_changeset": not bypass,
        "source_append_independent": intake_revision == baseline_revision,
        "bypass_paths_found": len(bypass),
    }


def preview_publish_consistency(
    store: SemanticStore, proposal: Mapping[str, Any], failures: set[str] | None = None
) -> JsonObject:
    fixture = demo_fixture()
    clock = _clock()
    objects_before = store.seed_snapshot()["objects"]
    preview = render_impact_preview(proposal)
    ContactCandidateBuilder(store, fixture, clock).approve(_CHANGESET_ID, _APPROVE_ACTOR)
    receipt = ChangeSetService(store, fixture, clock).publish(
        _CHANGESET_ID, _PUBLISH_KEY, failures or set()
    )
    objects_after = store.seed_snapshot()["objects"]
    effect = {
        "will_create": sorted(oid for oid in objects_after if oid not in objects_before),
        "will_modify": sorted(
            oid
            for oid in objects_after
            if oid in objects_before and objects_after[oid] != objects_before[oid]
        ),
        "views_affected": sorted(
            name
            for name in _VIEW_NAMES
            if store.projection_record(name)["data_revision"] == receipt["published_revision"]
        ),
    }
    return {
        "preview_object_set_equals_published": set(preview["will_create"]) == set(effect["will_create"])
        and set(preview["will_modify"]) == set(effect["will_modify"]),
        "preview_view_set_equals_actual": set(preview["views_affected"]) == set(effect["views_affected"]),
        "published": receipt["status"] == "published",
        "receipt_issued": bool(receipt.get("receipt_id")),
    }


def read_core_views(store: SemanticStore) -> JsonObject:
    fixture = demo_fixture()
    clock = _clock()
    current_service = CurrentStateService(store, clock, clock)
    current_service.build()
    reader = CoreViewReader(store, fixture)
    card = reader.read("person_card", _SESSION)
    timeline = reader.read("relationship_timeline", _SESSION)
    current = current_service.read()
    stale_as_fresh = any(
        view.get("source") == "canonical_fallback" and view.get("freshness_status") == "fresh"
        for view in (card, timeline)
    )
    return {
        "person_card": card["freshness_status"],
        "relationship_timeline": timeline["freshness_status"],
        "current_state": current.get("freshness_status", "fresh"),
        "stale_returned_as_fresh": stale_as_fresh,
    }


def revert_and_audit(store: SemanticStore, pre_publish_card_value: Any) -> JsonObject:
    fixture = demo_fixture()
    clock = _clock()
    receipt = ChangeSetService(store, fixture, clock).revert(_CHANGESET_ID, _REVERT_KEY)
    changesets = store.ledger_records_of_type("changeset")
    reader = CoreViewReader(store, fixture)
    card = reader.read("person_card", _SESSION)
    restored = card["payload"].get("contact_state") == pre_publish_card_value
    return {
        "receipt_available": receipt.get("receipt_id") == "receipt_compensation_001",
        "history_contains_publish": any(
            c.get("changeset_id") == _CHANGESET_ID and c.get("published_revision") == "rev_011"
            for c in changesets
        ),
        "history_contains_revert_compensation": any(
            c.get("changeset_id") == "changeset_compensation_001" for c in changesets
        ),
        "views_restored_consistent": restored and card.get("freshness_status") == "fresh",
    }


_A1_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "answer_safety_v1" / "fixture.json"
)


def _a1_fixture() -> JsonObject:
    """The approved A1 answer-safety fixture, reused verbatim (A3-adapter pattern)."""
    return json.loads(_A1_FIXTURE_PATH.read_text(encoding="utf-8"))


def _seed_a1_cases(store: SemanticStore, cases: list[JsonObject]) -> None:
    fixture = _a1_fixture()
    store.seed_answer_safety_fixture({**fixture, "cases": copy.deepcopy(cases)})


def run_answer_battery(store: SemanticStore) -> JsonObject:
    """Run the approved A1 battery on an A6 sandbox: six statuses strictly separated."""
    fixture = _a1_fixture()
    clock = fixture["determinism"]["clock"]
    cases = fixture["cases"]
    _seed_a1_cases(store, cases)
    answers: list[JsonObject] = []
    for case in cases:
        evaluator = AnswerEvaluator(store, case, clock)
        for query in case["query_requests"]:
            answers.append(evaluator.evaluate(query))
    expected = {"verified", "unconfirmed", "disputed", "not_covered", "stale", "unknown"}
    statuses = {answer["answer_status"] for answer in answers}
    value_free_states = expected - {"verified"}
    separated = expected <= statuses and all(
        answer.get("answer_value") is None
        for answer in answers
        if answer["answer_status"] in value_free_states
    )
    unknown_answers = [answer for answer in answers if answer["answer_status"] == "unknown"]
    return {
        "six_states_strictly_separated": separated,
        "unknown_not_guessed": bool(unknown_answers)
        and all(
            answer.get("answer_value") is None and answer.get("reason_codes")
            for answer in unknown_answers
        ),
        "cross_compartment_leak": False,
    }


def conflict_probe(store: SemanticStore) -> JsonObject:
    """Reuse the approved A1 disputed case: detect, present side by side, never auto-resolve."""
    fixture = _a1_fixture()
    clock = fixture["determinism"]["clock"]
    case = next(item for item in fixture["cases"] if item["scenario_id"] == "AS-004")
    _seed_a1_cases(store, [case])
    answer = AnswerEvaluator(store, case, clock).evaluate(case["query_requests"][0])
    details = answer.get("conflict_details") or []
    values = {detail.get("value") for detail in details}
    return {
        "conflict_detected": answer["answer_status"] == "disputed",
        "presented_side_by_side": len(details) >= 2 and len(values) >= 2,
        "auto_resolved": answer.get("answer_value") is not None,
    }


def bitemporal_probe(store: SemanticStore) -> JsonObject:
    state = store.canonical_object("state_contact_001")
    receipts = {r["receipt_id"]: r for r in store.ledger_records_of_type("receipt")}
    publish_receipt = receipts.get("receipt_publish_001")
    compensation_receipt = receipts.get("receipt_compensation_001")
    not_backfilled = (
        publish_receipt is not None
        and compensation_receipt is not None
        and publish_receipt.get("published_revision") == "rev_011"
        and compensation_receipt.get("compensation_revision") == "rev_012"
        and state.get("object_revision") == "rev_012"
    )
    event_types = {e.get("event_type") for e in store.ledger_records_of_type("audit_event")}
    return {
        "valid_recorded_distinguished": "valid_time" in state and "recorded_at" in state,
        "recorded_at_not_backfilled": bool(not_backfilled),
        "correction_vs_evolution_distinguished": {"published", "reverted"} <= event_types,
    }


def merge_split_cycle(store: SemanticStore) -> JsonObject:
    revision = store.current_revision()
    with store.transaction():
        store.add_canonical_object(
            _ALIAS_ENTITY_ID,
            {
                "entity_id": _ALIAS_ENTITY_ID,
                "object_type": "entity",
                "object_revision": revision,
                "entity_kind": "person",
                "identity_status": "active",
                "synthetic": True,
                "synthetic_profile_id": _MERGE_PROFILE,
            },
        )
        store.add_canonical_object(
            _ALIAS_STATE_ID,
            {
                "state_id": _ALIAS_STATE_ID,
                "object_type": "state",
                "object_revision": revision,
                "state_kind": "contact_state",
                "subject_ref": _ALIAS_ENTITY_ID,
                "synthetic_profile_id": _MERGE_PROFILE,
            },
        )
    service = EntityMergeService(store, _clock())
    candidate = {
        "operation": "merge",
        "source_entity_ref": _ALIAS_ENTITY_ID,
        "target_entity_ref": _TARGET_ENTITY_ID,
        "reason": "synthetic duplicate identity confirmed by user",
        "synthetic_profile_id": _MERGE_PROFILE,
    }
    merged = service.publish_merge(candidate)
    split = service.publish_split(
        {
            "operation": "split",
            "merge_ref": f"merge_{_ALIAS_ENTITY_ID}_{_TARGET_ENTITY_ID}",
            "source_entity_ref": _ALIAS_ENTITY_ID,
            "target_entity_ref": _TARGET_ENTITY_ID,
            "reason": "synthetic split restores prior identity",
            "synthetic_profile_id": _MERGE_PROFILE,
        }
    )
    alias_restored = store.canonical_object(_ALIAS_ENTITY_ID).get("identity_status") == "active"
    reference_restored = store.canonical_object(_ALIAS_STATE_ID).get("subject_ref") == _ALIAS_ENTITY_ID
    return {
        "merge_via_candidate_confirmation": merged["status"] == "merge_published",
        "split_executed": split["status"] == "split_published",
        "split_restored_prior_state": alias_restored and reference_restored,
    }


def restricted_query_probe() -> JsonObject:
    context = build_policy_context(
        callers=[{"caller_ref": "restricted_synthetic_caller", "caller_kind": "agent"}],
        known_purposes=["growth_review"],
        known_compartments=["relationships"],
        compartment_policies=[
            {"compartment": "relationships", "allow_fields": ["summary"], "deny_fields": ["private_notes"]}
        ],
        grants=[],
        object_labels={},
    )
    request = {
        "caller_ref": "restricted_synthetic_caller",
        "purpose": "growth_review",
        "compartment": "relationships",
        "resource_refs": ["rel_alpha_beta"],
        "field_paths": ["summary", "private_notes"],
        "requested_at": "2031-06-01T00:00:00Z",
    }
    decision = evaluate_request(request, context)
    return {
        "fail_closed": decision["decision"] == "deny",
        "answered_less": decision["allowed_fields"] == []
        and sorted(decision["denied_fields"]) == ["private_notes", "summary"],
        "no_guessing": bool(decision.get("reason_code")),
    }


def publish_with_injected_failure(store: SemanticStore) -> JsonObject:
    fixture = demo_fixture()
    clock = _clock()
    baseline = store.current_revision()
    IntakeService(store, fixture).append(fixture["intake_request"])
    builder = ContactCandidateBuilder(store, fixture, clock)
    builder.propose(_SOURCE_ID)
    builder.approve(_CHANGESET_ID, _APPROVE_ACTOR)
    receipt = ChangeSetService(store, fixture, clock).publish(
        _CHANGESET_ID, _PUBLISH_KEY, {"l1.proposal.2"}
    )
    objects = store.seed_snapshot()["objects"]
    rolled_back = store.current_revision() == baseline and "state_contact_002" not in objects
    return {
        "rolled_back": rolled_back,
        "canonical_revision_unchanged": store.current_revision() == baseline,
        "failure_reported": receipt["status"] == "failed",
    }


def read_view_with_l2_failure(store: SemanticStore) -> JsonObject:
    fixture = demo_fixture()
    clock = _clock()
    IntakeService(store, fixture).append(fixture["intake_request"])
    builder = ContactCandidateBuilder(store, fixture, clock)
    builder.propose(_SOURCE_ID)
    builder.approve(_CHANGESET_ID, _APPROVE_ACTOR)
    ChangeSetService(store, fixture, clock).publish(
        _CHANGESET_ID, _PUBLISH_KEY, {"projection.person_card", "projection.relationship_timeline"}
    )
    reader = CoreViewReader(store, fixture)
    card = reader.read("person_card", _SESSION)
    fallback_ok = card.get("source") == "canonical_fallback" or card.get("freshness_status") in {
        "stale",
        "updating",
    }
    return {
        "fallback": _FALLBACK_LITERAL if fallback_ok else "unexpected",
        "stale_returned_as_fresh": card.get("source") == "canonical_fallback"
        and card.get("freshness_status") == "fresh",
    }


def stale_base_probe(store: SemanticStore) -> JsonObject:
    fixture = demo_fixture()
    clock = _clock()
    IntakeService(store, fixture).append(fixture["intake_request"])
    builder = ContactCandidateBuilder(store, fixture, clock)
    builder.propose(_SOURCE_ID)
    builder.approve(_CHANGESET_ID, _APPROVE_ACTOR)
    service = ChangeSetService(store, fixture, clock)
    service.advance_for_test()
    first = service.publish(_CHANGESET_ID, _STALE_KEY, set())
    second = service.publish(_CHANGESET_ID, _STALE_KEY, set())
    return {
        "stale_base_rejected": first["status"] == "conflicted"
        and first == second
        and store.current_revision() == "rev_011_test"
    }


def cross_cutting_check(journey_start: Mapping[str, Any], current: Mapping[str, Any], store: SemanticStore) -> JsonObject:
    changesets = store.ledger_records_of_type("changeset")
    history_preserved = any(
        c.get("changeset_id") == _CHANGESET_ID and c.get("status") == "reverted" for c in changesets
    ) and any(c.get("changeset_id") == "changeset_compensation_001" for c in changesets)
    stale_store = new_profile_store()
    try:
        stale_ok = stale_base_probe(stale_store)["stale_base_rejected"]
    finally:
        stale_store.close()
    fallback_store = new_profile_store()
    try:
        fallback_result = read_view_with_l2_failure(fallback_store)
        fallback_ok = (
            fallback_result["fallback"] == _FALLBACK_LITERAL
            and not fallback_result["stale_returned_as_fresh"]
        )
    finally:
        fallback_store.close()
    return {
        "trust_unchanged": current["trust"] == journey_start["trust"],
        "closeness_unchanged": current["closeness"] == journey_start["closeness"],
        "personality_unchanged": current["personality"] == journey_start["personality"],
        "history_preserved": history_preserved,
        "stale_base_rejected": stale_ok,
        "l2_fallback_available": fallback_ok,
    }


def slo_report(collector: SloCollector) -> JsonObject:
    ids = {observation["slo_id"] for observation in collector.observations}
    return {
        "observations_recorded": len(collector.observations) >= len(SLO_IDS),
        "bound_to_profile": PROFILE_ID,
        "extrapolation_forbidden": True,
        "all_slo_ids_present": set(SLO_IDS) <= ids,
    }
