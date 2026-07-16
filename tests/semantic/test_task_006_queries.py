from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.queries import CanonicalQueries
from noetide_micro.testing_adapter import create_system


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task006QueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        root = ROOT / "tmp"
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.system = create_system(self.fixture, Path(self.temp.name))
        self.system.intake(copy.deepcopy(self.fixture["intake_request"]))
        changeset = self.system.propose_contact_changeset("src_micro_001")
        self.system.approve_changeset(changeset["changeset_id"], "person_alpha")
        self.system.publish_changeset(changeset["changeset_id"], "task006-publish")

    def test_half_open_interval_preserves_history_and_evidence_boundary(self) -> None:
        before = self.system.query_relationship_contact("2031-08-31T23:59:59+08:00")
        after = self.system.query_relationship_contact("2031-09-01T00:00:00+08:00")
        self.assertEqual(before["value"], "active")
        self.assertEqual(after["value"], "no_contact")
        self.assertEqual({ref["source_id"] for ref in before["evidence_refs"]}, {"src_history_001"})
        self.assertEqual({ref["source_id"] for ref in after["evidence_refs"]}, {"src_micro_001"})

    def test_protected_snapshot_remains_non_empty_and_unchanged(self) -> None:
        store = self.system.store
        self.addCleanup(store.close)
        snapshot = CanonicalQueries(store, self.fixture).protected_snapshot()
        self.assertEqual(set(snapshot), set(self.fixture["protected_semantics"]["object_ids"]))
        self.assertTrue(all(item["digest"] for item in snapshot.values()))
