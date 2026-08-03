"""Focused unit tests for Y2-S4 cloud model authorization boundaries."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.cloud_model import (
    CloudFixtureBackend,
    CloudGate,
    CloudHttpBackend,
    CloudModelCurator,
    EndpointRejectedError,
    static_stdlib_scan,
)
from noetide_micro.model_capability import VersionRegistry
from noetide_micro.store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/y2s4_cloud_model_v1/fixture.json"


class Y2S4UnitBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.clock = self.fixture["determinism"]["clock"]
        self.store = SemanticStore(self.root / "noetide.sqlite3")
        self.store.add_revision("rev_000", self.clock, "seed")
        self.gate = CloudGate(self.store, self.clock)
        for source in self.fixture["sources"]:
            content = source["content"].encode("utf-8")
            self.assertEqual(source["content_hash"], hashlib.sha256(content).hexdigest())
            self.store.append_source(
                dict(source),
                {
                    "receipt_id": source["append_receipt_id"],
                    "source_id": source["source_id"],
                    "status": "stored",
                    "actor": "y2s4_unit",
                },
            )

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def responses(self) -> dict[str, object]:
        return {
            source["content_hash"]: self.fixture["model_responses"][source["source_id"]]
            for source in self.fixture["sources"]
            if source["source_id"] in self.fixture["model_responses"]
        }

    def curator(self, registry=None, backend=None) -> CloudModelCurator:
        defaults = self.fixture["defaults"]
        return CloudModelCurator(
            self.store,
            self.gate,
            backend or CloudFixtureBackend(self.responses()),
            self.clock,
            defaults["model_id"],
            defaults["model_version"],
            defaults["prompt_version"],
            registry=registry,
        )

    def grant(self, source_ids, grant_id="grant_unit_001", purpose="summarize") -> dict[str, object]:
        return self.gate.create_grant(
            {
                "grant_id": grant_id,
                "actor": "person_alpha",
                "purpose": purpose,
                "compartments": ["general"],
                "source_scope": {"source_ids": list(source_ids)},
                "expires_at": "2026-08-04T00:00:00+00:00",
            }
        )


class CloudModelUnitTests(Y2S4UnitBase):
    def test_default_closed_and_red_line_deny_without_calls(self) -> None:
        backend = CloudFixtureBackend(self.responses())
        curator = self.curator(backend=backend)
        preview = self.gate.build_preview(["src_y2s4_001"], "summarize", "person_alpha", self.clock)
        batch = curator.propose(["src_y2s4_001"], "summarize", "person_alpha", preview["preview_id"], self.clock)
        self.assertEqual(batch["status"], "rejected")
        self.assertEqual(batch["rejected_outputs"][0]["reason"], "default_disabled")
        self.gate.create_grant(
            {
                "grant_id": "grant_redline",
                "actor": "person_alpha",
                "purpose": "summarize",
                "compartments": ["health", "general"],
                "source_scope": {"source_ids": ["src_y2s4_003"]},
                "expires_at": "2026-08-04T00:00:00+00:00",
            }
        )
        preview_red = self.gate.build_preview(["src_y2s4_003"], "summarize", "person_alpha", self.clock)
        batch_red = curator.propose(["src_y2s4_003"], "summarize", "person_alpha", preview_red["preview_id"], self.clock)
        self.assertEqual(batch_red["rejected_outputs"][0]["reason"], "red_line_denied")
        self.assertEqual(backend.calls, 0)
        self.assertEqual(self.store.current_revision(), "rev_000")

    def test_grant_preview_audit_and_canonical_guard(self) -> None:
        before = self.store.canonical_layer_digest()
        self.grant(["src_y2s4_001", "src_y2s4_002"])
        backend = CloudFixtureBackend(self.responses())
        registry = VersionRegistry(self.clock)
        curator = self.curator(backend=backend, registry=registry)
        preview = self.gate.build_preview(["src_y2s4_001", "src_y2s4_002"], "summarize", "person_alpha", self.clock)
        batch = curator.propose(
            ["src_y2s4_001", "src_y2s4_002"], "summarize", "person_alpha", preview["preview_id"], self.clock
        )
        self.assertEqual(batch["status"], "accepted")
        self.assertEqual(len(batch["candidates_proposed"]), 3)
        self.assertTrue(all(item["review_status"] == "unconfirmed" for item in batch["candidates_proposed"]))
        self.assertFalse(any(entry["raw_content_present"] for entry in preview["data_scope"]))
        types = {record["event_type"] for record in self.gate.audit_records()}
        self.assertTrue({"grant_created", "preview_built", "send_allowed", "send_succeeded"} <= types)
        self.assertEqual(self.store.canonical_layer_digest(), before)
        self.assertEqual(self.store.current_revision(), "rev_000")

    def test_preview_required_and_revocation_fail_closed(self) -> None:
        self.grant(["src_y2s4_001"])
        curator = self.curator()
        missing = curator.propose(["src_y2s4_001"], "summarize", "person_alpha", None, self.clock)
        self.assertEqual(missing["rejected_outputs"][0]["reason"], "preview_missing")
        self.gate.revoke_grant("grant_unit_001")
        preview = self.gate.build_preview(["src_y2s4_001"], "summarize", "person_alpha", self.clock)
        revoked = curator.propose(["src_y2s4_001"], "summarize", "person_alpha", preview["preview_id"], self.clock)
        self.assertEqual(revoked["rejected_outputs"][0]["reason"], "grant_revoked")
        self.assertEqual(curator.backend.calls, 0)

    def test_endpoint_validation_and_stdlib_scan(self) -> None:
        with self.assertRaises(EndpointRejectedError):
            CloudHttpBackend("http://203.0.113.10:8080/v1/chat/completions")
        CloudHttpBackend("https://example.com/v1/chat/completions")
        CloudHttpBackend("http://127.0.0.1:8080/v1/chat/completions", allow_loopback=True)
        ok, external = static_stdlib_scan()
        self.assertTrue(ok, external)

    def test_version_rollback_retains_history(self) -> None:
        registry = VersionRegistry(self.clock)
        curator = self.curator(registry=registry)
        self.grant(["src_y2s4_001"])
        preview = self.gate.build_preview(["src_y2s4_001"], "summarize", "person_alpha", self.clock)
        curator.propose(["src_y2s4_001"], "summarize", "person_alpha", preview["preview_id"], self.clock)
        registry.register("model_cloud_v1", "v2", "prompt_v2")
        rollback = registry.rollback("v1")
        self.assertEqual(rollback["model_version"], "v1")
        self.assertEqual(registry.active()["model_version"], "v1")
        self.assertEqual(len(registry.snapshot()["registered"]), 3)
