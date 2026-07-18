from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import json

from noetide_micro.importer import SyntheticImporter
from noetide_micro.store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/synthetic_ingestion_v1/fixture.json"
ORACLES = ROOT / "tests/fixtures/synthetic_ingestion_v1/oracles.json"


def scenario(scenario_id):
    def decorate(method):
        method._noetide_scenario_id = scenario_id
        return method
    return decorate


class SyntheticImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SemanticStore(Path(self.temp.name) / "import.sqlite3")
        self.addCleanup(self.store.close)
        self.importer = SyntheticImporter(self.store, "2031-10-15T02:00:00Z")
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.oracles = json.loads(ORACLES.read_text(encoding="utf-8"))["scenarios"]

    def case(self, scenario_id):
        return next(item for item in self.fixture["cases"] if item["scenario_id"] == scenario_id)

    @scenario("SI-001")
    def test_stored_means_durable_source_and_receipt(self) -> None:
        case = self.case("SI-001")
        expected = self.oracles["SI-001"]
        receipt = self.importer.import_text(case["text"], case["source_id"], case["subject_refs"], synthetic=case["synthetic_declaration"])
        self.assertEqual(receipt["status"], expected["status"])
        self.assertEqual(self.store.seeded_source(case["source_id"]) is not None, expected["durable_source"])
        self.assertEqual(self.store.append_receipt(receipt["receipt_id"]) is not None, expected["durable_receipt"])

    @scenario("SI-002")
    def test_requires_explicit_synthetic_declaration(self) -> None:
        case = self.case("SI-002")
        expected = self.oracles["SI-002"]
        receipt = self.importer.import_text(case["text"], case["source_id"], case["subject_refs"], synthetic=case["synthetic_declaration"])
        self.assertEqual((receipt["status"], receipt["failure"]), (expected["status"], expected["failure"]))
        self.assertEqual(self.store.seeded_source(case["source_id"]) is not None, expected["durable_source"])

    @scenario("SI-003")
    def test_duplicate_and_mismatch_are_distinct(self) -> None:
        case = self.case("SI-003")
        expected = self.oracles["SI-003"]
        self.importer.import_text(case["text"], case["source_id"], case["subject_refs"], synthetic=True)
        duplicate = self.importer.import_text(case["text"], case["source_id"], case["subject_refs"], synthetic=True)
        mismatch = self.importer.import_text("synthetic_record_changed", case["source_id"], case["subject_refs"], synthetic=True)
        self.assertEqual(duplicate["status"], expected["duplicate_status"])
        self.assertEqual((mismatch["status"], mismatch["failure"]), (expected["mismatch_status"], expected["mismatch_failure"]))

    @scenario("SI-004")
    def test_invalid_subject_ref_rejects_without_write(self) -> None:
        case = self.case("SI-004")
        expected = self.oracles["SI-004"]
        receipt = self.importer.import_text(case["text"], case["source_id"], case["subject_refs"], synthetic=case["synthetic_declaration"])
        self.assertEqual((receipt["status"], receipt["failure"]), (expected["status"], expected["failure"]))
        self.assertEqual(self.store.seeded_source(case["source_id"]) is not None, expected["durable_source"])
