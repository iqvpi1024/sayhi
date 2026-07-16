from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from noetide_micro.testing_adapter import create_system


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"


class Task005ChangeSetTests(unittest.TestCase):
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

    def test_atomic_publish_creates_rev_011_and_attempt(self) -> None:
        receipt = self.system.publish_changeset(self.changeset["changeset_id"], "task005-success")
        self.assertEqual(receipt["status"], "published")
        self.assertEqual(receipt["published_revision"], "rev_011")
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_011")
        attempts = self.system.get_publish_attempts(self.changeset["changeset_id"])
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["preflight_result"], "passed")

    def test_second_proposal_failure_rolls_back_and_stale_is_idempotent(self) -> None:
        self.system.inject_failure("l1.proposal.2")
        failed = self.system.publish_changeset(self.changeset["changeset_id"], "task005-failure")
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_010")

        stale_root = Path(self.temp.name) / "stale"
        stale_root.mkdir()
        fresh = create_system(self.fixture, stale_root)
        fresh.intake(copy.deepcopy(self.fixture["intake_request"]))
        changeset = fresh.propose_contact_changeset("src_micro_001")
        fresh.approve_changeset(changeset["changeset_id"], "person_alpha")
        fresh.advance_revision_for_test()
        first = fresh.publish_changeset(changeset["changeset_id"], "task005-stale")
        second = fresh.publish_changeset(changeset["changeset_id"], "task005-stale")
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "conflicted")
        self.assertEqual(fresh.canonical_snapshot()["data_revision"], "rev_011_test")
        retry = fresh.propose_retry(changeset["changeset_id"])
        self.assertNotEqual(retry["changeset_id"], changeset["changeset_id"])
        self.assertEqual(retry["retry_of"], changeset["changeset_id"])
