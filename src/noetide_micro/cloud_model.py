"""Y2-S4 cloud model capability: explicit opt-in, bounded grants, red-line fail closed.

This module adds a cloud backend to the Y2-S2 ModelCapability story without
relaxing the verified local-only slice. Cloud candidates stay Derived and
propose-only; the only ledger writes are cloud_audit records.
"""

from __future__ import annotations

import ast
import hashlib
import ipaddress
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping

from .model_capability import (
    EndpointRejectedError,
    ProfileRejectedError,
    RED_LINE_COMPARTMENTS,
    VersionRegistry,
    _candidate_id,
    _sha256,
    _validate_output,
    canonical_json,
)
from .store import SemanticStore


JsonObject = dict[str, Any]
SUPPORTED_PROFILE = "y2s4_cloud_model_v1"
CLOUD_BACKEND_KINDS = {"cloud_fixture", "cloud_http"}
ALLOWED_PURPOSES = {"summarize", "organize", "clarify"}
AUDIT_EVENT_TYPES = {
    "grant_created",
    "grant_revoked",
    "preview_built",
    "send_allowed",
    "send_denied",
    "send_failed",
    "send_succeeded",
}
REJECTED_REASONS = {
    "default_disabled",
    "red_line_denied",
    "purpose_mismatch",
    "scope_mismatch",
    "grant_expired",
    "grant_revoked",
    "preview_missing",
    "preview_mismatch",
    "invalid_output",
    "transport_failed",
}


def _is_loopback_host(host: str | None) -> bool:
    if host is None:
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _short_hash(value: str) -> str:
    return _sha256(value)[:16]


def _cloud_batch_id(
    backend_kind: str,
    model_id: str,
    model_version: str,
    prompt_version: str,
    purpose: str,
    actor: str,
    preview_id: str,
    source_ids: list[str],
    requested_at: str,
) -> str:
    material = {
        "backend_kind": backend_kind,
        "model_id": model_id,
        "model_version": model_version,
        "prompt_version": prompt_version,
        "purpose": purpose,
        "actor": actor,
        "preview_id": preview_id,
        "sources_seen": sorted(source_ids),
        "requested_at": requested_at,
    }
    return "cloud_batch_" + _short_hash(canonical_json(material))


class PreviewMissingError(KeyError):
    pass


class PreviewMismatchError(ValueError):
    pass


class CloudTransportError(RuntimeError):
    pass


