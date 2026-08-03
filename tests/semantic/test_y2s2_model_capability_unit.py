"""Focused unit tests for Y2-S2 model capability boundaries."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

from noetide_micro.model_capability import (
    CandidateNotFoundError,
    EndpointRejectedError,
    FixtureModelBackend,
    LocalHttpBackend,
    ModelCurator,
    ProfileRejectedError,
    UnconfirmedCandidateError,
    UnregisteredVersionError,
    VersionRegistry,
)
from noetide_micro.store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/y2s2_local_model_v1/fixture.json").read_text(encoding="utf-8"))
CLOCK = FIXTURE["determinism"]["clock"]


class Y2S2UnitBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = Path(tempfile.mkdtemp())
        self.store = SemanticStore(self._tmp / "noetide.sqlite3")
        self.store.add_revision("rev_000", CLOCK, "seed")
        self.sources = {source["source_id"]: source for source in FIXTURE["sources"]}
        self.responses = {}
        for content_hash, entry in FIXTURE["model_responses"].items():
            if entry["kind"] == "valid":
                raw = json.dumps(entry["raw_json"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            else:
                raw = entry["raw"]
            self.responses[content_hash] = raw

    def tearDown(self) -> None:
        try:
            self.store.close()
        finally:
            shutil.rmtree(self._tmp, ignore_errors=True)

    def append_source(self, source_id: str) -> None:
        source = self.sources[source_id]
        if source["content_hash"] != hashlib.sha256(source["content"].encode("utf-8")).hexdigest():
            raise ValueError(source_id)
        receipt = {"receipt_id": source["append_receipt_id"], "source_id": source_id, "status": "stored", "actor": "unit"}
        self.store.append_source(dict(source), receipt)

    def curator(self, version: str = "v1", prompt: str = "prompt_v1", backend: Any | None = None) -> ModelCurator:
        return ModelCurator(
            self.store,
            backend if backend is not None else FixtureModelBackend(self.responses),
            CLOCK,
            "model_fixture_v1",
            version,
            prompt,
        )


class ModelCapabilityUnitTests(Y2S2UnitBase):
    def test_fixture_propose_is_derived_and_unconfirmed(self) -> None:
        self.append_source("src_y2s2_001")
        self.append_source("src_y2s2_002")
        before = self.store.canonical_layer_digest()
        batch = self.curator().propose(["src_y2s2_001", "src_y2s2_002"])
        self.assertEqual(len(batch["candidates_proposed"]), 3)
        self.assertTrue(all(item["review_status"] == "unconfirmed" for item in batch["candidates_proposed"]))
        self.assertEqual(self.store.canonical_layer_digest(), before)
        self.assertTrue(all(item["candidate_id"].startswith("cand_") for item in batch["candidates_proposed"]))

    def test_malformed_output_rejects_whole_batch(self) -> None:
        for source_id in ("src_y2s2_bad_json", "src_y2s2_bad_missing", "src_y2s2_bad_kind"):
            self.append_source(source_id)
        batch = self.curator().propose(["src_y2s2_bad_json", "src_y2s2_bad_missing", "src_y2s2_bad_kind"])
        self.assertEqual(batch["candidates_proposed"], [])
        self.assertEqual(
            [item["reason"] for item in batch["rejected_outputs"]],
            ["invalid_json", "missing_field", "unknown_kind"],
        )

    def test_escalation_fields_reject_batch(self) -> None:
        self.append_source("src_y2s2_004")
        batch = self.curator().propose(["src_y2s2_004"])
        self.assertEqual(batch["candidates_proposed"], [])
        self.assertEqual(batch["rejected_outputs"][0]["reason"], "escalation_field")

    def test_cloud_kind_is_rejected_before_backend_call(self) -> None:
        class CloudProbe:
            kind = "cloud"
            calls = 0

            def propose(self, source: dict[str, Any]) -> str:
                type(self).calls += 1
                raise AssertionError("must not be called")

        probe = CloudProbe()
        with self.assertRaises(EndpointRejectedError):
            self.curator(backend=probe)
        self.assertEqual(probe.calls, 0)

    def test_non_loopback_endpoint_is_rejected_at_construction(self) -> None:
        with self.assertRaises(EndpointRejectedError):
            LocalHttpBackend("http://203.0.113.10:8080/v1/chat/completions")

    def test_profile_fail_closed(self) -> None:
        with self.assertRaises(ProfileRejectedError):
            ModelCurator(
                self.store,
                FixtureModelBackend(self.responses),
                CLOCK,
                "model_fixture_v1",
                "v1",
                "prompt_v1",
                profile="y2s2_unknown_profile_v9",
            )

    def test_version_registry_rollback_and_unregistered_activation(self) -> None:
        registry = VersionRegistry(CLOCK)
        registry.register("model_fixture_v1", "v1", "prompt_v1")
        registry.register("model_fixture_v1", "v2", "prompt_v2")
        with self.assertRaises(UnregisteredVersionError):
            registry.activate("model_fixture_v1", "v9", "prompt_v9")
        rollback = registry.rollback("v1")
        self.assertEqual(rollback["model_version"], "v1")
        self.assertGreaterEqual(len(registry.snapshot()["registered"]), 3)

    def test_confirmation_requires_explicit_user_action(self) -> None:
        self.append_source("src_y2s2_001")
        self.append_source("src_y2s2_002")
        curator = self.curator()
        batch = curator.propose(["src_y2s2_001", "src_y2s2_002"])
        commitment = next(item for item in batch["candidates_proposed"] if item["candidate_kind"] == "commitment")
        with self.assertRaises(UnconfirmedCandidateError):
            curator.propose_changeset_for_candidate(commitment["candidate_id"], "person_alpha")
        confirmed = curator.confirm_candidate(batch["candidates_proposed"][0]["candidate_id"], "person_alpha")
        self.assertEqual(confirmed["status"], "proposed")
        self.assertIsNone(confirmed["published_revision"])
        with self.assertRaises(CandidateNotFoundError):
            curator.confirm_candidate("cand_missing_0000000000000000", "person_alpha")


if __name__ == "__main__":
    unittest.main()