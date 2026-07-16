from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.testing_adapter import FixedClock, create_system
from tests.runner.adapter_protocol import MicroSystem


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task002AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        temporary_root = ROOT / "tmp"
        temporary_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temporary_root)
        self.addCleanup(self.temp.cleanup)

    def test_factory_uses_fixture_clock_and_protocol_shape(self) -> None:
        system = create_system(self.fixture, Path(self.temp.name))
        self.addCleanup(system.store.close)
        self.assertIsInstance(system, MicroSystem)
        self.assertEqual(system.clock, FixedClock("2031-10-15T02:00:00Z"))
        self.assertEqual(system.clock.now(), "2031-10-15T02:00:00Z")
        self.assertEqual(system.canonical_snapshot()["data_revision"], "rev_010")
        self.assertTrue((Path(self.temp.name) / "micro.sqlite3").is_file())

    def test_factory_rejects_external_root_and_non_synthetic_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as external:
            with self.assertRaises(ValueError):
                create_system(self.fixture, Path(external))
        non_synthetic = copy.deepcopy(self.fixture)
        non_synthetic["synthetic"] = False
        with self.assertRaises(ValueError):
            create_system(non_synthetic, Path(self.temp.name))
