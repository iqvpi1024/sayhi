from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.app_shell import render_impact_preview, render_review, shell_write_scan
from noetide_micro.candidate import ContactCandidateBuilder
from noetide_micro.intake import IntakeService
from noetide_micro.runtime import demo_fixture
from noetide_micro.store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
ORACLES = json.loads((ROOT / "tests/fixtures/a5_app_shell_v1/oracles.json").read_text(encoding="utf-8"))["scenarios"]
_CLOCK = "2031-10-15T02:00:00Z"


class A5Task001AppShellTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.store = SemanticStore(str(Path(self._tmp.name) / "a5_task_001.sqlite"))
        self.fixture = demo_fixture()
        self.store.seed_rev_010(self.fixture)
        IntakeService(self.store, self.fixture).append(self.fixture["intake_request"])
        builder = ContactCandidateBuilder(self.store, self.fixture, _CLOCK)
        self.changeset = builder.propose("src_micro_001")
        relationship = self.store.canonical_object("rel_alpha_beta")
        self.labels = [
            self.store.canonical_object(ref)["canonical_label"]
            for ref in relationship["participant_refs"]
        ]

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def test_render_review_matches_oracle(self) -> None:
        item = render_review(self.changeset, self.labels)
        expected = ORACLES["A5-002"]["result"]["step_results"]["review"]
        self.assertEqual(item, expected)

    def test_render_impact_preview_matches_oracle(self) -> None:
        preview = render_impact_preview(self.changeset)
        expected = ORACLES["A5-003"]["result"]["step_results"]["preview"]
        self.assertEqual(preview, expected)

    def test_presentation_is_zero_write(self) -> None:
        before = self.store.canonical_layer_digest()
        render_review(self.changeset, self.labels)
        render_impact_preview(self.changeset)
        self.assertEqual(self.store.canonical_layer_digest(), before)
        self.assertEqual(self.store.current_revision(), "rev_010")

    def test_shell_write_scan_finds_no_forbidden_calls(self) -> None:
        allowed, forbidden = shell_write_scan()
        self.assertEqual(forbidden, [])
        self.assertIn("read_text", allowed)

    def test_render_review_requires_two_labels(self) -> None:
        with self.assertRaises(ValueError):
            render_review(self.changeset, ["Synthetic Alpha"])

    def test_presentation_shape_has_no_changeset_json(self) -> None:
        item = render_review(self.changeset, self.labels)
        self.assertEqual(set(item), {"candidate_ref", "summary_text", "evidence_citations", "presentation_revision"})
        self.assertNotIn("proposals", item)


if __name__ == "__main__":
    unittest.main()