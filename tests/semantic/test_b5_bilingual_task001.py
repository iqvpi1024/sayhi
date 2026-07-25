"""B5-TASK-001 narrow tests: bilingual overlay separation and pairing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.bilingual import (
    append_bilingual_pair,
    read_bilingual_view,
    read_original,
    revise_source_with_translation,
    revise_translation,
    translation_anomalies,
    translation_history,
)
from noetide_micro.store import SemanticStore


CLOCK = "2032-05-01T09:00:00Z"
SOURCE_A = {"source_id": "src_b5_orig_001", "source_kind": "synthetic_statement", "language": "synthetic_lang_a", "text": "synthetic original alpha"}
SOURCE_B = {"source_id": "src_b5_orig_002", "source_kind": "synthetic_statement", "language": "synthetic_lang_a", "text": "synthetic original beta"}
TRANSLATION_A = {"translation_id": "tr_pair_001", "source_ref": "src_b5_orig_001", "target_language": "synthetic_lang_b", "translated_text": "synthetic translation alpha", "translation_revision": "tr_001"}


def build_store(directory: str) -> SemanticStore:
    store = SemanticStore(Path(directory) / "b5_task001.sqlite3")
    append_bilingual_pair(store, SOURCE_A, TRANSLATION_A, CLOCK)
    # source without translation
    append_bilingual_pair(store, SOURCE_B, {"translation_id": "tr_temp_b", "source_ref": "src_b5_orig_002", "target_language": "synthetic_lang_b", "translated_text": "x", "translation_revision": "tr_000"}, CLOCK)
    # remove temp translation to model "no translation" (mark superseded)
    for record in translation_history(store):
        if record["translation_id"] == "tr_temp_b":
            record["status"] = "superseded"
            store.replace_ledger_record(f"translation:{record['source_ref']}:{record['translation_revision']}", record)
    return store


class BilingualTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = build_store(self._tmp.name)
        self.addCleanup(self.store.close)

    def test_pair_stored_separately(self) -> None:
        source = self.store.seeded_source("src_b5_orig_001")
        self.assertEqual(source["text"], "synthetic original alpha")
        history = [r for r in translation_history(self.store) if r["translation_id"] == "tr_pair_001"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["record_kind"], "translation_overlay")

    def test_original_read_and_evidence_resolution(self) -> None:
        result = read_original(self.store, "src_b5_orig_001")
        self.assertEqual(result["original_text"], "synthetic original alpha")
        self.assertTrue(result["content_hash_matches"])
        self.assertEqual(result["evidence_target"], "src_b5_orig_001")
        self.assertFalse(result["evidence_target_is_translation"])

    def test_bilingual_view_paired(self) -> None:
        view = read_bilingual_view(self.store, "src_b5_orig_001")
        self.assertEqual(view["pairing_status"], "paired")
        self.assertEqual(view["translated_text"], "synthetic translation alpha")
        self.assertEqual(view["record_kind"], "translation_overlay")
        self.assertTrue(view["derived_only"])

    def test_translation_unavailable_not_faked(self) -> None:
        view = read_bilingual_view(self.store, "src_b5_orig_002")
        self.assertEqual(view["pairing_status"], "translation_unavailable")
        self.assertIsNone(view["translation"])
        self.assertFalse(view["original_presented_as_translation"])

    def test_overwrite_rejected_no_write(self) -> None:
        before = self.store.seeded_source("src_b5_orig_001")
        result = revise_source_with_translation(self.store, "src_b5_orig_001", "synthetic translation alpha")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["reason_code"], "original_overwrite_rejected")
        after = self.store.seeded_source("src_b5_orig_001")
        self.assertEqual(before, after)

    def test_revision_history_retained(self) -> None:
        update = {"translation_id": "tr_pair_001", "source_ref": "src_b5_orig_001", "target_language": "synthetic_lang_b", "translated_text": "synthetic translation alpha revised", "translation_revision": "tr_002"}
        result = revise_translation(self.store, update, CLOCK)
        self.assertEqual(result["active_revision"], "tr_002")
        self.assertEqual(result["superseded_revisions"], ["tr_001"])
        self.assertTrue(result["history_retained"])
        history = [r for r in translation_history(self.store) if r["translation_id"] == "tr_pair_001"]
        self.assertEqual({r["translation_revision"]: r["status"] for r in history}, {"tr_001": "superseded", "tr_002": "active"})
        self.assertEqual(self.store.seeded_source("src_b5_orig_001")["text"], "synthetic original alpha")

    def test_orphan_translation_reported(self) -> None:
        from noetide_micro.bilingual import _append_translation
        _append_translation(self.store, {"translation_id": "tr_orphan_001", "source_ref": "missing_source_001", "target_language": "synthetic_lang_b", "translated_text": "orphan", "translation_revision": "tr_001"}, CLOCK)
        result = translation_anomalies(self.store)
        self.assertEqual(result["orphan_translations"], ["translation:missing_source_001:tr_001"])
        self.assertFalse(result["silent_pairing"])

    def test_unknown_source_view_rejected(self) -> None:
        with self.assertRaises(KeyError):
            read_bilingual_view(self.store, "missing_source_001")

    def test_view_never_persisted(self) -> None:
        before = len(self.store.ledger_records_of_type("bilingual_view"))
        read_bilingual_view(self.store, "src_b5_orig_001")
        read_bilingual_view(self.store, "src_b5_orig_002")
        self.assertEqual(len(self.store.ledger_records_of_type("bilingual_view")), before)


if __name__ == "__main__":
    unittest.main()
