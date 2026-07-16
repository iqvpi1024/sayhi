from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.testing_adapter import create_system


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task004CandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        root = ROOT / "tmp"
        root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.system = create_system(fixture, Path(self.temp.name))
        self.addCleanup(self.system.store.close)
        self.fixture = fixture
        self.system.intake(copy.deepcopy(fixture["intake_request"]))

    def test_proposal_is_allowlisted_and_does_not_write_canonical(self) -> None:
        before = self.system.canonical_snapshot()
        changeset = self.system.propose_contact_changeset("src_micro_001")
        self.assertEqual(changeset["status"], "proposed")
        self.assertEqual([item["operation"] for item in changeset["proposals"]], ["end", "add"])
        self.assertEqual(changeset["proposals"][1]["after_value"]["value"], "no_contact")
        self.assertEqual(changeset["impact_set"]["derived_views"], ["person_card", "relationship_timeline"])
        self.assertEqual(self.system.canonical_snapshot(), before)

    def test_preview_and_single_approval_only_change_ledger_status(self) -> None:
        changeset = self.system.propose_contact_changeset("src_micro_001")
        self.assertEqual(self.system.preview_changeset(changeset["changeset_id"]), changeset)
        approved = self.system.approve_changeset(changeset["changeset_id"], "person_alpha")
        self.assertEqual(approved["status"], "approved")
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_010")
