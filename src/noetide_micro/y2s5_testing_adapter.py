"""Y2-S5 testing adapter: synthetic MCP runtime over 127.0.0.1 HTTP.

Each case owns a temporary SQLite store, a fixture materialization, an explicit
capability set, and a loopback MCP HTTP service. Responses are collected from
the HTTP transport so the official runner also exercises the runtime boundary.
"""

from __future__ import annotations

import copy
import hashlib
import http.client
import json
import shutil
import tempfile
import weakref
from pathlib import Path
from typing import Any, Mapping

from .mcp_runtime import (
    CONTRACT_VERSION,
    McpRuntime,
    McpService,
    ProfileRejectedError,
    static_stdlib_scan,
)
from .store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "y2s5_mcp_runtime_v1" / "fixture.json"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _is_exact_denied(response: Mapping[str, Any]) -> bool:
    return (
        response.get("authorization") == "denied"
        and response.get("result_status") == "denied"
        and response.get("data_revision") == "withheld"
        and response.get("view_revision") == "withheld"
        and response.get("freshness_status") == "withheld"
        and response.get("answer_status") == "withheld"
        and response.get("evidence_refs") == []
        and response.get("missing_evidence") == "withheld"
        and response.get("receipt_ref") is None
        and response.get("payload") == "withheld"
        and response.get("error") == {"code": "denied", "message": "denied"}
    )


def _finalize(system: "Y2S5CaseSystem") -> None:
    system.close()


def create_system(case: Mapping[str, Any]) -> "Y2S5CaseSystem":
    return Y2S5CaseSystem(case)


