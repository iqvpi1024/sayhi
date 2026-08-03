"""Y2-S2 testing adapter: materializes synthetic sources and runs contract cases.

Environment isolation: every case lives in a TemporaryDirectory; timestamps come
from the fixture clock; HTTP is only the loopback stub server used by scenario
Y2S2-007.
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

from .model_capability import (
    EndpointRejectedError,
    FixtureModelBackend,
    LocalHttpBackend,
    ModelCurator,
    ProfileRejectedError,
    UnconfirmedCandidateError,
    UnregisteredVersionError,
    VersionRegistry,
    canonical_json,
)
from .store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "y2s2_local_model_v1" / "fixture.json"


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _finalize(store: SemanticStore, path: Path) -> None:
    try:
        store.close()
    except Exception:
        pass
    shutil.rmtree(path, ignore_errors=True)


class _CloudProbe:
    kind = "cloud"

    def __init__(self) -> None:
        self.calls = 0

    def propose(self, source: Mapping[str, Any]) -> str:
        self.calls += 1
        raise AssertionError("cloud backend must never be called in Y2-S2")


class _StubHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        body = json.dumps(
            {"choices": [{"message": {"content": self.server.raw}}]},
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


class _StubServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], handler_class: type[BaseHTTPRequestHandler], raw: str) -> None:
        self.raw = raw
        super().__init__(server_address, handler_class)


def create_system(case: Mapping[str, Any]) -> "Y2S2CaseSystem":
    return Y2S2CaseSystem(case)


class Y2S2CaseSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._case = dict(case)
        self._fixture = _fixture()
        self._clock = self._fixture["determinism"]["clock"]
        self._tmp_path = Path(tempfile.mkdtemp())
        self._store = SemanticStore(self._tmp_path / "noetide.sqlite3")
        self._store.add_revision("rev_000", self._clock, "seed")
        self._finalizer = weakref.finalize(self, _finalize, self._store, self._tmp_path)
        self._materialize_sources(self._fixture["sources"])

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
                "actor": "y2s2_adapter",
            }
            self._store.append_source(dict(source), receipt)

    # -- backend helpers --------------------------------------------------

    def _raw_response(self, content_hash: str) -> str:
        entry = self._fixture["model_responses"][content_hash]
        if entry["kind"] == "valid":
            return json.dumps(entry["raw_json"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return entry["raw"]

    def _responses(self) -> dict[str, str]:
        return {content_hash: self._raw_response(content_hash) for content_hash in self._fixture["model_responses"]}

    def _curator(self, case: Mapping[str, Any], backend: Any | None = None, version: Mapping[str, Any] | None = None) -> ModelCurator:
        config = dict(case["backend"])
        if version:
            config.update(version)
        if backend is None:
            if config["kind"] != "fixture":
                raise ValueError("non-fixture backend must be provided by the case runner")
            backend = FixtureModelBackend(self._responses())
        profile = case.get("profile_override", "y2s2_local_model_v1")
        return ModelCurator(
            self._store,
            backend,
            self._clock,
            config["model_id"],
            config["model_version"],
            config["prompt_version"],
            profile=profile,
        )

    def _unchanged(self, before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, bool]:
        return {
            "canonical_unchanged": before["canonical_layer"] == after["canonical_layer"],
            "revision_unchanged": before["revision_layer"] == after["revision_layer"],
        }

    # -- protocol ---------------------------------------------------------

    def layer_snapshot(self) -> dict[str, Any]:
        return {
            "canonical_layer": self._store.canonical_layer_digest(),
            "revision_layer": self._store.current_revision(),
        }

    def run_case(self, case: Mapping[str, Any]) -> dict[str, Any]:
        action = case["action"]
        if action == "propose":
            return self._run_propose(case)
        if action == "inspect":
            return self._run_inspect(case)
        if action == "malformed":
            return self._run_malformed(case)
        if action == "injection_probe":
            return self._run_injection(case)
        if action == "canonical_guard":
            return self._run_canonical_guard(case)
        if action == "redline_probe":
            return self._run_redline(case)
        if action == "local_http_probe":
            return self._run_local_http(case)
        if action == "version_probe":
            return self._run_version(case)
        if action == "confirmation_probe":
            return self._run_confirmation(case)
        if action == "determinism_probe":
            return self._run_determinism(case)
        raise KeyError(action)

    # -- case runners -----------------------------------------------------

    def _run_propose(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        curator = self._curator(case)
        batch = curator.propose(list(case["source_ids"]))
        after = self.layer_snapshot()
        return {
            "batch": batch,
            "candidates": batch["candidates_proposed"],
            "all_unconfirmed": all(item["review_status"] == "unconfirmed" for item in batch["candidates_proposed"]),
            **self._unchanged(before, after),
        }

    def _run_inspect(self, case: Mapping[str, Any]) -> dict[str, Any]:
        curator = self._curator(case)
        batch = curator.propose(list(case["source_ids"]))
        peer = Y2S2CaseSystem(case)
        try:
            peer_batch = peer._curator(case).propose(list(case["source_ids"]))
            identical = canonical_json(batch) == canonical_json(peer_batch)
        finally:
            peer.close()
        candidates = batch["candidates_proposed"]
        checks = {
            "candidate_id_prefix": all(item["candidate_id"].startswith("cand_") for item in candidates),
            "candidate_id_length": all(len(item["candidate_id"]) == 21 for item in candidates),
            "review_status_closed": all(item["review_status"] == "unconfirmed" for item in candidates),
            "evidence_refs_all_imported": all(
                ref["source_id"] in set(case["source_ids"])
                for item in candidates
                for ref in item["evidence_refs"]
            ),
            "provenance_complete": all(
                {"model_id", "model_version", "prompt_version", "backend_kind", "proposed_at"}
                <= set(item["provenance"])
                for item in candidates
            ),
        }
        return {"candidates": candidates, "field_checks": checks, "determinism_byte_identical": identical}

    def _run_malformed(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        curator = self._curator(case)
        batch = curator.propose(list(case["source_ids"]))
        after = self.layer_snapshot()
        return {
            "batch": batch,
            "zero_candidates": len(batch["candidates_proposed"]) == 0,
            **self._unchanged(before, after),
        }

    def _run_injection(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        clean_curator = self._curator(case)
        clean_batch = clean_curator.propose([case["clean_source_id"]])
        escalated_curator = self._curator(case)
        escalated_batch = escalated_curator.propose([case["escalated_source_id"]])
        after = self.layer_snapshot()
        return {
            "clean_source_batch": clean_batch,
            "clean_all_unconfirmed": all(
                item["review_status"] == "unconfirmed" for item in clean_batch["candidates_proposed"]
            ),
            "escalated_batch": escalated_batch,
            "escalated_zero_candidates": len(escalated_batch["candidates_proposed"]) == 0,
            **self._unchanged(before, after),
        }

    def _run_canonical_guard(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        curator = self._curator(case)
        batch = curator.propose(list(case["source_ids"]))
        after = self.layer_snapshot()
        snapshot = self._store.seed_snapshot()
        candidate_ids = {item["candidate_id"] for item in batch["candidates_proposed"]}
        not_in_canonical = not any(object_id in candidate_ids for object_id in snapshot["objects"])
        not_in_evidence = not any(
            ref.get("source_id") in candidate_ids
            for obj in snapshot["objects"].values()
            for ref in obj.get("evidence_refs", [])
        )
        return {
            "candidates": batch["candidates_proposed"],
            **self._unchanged(before, after),
            "candidate_ids_not_in_canonical": not_in_canonical,
            "candidate_ids_not_in_evidence": not_in_evidence,
        }

    def _run_redline(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        curator = self._curator(case)
        batch = curator.propose(list(case["source_ids"]))
        after = self.layer_snapshot()
        cloud = _CloudProbe()
        cloud_rejected = False
        try:
            ModelCurator(
                self._store,
                cloud,
                self._clock,
                "model_fixture_v1",
                "v1",
                "prompt_v1",
            )
        except EndpointRejectedError:
            cloud_rejected = True
        return {
            "fixture_allowed": {
                "candidates_proposed": len(batch["candidates_proposed"]),
                "all_unconfirmed": all(
                    item["review_status"] == "unconfirmed" for item in batch["candidates_proposed"]
                ),
            },
            "cloud_rejected": cloud_rejected,
            "cloud_backend_not_called": cloud.calls == 0,
            **self._unchanged(before, after),
        }

    def _run_local_http(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        source = self._store.seeded_source(case["source_ids"][0])
        if source is None:
            raise KeyError(case["source_ids"][0])
        raw = self._raw_response(source["content_hash"])
        server = _StubServer(("127.0.0.1", 0), _StubHandler, raw)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1/chat/completions"
            backend = LocalHttpBackend(endpoint)
            config = case["backend"]
            curator = ModelCurator(
                self._store,
                backend,
                self._clock,
                config["model_id"],
                config["model_version"],
                config["prompt_version"],
            )
            batch = curator.propose(list(case["source_ids"]))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        after = self.layer_snapshot()
        non_loopback_rejected = False
        try:
            LocalHttpBackend("http://203.0.113.10:8080/v1/chat/completions")
        except EndpointRejectedError:
            non_loopback_rejected = True
        return {
            "batch": batch,
            "candidates": batch["candidates_proposed"],
            "all_unconfirmed": all(
                item["review_status"] == "unconfirmed" for item in batch["candidates_proposed"]
            ),
            "non_loopback_rejected": non_loopback_rejected,
            **self._unchanged(before, after),
        }

    def _run_version(self, case: Mapping[str, Any]) -> dict[str, Any]:
        backend = FixtureModelBackend(self._responses())
        registry = VersionRegistry(self._clock)
        registry.register("model_fixture_v1", "v1", "prompt_v1")
        curator_v1 = ModelCurator(
            self._store,
            backend,
            self._clock,
            "model_fixture_v1",
            "v1",
            "prompt_v1",
            registry=registry,
        )
        batch_v1 = curator_v1.propose(list(case["source_ids"]))
        registry.register("model_fixture_v1", "v2", "prompt_v2")
        curator_v2 = ModelCurator(
            self._store,
            backend,
            self._clock,
            "model_fixture_v1",
            "v2",
            "prompt_v2",
            registry=registry,
        )
        batch_v2 = curator_v2.propose(list(case["source_ids"]))
        unregistered_rejected = False
        try:
            registry.activate(
                model_id=case["unregistered"]["model_id"],
                model_version=case["unregistered"]["model_version"],
                prompt_version=case["unregistered"]["prompt_version"],
            )
        except UnregisteredVersionError:
            unregistered_rejected = True
        rollback = registry.rollback("v1")
        separated = all(
            item["provenance"]["model_version"] == "v1" for item in batch_v1["candidates_proposed"]
        ) and all(item["provenance"]["model_version"] == "v2" for item in batch_v2["candidates_proposed"])
        snapshot = registry.snapshot()
        history_retained = len(snapshot["registered"]) >= 3 and snapshot["registered"][0]["model_version"] == "v1"
        return {
            "v1_candidates": batch_v1["candidates_proposed"],
            "v2_candidates": batch_v2["candidates_proposed"],
            "provenance_separated": separated,
            "unregistered_activation_rejected": unregistered_rejected,
            "rollback_active": {
                "model_id": rollback["model_id"],
                "model_version": rollback["model_version"],
                "prompt_version": rollback["prompt_version"],
            },
            "history_retained": history_retained,
        }

    def _run_confirmation(self, case: Mapping[str, Any]) -> dict[str, Any]:
        before = self.layer_snapshot()
        curator = self._curator(case)
        curator.propose(list(case["source_ids"]))
        confirmed = curator.confirm_candidate(case["confirm_candidate_id"], case["actor"])
        after = self.layer_snapshot()
        rejected = False
        try:
            curator.propose_changeset_for_candidate(case["unconfirmed_candidate_id"], case["actor"])
        except UnconfirmedCandidateError:
            rejected = True
        not_published = (
            confirmed["status"] == "proposed"
            and confirmed["published_revision"] is None
            and self._store.ledger_records_of_type("receipt") == []
        )
        return {
            "confirmed_changeset": confirmed,
            "unconfirmed_changeset_rejected": rejected,
            "changeset_not_published": not_published,
            **self._unchanged(before, after),
        }

    def _run_determinism(self, case: Mapping[str, Any]) -> dict[str, Any]:
        normal_case = {key: value for key, value in case.items() if key != "profile_override"}
        profile_rejected = None
        try:
            ModelCurator(
                self._store,
                FixtureModelBackend(self._responses()),
                self._clock,
                case["backend"]["model_id"],
                case["backend"]["model_version"],
                case["backend"]["prompt_version"],
                profile=case["profile_override"],
            )
        except ProfileRejectedError as exc:
            profile_rejected = exc.profile
        before = self.layer_snapshot()
        curator = self._curator(normal_case)
        batch = curator.propose(list(normal_case["source_ids"]))
        after = self.layer_snapshot()
        peer = Y2S2CaseSystem(normal_case)
        try:
            peer_batch = peer._curator(normal_case).propose(list(normal_case["source_ids"]))
            identical = canonical_json(batch) == canonical_json(peer_batch)
        finally:
            peer.close()
        non_loopback_rejected = False
        try:
            LocalHttpBackend("http://203.0.113.10:8080/v1/chat/completions")
        except EndpointRejectedError:
            non_loopback_rejected = True
        snapshot = self._store.seed_snapshot()
        candidate_ids = {item["candidate_id"] for item in batch["candidates_proposed"]}
        not_in_canonical = not any(object_id in candidate_ids for object_id in snapshot["objects"])
        return {
            "determinism_byte_identical": identical,
            "profile_rejected": profile_rejected,
            **self._unchanged(before, after),
            "non_loopback_rejected": non_loopback_rejected,
            "candidate_ids_not_in_canonical": not_in_canonical,
        }