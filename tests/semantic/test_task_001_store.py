from __future__ import annotations

import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from noetide_micro.store import SeedConflictError, SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task001StoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.store = SemanticStore(Path(self.temp_dir.name) / "micro.sqlite3")
        self.addCleanup(self.store.close)
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_schema_initializes_logical_layers_without_triggers(self) -> None:
        self.assertTrue(
            {
                "source_records",
                "append_receipts",
                "canonical_revisions",
                "canonical_objects",
                "canonical_evidence_refs",
                "ledger_records",
                "projection_rows",
            }.issubset(self.store.schema_objects())
        )
        triggers = self.store._connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'trigger'"
        ).fetchall()
        self.assertEqual(triggers, [])

    def test_connection_uses_approved_sqlite_pragmas(self) -> None:
        self.assertEqual(
            self.store.pragma_values(),
            {"foreign_keys": 1, "journal_mode": "delete", "synchronous": 2},
        )

    def test_rev_010_seed_preserves_fixture_and_only_seeds_existing_evidence_source(self) -> None:
        self.assertTrue(self.store.seed_rev_010(self.fixture))
        snapshot = self.store.seed_snapshot()
        self.assertEqual(snapshot["data_revision"], "rev_010")
        self.assertEqual(
            snapshot["objects"],
            {
                self._object_id(item): item
                for item in self.fixture["initial_state"]["canonical_objects"]
            },
        )
        self.assertEqual(
            snapshot["projections"], self.fixture["initial_state"]["core_views"]
        )
        history_source = next(
            item for item in self.fixture["source_records"] if item["source_id"] == "src_history_001"
        )
        self.assertEqual(self.store.seeded_source("src_history_001"), history_source)
        self.assertIsNone(self.store.seeded_source("src_micro_001"))

    def test_foreign_key_rejects_evidence_that_does_not_reference_a_source(self) -> None:
        self.store.seed_rev_010(self.fixture)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction() as connection:
                connection.execute(
                    "INSERT INTO canonical_evidence_refs "
                    "(object_id, source_id, locator_json, stance, claim_ref) VALUES (?, ?, ?, ?, ?)",
                    ("state_contact_001", "missing_source", "{}", "supports", "state_contact_001"),
                )

    def test_repeat_seed_is_a_noop_and_different_fixture_is_rejected(self) -> None:
        self.assertTrue(self.store.seed_rev_010(self.fixture))
        before = self.store.seed_snapshot()
        self.assertFalse(self.store.seed_rev_010(self.fixture))
        self.assertEqual(self.store.seed_snapshot(), before)
        changed_fixture = copy.deepcopy(self.fixture)
        changed_fixture["determinism"]["clock"] = "2031-10-15T02:00:01Z"
        with self.assertRaises(SeedConflictError):
            self.store.seed_rev_010(changed_fixture)
        self.assertEqual(self.store.seed_snapshot(), before)

    @staticmethod
    def _object_id(item: dict[str, object]) -> str:
        for key in (
            "entity_id",
            "relationship_id",
            "state_id",
            "assertion_id",
            "hypothesis_id",
        ):
            value = item.get(key)
            if isinstance(value, str):
                return value
        raise AssertionError("fixture object is missing a stable ID")
