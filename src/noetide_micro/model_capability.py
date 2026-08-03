"""Y2-S2 model capability: propose-only local model curation.

The slice intentionally stays in the Derived layer: candidates never enter
Canonical, user confirmation only creates a proposed ChangeSet ledger record,
and the only network allowed is loopback HTTP via the local backend.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import urllib.parse
import urllib.request
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
CANDIDATE_KINDS = {"entity", "episode", "commitment", "assertion"}
RED_LINE_COMPARTMENTS = {"health", "finance", "relationship", "sealed"}
LOCAL_BACKEND_KINDS = {"fixture", "local_http"}
ESCALATION_FIELDS = {"review_status", "confirmed", "auto_publish", "publish"}
SUPPORTED_PROFILE = "y2s2_local_model_v1"


class ProfileRejectedError(ValueError):
    def __init__(self, profile: str) -> None:
        super().__init__(f"unsupported model profile: {profile}")
        self.profile = profile


class EndpointRejectedError(ValueError):
    pass


class FixtureResponseMissingError(KeyError):
    pass


class UnregisteredVersionError(KeyError):
    pass


class CandidateNotFoundError(KeyError):
    pass


class UnconfirmedCandidateError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _candidate_id(candidate_kind: str, payload: Mapping[str, Any], evidence_refs: list[Mapping[str, Any]]) -> str:
    material = {
        "candidate_kind": candidate_kind,
        "payload": payload,
        "evidence_refs": evidence_refs,
    }
    return "cand_" + _sha256(canonical_json(material))[:16]


def _batch_id(
    backend_kind: str,
    model_id: str,
    model_version: str,
    prompt_version: str,
    source_ids: list[str],
    proposed_at: str,
) -> str:
    material = {
        "backend_kind": backend_kind,
        "model_id": model_id,
        "model_version": model_version,
        "prompt_version": prompt_version,
        "sources_seen": sorted(source_ids),
        "proposed_at": proposed_at,
    }
    return "batch_" + _sha256(canonical_json(material))[:16]


def _is_loopback_host(host: str | None) -> bool:
    if host is None:
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _validate_output(raw: str, imported_source_ids: set[str]) -> tuple[list[JsonObject] | None, str | None]:
    try:
        obj = json.loads(raw)
    except Exception:
        return None, "invalid_json"
    if not isinstance(obj, dict) or not isinstance(obj.get("candidates"), list):
        return None, "missing_field"
    for field in ESCALATION_FIELDS:
        if field in obj:
            return None, "escalation_field"
    for item in obj["candidates"]:
        if not isinstance(item, dict):
            return None, "missing_field"
        if item.get("candidate_kind") not in CANDIDATE_KINDS:
            return None, "unknown_kind"
        if not isinstance(item.get("payload"), dict) or not isinstance(item.get("evidence_refs"), list) or not item["evidence_refs"]:
            return None, "missing_field"
        for field in ESCALATION_FIELDS:
            if field in item:
                return None, "escalation_field"
        for ref in item["evidence_refs"]:
            if not isinstance(ref, dict) or not isinstance(ref.get("source_id"), str) or ref["source_id"] not in imported_source_ids:
                return None, "missing_field"
    return obj["candidates"], None


class FixtureModelBackend:
    """Deterministic backend keyed by source content_hash; no I/O."""

    kind = "fixture"

    def __init__(self, responses: Mapping[str, str]) -> None:
        self._responses = dict(responses)

    def propose(self, source: Mapping[str, Any]) -> str:
        key = source.get("content_hash")
        if not isinstance(key, str) or key not in self._responses:
            raise FixtureResponseMissingError(key)
        return self._responses[key]


class LocalHttpBackend:
    """Loopback-only OpenAI-compatible chat completion stub client."""

    kind = "local_http"

    def __init__(self, endpoint: str, timeout: float = 2.0) -> None:
        parsed = urllib.parse.urlparse(endpoint)
        if parsed.scheme != "http" or not _is_loopback_host(parsed.hostname):
            raise EndpointRejectedError("local_http endpoint must be http://127.0.0.1 or ::1")
        if parsed.path != "/v1/chat/completions":
            raise EndpointRejectedError("local_http endpoint path must be /v1/chat/completions")
        self.endpoint = endpoint
        self._timeout = timeout

    def propose(self, source: Mapping[str, Any]) -> str:
        request_body = {
            "model": "y2s2-local",
            "messages": [
                {"role": "system", "content": "You are a local synthetic candidate extractor. Return JSON only."},
                {"role": "user", "content": str(source.get("content", ""))},
            ],
            "temperature": 0,
            "max_tokens": 1024,
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


class VersionRegistry:
    """Derived version audit with rollback history retained."""

    def __init__(self, clock: str) -> None:
        self._clock = clock
        self._records: list[JsonObject] = []
        self._active: tuple[str, str, str] | None = None

    @staticmethod
    def _key(model_id: str, model_version: str, prompt_version: str) -> tuple[str, str, str]:
        return (model_id, model_version, prompt_version)

    def _matching(self, model_id: str, model_version: str, prompt_version: str) -> JsonObject | None:
        key = self._key(model_id, model_version, prompt_version)
        for record in reversed(self._records):
            if self._key(record["model_id"], record["model_version"], record["prompt_version"]) == key:
                return record
        return None

    def has(self, model_id: str, model_version: str, prompt_version: str) -> bool:
        return self._matching(model_id, model_version, prompt_version) is not None

    def register(self, model_id: str, model_version: str, prompt_version: str) -> JsonObject:
        record = {
            "model_id": model_id,
            "model_version": model_version,
            "prompt_version": prompt_version,
            "registered_at": self._clock,
            "reason": "register",
        }
        self._records.append(record)
        if self._active is None:
            self._active = self._key(model_id, model_version, prompt_version)
        return record

    def activate(self, model_id: str, model_version: str, prompt_version: str) -> JsonObject:
        if self._matching(model_id, model_version, prompt_version) is None:
            raise UnregisteredVersionError(model_version)
        self._active = self._key(model_id, model_version, prompt_version)
        return self.active()

    def rollback(self, model_version: str, model_id: str | None = None) -> JsonObject:
        matches = [
            record
            for record in self._records
            if record["model_version"] == model_version and (model_id is None or record["model_id"] == model_id)
        ]
        if not matches:
            raise UnregisteredVersionError(model_version)
        target = matches[-1]
        record = {
            "model_id": target["model_id"],
            "model_version": target["model_version"],
            "prompt_version": target["prompt_version"],
            "registered_at": self._clock,
            "reason": "rollback",
        }
        self._records.append(record)
        self._active = self._key(record["model_id"], record["model_version"], record["prompt_version"])
        return record

    def active(self) -> JsonObject:
        if self._active is None:
            raise UnregisteredVersionError("no active version")
        record = self._matching(*self._active)
        if record is None:
            raise UnregisteredVersionError("no active version")
        return record

    def snapshot(self) -> JsonObject:
        return {"registered": self._records, "active": self.active()}


class ModelCurator:
    """Orchestrates backend selection, batch validation, candidate provenance and confirmation."""

    def __init__(
        self,
        store: SemanticStore,
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
        if backend.kind not in LOCAL_BACKEND_KINDS:
            raise EndpointRejectedError(f"backend kind not allowed in Y2-S2: {backend.kind}")
        self._store = store
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

    def candidates(self) -> list[JsonObject]:
        return list(self._candidates.values())

    def propose(self, source_ids: list[str]) -> JsonObject:
        sources: list[JsonObject] = []
        for source_id in source_ids:
            source = self._store.seeded_source(source_id)
            if source is None:
                raise KeyError(source_id)
            sources.append(source)
        imported = {source["source_id"] for source in sources}
        candidates: list[JsonObject] = []
        rejected: list[JsonObject] = []
        for source in sources:
            raw = self._backend.propose(source)
            items, reason = _validate_output(raw, imported)
            if reason is not None:
                rejected.append({"source_id": source["source_id"], "reason": reason})
            elif not rejected:
                for item in items:
                    candidate = self._build_candidate(item)
                    self._candidates[candidate["candidate_id"]] = candidate
                    candidates.append(candidate)
        batch = {
            "batch_id": _batch_id(
                self._backend.kind,
                self._model_id,
                self._model_version,
                self._prompt_version,
                source_ids,
                self._clock,
            ),
            "backend_kind": self._backend.kind,
            "model_id": self._model_id,
            "model_version": self._model_version,
            "prompt_version": self._prompt_version,
            "sources_seen": source_ids,
            "candidates_proposed": [] if rejected else candidates,
            "rejected_outputs": rejected,
            "proposed_at": self._clock,
        }
        return batch

    def _build_candidate(self, item: Mapping[str, Any]) -> JsonObject:
        provenance = {
            "model_id": self._model_id,
            "model_version": self._model_version,
            "prompt_version": self._prompt_version,
            "backend_kind": self._backend.kind,
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

    def confirm_candidate(self, candidate_id: str, actor: str) -> JsonObject:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(candidate_id)
        candidate["confirmation"] = {"actor": actor, "recorded_at": self._clock}
        return self.propose_changeset_for_candidate(candidate_id, actor)

    def propose_changeset_for_candidate(self, candidate_id: str, actor: str) -> JsonObject:
        candidate = self._candidates.get(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(candidate_id)
        if "confirmation" not in candidate:
            raise UnconfirmedCandidateError(candidate_id)
        suffix = candidate_id.removeprefix("cand_")[:16]
        changeset_id = f"changeset_y2s2_{candidate_id}"
        existing = self._store.ledger_record(changeset_id)
        if existing is not None:
            return existing
        changeset = {
            "changeset_id": changeset_id,
            "base_revision": self._store.current_revision(),
            "actor": actor,
            "candidate_ref": candidate_id,
            "trigger_sources": candidate["evidence_refs"],
            "status": "proposed",
            "published_revision": None,
            "recorded_at": self._clock,
            "derived_only": True,
        }
        self._store.put_ledger_record(changeset_id, "changeset", changeset)
        return changeset