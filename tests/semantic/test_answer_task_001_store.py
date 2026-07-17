from __future__ import annotations
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from noetide_micro.store import SeedConflictError, SemanticStore

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / 'tests/fixtures/answer_safety_v1/fixture.json'

class AnswerTask001StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.store = SemanticStore(Path(self.temp_dir.name) / 'a1.sqlite3')
        self.addCleanup(self.store.close)
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))

    def test_a1_schema_includes_coverage_windows(self):
        self.assertIn('coverage_windows', self.store.schema_objects())

    def test_pragmas_unchanged(self):
        self.assertEqual(
            self.store.pragma_values(),
            {'foreign_keys': 1, 'journal_mode': 'delete', 'synchronous': 2},
        )

    def test_seed_all_cases_and_coverage_windows_present(self):
        self.assertTrue(self.store.seed_answer_safety_fixture(self.fixture))
        snapshot = self.store.a1_seed_snapshot()
        self.assertEqual(snapshot['source']['count'], 8)  # total unique sources across all cases
        self.assertEqual(snapshot['coverage']['count'], 11)  # total coverage windows
        cw = self.store.coverage_window('as001_coverage')
        self.assertIsNotNone(cw)
        self.assertEqual(cw['scope_ref'], 'synthetic.signal')

    def test_repeat_seed_is_noop(self):
        self.assertTrue(self.store.seed_answer_safety_fixture(self.fixture))
        before = self.store.a1_seed_snapshot()
        self.assertFalse(self.store.seed_answer_safety_fixture(self.fixture))
        self.assertEqual(self.store.a1_seed_snapshot(), before)

    def test_different_fixture_rejected(self):
        self.assertTrue(self.store.seed_answer_safety_fixture(self.fixture))
        changed = copy.deepcopy(self.fixture)
        changed['determinism']['clock'] = '2033-01-15T12:00:00Z'
        with self.assertRaises(SeedConflictError):
            self.store.seed_answer_safety_fixture(changed)

    def test_invalid_fixture_rejected(self):
        bad = {'fixture_id': 'bad', 'synthetic': True}
        with self.assertRaises(Exception):
            self.store.seed_answer_safety_fixture(bad)

if __name__ == '__main__':
    unittest.main()
