from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.testing_adapter import create_system


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task008RevertTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        root = ROOT / "tmp"
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.system = create_system(fixture, Path(self.temp.name))
        self.fixture = fixture
        self.system.intake(copy.deepcopy(fixture["intake_request"]))
        self.changeset = self.system.propose_contact_changeset("src_micro_001")
        self.system.approve_changeset(self.changeset["changeset_id"], "person_alpha")
        self.system.publish_changeset(self.changeset["changeset_id"], "task008-publish")

    def test_compensation_creates_rev_012_and_preserves_audit(self) -> None:
        receipt = self.system.revert_changeset(self.changeset["changeset_id"], "task008-revert")
        self.assertEqual(receipt["status"], "published")
        self.assertEqual(receipt["compensation_revision"], "rev_012")
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_012")
        self.assertEqual(self.system.query_relationship_contact("2031-10-15T02:00:00Z")["value"], "active")
        for view_name in ("person_card", "relationship_timeline"):
            view = self.system.read_core_view(view_name, "task008")
            self.assertEqual((view["data_revision"], view["view_revision"]), ("rev_012", "rev_012"))
        event_types = {event["event_type"] for event in self.system.list_audit_events(self.changeset["changeset_id"])}
        self.assertEqual(event_types, {"published", "reverted"})
