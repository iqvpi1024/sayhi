from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from noetide_micro.importer import SyntheticImporter
from noetide_micro.store import SemanticStore


class SyntheticImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SemanticStore(Path(self.temp.name) / "import.sqlite3")
        self.addCleanup(self.store.close)
        self.importer = SyntheticImporter(self.store, "2031-10-15T02:00:00Z")

    def test_stored_means_durable_source_and_receipt(self) -> None:
        receipt = self.importer.import_text("synthetic_record_001", "source_001", [], synthetic=True)
        self.assertEqual(receipt["status"], "stored")
        self.assertIsNotNone(self.store.seeded_source("source_001"))
        self.assertEqual(self.store.append_receipt("receipt_source_001")["status"], "stored")

    def test_requires_explicit_synthetic_declaration(self) -> None:
        receipt = self.importer.import_text("synthetic_record_002", "source_002", [], synthetic=False)
        self.assertEqual((receipt["status"], receipt["failure"]), ("rejected", "synthetic_declaration_required"))
        self.assertIsNone(self.store.seeded_source("source_002"))

    def test_duplicate_and_mismatch_are_distinct(self) -> None:
        self.importer.import_text("synthetic_record_003", "source_003", [], synthetic=True)
        duplicate = self.importer.import_text("synthetic_record_003", "source_003", [], synthetic=True)
        mismatch = self.importer.import_text("synthetic_record_changed", "source_003", [], synthetic=True)
        self.assertEqual(duplicate["status"], "duplicate")
        self.assertEqual((mismatch["status"], mismatch["failure"]), ("rejected", "idempotency_mismatch"))

    def test_invalid_subject_ref_rejects_without_write(self) -> None:
        receipt = self.importer.import_text("synthetic_record_004", "source_004", ["missing_subject"], synthetic=True)
        self.assertEqual((receipt["status"], receipt["failure"]), ("rejected", "invalid_subject_ref"))
        self.assertIsNone(self.store.seeded_source("source_004"))
