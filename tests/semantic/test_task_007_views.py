from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.testing_adapter import create_system


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task007ViewTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        root = ROOT / "tmp"
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.system = create_system(fixture, Path(self.temp.name))
        self.fixture = fixture
        self.system.intake(copy.deepcopy(fixture["intake_request"]))
        changeset = self.system.propose_contact_changeset("src_micro_001")
        self.system.approve_changeset(changeset["changeset_id"], "person_alpha")

    def test_two_fresh_views_share_published_revision(self) -> None:
        self.system.publish_changeset("changeset_micro_001", "task007-success")
        card = self.system.read_core_view("person_card", "task007")
        timeline = self.system.read_core_view("relationship_timeline", "task007")
        self.assertEqual((card["data_revision"], card["view_revision"]), ("rev_011", "rev_011"))
        self.assertEqual((timeline["data_revision"], timeline["view_revision"]), ("rev_011", "rev_011"))
        self.assertEqual(card["payload"]["contact_state"], "no_contact")
        self.assertIn("active", [item["value"] for item in timeline["payload"]["history"]])

    def test_failed_projection_returns_canonical_fallback_then_reconciles(self) -> None:
        self.system.inject_failure("projection.person_card")
        receipt = self.system.publish_changeset("changeset_micro_001", "task007-failure")
        self.assertIn({"target": "person_card", "result": "failed"}, receipt["view_results"])
        fallback = self.system.read_core_view("person_card", "task007")
        self.assertEqual(fallback["data_revision"], "rev_011")
        self.assertEqual(fallback["payload"]["contact_state"], "no_contact")
        self.assertEqual(fallback["source"], "canonical_fallback")
        self.system.reconcile_views()
        self.assertEqual(self.system.read_core_view("person_card", "task007")["freshness_status"], "fresh")
