"""Y2-S5 minimal local MCP runtime: loopback HTTP, read/propose/append only.

The slice intentionally implements a small JSON-RPC 2.0 wrapper over 127.0.0.1.
It does not provide irreversible tools, A2A, SDK integration, real data, or
large-file transfer. Capabilities are explicit and default closed.
"""

from __future__ import annotations

import ast
import hashlib
import http.server
import ipaddress
import json
import sys
import threading
from pathlib import Path
from typing import Any, Mapping

from .model_capability import RED_LINE_COMPARTMENTS, ProfileRejectedError, canonical_json
from .store import SemanticStore


JsonObject = dict[str, Any]
SUPPORTED_PROFILE = "y2s5_mcp_runtime_v1"
CONTRACT_VERSION = "y2s5-mcp-runtime-v1"
READ_TOOLS = {"list_resources", "read_resource"}
MUTATING_TOOLS = {"propose_changeset", "record_source"}
ENABLED_TOOLS = READ_TOOLS | MUTATING_TOOLS
DISABLED_IRREVERSIBLE_TOOLS = {
    "approve_changeset",
    "seal_item",
    "delete_item",
    "export_sensitive_pack",
    "correct_assertion",
    "revert_changeset",
}
CANDIDATE_KINDS = {"entity", "episode", "commitment", "assertion"}
ESCALATION_FIELDS = {"review_status", "confirmed", "auto_publish", "publish", "verified"}
MAX_SOURCE_BYTES = 65536
SOURCE_FIELDS = {"metadata", "content"}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _short_hash(value: str) -> str:
    return _sha256(value)[:16]


