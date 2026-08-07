"""A4 query-time access policy evaluator (pure functions, zero persistence).

Implements SPEC-A4-ACCESS-POLICY-001: fail-closed evaluation of synthetic
access requests against fixed grants, compartment policies and S1 object
labels. PolicyDecision is request-time Derived: it is never persisted and
never becomes evidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


JsonObject = dict[str, Any]

POLICY_REVISION = "a4_policy_v1"

REASON_CODES = frozenset(
    {
        "none",
        "grant_expired",
        "grant_scope_mismatch",
        "unknown_caller",
        "unknown_purpose",
        "unknown_compartment",
        "policy_missing",
        "policy_conflict",
        "sealed_excluded",
        "field_denied",
    }
)

_SEALED_ACTIONS = frozenset({"read", "search", "summarize"})


def _parse_instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _try_parse_instant(value: Any) -> datetime | None:
    """畸形/缺失时间输入返回 None,由调用方 fail-closed 为 deny。"""
    if not isinstance(value, str):
        return None
    try:
        return _parse_instant(value)
    except ValueError:
        return None


def build_policy_context(
    *,
    callers: list[Mapping[str, Any]],
    known_purposes: list[str],
    known_compartments: list[str],
    compartment_policies: list[Mapping[str, Any]],
    grants: list[Mapping[str, Any]],
    object_labels: Mapping[str, Mapping[str, Any]],
) -> JsonObject:
    """Build an immutable-by-convention evaluation context from plain data."""
    policies: dict[str, JsonObject] = {}
    for policy in compartment_policies:
        policies[policy["compartment"]] = {
            "allow_fields": list(policy.get("allow_fields", [])),
            "deny_fields": list(policy.get("deny_fields", [])),
            "unresolvable": bool(policy.get("unresolvable", False)),
        }
    return {
        "callers": {entry["caller_ref"]: entry.get("caller_kind", "unknown") for entry in callers},
        "known_purposes": list(known_purposes),
        "known_compartments": list(known_compartments),
        "compartment_policies": policies,
        "grants": {grant["grant_id"]: grant for grant in grants},
        "object_labels": dict(object_labels),
    }


def _deny(request: Mapping[str, Any], reason_code: str) -> JsonObject:
    return {
        "decision": "deny",
        "allowed_fields": [],
        "denied_fields": list(request.get("field_paths", [])),
        "reason_code": reason_code,
    }


def _grant_covers_resource(grant: Mapping[str, Any], resource: str) -> bool:
    return resource in grant.get("resource_refs", [])


def _grant_matches_scope(grant: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
    return (
        grant.get("caller_ref") == request.get("caller_ref")
        and grant.get("purpose") == request.get("purpose")
        and request.get("action") in grant.get("actions", [])
    )


def _grant_in_window(grant: Mapping[str, Any], requested_at: datetime) -> bool:
    # grant 时间窗畸形时视为不在窗内(fail-closed),由调用方记 grant_expired
    valid_from = _try_parse_instant(grant.get("valid_from"))
    valid_until = _try_parse_instant(grant.get("valid_until"))
    if valid_from is None or valid_until is None:
        return False
    return valid_from <= requested_at <= valid_until


def _evaluate_resource(request: Mapping[str, Any], context: Mapping[str, Any], resource: str) -> JsonObject:
    labels = context["object_labels"].get(resource)
    if labels is None:
        return _deny(request, "policy_missing")

    known_compartments = set(context["known_compartments"])
    compartments = list(labels.get("compartments", []))
    if any(compartment not in known_compartments for compartment in compartments):
        return _deny(request, "unknown_compartment")

    if labels.get("sensitivity") == "sealed" and request.get("action") in _SEALED_ACTIONS:
        return _deny(request, "sealed_excluded")

    policies = context["compartment_policies"]
    applicable = [policies.get(compartment) for compartment in compartments]
    if any(policy is None for policy in applicable):
        return _deny(request, "policy_missing")
    if any(policy["unresolvable"] for policy in applicable):
        return _deny(request, "policy_conflict")

    grants = context["grants"]
    cited = [grants[ref] for ref in request.get("authorization_refs", []) if ref in grants]
    covering = [grant for grant in cited if _grant_covers_resource(grant, resource)]
    if not covering:
        return _deny(request, "policy_missing")
    scoped = [grant for grant in covering if _grant_matches_scope(grant, request)]
    if not scoped:
        return _deny(request, "grant_scope_mismatch")
    requested_at = _try_parse_instant(request.get("requested_at"))
    if requested_at is None:
        # 请求时间缺失/畸形:无法验证任何 grant 时间窗,fail-closed 拒绝
        return _deny(request, "grant_expired")
    valid = [grant for grant in scoped if _grant_in_window(grant, requested_at)]
    if not valid:
        return _deny(request, "grant_expired")

    policy_allow = set(applicable[0]["allow_fields"])
    for policy in applicable[1:]:
        policy_allow &= set(policy["allow_fields"])
    policy_deny: set[str] = set()
    for policy in applicable:
        policy_deny |= set(policy["deny_fields"])

    grant_allow = set(valid[0].get("allowed_fields", []))
    for grant in valid[1:]:
        grant_allow &= set(grant.get("allowed_fields", []))
    grant_deny: set[str] = set()
    for grant in valid:
        grant_deny |= set(grant.get("denied_fields", []))

    effective_allow = policy_allow & grant_allow
    effective_deny = policy_deny | grant_deny

    allowed_fields: list[str] = []
    denied_fields: list[str] = []
    for field in request.get("field_paths", []):
        if field in effective_allow and field not in effective_deny:
            allowed_fields.append(field)
        else:
            denied_fields.append(field)

    if not denied_fields:
        return {"decision": "allow", "allowed_fields": allowed_fields, "denied_fields": [], "reason_code": "none"}
    if allowed_fields:
        return {
            "decision": "allow_with_redaction",
            "allowed_fields": allowed_fields,
            "denied_fields": denied_fields,
            "reason_code": "field_denied",
        }
    return {"decision": "deny", "allowed_fields": [], "denied_fields": denied_fields, "reason_code": "field_denied"}


def evaluate_request(request: Mapping[str, Any], context: Mapping[str, Any]) -> JsonObject:
    """Evaluate one synthetic access request; fail closed on every gap."""
    caller_kind = context["callers"].get(request.get("caller_ref"), "unknown")
    if caller_kind == "unknown":
        return _deny(request, "unknown_caller")
    if request.get("purpose") not in context["known_purposes"]:
        return _deny(request, "unknown_purpose")

    resources = list(request.get("resource_refs", []))
    if not resources:
        return _deny(request, "policy_missing")

    verdicts = [_evaluate_resource(request, context, resource) for resource in resources]
    for verdict in verdicts:
        if verdict["decision"] == "deny":
            return verdict
    allowed = set(verdicts[0]["allowed_fields"])
    for verdict in verdicts[1:]:
        allowed &= set(verdict["allowed_fields"])
    allowed_fields = [field for field in verdicts[0]["allowed_fields"] if field in allowed]
    denied_fields: list[str] = []
    for verdict in verdicts:
        for field in verdict["denied_fields"]:
            if field not in denied_fields:
                denied_fields.append(field)
    if not denied_fields:
        return {"decision": "allow", "allowed_fields": allowed_fields, "denied_fields": [], "reason_code": "none"}
    if allowed_fields:
        return {
            "decision": "allow_with_redaction",
            "allowed_fields": allowed_fields,
            "denied_fields": denied_fields,
            "reason_code": "field_denied",
        }
    return {"decision": "deny", "allowed_fields": [], "denied_fields": denied_fields, "reason_code": "field_denied"}


def evaluate_case_requests(requests: list[Mapping[str, Any]], context: Mapping[str, Any]) -> list[JsonObject]:
    """Evaluate every request in a fixture case, preserving request order."""
    return [evaluate_request(request, context) for request in requests]