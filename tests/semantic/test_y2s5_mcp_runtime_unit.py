"""Focused unit tests for Y2-S5 MCP runtime boundaries."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.mcp_runtime import (
    CONTRACT_VERSION,
    MAX_SOURCE_BYTES,
    McpRuntime,
    McpService,
    ProfileRejectedError,
    static_stdlib_scan,
)
from noetide_micro.store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/y2s5_mcp_runtime_v1/fixture.json"


class Y2S5UnitBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.clock = self.fixture["determinism"]["clock"]
        self.store = SemanticStore(self.root / "noetide.sqlite3", check_same_thread=False)
        for view in self.fixture["views"].values():
            self.store.add_revision(view["view_revision"], self.clock, "seed")
        self.store.add_revision("rev_000", self.clock, "seed")
        for source in self.fixture["sources"]:
            self.store.append_source(dict(source), {
                "receipt_id": source["append_receipt_id"],
                "source_id": source["source_id"],
                "status": "stored",
                "actor": "y2s5_unit",
            })
        for name, projection in self.fixture["views"].items():
            self.store.upsert_projection(
                name,
                projection["data_revision"],
                projection["view_revision"],
                projection["freshness_status"],
                projection["payload"],
            )
        self.runtime = McpRuntime(self.store, self.clock)

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def full_capability(self) -> dict[str, object]:
        return {
            "capability_id": "cap_unit_full",
            "actor": "person_alpha",
            "purpose": "review",
            "tools": ["list_resources", "read_resource", "propose_changeset", "record_source"],
            "resource_ids": ["src_y2s5_001", "src_y2s5_002", "person_card"],
            "resource_fields": {"read_resource": ["metadata", "content"]},
            "expires_at": "2026-08-04T00:00:00+00:00",
        }

    def call(
        self,
        action: str,
        resource_ids: list[str],
        payload: dict[str, object] | None = None,
        capability: str = "cap_unit_full",
        idem: str | None = None,
        precondition: str | None = None,
    ) -> dict[str, object]:
        request: dict[str, object] = {
            "contract_version": CONTRACT_VERSION,
            "request_id": "req_unit_001",
            "caller_ref": "person_alpha",
            "purpose": "review",
            "capability_ref": capability,
            "action": action,
            "scope": {"resource_ids": resource_ids},
            "requested_at": self.clock,
        }
        if idem is not None:
            request["idempotency_key"] = idem
        if precondition is not None:
            request["data_revision_precondition"] = precondition
        return self.runtime.handle_request(request, payload)


class McpRuntimeUnitTests(Y2S5UnitBase):
    def test_default_closed_denied_profile(self) -> None:
        response = self.call(
            "read_resource",
            ["src_y2s5_001"],
            {"resource_id": "src_y2s5_001"},
            capability="missing",
        )
        self.assertEqual(response["authorization"], "denied")
        self.assertEqual(response["result_status"], "denied")
        self.assertEqual(response["data_revision"], "withheld")
        self.assertEqual(response["payload"], "withheld")
        self.assertEqual(response["error"], {"code": "denied", "message": "denied"})

    def test_authorized_read_returns_minimal_fields(self) -> None:
        self.runtime.create_capability(self.full_capability())
        response = self.call(
            "read_resource",
            ["src_y2s5_001"],
            {"resource_id": "src_y2s5_001", "fields": ["metadata", "content"]},
        )
        self.assertEqual(response["result_status"], "ok")
        self.assertEqual(response["authorization"], "allowed")
        self.assertEqual(response["data_revision"], "rev_000")
        self.assertEqual(response["payload"]["source_id"], "src_y2s5_001")
        self.assertEqual(response["payload"]["content"], "今天完成识海实验记录。\n")

    def test_redacted_read_excludes_content(self) -> None:
        capability = self.full_capability()
        capability["resource_fields"] = {"read_resource": ["metadata"]}
        self.runtime.create_capability(capability)
        response = self.call(
            "read_resource",
            ["src_y2s5_001"],
            {"resource_id": "src_y2s5_001", "fields": ["metadata", "content"]},
        )
        self.assertEqual(response["authorization"], "allowed_with_redaction")
        self.assertNotIn("content", response["payload"])

    def test_propose_only_writes_ledger_not_canonical(self) -> None:
        before = self.store.canonical_layer_digest()
        self.runtime.create_capability(self.full_capability())
        candidate = {
            "candidate_kind": "entity",
            "payload": {"display_name": "识海实验"},
            "evidence_refs": [{"source_id": "src_y2s5_001", "locator": {}}],
        }
        response = self.call(
            "propose_changeset",
            ["src_y2s5_001"],
            {"candidate": candidate},
            idem="idem_unit_propose",
        )
        self.assertEqual(response["result_status"], "accepted")
        self.assertTrue(response["receipt_ref"].startswith("changeset_y2s5_"))
        self.assertEqual(len(self.store.ledger_records_of_type("changeset")), 1)
        self.assertEqual(self.store.canonical_layer_digest(), before)

    def test_irreversible_always_denied(self) -> None:
        self.runtime.create_capability(self.full_capability())
        response = self.call(
            "delete_item",
            ["src_y2s5_001"],
            {"answer_status": "verified"},
            idem="idem_unit_delete",
        )
        self.assertEqual(response["authorization"], "denied")
        self.assertEqual(response["error"], {"code": "denied", "message": "denied"})
        self.assertEqual(len(self.store.ledger_records_of_type("changeset")), 0)

    def test_large_file_returns_import_reference(self) -> None:
        capability = self.full_capability()
        capability["resource_ids"] = [*capability["resource_ids"], "src_y2s5_large"]
        self.runtime.create_capability(capability)
        source = {
            "source_id": "src_y2s5_large",
            "source_kind": "y2s5_text_v1",
            "source_created_at": self.clock,
            "language": "zh",
            "locator": {},
            "coverage_window": {},
            "content": "x" * (MAX_SOURCE_BYTES + 1),
            "compartments": ["general"],
        }
        response = self.call(
            "record_source",
            ["src_y2s5_large"],
            {"source": source},
            idem="idem_unit_large",
        )
        self.assertEqual(response["result_status"], "failed")
        self.assertEqual(response["error"]["code"], "large_file_required")
        self.assertEqual(response["payload"]["import_reference_required"], True)

    def test_policy_unavailable_fail_closed(self) -> None:
        runtime = McpRuntime(self.store, self.clock, policy_available=False)
        response = runtime.handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "req_unit_001",
                "caller_ref": "person_alpha",
                "purpose": "review",
                "capability_ref": "missing",
                "action": "read_resource",
                "scope": {"resource_ids": ["src_y2s5_001"]},
                "requested_at": self.clock,
            },
            {"resource_id": "src_y2s5_001"},
        )
        self.assertEqual(response["authorization"], "denied")
        self.assertEqual(response["error"], {"code": "denied", "message": "denied"})

    def test_loopback_and_stdlib_guards(self) -> None:
        with self.assertRaises(ValueError):
            McpService(self.runtime, host="0.0.0.0", port=0, autostart=False)
        with self.assertRaises(ProfileRejectedError):
            McpRuntime(self.store, self.clock, profile="unknown")
        ok, external = static_stdlib_scan()
        self.assertTrue(ok, external)