def _is_loopback_host(host: str | None) -> bool:
    if not isinstance(host, str):
        return False
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class McpHttpHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/mcp":
            self._send_json(404, {"jsonrpc": "2.0", "id": None, "error": {"code": -32601, "message": "method not found"}})
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            length = 0
        raw = self.rfile.read(max(0, length))
        try:
            message = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
            return
        if not isinstance(message, dict) or not isinstance(message.get("params"), dict):
            self._send_json(400, {"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None, "error": {"code": -32602, "message": "invalid params"}})
            return
        request = message["params"].get("request")
        payload = message["params"].get("payload")
        if not isinstance(request, dict):
            self._send_json(400, {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32602, "message": "invalid request"}})
            return
        response = self.server.runtime.handle_request(request, payload)
        self._send_json(200, {"jsonrpc": "2.0", "id": message.get("id"), "result": response})

    def _send_json(self, status: int, payload: JsonObject) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


class McpHttpServer(http.server.HTTPServer):

    def __init__(self, runtime: "McpRuntime", server_address: tuple[str, int]) -> None:
        self.runtime = runtime
        super().__init__(server_address, McpHttpHandler)


class McpService:
    """Loopback-only HTTP service wrapper around McpRuntime."""

    def __init__(
        self,
        runtime: "McpRuntime",
        host: str = "127.0.0.1",
        port: int = 0,
        autostart: bool = True,
    ) -> None:
        if not _is_loopback_host(host):
            raise ValueError("MCP service host must be loopback only")
        self.runtime = runtime
        self.host = host
        self.port = port
        self._server: McpHttpServer | None = None
        self._closed = False
        if autostart:
            self.start()

    def start(self) -> None:
        if self._server is not None:
            raise RuntimeError("MCP service is already started")
        self._server = McpHttpServer(self.runtime, (self.host, self.port))
        self.port = self._server.server_address[1]
        thread = threading.Thread(target=self._serve, name="noetide-y2s5-mcp", daemon=True)
        thread.start()

    def _serve(self) -> None:
        if self._server is not None:
            self._server.serve_forever(poll_interval=0.05)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        server = self._server
        if server is None:
            return
        server.shutdown()
        server.server_close()
        self._server = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


class McpRuntime:
    def __init__(
        self,
        store: SemanticStore,
        clock: str,
        profile: str = SUPPORTED_PROFILE,
        policy_available: bool = True,
    ) -> None:
        if profile != SUPPORTED_PROFILE:
            raise ProfileRejectedError(profile)
        self._store = store
        self._clock = clock
        self._policy_available = bool(policy_available)
        self._capabilities: dict[str, JsonObject] = {}

    # -- capability lifecycle -------------------------------------------------

    def create_capability(self, spec: Mapping[str, Any]) -> JsonObject:
        capability = dict(spec)
        capability_id = capability.get("capability_id")
        if not isinstance(capability_id, str) or not capability_id:
            raise ValueError("capability_id is required")
        if not isinstance(capability.get("actor"), str) or not capability.get("actor"):
            raise ValueError("actor is required")
        if not isinstance(capability.get("purpose"), str) or not capability.get("purpose"):
            raise ValueError("purpose is required")
        tools = capability.get("tools")
        resource_ids = capability.get("resource_ids")
        if not isinstance(tools, list) or not tools or not set(tools) <= ENABLED_TOOLS:
            raise ValueError("tools must be a non-empty subset of enabled MCP tools")
        if not isinstance(resource_ids, list) or not resource_ids:
            raise ValueError("resource_ids must be non-empty")
        if not isinstance(capability.get("expires_at"), str) or not capability["expires_at"]:
            raise ValueError("expires_at is required")
        if "resource_fields" in capability and capability["resource_fields"] is not None:
            fields = capability["resource_fields"]
            if not isinstance(fields, dict):
                raise ValueError("resource_fields must be a mapping")
            for values in fields.values():
                if not isinstance(values, list) or not set(values) <= SOURCE_FIELDS:
                    raise ValueError("resource_fields values must be subsets of metadata/content")
        capability.setdefault("revoked", False)
        capability.setdefault("created_at", self._clock)
        capability.setdefault("resource_fields", None)
        capability = {key: capability[key] for key in (
            "capability_id", "actor", "purpose", "tools", "resource_ids", "resource_fields",
            "expires_at", "revoked", "created_at",
        )}
        self._capabilities[capability_id] = capability
        self._audit("capability_created", {"capability_ref": capability_id, "actor": capability["actor"]})
        return dict(capability)

    def revoke_capability(self, capability_id: str) -> JsonObject:
        capability = self._capabilities.get(capability_id)
        if capability is None:
            raise KeyError(capability_id)
        capability["revoked"] = True
        self._audit("capability_revoked", {"capability_ref": capability_id})
        return dict(capability)

    def capabilities(self) -> list[JsonObject]:
        return [dict(item) for item in self._capabilities.values()]

    def audit_records(self) -> list[JsonObject]:
        return self._store.ledger_records_of_type("mcp_audit")

    # -- envelope helpers -----------------------------------------------------

    def _audit(self, event_type: str, payload: Mapping[str, Any]) -> None:
        combined = {"event_type": event_type, "recorded_at": self._clock, **dict(payload)}
        index = len(self._store.ledger_records_of_type("mcp_audit"))
        record_id = f"mcp_audit_{index:04d}_{_short_hash(canonical_json(combined))}"
        self._store.put_ledger_record(record_id, "mcp_audit", combined)

    def _denied(self, request_id: str, reason: str) -> JsonObject:
        self._audit("request_denied", {"request_id": request_id, "reason": reason})
        return {
            "request_id": request_id,
            "authorization": "denied",
            "result_status": "denied",
            "data_revision": "withheld",
            "view_revision": "withheld",
            "freshness_status": "withheld",
            "answer_status": "withheld",
            "evidence_refs": [],
            "missing_evidence": "withheld",
            "receipt_ref": None,
            "payload": "withheld",
            "error": {"code": "denied", "message": "denied"},
        }

    def _failed(
        self,
        request_id: str,
        code: str,
        *,
        authorization: str = "denied",
        payload: Any = "withheld",
        data_revision: str = "withheld",
    ) -> JsonObject:
        self._audit("request_failed", {"request_id": request_id, "reason": code})
        return {
            "request_id": request_id,
            "authorization": authorization,
            "result_status": "failed",
            "data_revision": data_revision,
            "view_revision": "not_applicable" if authorization == "allowed" else "withheld",
            "freshness_status": "not_applicable" if authorization == "allowed" else "withheld",
            "answer_status": "not_applicable" if authorization == "allowed" else "withheld",
            "evidence_refs": [],
            "missing_evidence": "not_applicable" if authorization == "allowed" else "withheld",
            "receipt_ref": None,
            "payload": payload,
            "error": {"code": code, "message": code},
        }

    def _conflict(self, request_id: str, reason: str = "revision_precondition") -> JsonObject:
        current = self._store.current_revision()
        self._audit("request_conflict", {"request_id": request_id, "reason": reason})
        return {
            "request_id": request_id,
            "authorization": "allowed",
            "result_status": "conflict",
            "data_revision": current,
            "view_revision": "not_applicable",
            "freshness_status": "not_applicable",
            "answer_status": "not_applicable",
            "evidence_refs": [],
            "missing_evidence": "not_applicable",
            "receipt_ref": None,
            "payload": {"current_revision": current},
            "error": {"code": "conflict", "message": "conflict"},
        }

    def _ok(
        self,
        request_id: str,
        *,
        view_revision: str = "not_applicable",
        freshness_status: str = "not_applicable",
        evidence_refs: list[JsonObject] | None = None,
        missing_evidence: str | bool = "not_applicable",
        payload: Any,
        receipt_ref: str | None = None,
        authorization: str = "allowed",
        extra: Mapping[str, Any] | None = None,
    ) -> JsonObject:
        self._audit("request_allowed", {"request_id": request_id, "authorization": authorization})
        response: JsonObject = {
            "request_id": request_id,
            "authorization": authorization,
            "result_status": "accepted" if receipt_ref else "ok",
            "data_revision": self._store.current_revision(),
            "view_revision": view_revision,
            "freshness_status": freshness_status,
            "answer_status": "not_applicable",
            "evidence_refs": evidence_refs or [],
            "missing_evidence": missing_evidence,
            "receipt_ref": receipt_ref,
            "payload": payload,
            "error": None,
        }
        if extra:
            response.update(extra)
        return response

    # -- request handling -----------------------------------------------------

    def handle_request(self, request: Mapping[str, Any], payload: Mapping[str, Any] | None = None) -> JsonObject:
        if not isinstance(request, dict):
            return self._failed("unknown", "invalid_request")
        request_id = request.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            request_id = "unknown"
        action = request.get("action")
        if not isinstance(action, str) or not action:
            return self._failed(request_id, "invalid_request")

        if not self._policy_available:
            return self._denied(request_id, "policy_unavailable")

        required = ("contract_version", "request_id", "caller_ref", "purpose", "capability_ref", "scope", "requested_at")
        for field in required:
            if field not in request:
                return self._failed(request_id, "invalid_request")
        if request.get("contract_version") != CONTRACT_VERSION:
            return self._failed(request_id, "unsupported_contract")
        scope = request.get("scope")
        if not isinstance(scope, dict) or not isinstance(scope.get("resource_ids"), list):
            return self._failed(request_id, "invalid_request")

        capability = self._capabilities.get(request.get("capability_ref"))
        if capability is None:
            return self._denied(request_id, "no_capability")
        if capability.get("revoked") is True:
            return self._denied(request_id, "capability_revoked")
        requested_at = request.get("requested_at")
        if not isinstance(requested_at, str) or requested_at > capability["expires_at"]:
            return self._denied(request_id, "capability_expired")
        if request.get("caller_ref") != capability["actor"]:
            return self._denied(request_id, "actor_mismatch")
        if request.get("purpose") != capability["purpose"]:
            return self._denied(request_id, "purpose_mismatch")
        if action not in capability["tools"]:
            reason = "irreversible_disabled" if action in DISABLED_IRREVERSIBLE_TOOLS else "tool_not_granted"
            return self._denied(request_id, reason)
        if action not in ENABLED_TOOLS:
            return self._denied(request_id, "tool_not_granted")

        resource_ids = list(scope["resource_ids"])
        if action != "list_resources" and not resource_ids:
            return self._denied(request_id, "scope_mismatch")
        if not set(resource_ids) <= set(capability["resource_ids"]):
            return self._denied(request_id, "scope_mismatch")

        precondition = request.get("data_revision_precondition")
        if precondition is not None:
            if not isinstance(precondition, str) or precondition != self._store.current_revision():
                return self._conflict(request_id)

        for resource_id in resource_ids:
            if not isinstance(resource_id, str) or not resource_id.startswith("src_"):
                continue
            source = self._store.seeded_source(resource_id)
            if source is not None and set(source.get("compartments", [])) & RED_LINE_COMPARTMENTS:
                return self._denied(request_id, "red_line_denied")

        try:
            if action == "list_resources":
                return self._list_resources(request_id, capability, resource_ids)
            if action == "read_resource":
                return self._read_resource(request_id, capability, resource_ids, payload)
            if action == "propose_changeset":
                return self._propose_changeset(request_id, request, capability, resource_ids, payload)
            if action == "record_source":
                return self._record_source(request_id, request, capability, resource_ids, payload)
        except (KeyError, TypeError, ValueError):
            return self._failed(request_id, "invalid_payload", authorization="allowed", data_revision=self._store.current_revision())
        return self._denied(request_id, "tool_not_granted")

    # -- tools -----------------------------------------------------------------

    def _list_resources(self, request_id: str, capability: JsonObject, resource_ids: list[str]) -> JsonObject:
        allowed = set(capability["resource_ids"])
        projections = self._store.seed_snapshot()["projections"]
        source_ids = sorted(
            rid for rid in allowed
            if isinstance(rid, str) and rid.startswith("src_")
            and self._store.seeded_source(rid) is not None
            and not (set(self._store.seeded_source(rid).get("compartments", [])) & RED_LINE_COMPARTMENTS)
        )
        view_names = sorted(rid for rid in allowed if isinstance(rid, str) and rid in projections)
        return self._ok(
            request_id,
            payload={"resource_ids": source_ids, "view_names": view_names},
            missing_evidence=False,
        )

    def _read_resource(self, request_id: str, capability: JsonObject, resource_ids: list[str], payload: Mapping[str, Any] | None) -> JsonObject:
        if not isinstance(payload, dict):
            raise ValueError("read_resource payload required")
        resource_id = payload.get("resource_id")
        if not isinstance(resource_id, str) or resource_id not in resource_ids:
            return self._denied(request_id, "scope_mismatch")
        if resource_id in self._store.seed_snapshot()["projections"]:
            projection = self._store.projection_record(resource_id)
            return self._ok(
                request_id,
                view_revision=str(projection.get("view_revision", "not_applicable")),
                freshness_status=str(projection.get("freshness_status", "not_applicable")),
                missing_evidence=False,
                payload=projection.get("payload", {}),
            )
        if not resource_id.startswith("src_"):
            return self._denied(request_id, "resource_not_found")
        source = self._store.seeded_source(resource_id)
        if source is None:
            return self._denied(request_id, "resource_not_found")
        if set(source.get("compartments", [])) & RED_LINE_COMPARTMENTS:
            return self._denied(request_id, "red_line_denied")

        allowed_values = capability.get("resource_fields", {}).get("read_resource")
        allowed_fields = set(allowed_values) if isinstance(allowed_values, list) else set(SOURCE_FIELDS)
        requested_values = payload.get("fields")
        requested_fields = set(requested_values) if isinstance(requested_values, list) and requested_values else set(allowed_fields)
        visible_fields = requested_fields & allowed_fields
        redacted = visible_fields != requested_fields
        result: JsonObject = {
            "source_id": source["source_id"],
            "source_kind": source["source_kind"],
            "content_hash": source["content_hash"],
            "byte_length": source["byte_length"],
            "locator": source["locator"],
            "coverage_window": source["coverage_window"],
            "compartments": list(source["compartments"]),
        }
        if "content" in visible_fields:
            result["content"] = source["content"]
        return self._ok(
            request_id,
            evidence_refs=[{"source_id": source["source_id"], "locator": source["locator"]}],
            missing_evidence=False,
            payload={"redacted": redacted, "fields": sorted(visible_fields), **result},
            authorization="allowed_with_redaction" if redacted else "allowed",
        )

    def _propose_changeset(
        self,
        request_id: str,
        request: Mapping[str, Any],
        capability: JsonObject,
        resource_ids: list[str],
        payload: Mapping[str, Any] | None,
    ) -> JsonObject:
        if not isinstance(payload, dict) or not isinstance(payload.get("candidate"), dict):
            raise ValueError("propose_changeset payload required")
        candidate = dict(payload["candidate"])
        idempotency_key = request.get("idempotency_key")
        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ValueError("idempotency_key required")
        payload_hash = canonical_json(candidate)
        idem = self._store.ledger_record(f"mcp_idem_{idempotency_key}")
        if idem is not None:
            if idem.get("payload_hash") == payload_hash:
                self._audit("idempotent_replayed", {"request_id": request_id, "tool": "propose_changeset"})
                return self._ok(
                    request_id,
                    evidence_refs=[],
                    missing_evidence=False,
                    payload={"changeset_id": idem["receipt_ref"], "status": "proposed"},
                    receipt_ref=idem["receipt_ref"],
                )
            return self._conflict(request_id, "idempotency_key_reused")

        candidate_kind = candidate.get("candidate_kind")
        if candidate_kind not in CANDIDATE_KINDS:
            raise ValueError("invalid candidate_kind")
        if not isinstance(candidate.get("payload"), dict):
            raise ValueError("candidate payload required")
        if ESCALATION_FIELDS & set(candidate):
            raise ValueError("escalation fields are not allowed")
        evidence_refs = candidate.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            raise ValueError("evidence_refs required")
        source_ids: list[str] = []
        for ref in evidence_refs:
            if not isinstance(ref, dict) or not isinstance(ref.get("source_id"), str):
                raise ValueError("evidence_refs invalid")
            source_id = ref["source_id"]
            source_ids.append(source_id)
            if source_id not in resource_ids or source_id not in capability["resource_ids"]:
                raise ValueError("evidence_refs out of scope")
            source = self._store.seeded_source(source_id)
            if source is None:
                raise ValueError("evidence_refs source missing")
            if set(source.get("compartments", [])) & RED_LINE_COMPARTMENTS:
                raise ValueError("evidence_refs red line denied")

        current = self._store.current_revision()
        candidate_id = "cand_" + _short_hash(canonical_json(candidate))
        changeset_id = "changeset_y2s5_" + _short_hash(canonical_json({
            "capability_ref": capability["capability_id"],
            "idempotency_key": idempotency_key,
        }))
        changeset = {
            "changeset_id": changeset_id,
            "base_revision": current,
            "actor": request.get("caller_ref"),
            "purpose": request.get("purpose"),
            "capability_ref": capability["capability_id"],
            "candidate_ref": candidate_id,
            "trigger_sources": sorted(set(source_ids)),
            "status": "proposed",
            "published_revision": None,
            "recorded_at": request.get("requested_at"),
            "derived_only": True,
        }
        self._store.put_ledger_record(changeset_id, "changeset", changeset)
        self._store.put_ledger_record(
            f"mcp_idem_{idempotency_key}",
            "mcp_idempotency",
            {
                "idempotency_key": idempotency_key,
                "tool": "propose_changeset",
                "payload_hash": payload_hash,
                "receipt_ref": changeset_id,
                "recorded_at": request.get("requested_at"),
            },
        )
        self._audit("changeset_proposed", {"request_id": request_id, "receipt_ref": changeset_id})
        return self._ok(
            request_id,
            evidence_refs=[{"source_id": source_id, "locator": self._store.seeded_source(source_id)["locator"]} for source_id in sorted(set(source_ids))],
            missing_evidence=False,
            payload={"changeset_id": changeset_id, "status": "proposed", "base_revision": current},
            receipt_ref=changeset_id,
        )

    def _record_source(
        self,
        request_id: str,
        request: Mapping[str, Any],
        capability: JsonObject,
        resource_ids: list[str],
        payload: Mapping[str, Any] | None,
    ) -> JsonObject:
        if not isinstance(payload, dict) or not isinstance(payload.get("source"), dict):
            raise ValueError("record_source payload required")
        source = dict(payload["source"])
        idempotency_key = request.get("idempotency_key")
        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ValueError("idempotency_key required")
        source_id = source.get("source_id")
        content = source.get("content")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("source_id required")
        if not isinstance(content, str):
            raise ValueError("content required")
        if source_id not in resource_ids or source_id not in capability["resource_ids"]:
            raise ValueError("source out of scope")

        content_bytes = content.encode("utf-8")
        content_hash = _sha256(content)
        byte_length = len(content_bytes)
        payload_hash = canonical_json({"source": source, "content_hash": content_hash, "byte_length": byte_length})
        idem = self._store.ledger_record(f"mcp_idem_{idempotency_key}")
        if idem is not None:
            if idem.get("payload_hash") == payload_hash:
                self._audit("idempotent_replayed", {"request_id": request_id, "tool": "record_source"})
                return self._ok(
                    request_id,
                    evidence_refs=[],
                    missing_evidence=False,
                    payload={"source_id": source_id, "receipt_id": idem["receipt_ref"], "status": "stored"},
                    receipt_ref=idem["receipt_ref"],
                )
            return self._conflict(request_id, "idempotency_key_reused")

        if byte_length > MAX_SOURCE_BYTES:
            return self._failed(
                request_id,
                "large_file_required",
                authorization="allowed",
                payload={"import_reference_required": True, "max_bytes": MAX_SOURCE_BYTES},
                data_revision=self._store.current_revision(),
            )
        if not isinstance(source.get("locator"), dict) or not isinstance(source.get("coverage_window"), dict):
            raise ValueError("source locator/coverage required")
        if not isinstance(source.get("compartments"), list):
            raise ValueError("source compartments required")
        if set(source["compartments"]) & RED_LINE_COMPARTMENTS:
            return self._denied(request_id, "red_line_denied")
        if self._store.seeded_source(source_id) is not None:
            return self._conflict(request_id, "source_exists")

        source_record = {
            "source_id": source_id,
            "append_receipt_id": f"receipt_y2s5_{_short_hash(source_id + content_hash)}",
            "source_kind": source.get("source_kind"),
            "content_hash": content_hash,
            "byte_length": byte_length,
            "source_created_at": source.get("source_created_at"),
            "ingested_at": request.get("requested_at"),
            "language": source.get("language"),
            "locator": source["locator"],
            "coverage_window": source["coverage_window"],
            "content": content,
            "compartments": list(source["compartments"]),
        }
        receipt = {
            "receipt_id": source_record["append_receipt_id"],
            "source_id": source_id,
            "status": "stored",
            "actor": request.get("caller_ref"),
        }
        self._store.append_source(source_record, receipt)
        self._store.put_ledger_record(
            f"mcp_idem_{idempotency_key}",
            "mcp_idempotency",
            {
                "idempotency_key": idempotency_key,
                "tool": "record_source",
                "payload_hash": payload_hash,
                "receipt_ref": receipt["receipt_id"],
                "recorded_at": request.get("requested_at"),
            },
        )
        self._audit("source_appended", {"request_id": request_id, "source_id": source_id, "receipt_ref": receipt["receipt_id"]})
        return self._ok(
            request_id,
            evidence_refs=[{"source_id": source_id, "locator": source["locator"]}],
            missing_evidence=False,
            payload={"source_id": source_id, "receipt_id": receipt["receipt_id"], "status": "stored"},
            receipt_ref=receipt["receipt_id"],
        )


def static_stdlib_scan(module_path: str | Path | None = None) -> tuple[bool, list[str]]:
    """Return whether mcp_runtime.py only imports stdlib plus local package modules."""
    path = Path(module_path) if module_path else Path(__file__).resolve()
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
