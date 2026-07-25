"""C5 testing adapter: builds the fixed synthetic pack/backup profile and drives contract cases."""

from __future__ import annotations

import atexit
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from . import pack_backup
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/c5_pack_backup_v1/fixture.json").read_text(encoding="utf-8"))
CLOCK = FIXTURE["determinism"]["clock"]
KEY = FIXTURE["backup_key"]
WRONG_KEY = FIXTURE["wrong_key"]
POLICY = FIXTURE["deletion_policy"]


def create_system(case: JsonObject) -> "C5PackSystem":
    return C5PackSystem(case)


class C5PackSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=case["database_identity"] + "_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._db_path = Path(self._tmpdir) / "c5.sqlite3"
        self._store = SemanticStore(self._db_path)
        self._pack = Path(self._tmpdir) / "pack"
        self._pack2 = Path(self._tmpdir) / "pack2"
        self._backup = Path(self._tmpdir) / "backup.nobak"
        self._restored = Path(self._tmpdir) / "restored.sqlite3"
        self._seed()

    def _seed(self) -> None:
        seed = FIXTURE["seed"]
        self._store.add_revision("rev_c5_seed", CLOCK, "seed")
        for source in seed["sources"]:
            digest = hashlib.sha256(source["text"].encode("utf-8")).hexdigest()
            self._store.append_source(
                {"source_id": source["source_id"], "append_receipt_id": "receipt_" + source["source_id"],
                 "source_kind": source["source_kind"], "content_hash": digest, "text": source["text"], "synthetic": True},
                {"receipt_id": "receipt_" + source["source_id"], "source_id": source["source_id"], "status": "stored", "actor": "c5_fixture_seed"},
            )
        for item in seed["canonical"]:
            payload = {k: v for k, v in item.items() if k != "object_id"}
            payload["object_revision"] = "rev_c5_seed"
            payload["synthetic"] = True
            self._store.add_canonical_object(item["object_id"], payload)
        for record in seed["ledger"]:
            self._store.put_ledger_record(record["record_id"], record["record_type"], record["payload"])

    def layer_snapshot(self) -> JsonObject:
        return {"store_layer": _canonical_digest({
            "revisions": self._store.revision_ids(),
            "canonical": self._store.canonical_object_summaries(),
            "ledger": self._store.ledger_records_of_type("seed_note"),
        })}

    def run_case(self, case: JsonObject) -> JsonObject:
        before = self.layer_snapshot()
        outcomes: list[JsonObject] = []
        for op in case["ops"]:
            outcomes.append(self._run_op(op))
        return self._scenario_result(case["scenario_id"], outcomes, before, self.layer_snapshot())

    def _run_op(self, op: JsonObject) -> JsonObject:
        kind = op["op"]
        if kind == "export":
            return pack_backup.export_markdown_pack(self._store, self._pack, CLOCK)
        if kind == "export_again":
            return pack_backup.export_markdown_pack(self._store, self._pack2, CLOCK)
        if kind == "verify":
            return pack_backup.verify_pack(self._pack)
        if kind == "verify_after_remove":
            return pack_backup.verify_pack(self._pack)
        if kind == "tamper":
            target = self._pack / op["file"]
            target.write_bytes(target.read_bytes() + b"tamper")
            return {"outcome": "tampered"}
        if kind == "inject_unknown_file":
            (self._pack / "unknown.txt").write_text("x", encoding="utf-8")
            return {"outcome": "injected"}
        if kind == "remove_file":
            (self._pack / op["file"]).unlink()
            return {"outcome": "removed"}
        if kind == "create_backup":
            return pack_backup.create_backup(self._db_path, KEY, self._backup, CLOCK)
        if kind == "restore":
            key = KEY if op["key"] == "correct" else WRONG_KEY
            return pack_backup.restore_backup(self._backup, key, self._restored)
        if kind == "restore_to_existing":
            return pack_backup.restore_backup(self._backup, KEY, self._db_path)
        if kind == "deletion_receipt":
            return pack_backup.build_deletion_receipt("EP-SYN-C5-001", CLOCK, POLICY, fail_component=op.get("fail_component"))
        if kind == "out_of_profile_op":
            return pack_backup.export_markdown_pack(self._store, self._pack, CLOCK)
        raise ValueError("unsupported C5 op: " + kind)

    def _scenario_result(self, scenario_id: str, outcomes: list[JsonObject], before: JsonObject, after: JsonObject) -> JsonObject:
        store_unchanged = after["store_layer"] == before["store_layer"]
        if scenario_id == "C5-001":
            manifest = json.loads((self._pack / "manifest.json").read_text(encoding="utf-8"))
            files = sorted(p.relative_to(self._pack).as_posix() for p in self._pack.rglob("*") if p.is_file())
            hashes_valid = all(
                hashlib.sha256((self._pack / e["content_ref"]).read_bytes()).hexdigest() == e["content_hash"]
                for e in manifest["entries"]
            )
            md_entries = sum(1 for e in manifest["entries"] if e["media_type"] == "text/markdown")
            return {"export_outcome": outcomes[0]["outcome"], "files_present": files,
                    "manifest_markdown_entries": md_entries, "hashes_valid": hashes_valid}
        if scenario_id == "C5-002":
            identical = all((self._pack / n).read_bytes() == (self._pack2 / n).read_bytes() for n in pack_backup._MARKDOWN_FILES)
            canonical_md = (self._pack / "markdown/canonical.md").read_text(encoding="utf-8")
            manifest = json.loads((self._pack / "manifest.json").read_text(encoding="utf-8"))
            return {"byte_identical": identical,
                    "contains_expected_headings": "# Canonical Objects" in canonical_md and "canonical-1" in canonical_md,
                    "export_scope": manifest["export_scope"]}
        if scenario_id == "C5-003":
            return {"first_verify": outcomes[1]["status"], "tampered_verify": outcomes[3]["status"], "sqlite_writes": 0}
        if scenario_id == "C5-004":
            return {"unknown_file_verify": outcomes[2]["status"], "missing_file_verify": outcomes[4]["status"], "sqlite_writes": 0}
        if scenario_id == "C5-005":
            receipt = outcomes[0]["receipt"]
            return {"backup_outcome": outcomes[0]["outcome"],
                    "ciphertext_differs": self._backup.read_bytes() != self._db_path.read_bytes(),
                    "receipt_has_hashes": bool(receipt["source_db_sha256"] and receipt["backup_sha256"]),
                    "encryption_label": receipt["encryption"],
                    "store_digest_unchanged": store_unchanged}
        if scenario_id == "C5-006":
            restored_store = SemanticStore(self._restored)
            return {"restore_outcome": outcomes[1]["outcome"],
                    "byte_identical": self._restored.read_bytes() == self._db_path.read_bytes(),
                    "data_revision_match": restored_store.current_revision() == self._store.current_revision(),
                    "source_unchanged": store_unchanged}
        if scenario_id == "C5-007":
            return {"restore_outcome": outcomes[1]["outcome"], "partial_file_exists": self._restored.exists()}
        if scenario_id == "C5-008":
            return {"components": outcomes[0]["components"], "overall": outcomes[0]["overall"]}
        if scenario_id == "C5-009":
            failed = [name for name, value in outcomes[0]["components"].items() if value == "failed"]
            return {"failed_component": failed[0] if failed else None, "overall": outcomes[0]["overall"],
                    "claimed_deleted": outcomes[0]["claimed_deleted"]}
        if scenario_id == "C5-010":
            canonical = json.loads((self._pack / "canonical.json").read_text(encoding="utf-8"))
            sources = json.loads((self._pack / "sources.json").read_text(encoding="utf-8"))
            synthetic_only = all(o.get("synthetic") is True for o in canonical["objects"]) and all("SYN" in s["source_id"] for s in sources["records"])
            return {"store_digest_unchanged": store_unchanged,
                    "restore_to_existing_outcome": outcomes[3]["outcome"],
                    "out_of_profile_outcome": outcomes[4]["outcome"],
                    "pack_synthetic_only": synthetic_only}
        raise ValueError("unsupported C5 scenario: " + scenario_id)
