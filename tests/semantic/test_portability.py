from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.portability import ContextPackExporter, ContextPackVerifier
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


def scenario(identifier: str):
    def decorate(method):
        method._noetide_scenario_id = identifier
        return method
    return decorate


class ContextPackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = SemanticStore(self.root / "state.sqlite3")
        self.addCleanup(self.store.close)
        self.store.seed_rev_010(demo_fixture())
        self.exporter = ContextPackExporter("2031-10-15T02:00:00Z")
        self.verifier = ContextPackVerifier()

    def export(self, name: str) -> Path:
        target = self.root / name
        self.exporter.export(self.store, target)
        return target

    @scenario("CP-001")
    def test_export_is_independently_readable_and_hashed(self) -> None:
        pack = self.export("pack")
        self.assertEqual(self.verifier.verify(pack, self.store.current_revision())["status"], "validated")
        self.assertEqual(set(path.name for path in pack.iterdir()), {"manifest.json", "sources.json", "canonical.json", "ledger.json", "README.md", "checksums.sha256"})

    @scenario("CP-002")
    def test_tamper_rejects_without_store_write(self) -> None:
        pack = self.export("pack")
        before = self.store.portability_snapshot()
        (pack / "canonical.json").write_text("{}\n", encoding="utf-8")
        self.assertEqual(self.verifier.verify(pack)["status"], "rejected_hash_mismatch")
        self.assertEqual(self.store.portability_snapshot(), before)

    @scenario("CP-003")
    def test_unknown_namespaced_field_round_trips(self) -> None:
        entity = self.store.canonical_object("person_alpha")
        entity["x.synthetic.extension"] = {"kind": "nested", "value": [1, {"flag": True}]}
        self.store.replace_canonical_object("person_alpha", entity)
        result = self.verifier.verify(self.export("pack"), self.store.current_revision())
        round_tripped = next(item for item in result["snapshot"]["canonical"] if item["entity_id"] == "person_alpha")
        self.assertEqual(round_tripped["x.synthetic.extension"], entity["x.synthetic.extension"])

    @scenario("CP-004")
    def test_unsafe_manifest_reference_is_rejected(self) -> None:
        pack = self.export("pack")
        manifest_path = pack / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["entries"][0]["content_ref"] = "../outside.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(self.verifier.verify(pack)["status"], "rejected_path")

    @scenario("CP-005")
    def test_old_pack_is_not_mutated_by_later_export(self) -> None:
        first = self.export("first")
        before = {path.name: path.read_bytes() for path in first.iterdir()}
        self.export("second")
        self.assertEqual({path.name: path.read_bytes() for path in first.iterdir()}, before)
        self.assertEqual(self.verifier.verify(first, self.store.current_revision())["pack_relation"], "current")

    @scenario("CP-006")
    def test_projection_payload_is_not_exported_as_evidence(self) -> None:
        projection = self.store.projection_record("person_card")
        self.store.replace_projection("person_card", projection["data_revision"], projection["view_revision"], "fresh", {"derived_only_sentinel": "not_evidence"})
        pack = self.export("pack")
        content = b"".join((pack / name).read_bytes() for name in ("sources.json", "canonical.json", "ledger.json"))
        self.assertNotIn(b"derived_only_sentinel", content)