class Y2S5CaseSystem:
    def __init__(self, case: Mapping[str, Any], *, policy_available: bool = True) -> None:
        self._case = copy.deepcopy(dict(case))
        self._fixture = _fixture()
        self._clock = self._fixture["determinism"]["clock"]
        self._tmp = Path(tempfile.mkdtemp(prefix="noetide-y2s5-"))
        self._store = SemanticStore(self._tmp / "noetide.sqlite3", check_same_thread=False)
        for view in self._fixture["views"].values():
            self._store.add_revision(view["view_revision"], self._clock, "seed")
        self._store.add_revision("rev_000", self._clock, "seed")
        self._materialize_sources(self._fixture["sources"])
        self._seed_views(self._fixture["views"])
        self._runtime = McpRuntime(self._store, self._clock, policy_available=policy_available)
        self._service = McpService(self._runtime, host="127.0.0.1", port=0)
        self._closed = False
        weakref.finalize(self, _finalize, self)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._service.close()
        finally:
            try:
                self._store.close()
            finally:
                shutil.rmtree(self._tmp, ignore_errors=True)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def layer_snapshot(self) -> dict[str, Any]:
        portability = self._store.portability_snapshot()
        return {
            "canonical_layer": self._store.canonical_layer_digest(),
            "revision": self._store.current_revision(),
            "sources": _canonical(portability["sources"]),
            "changesets": _canonical(self._store.ledger_records_of_type("changeset")),
            "audit": _canonical(self._store.ledger_records_of_type("mcp_audit")),
            "idempotency": _canonical(self._store.ledger_records_of_type("mcp_idempotency")),
        }

    # -- fixture materialization ---------------------------------------------

    def _materialize_sources(self, sources: list[Mapping[str, Any]]) -> None:
        for source in sources:
            content = source["content"].encode("utf-8")
            if source["content_hash"] != hashlib.sha256(content).hexdigest():
                raise ValueError(f"fixture content hash mismatch: {source['source_id']}")
            if source["byte_length"] != len(content):
                raise ValueError(f"fixture byte length mismatch: {source['source_id']}")
            receipt = {
                "receipt_id": source["append_receipt_id"],
                "source_id": source["source_id"],
                "status": "stored",
                "actor": "y2s5_adapter",
            }
            self._store.append_source(dict(source), receipt)

    def _seed_views(self, views: Mapping[str, Any]) -> None:
        for name, projection in views.items():
            self._store.upsert_projection(
                name,
                projection["data_revision"],
                projection["view_revision"],
                projection["freshness_status"],
                projection["payload"],
            )

    # -- HTTP transport ------------------------------------------------------

    def _http_request(self, request: Mapping[str, Any], payload: Any = None) -> dict[str, Any]:
        message = {
            "jsonrpc": "2.0",
            "id": request.get("request_id", "unknown"),
            "method": "noetide/call",
            "params": {"request": request, "payload": payload},
        }
        body = _canonical(message).encode("utf-8")
        connection = http.client.HTTPConnection("127.0.0.1", self._service.port, timeout=5)
        try:
            connection.request(
                "POST",
                "/mcp",
                body=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            raw = connection.getresponse().read()
        finally:
            connection.close()
        parsed = json.loads(raw.decode("utf-8"))
        if "result" not in parsed:
            raise RuntimeError(parsed)
        return parsed["result"]

    def _request_envelope(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        request: dict[str, Any] = {
            "contract_version": CONTRACT_VERSION,
            "request_id": spec["request_id"],
            "caller_ref": self._case.get("actor", self._fixture["defaults"]["actor"]),
            "purpose": self._case.get("purpose", self._fixture["defaults"]["purpose"]),
            "capability_ref": spec["capability_ref"],
            "action": spec["action"],
            "scope": spec["scope"],
            "requested_at": self._clock,
        }
        if "idempotency_key" in spec:
            request["idempotency_key"] = spec["idempotency_key"]
        if "data_revision_precondition" in spec:
            request["data_revision_precondition"] = spec["data_revision_precondition"]
        return request

    def run_requests(self, requests: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        responses: list[dict[str, Any]] = []
        for spec in requests:
            request = self._request_envelope(spec)
            responses.append(self._http_request(request, spec.get("payload")))
        return responses

    # -- case runners --------------------------------------------------------

    def _create_case_capabilities(self) -> None:
        by_id = {item["capability_id"]: item for item in self._fixture["capabilities"]}
        for capability_id in self._case.get("capabilities", []):
            if capability_id not in by_id:
                raise KeyError(capability_id)
            self._runtime.create_capability(by_id[capability_id])

    def _base_summary(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        responses: list[dict[str, Any]],
        malformed_response: dict[str, Any] | None = None,
        policy_response: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        denied = [item for item in responses if item.get("result_status") == "denied"]
        if malformed_response is not None and malformed_response.get("result_status") == "denied":
            denied.append(malformed_response)
        if policy_response is not None and policy_response.get("result_status") == "denied":
            denied.append(policy_response)
        return {
            "responses": responses,
            "malformed_response": malformed_response,
            "policy_response": policy_response,
            "audit_event_types": sorted({item.get("event_type") for item in self._runtime.audit_records()}),
            "source_count": len(self._store.portability_snapshot()["sources"]),
            "changeset_count": len(self._store.ledger_records_of_type("changeset")),
            "canonical_unchanged": before["canonical_layer"] == after["canonical_layer"],
            "revision_unchanged": before["revision"] == after["revision"],
            "denied_profile_exact": all(_is_exact_denied(item) for item in denied),
            "large_file_import_required": any(
                item.get("error") is not None and item["error"].get("code") == "large_file_required"
                for item in responses
            ),
            "redacted_no_content": any(
                item.get("authorization") == "allowed_with_redaction"
                and isinstance(item.get("payload"), dict)
                and "content" not in item["payload"]
                and item["payload"].get("redacted") is True
                for item in responses
            ),
            "determinism_byte_identical": False,
            "stdlib_only": False,
            "loopback_only": False,
            "synthetic_fixture": False,
            "profile_rejected": None,
        }

    def _run_determinism_probe(self) -> dict[str, Any]:
        before = self.layer_snapshot()
        self._create_case_capabilities()
        responses = self.run_requests(self._case["requests"])
        peer = Y2S5CaseSystem(self._case)
        try:
            peer._create_case_capabilities()
            peer_responses = peer.run_requests(self._case["requests"])
            identical = _canonical(responses) == _canonical(peer_responses)
        finally:
            peer.close()
        after = self.layer_snapshot()
        stdlib_ok, _ = static_stdlib_scan()
        loopback_rejected = False
        try:
            McpService(self._runtime, host="0.0.0.0", port=0, autostart=False)
        except ValueError:
            loopback_rejected = True
        profile_rejected = None
        try:
            McpRuntime(self._store, self._clock, profile=self._case.get("profile_override", "y2s5_unknown_profile_v9"))
        except ProfileRejectedError as exc:
            profile_rejected = exc.profile
        summary = self._base_summary(before, after, responses)
        summary.update({
            "determinism_byte_identical": identical,
            "stdlib_only": stdlib_ok,
            "loopback_only": loopback_rejected,
            "synthetic_fixture": self._fixture.get("synthetic") is True and self._fixture.get("external_data_used") is False,
            "profile_rejected": profile_rejected,
        })
        return summary

    def _run_failure_probe(self) -> dict[str, Any]:
        before = self.layer_snapshot()
        self._create_case_capabilities()
        responses = self.run_requests(self._case["requests"])
        malformed = self._case.get("malformed_request")
        malformed_response = self._http_request(dict(malformed), None) if malformed else None
        policy_response = None
        if self._case.get("policy_unavailable"):
            policy_system = Y2S5CaseSystem(self._case, policy_available=False)
            try:
                policy_system._create_case_capabilities()
                policy_response = policy_system.run_requests([self._case["requests"][0]])[0]
            finally:
                policy_system.close()
        after = self.layer_snapshot()
        summary = self._base_summary(before, after, responses, malformed_response=malformed_response, policy_response=policy_response)
        stdlib_ok, _ = static_stdlib_scan()
        summary.update({
            "stdlib_only": stdlib_ok,
            "loopback_only": True,
            "synthetic_fixture": self._fixture.get("synthetic") is True and self._fixture.get("external_data_used") is False,
        })
        return summary

    def run_case(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        action = case.get("action")
        if action == "determinism_stdlib_loopback":
            return self._run_determinism_probe()
        self._create_case_capabilities()
        if action == "failure_policy_large_file":
            return self._run_failure_probe()
        responses = self.run_requests(case["requests"])
        after = self.layer_snapshot()
        summary = self._base_summary(before, after, responses)
        stdlib_ok, _ = static_stdlib_scan()
        summary.update({
            "stdlib_only": stdlib_ok,
            "loopback_only": True,
            "synthetic_fixture": self._fixture.get("synthetic") is True and self._fixture.get("external_data_used") is False,
        })
        return summary
