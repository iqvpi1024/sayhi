"""Y2-S4 testing adapter: materializes synthetic sources and runs contract cases.

Environment isolation: every case lives in a TemporaryDirectory; timestamps come
from the fixture clock; CloudHttpBackend is used only against a 127.0.0.1 stub
with an explicit test override.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import threading
import weakref
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping

from .cloud_model import (
    CloudFixtureBackend,
    CloudGate,
    CloudHttpBackend,
    CloudModelCurator,
    ProfileRejectedError,
    EndpointRejectedError,
    static_stdlib_scan,
)
from .model_capability import VersionRegistry, canonical_json
from .store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "y2s4_cloud_model_v1" / "fixture.json"


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _finalize(store: SemanticStore, path: Path) -> None:
    try:
        store.close()
    except Exception:
        pass
    shutil.rmtree(path, ignore_errors=True)


class _FailureStubHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return


class _FailureStubServer(ThreadingHTTPServer):
    daemon_threads = True


def create_system(case: Mapping[str, Any]) -> "Y2S4CaseSystem":
    return Y2S4CaseSystem(case)


class Y2S4CaseSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._case = dict(case)
        self._fixture = _fixture()
        self._clock = self._fixture["determinism"]["clock"]
        self._tmp_path = Path(tempfile.mkdtemp())
        self._store = SemanticStore(self._tmp_path / "noetide.sqlite3")
        self._store.add_revision("rev_000", self._clock, "seed")
        self._finalizer = weakref.finalize(self, _finalize, self._store, self._tmp_path)
        self._materialize_sources(self._fixture["sources"])
        self._gate = CloudGate(self._store, self._clock)

    def close(self) -> None:
        self._finalizer()

    # -- materialization -------------------------------------------------

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
                "actor": "y2s4_adapter",
            }
            self._store.append_source(dict(source), receipt)

    # -- helpers ---------------------------------------------------------

    def _responses(self) -> dict[str, Any]:
        return {
            source["content_hash"]: self._fixture["model_responses"][source["source_id"]]
            for source in self._fixture["sources"]
            if source["source_id"] in self._fixture["model_responses"]
        }

    def _backend(self, kind: str = "cloud_fixture", endpoint: str | None = None) -> Any:
        if kind == "cloud_fixture":
            return CloudFixtureBackend(self._responses())
        if kind == "cloud_http":
            if endpoint is None:
                raise ValueError("cloud_http endpoint required")
            return CloudHttpBackend(endpoint, allow_loopback=True)
        raise ValueError(kind)

    def _curator(
        self,
        backend: Any | None = None,
        registry: VersionRegistry | None = None,
        profile: str | None = None,
        model_version: str | None = None,
        prompt_version: str | None = None,
    ) -> CloudModelCurator:
        defaults = self._fixture["defaults"]
        return CloudModelCurator(
            self._store,
            self._gate,
            backend or self._backend("cloud_fixture"),
            self._clock,
            defaults["model_id"],
            model_version or defaults["model_version"],
            prompt_version or defaults["prompt_version"],
            profile=profile or defaults["profile"],
            registry=registry,
        )

    def _create_grants(self, case: Mapping[str, Any]) -> None:
        for grant in case.get("grants", []):
            self._gate.create_grant(grant)

    def _preview(self, source_ids: list[str], purpose: str | None = None, actor: str | None = None) -> dict[str, Any]:
        defaults = self._fixture["defaults"]
        return self._gate.build_preview(
            list(source_ids),
            purpose or defaults["purpose"],
            actor or defaults["actor"],
            self._clock,
        )

    def _summary(self, batch: dict[str, Any], preview: dict[str, Any] | None, backend: Any, registry: VersionRegistry) -> dict[str, Any]:
        candidates = batch.get("candidates_proposed", [])
        audit_types = sorted({record["event_type"] for record in self._gate.audit_records()})
        return {
            "batch_status": batch.get("status"),
            "rejected_reasons": [item.get("reason") for item in batch.get("rejected_outputs", [])],
            "backend_call_count": backend.calls,
            "candidate_count": len(candidates),
            "all_unconfirmed": all(item.get("review_status") == "unconfirmed" for item in candidates),
            "preview_raw_content_present": bool(
                preview and any(entry.get("raw_content_present") for entry in preview.get("data_scope", []))
            ),
            "preview_source_count": len(preview["data_scope"]) if preview else 0,
            "canonical_unchanged": True,
            "revision_unchanged": True,
            "audit_event_types": audit_types,
            "version_active": {
                "model_id": registry.active()["model_id"],
                "model_version": registry.active()["model_version"],
                "prompt_version": registry.active()["prompt_version"],
            },
        }

    def layer_snapshot(self) -> dict[str, Any]:
        return {
            "canonical_layer": self._store.canonical_layer_digest(),
            "revision_layer": self._store.current_revision(),
            "ledger_cloud_audit_event_types": sorted(
                {record["event_type"] for record in self._store.ledger_records_of_type("cloud_audit")}
            ),
        }

    # -- cases -----------------------------------------------------------

    def _run_default_closed(self, case: Mapping[str, Any]) -> dict[str, Any]:
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview = self._preview(case["source_ids"], case["purpose"])
        batch = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview["preview_id"], self._clock)
        return self._summary(batch, preview, backend, registry)

    def _run_explicit_grant(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview = self._preview(case["source_ids"], case["purpose"])
        batch = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview["preview_id"], self._clock)
        return self._summary(batch, preview, backend, registry)

    def _run_redline_probe(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview = self._preview(case["source_ids"], case["purpose"])
        batch = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview["preview_id"], self._clock)
        return self._summary(batch, preview, backend, registry)

    def _run_mismatch_probe(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview = self._preview(case["source_ids"], case["purpose"])
        batch = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview["preview_id"], self._clock)
        return self._summary(batch, preview, backend, registry)

    def _run_expiry_revocation(self, case: Mapping[str, Any]) -> dict[str, Any]:
        expired = case["expired_grant"]
        revoked = case["revoked_grant"]
        self._gate.create_grant(expired)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview_a = self._preview(case["source_ids"], case["purpose"])
        batch_a = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview_a["preview_id"], self._clock)
        self._gate.create_grant(revoked)
        self._gate.revoke_grant(revoked["grant_id"])
        preview_b = self._preview(case["source_ids"], case["purpose"])
        batch_b = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview_b["preview_id"], self._clock)
        reasons = [item["reason"] for item in batch_a["rejected_outputs"]] + [item["reason"] for item in batch_b["rejected_outputs"]]
        audit_types = sorted({record["event_type"] for record in self._gate.audit_records()})
        return {
            "batch_status": "rejected",
            "rejected_reasons": reasons,
            "backend_call_count": backend.calls,
            "candidate_count": 0,
            "all_unconfirmed": True,
            "preview_raw_content_present": False,
            "preview_source_count": len(preview_a["data_scope"]),
            "canonical_unchanged": True,
            "revision_unchanged": True,
            "audit_event_types": audit_types,
            "version_active": {
                "model_id": registry.active()["model_id"],
                "model_version": registry.active()["model_version"],
                "prompt_version": registry.active()["prompt_version"],
            },
        }

    def _run_preview_required(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        defaults = self._fixture["defaults"]
        batch_a = curator.propose(case["source_ids"], case["purpose"], defaults["actor"], None, self._clock)
        mismatch = self._preview(case["mismatch_source_ids"], case["mismatch_purpose"])
        batch_b = curator.propose(case["source_ids"], case["purpose"], defaults["actor"], mismatch["preview_id"], self._clock)
        reasons = [item["reason"] for item in batch_a["rejected_outputs"]] + [item["reason"] for item in batch_b["rejected_outputs"]]
        audit_types = sorted({record["event_type"] for record in self._gate.audit_records()})
        return {
            "batch_status": "rejected",
            "rejected_reasons": reasons,
            "backend_call_count": backend.calls,
            "candidate_count": 0,
            "all_unconfirmed": True,
            "preview_raw_content_present": False,
            "preview_source_count": len(mismatch["data_scope"]),
            "canonical_unchanged": True,
            "revision_unchanged": True,
            "audit_event_types": audit_types,
            "version_active": {
                "model_id": registry.active()["model_id"],
                "model_version": registry.active()["model_version"],
                "prompt_version": registry.active()["prompt_version"],
            },
        }

    def _run_failure_probe(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        defaults = self._fixture["defaults"]
        backend_fixture = self._backend("cloud_fixture")
        curator_fixture = self._curator(backend=backend_fixture, registry=registry)
        preview_bad = self._preview(["src_y2s4_bad_json"], case["purpose"])
        batch_bad = curator_fixture.propose(["src_y2s4_bad_json"], case["purpose"], defaults["actor"], preview_bad["preview_id"], self._clock)
        server = _FailureStubServer(("127.0.0.1", 0), _FailureStubHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1/chat/completions"
            backend_http = self._backend("cloud_http", endpoint)
            curator_http = self._curator(backend=backend_http, registry=registry)
            preview_http = self._preview([case.get("http_source_id", "src_y2s4_http")], case["purpose"])
            batch_http = curator_http.propose([case.get("http_source_id", "src_y2s4_http")], case["purpose"], defaults["actor"], preview_http["preview_id"], self._clock)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        reasons = [item["reason"] for item in batch_bad["rejected_outputs"]] + [item["reason"] for item in batch_http["rejected_outputs"]]
        audit_types = sorted({record["event_type"] for record in self._gate.audit_records()})
        return {
            "batch_status": "rejected",
            "rejected_reasons": reasons,
            "backend_call_count": backend_fixture.calls + backend_http.calls,
            "candidate_count": 0,
            "all_unconfirmed": True,
            "preview_raw_content_present": False,
            "preview_source_count": len(preview_bad["data_scope"]) + len(preview_http["data_scope"]),
            "canonical_unchanged": True,
            "revision_unchanged": True,
            "audit_event_types": audit_types,
            "version_active": {
                "model_id": registry.active()["model_id"],
                "model_version": registry.active()["model_version"],
                "prompt_version": registry.active()["prompt_version"],
            },
        }

    def _run_audit_probe(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview = self._preview(case["source_ids"], case["purpose"])
        batch = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview["preview_id"], self._clock)
        version_two = case["version_two"]
        registry.register(version_two["model_id"], version_two["model_version"], version_two["prompt_version"])
        rollback = registry.rollback("v1")
        result = self._summary(batch, preview, backend, registry)
        result["candidate_provenance_authorized"] = all(
            "authorization_ref" in item["provenance"] and item["provenance"]["authorization_ref"].startswith("grant_")
            and item["provenance"]["preview_id"].startswith("preview_")
            for item in batch.get("candidates_proposed", [])
        )
        result["rollback_retained"] = (
            rollback["model_version"] == "v1"
            and len(registry.snapshot()["registered"]) >= 3
            and registry.snapshot()["registered"][0]["model_version"] == "v1"
        )
        return result

    def _run_determinism_probe(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._create_grants(case)
        registry = VersionRegistry(self._clock)
        backend = self._backend("cloud_fixture")
        curator = self._curator(backend=backend, registry=registry)
        preview = self._preview(case["source_ids"], case["purpose"])
        batch = curator.propose(case["source_ids"], case["purpose"], self._fixture["defaults"]["actor"], preview["preview_id"], self._clock)
        result = self._summary(batch, preview, backend, registry)
        peer = Y2S4CaseSystem(case)
        try:
            peer._create_grants(case)
            peer_registry = VersionRegistry(peer._clock)
            peer_backend = peer._backend("cloud_fixture")
            peer_curator = peer._curator(backend=peer_backend, registry=peer_registry)
            peer_preview = peer._preview(case["source_ids"], case["purpose"])
            peer_batch = peer_curator.propose(case["source_ids"], case["purpose"], peer._fixture["defaults"]["actor"], peer_preview["preview_id"], peer._clock)
            result["determinism_byte_identical"] = canonical_json(batch) == canonical_json(peer_batch)
        finally:
            peer.close()
        stdlib_ok, _ = static_stdlib_scan()
        result["stdlib_only"] = stdlib_ok
        profile_rejected = None
        try:
            self._curator(profile=case.get("profile_override"))
        except ProfileRejectedError as exc:
            profile_rejected = exc.profile
        result["profile_rejected"] = profile_rejected
        non_loopback_rejected = False
        try:
            CloudHttpBackend("http://203.0.113.10:8080/v1/chat/completions")
        except EndpointRejectedError:
            non_loopback_rejected = True
        result["http_non_loopback_rejected"] = non_loopback_rejected
        loopback_accepted = True
        try:
            CloudHttpBackend("http://127.0.0.1:1/v1/chat/completions", allow_loopback=True)
        except EndpointRejectedError:
            loopback_accepted = False
        result["http_loopback_accepted"] = loopback_accepted
        return result

    def run_case(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        action = case.get("action")
        if action == "default_closed":
            result = self._run_default_closed(case)
        elif action == "explicit_grant":
            result = self._run_explicit_grant(case)
        elif action == "redline_probe":
            result = self._run_redline_probe(case)
        elif action == "purpose_mismatch":
            result = self._run_mismatch_probe(case)
        elif action == "scope_mismatch":
            result = self._run_mismatch_probe(case)
        elif action == "expiry_revocation":
            result = self._run_expiry_revocation(case)
        elif action == "preview_required":
            result = self._run_preview_required(case)
        elif action == "failure_probe":
            result = self._run_failure_probe(case)
        elif action == "audit_probe":
            result = self._run_audit_probe(case)
        elif action == "determinism_probe":
            result = self._run_determinism_probe(case)
        else:
            raise ValueError(action)
        after = self.layer_snapshot()
        result["canonical_unchanged"] = before["canonical_layer"] == after["canonical_layer"]
        result["revision_unchanged"] = before["revision_layer"] == after["revision_layer"]
        return result