class CloudFixtureBackend:
    """Deterministic cloud backend keyed by source content_hash; no I/O."""

    kind = "cloud_fixture"

    def __init__(self, responses: Mapping[str, Any]) -> None:
        self._responses = dict(responses)
        self.calls = 0

    def propose(self, source: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> str:
        self.calls += 1
        key = source.get("content_hash")
        if not isinstance(key, str) or key not in self._responses:
            raise KeyError(key)
        entry = self._responses[key]
        if entry.get("kind") == "valid":
            return json.dumps(entry["raw_json"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return entry["raw"]


class CloudHttpBackend:
    """Minimal stdlib cloud HTTP client; external https by default."""

    kind = "cloud_http"

    def __init__(self, endpoint: str, timeout: float = 2.0, allow_loopback: bool = False) -> None:
        parsed = urllib.parse.urlparse(endpoint)
        loopback_http = parsed.scheme == "http" and allow_loopback and _is_loopback_host(parsed.hostname)
        if parsed.scheme != "https" and not loopback_http:
            raise EndpointRejectedError("cloud_http endpoint must use https (or explicit loopback test override)")
        if parsed.path != "/v1/chat/completions":
            raise EndpointRejectedError("cloud_http endpoint path must be /v1/chat/completions")
        self.endpoint = endpoint
        self._timeout = timeout
        self.calls = 0

    def propose(self, source: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> str:
        self.calls += 1
        meta = dict(context or {})
        request_body = {
            "model": meta.get("model_id", "cloud-model"),
            "messages": [
                {"role": "system", "content": "You are a synthetic cloud candidate extractor. Return JSON only."},
                {"role": "user", "content": str(source.get("content", ""))},
            ],
            "temperature": 0,
            "max_tokens": 1024,
            "noetide_meta": {
                "actor": meta.get("actor"),
                "purpose": meta.get("purpose"),
                "grant_ref": meta.get("grant_ref"),
                "preview_id": meta.get("preview_id"),
                "model_version": meta.get("model_version"),
                "prompt_version": meta.get("prompt_version"),
                "requested_at": meta.get("requested_at"),
            },
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"]


class CloudGate:
    """Default-closed authorization, preview and audit gate for cloud model calls."""

    def __init__(self, store: SemanticStore, clock: str) -> None:
        self._store = store
        self._clock = clock
        self._grants: dict[str, JsonObject] = {}
        self._previews: dict[str, JsonObject] = {}
        self._next_audit_seq = 1

    def grants(self) -> list[JsonObject]:
        return [dict(item) for item in self._grants.values()]

    def previews(self) -> list[JsonObject]:
        return [dict(item) for item in self._previews.values()]

    def audit_records(self) -> list[JsonObject]:
        return self._store.ledger_records_of_type("cloud_audit")

    def _audit(self, event_type: str, payload: Mapping[str, Any]) -> JsonObject:
        if event_type not in AUDIT_EVENT_TYPES:
            raise ValueError(event_type)
        record_id = f"cloud_audit_{self._next_audit_seq:03d}"
        self._next_audit_seq += 1
        record = {
            "record_id": record_id,
            "event_type": event_type,
            "recorded_at": self._clock,
            **dict(payload),
        }
        self._store.put_ledger_record(record_id, "cloud_audit", record)
        return record

    def create_grant(self, grant: Mapping[str, Any]) -> JsonObject:
        grant = dict(grant)
        for field in ("grant_id", "actor", "purpose", "compartments", "source_scope", "expires_at"):
            if not grant.get(field):
                raise ValueError(f"cloud grant missing field: {field}")
        if grant["purpose"] not in ALLOWED_PURPOSES:
            raise ValueError(f"unsupported cloud purpose: {grant['purpose']}")
        if not isinstance(grant["compartments"], list) or not grant["compartments"]:
            raise ValueError("cloud grant compartments must be non-empty")
        scope = grant["source_scope"]
        if not isinstance(scope, dict) or not isinstance(scope.get("source_ids"), list) or not scope["source_ids"]:
            raise ValueError("cloud grant source scope must be non-empty")
        grant.setdefault("created_at", self._clock)
        grant.setdefault("policy_revision", "y2s4_cloud_policy_v1")
        grant.setdefault("revoked", False)
        self._grants[grant["grant_id"]] = grant
        self._audit(
            "grant_created",
            {
                "grant_ref": grant["grant_id"],
                "actor": grant["actor"],
                "purpose": grant["purpose"],
                "compartments": list(grant["compartments"]),
                "source_scope": {"source_ids": list(grant["source_scope"]["source_ids"])},
                "expires_at": grant["expires_at"],
            },
        )
        return dict(grant)

    def revoke_grant(self, grant_id: str, reason: str = "user_revoked") -> JsonObject:
        grant = self._grants.get(grant_id)
        if grant is None:
            raise KeyError(grant_id)
        grant["revoked"] = True
        self._audit(
            "grant_revoked",
            {"grant_ref": grant_id, "actor": grant["actor"], "purpose": grant["purpose"], "reason": reason},
        )
        return dict(grant)

    def build_preview(self, source_ids: list[str], purpose: str, actor: str, now: str | None = None) -> JsonObject:
        built_at = now or self._clock
        preview_id = "preview_y2s4_" + _short_hash(
            canonical_json(
                {"sources": sorted(source_ids), "purpose": purpose, "actor": actor, "built_at": built_at}
            )
        )
        data_scope: list[JsonObject] = []
        for source_id in source_ids:
            source = self._store.seeded_source(source_id)
            if source is None:
                raise KeyError(source_id)
            data_scope.append(
                {
                    "source_id": source["source_id"],
                    "content_hash": source["content_hash"],
                    "byte_length": source["byte_length"],
                    "compartments": list(source.get("compartments", [])),
                    "locator": source.get("locator", {}),
                    "raw_content_present": False,
                    "redacted": True,
                }
            )
        preview = {
            "preview_id": preview_id,
            "status": "preview_ready",
            "actor": actor,
            "purpose": purpose,
            "built_at": built_at,
            "data_scope": data_scope,
        }
        self._previews[preview_id] = preview
        self._audit(
            "preview_built",
            {
                "preview_id": preview_id,
                "actor": actor,
                "purpose": purpose,
                "source_ids": list(source_ids),
                "raw_content_present": False,
            },
        )
        return dict(preview)

    def get_preview(self, preview_id: str) -> JsonObject | None:
        preview = self._previews.get(preview_id)
        return dict(preview) if preview is not None else None

    def _reject_reason(
        self, source: Mapping[str, Any], purpose: str, actor: str, requested_at: str
    ) -> str:
        compartments = set(source.get("compartments", []))
        if compartments & RED_LINE_COMPARTMENTS:
            return "red_line_denied"
        source_id = source["source_id"]
        actor_matches = [grant for grant in self._grants.values() if grant["actor"] == actor]
        purpose_matches = [
            grant for grant in actor_matches
            if grant["purpose"] == purpose and source_id in grant["source_scope"]["source_ids"]
        ]
        for grant in purpose_matches:
            if grant["revoked"]:
                continue
            if grant["expires_at"] <= requested_at:
                continue
            if set(compartments).issubset(set(grant["compartments"])):
                return "allowed"
        if purpose_matches:
            if any(grant["revoked"] for grant in purpose_matches):
                return "grant_revoked"
            if any(not grant["revoked"] and grant["expires_at"] <= requested_at for grant in purpose_matches):
                return "grant_expired"
        if any(grant["purpose"] == purpose for grant in actor_matches):
            return "scope_mismatch"
        if actor_matches:
            return "purpose_mismatch"
        return "default_disabled"

    def evaluate_batch(
        self, source_ids: list[str], purpose: str, actor: str, requested_at: str
    ) -> tuple[list[str], list[str]]:
        grant_refs: list[str] = []
        reasons: list[str] = []
        for source_id in source_ids:
            source = self._store.seeded_source(source_id)
            if source is None:
                raise KeyError(source_id)
            reason = self._reject_reason(source, purpose, actor, requested_at)
            if reason == "allowed":
                grant_refs.append(self._matching_grant(source, purpose, actor, requested_at)["grant_id"])
                reasons.append("")
            else:
                grant_refs.append("")
                reasons.append(reason)
        return grant_refs, reasons

    def _matching_grant(self, source: Mapping[str, Any], purpose: str, actor: str, requested_at: str) -> JsonObject:
        for grant in self._grants.values():
            if grant["actor"] != actor or grant["purpose"] != purpose or grant["revoked"]:
                continue
            if source["source_id"] not in grant["source_scope"]["source_ids"]:
                continue
            if grant["expires_at"] <= requested_at:
                continue
            if set(source.get("compartments", [])).issubset(set(grant["compartments"])):
                return grant
        raise KeyError(source["source_id"])


class CloudModelCurator:
    """Orchestrates preview validation, grant evaluation, backend calls and audit."""

    def __init__(
        self,
        store: SemanticStore,
        gate: CloudGate,
        backend: Any,
        clock: str,
        model_id: str,
        model_version: str,
        prompt_version: str,
        profile: str = SUPPORTED_PROFILE,
        registry: VersionRegistry | None = None,
    ) -> None:
        if profile != SUPPORTED_PROFILE:
            raise ProfileRejectedError(profile)
        if backend.kind not in CLOUD_BACKEND_KINDS:
            raise EndpointRejectedError(f"backend kind not allowed in Y2-S4: {backend.kind}")
        self._store = store
        self._gate = gate
        self._backend = backend
        self._clock = clock
        self._model_id = model_id
        self._model_version = model_version
        self._prompt_version = prompt_version
        self._registry = registry if registry is not None else VersionRegistry(clock)
        if not self._registry.has(model_id, model_version, prompt_version):
            self._registry.register(model_id, model_version, prompt_version)
        self._candidates: dict[str, JsonObject] = {}

    @property
    def registry(self) -> VersionRegistry:
        return self._registry

    @property
    def gate(self) -> CloudGate:
        return self._gate

    @property
    def backend(self) -> Any:
        return self._backend

    def candidates(self) -> list[JsonObject]:
        return list(self._candidates.values())

    def propose(
        self,
        source_ids: list[str],
        purpose: str,
        actor: str,
        preview_id: str | None,
        requested_at: str | None = None,
    ) -> JsonObject:
        if purpose not in ALLOWED_PURPOSES:
            raise ValueError(f"unsupported cloud purpose: {purpose}")
        now = requested_at or self._clock
        preview = None if preview_id is None else self._gate.get_preview(preview_id)
        if preview is None:
            return self._rejected_batch(source_ids, purpose, actor, preview_id, now, ["preview_missing"] * len(source_ids))
        preview_source_ids = [item["source_id"] for item in preview["data_scope"]]
        if (
            preview["actor"] != actor
            or preview["purpose"] != purpose
            or set(preview_source_ids) != set(source_ids)
        ):
            return self._rejected_batch(source_ids, purpose, actor, preview_id, now, ["preview_mismatch"] * len(source_ids))
        grant_refs, reasons = self._gate.evaluate_batch(source_ids, purpose, actor, now)
        if any(reasons):
            return self._rejected_batch(source_ids, purpose, actor, preview_id, now, reasons)
        imported = set(source_ids)
        failed: list[JsonObject] = []
        collected: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
        for index, source_id in enumerate(source_ids):
            source = self._store.seeded_source(source_id)
            if source is None:
                raise KeyError(source_id)
            context = {
                "actor": actor,
                "purpose": purpose,
                "grant_ref": grant_refs[index],
                "preview_id": preview_id,
                "model_id": self._model_id,
                "model_version": self._model_version,
                "prompt_version": self._prompt_version,
                "requested_at": now,
            }
            self._gate._audit(
                "send_allowed",
                {
                    "actor": actor,
                    "purpose": purpose,
                    "grant_ref": grant_refs[index],
                    "preview_id": preview_id,
                    "source_ids": [source_id],
                    "model_id": self._model_id,
                    "model_version": self._model_version,
                    "prompt_version": self._prompt_version,
                },
            )
            try:
                raw = self._backend.propose(source, context)
            except Exception:
                failed.append({"source_id": source_id, "reason": "transport_failed"})
                self._gate._audit(
                    "send_failed",
                    {
                        "actor": actor,
                        "purpose": purpose,
                        "grant_ref": grant_refs[index],
                        "preview_id": preview_id,
                        "source_ids": [source_id],
                        "reason": "transport_failed",
                        "model_id": self._model_id,
                        "model_version": self._model_version,
                        "prompt_version": self._prompt_version,
                    },
                )
                continue
            items, invalid = _validate_output(raw, imported)
            if invalid is not None:
                failed.append({"source_id": source_id, "reason": "invalid_output"})
                self._gate._audit(
                    "send_failed",
                    {
                        "actor": actor,
                        "purpose": purpose,
                        "grant_ref": grant_refs[index],
                        "preview_id": preview_id,
                        "source_ids": [source_id],
                        "reason": "invalid_output",
                        "model_id": self._model_id,
                        "model_version": self._model_version,
                        "prompt_version": self._prompt_version,
                    },
                )
                continue
            for item in items:
                collected.append((item, context))
        if failed:
            return {
                "batch_id": _cloud_batch_id(
                    self._backend.kind, self._model_id, self._model_version, self._prompt_version,
                    purpose, actor, preview_id, source_ids, now,
                ),
                "status": "rejected",
                "backend_kind": self._backend.kind,
                "purpose": purpose,
                "preview_id": preview_id,
                "authorization_refs": [],
                "sources_seen": list(source_ids),
                "candidates_proposed": [],
                "rejected_outputs": failed,
                "requested_at": now,
                "proposed_at": self._clock,
            }
        candidates: list[JsonObject] = []
        for item, context in collected:
            candidate = self._build_candidate(item, context)
            self._candidates[candidate["candidate_id"]] = candidate
            candidates.append(candidate)
        self._gate._audit(
            "send_succeeded",
            {
                "actor": actor,
                "purpose": purpose,
                "grant_refs": list(grant_refs),
                "preview_id": preview_id,
                "source_ids": list(source_ids),
                "model_id": self._model_id,
                "model_version": self._model_version,
                "prompt_version": self._prompt_version,
            },
        )
        return {
            "batch_id": _cloud_batch_id(
                self._backend.kind, self._model_id, self._model_version, self._prompt_version,
                purpose, actor, preview_id, source_ids, now,
            ),
            "status": "accepted",
            "backend_kind": self._backend.kind,
            "purpose": purpose,
            "preview_id": preview_id,
            "authorization_refs": list(grant_refs),
            "sources_seen": list(source_ids),
            "candidates_proposed": candidates,
            "rejected_outputs": [],
            "requested_at": now,
            "proposed_at": self._clock,
        }

    def _rejected_batch(
        self,
        source_ids: list[str],
        purpose: str,
        actor: str,
        preview_id: str | None,
        now: str,
        reasons: list[str],
    ) -> JsonObject:
        for source_id, reason in zip(source_ids, reasons):
            self._gate._audit(
                "send_denied",
                {
                    "actor": actor,
                    "purpose": purpose,
                    "preview_id": preview_id,
                    "source_ids": [source_id],
                    "reason": reason,
                },
            )
        rejected_outputs = [
            {"source_id": source_id, "reason": reason}
            for source_id, reason in zip(source_ids, reasons)
        ]
        return {
            "batch_id": _cloud_batch_id(
                self._backend.kind, self._model_id, self._model_version, self._prompt_version,
                purpose, actor, preview_id or "preview_missing", source_ids, now,
            ),
            "status": "rejected",
            "backend_kind": self._backend.kind,
            "purpose": purpose,
            "preview_id": preview_id,
            "authorization_refs": [],
            "sources_seen": list(source_ids),
            "candidates_proposed": [],
            "rejected_outputs": rejected_outputs,
            "requested_at": now,
            "proposed_at": self._clock,
        }

    def _build_candidate(self, item: Mapping[str, Any], context: Mapping[str, Any]) -> JsonObject:
        provenance = {
            "model_id": context["model_id"],
            "model_version": context["model_version"],
            "prompt_version": context["prompt_version"],
            "backend_kind": self._backend.kind,
            "purpose": context["purpose"],
            "authorization_ref": context["grant_ref"],
            "preview_id": context["preview_id"],
            "requested_at": context["requested_at"],
            "proposed_at": self._clock,
        }
        return {
            "candidate_id": _candidate_id(item["candidate_kind"], item["payload"], item["evidence_refs"]),
            "candidate_kind": item["candidate_kind"],
            "payload": item["payload"],
            "evidence_refs": item["evidence_refs"],
            "review_status": "unconfirmed",
            "provenance": provenance,
        }


def static_stdlib_scan(module_path: Path | None = None) -> tuple[bool, list[str]]:
    """Return whether cloud_model.py only imports the standard library plus local package modules."""
    path = module_path or Path(__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    external: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                if name not in sys.stdlib_module_names:
                    external.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            name = node.module.split(".")[0]
            if name not in sys.stdlib_module_names:
                external.append(node.module)
    return (not external, sorted(set(external)))
