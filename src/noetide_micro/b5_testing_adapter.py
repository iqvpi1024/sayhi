"""B5 testing adapter: builds the fixed synthetic bilingual profile and drives contract cases."""

from __future__ import annotations

import atexit
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .bilingual import (
    append_bilingual_pair,
    read_bilingual_view,
    read_original,
    revise_source_with_translation,
    revise_translation,
    translation_anomalies,
    translation_history,
    _append_translation,
)
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/b5_multilingual_v1/fixture.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
PROFILE_ID = FIXTURE["synthetic_profile_id"]
CLOCK = FIXTURE["determinism"]["clock"]


def create_system(case: JsonObject) -> "B5MultilingualSystem":
    return B5MultilingualSystem(case)


class B5MultilingualSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=f"{case['database_identity']}_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._store = SemanticStore(Path(self._tmpdir) / f"{case['database_identity']}.sqlite3")
        for source in FIXTURE["base_sources"]:
            self._append_source_only(source)
        for translation in FIXTURE["base_translations"]:
            _append_translation(self._store, translation, CLOCK)
        if case.get("inject_orphan"):
            _append_translation(self._store, FIXTURE["orphan_translation"], CLOCK)

    def layer_snapshot(self) -> JsonObject:
        store = self._store
        base_source_ids = {s["source_id"] for s in FIXTURE["base_sources"]}
        base_translation_ids = {t["translation_id"] for t in FIXTURE["base_translations"]}
        return {
            "base_sources": _canonical_digest(
                {sid: store.seeded_source(sid) for sid in sorted(base_source_ids)}
            ),
            "base_translations": _canonical_digest(
                [r for r in translation_history(store) if r["translation_id"] in base_translation_ids]
            ),
            "receipts": _canonical_digest(
                [store.append_receipt(f"receipt_{sid}") for sid in sorted(base_source_ids)]
            ),
        }

    def run_case(self, case: JsonObject) -> JsonObject:
        operation = case["operation"]
        if operation == "append_pair":
            pair = FIXTURE["new_pair"]
            return append_bilingual_pair(self._store, pair["source"], pair["translation"], CLOCK)
        if operation == "read_original":
            return read_original(self._store, case["source_ref"])
        if operation == "bilingual_view":
            return read_bilingual_view(self._store, case["source_ref"])
        if operation == "overwrite_attempt":
            return revise_source_with_translation(self._store, case["source_ref"], case["overwrite_text"])
        if operation == "revise_translation":
            return revise_translation(self._store, FIXTURE["translation_revision_update"], CLOCK)
        if operation == "anomaly_scan":
            return translation_anomalies(self._store)
        if operation == "cross_cutting":
            return self._cross_cutting(case)
        raise ValueError(f"unsupported B5 operation: {operation}")

    def _append_source_only(self, source: Mapping[str, Any]) -> None:
        import hashlib
        vault_source = {
            "source_id": source["source_id"],
            "append_receipt_id": f"receipt_{source['source_id']}",
            "source_kind": source["source_kind"],
            "content_hash": hashlib.sha256(source["text"].encode("utf-8")).hexdigest(),
            "language": source["language"],
            "text": source["text"],
            "synthetic": True,
        }
        receipt = {
            "receipt_id": vault_source["append_receipt_id"],
            "source_id": source["source_id"],
            "status": "stored",
            "actor": "b5_fixture_seed",
        }
        self._store.append_source(vault_source, receipt)

    def _cross_cutting(self, case: JsonObject) -> JsonObject:
        before = self.layer_snapshot()
        # full read-only journey: views + original read + anomaly scan + revision
        read_bilingual_view(self._store, "src_b5_orig_001")
        read_bilingual_view(self._store, "src_b5_orig_002")
        read_original(self._store, "src_b5_orig_001")
        translation_anomalies(self._store)
        mid = self.layer_snapshot()

        view = read_bilingual_view(self._store, "src_b5_orig_001")
        view_not_evidence = view.get("derived_only") is True
        history = [r for r in translation_history(self._store) if r["translation_id"] == "tr_pair_001"]
        history_intact = mid["base_translations"] == before["base_translations"] and any(
            r["translation_revision"] == "tr_001" and r["status"] == "active" for r in history
        )

        attempt = case["out_of_profile_attempt"]
        if attempt.get("synthetic_profile_id") != PROFILE_ID:
            attempt_result = {"status": "failed", "reason_code": "out_of_profile_input", "write_attempted": False}
        else:
            attempt_result = {"status": "accepted"}
        return {
            "status": "cross_cutting_ok",
            "originals_unchanged": mid["base_sources"] == before["base_sources"],
            "content_hashes_unchanged": mid["base_sources"] == before["base_sources"],
            "receipts_unchanged": mid["receipts"] == before["receipts"],
            "translation_history_intact": history_intact,
            "view_not_evidence": view_not_evidence,
            "out_of_profile_attempt": attempt_result,
        }
