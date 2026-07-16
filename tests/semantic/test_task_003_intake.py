from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.testing_adapter import create_system


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task003IntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        root = ROOT / "tmp"
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.system = create_system(self.fixture, Path(self.temp.name))
        self.addCleanup(self.system.store.close)

    def test_exact_synthetic_source_append_does_not_mutate_canonical(self) -> None:
        before = self.system.canonical_snapshot()
        receipt = self.system.intake(copy.deepcopy(self.fixture["intake_request"]))
        self.assertEqual(receipt, self.fixture["expected_append_receipt"])
        expected_source = next(
            item for item in self.fixture["source_records"] if item["source_id"] == "src_micro_001"
        )
        self.assertEqual(self.system.get_source("src_micro_001"), expected_source)
        self.assertEqual(self.system.canonical_snapshot(), before)

    def test_invalid_intake_is_rejected_without_source_or_canonical_write(self) -> None:
        request = copy.deepcopy(self.fixture["intake_request"])
        request["inline_content"] = "synthetic altered input"
        before = self.system.canonical_snapshot()
        receipt = self.system.intake(request)
        self.assertEqual(receipt["status"], "rejected")
        self.assertEqual(receipt["failure"], "request_mismatch")
        with self.assertRaises(KeyError):
            self.system.get_source("src_micro_001")
        self.assertEqual(self.system.canonical_snapshot(), before)
