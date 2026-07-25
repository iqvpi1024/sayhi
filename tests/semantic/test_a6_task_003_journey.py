from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from noetide_micro import a6_journey as journey


class A6Task003JourneyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = journey.new_profile_store()
        journey.seed_protected_layers(self.store)

    def tearDown(self) -> None:
        self.store.close()

    def test_layer_snapshot_shape_and_protected_layers(self) -> None:
        snapshot = journey.layer_snapshot(self.store)
        self.assertEqual(set(snapshot), {"canonical", "trust", "closeness", "personality", "history"})
        self.assertEqual(journey.layer_snapshot(self.store), snapshot)

    def test_record_propose_candidate_visibility(self) -> None:
        baseline = self.store.current_revision()
        result = journey.record_source(self.store)
        self.assertEqual(
            result,
            {"source_appended": True, "receipt_issued": True, "canonical_revision_unchanged": True},
        )
        proposal = journey.propose_candidate(self.store)
        visibility = journey.candidate_visibility(self.store, proposal)
        self.assertEqual(
            visibility,
            {"candidate_visible_in_review": True, "candidate_in_canonical": False, "candidate_in_core_views": False},
        )
        audit = journey.write_path_audit(self.store, baseline, self.store.current_revision())
        self.assertEqual(
            audit,
            {"all_normative_writes_via_changeset": True, "source_append_independent": True, "bypass_paths_found": 0},
        )

    def test_publish_views_revert_journey(self) -> None:
        journey.record_source(self.store)
        proposal = journey.propose_candidate(self.store)
        pre_publish_value = self.store.canonical_object("state_contact_001")["value"]
        confirm = journey.preview_publish_consistency(self.store, proposal)
        self.assertEqual(
            confirm,
            {
                "preview_object_set_equals_published": True,
                "preview_view_set_equals_actual": True,
                "published": True,
                "receipt_issued": True,
            },
        )
        views = journey.read_core_views(self.store)
        self.assertEqual(
            views,
            {
                "person_card": "fresh",
                "relationship_timeline": "fresh",
                "current_state": "fresh",
                "stale_returned_as_fresh": False,
            },
        )
        revert = journey.revert_and_audit(self.store, pre_publish_value)
        self.assertEqual(
            revert,
            {
                "receipt_available": True,
                "history_contains_publish": True,
                "history_contains_revert_compensation": True,
                "views_restored_consistent": True,
            },
        )

    def test_answer_battery_six_states(self) -> None:
        result = journey.run_answer_battery(self.store)
        self.assertEqual(
            result,
            {"six_states_strictly_separated": True, "unknown_not_guessed": True, "cross_compartment_leak": False},
        )

    def test_conflict_probe(self) -> None:
        result = journey.conflict_probe(self.store)
        self.assertEqual(
            result,
            {"conflict_detected": True, "presented_side_by_side": True, "auto_resolved": False},
        )

    def test_bitemporal_probe_after_revert(self) -> None:
        journey.record_source(self.store)
        proposal = journey.propose_candidate(self.store)
        pre_publish_value = self.store.canonical_object("state_contact_001")["value"]
        journey.preview_publish_consistency(self.store, proposal)
        journey.revert_and_audit(self.store, pre_publish_value)
        result = journey.bitemporal_probe(self.store)
        self.assertEqual(
            result,
            {
                "valid_recorded_distinguished": True,
                "recorded_at_not_backfilled": True,
                "correction_vs_evolution_distinguished": True,
            },
        )

    def test_merge_split_cycle(self) -> None:
        before = journey.layer_snapshot(self.store)
        result = journey.merge_split_cycle(self.store)
        self.assertEqual(
            result,
            {
                "merge_via_candidate_confirmation": True,
                "split_executed": True,
                "split_restored_prior_state": True,
            },
        )
        after = journey.layer_snapshot(self.store)
        for layer in ("trust", "closeness", "personality"):
            self.assertEqual(after[layer], before[layer], f"{layer} changed")

    def test_restricted_query_probe(self) -> None:
        result = journey.restricted_query_probe()
        self.assertEqual(result, {"fail_closed": True, "answered_less": True, "no_guessing": True})

    def test_publish_injected_failure_rolls_back(self) -> None:
        result = journey.publish_with_injected_failure(self.store)
        self.assertEqual(
            result,
            {"rolled_back": True, "canonical_revision_unchanged": True, "failure_reported": True},
        )

    def test_read_view_with_l2_failure_falls_back(self) -> None:
        result = journey.read_view_with_l2_failure(self.store)
        self.assertEqual(
            result,
            {"fallback": "canonical_or_explicit_unavailable", "stale_returned_as_fresh": False},
        )

    def test_stale_base_rejected(self) -> None:
        result = journey.stale_base_probe(self.store)
        self.assertEqual(result, {"stale_base_rejected": True})

    def test_cross_cutting_check_after_full_journey(self) -> None:
        journey_start = journey.layer_snapshot(self.store)
        journey.record_source(self.store)
        proposal = journey.propose_candidate(self.store)
        pre_publish_value = self.store.canonical_object("state_contact_001")["value"]
        journey.preview_publish_consistency(self.store, proposal)
        journey.revert_and_audit(self.store, pre_publish_value)
        current = journey.layer_snapshot(self.store)
        result = journey.cross_cutting_check(journey_start, current, self.store)
        self.assertEqual(
            result,
            {
                "trust_unchanged": True,
                "closeness_unchanged": True,
                "personality_unchanged": True,
                "history_preserved": True,
                "stale_base_rejected": True,
                "l2_fallback_available": True,
            },
        )

    def test_slo_collector_and_report(self) -> None:
        collector = journey.SloCollector()
        for slo_id in journey.SLO_IDS:
            collector.measure(slo_id, lambda: None)
        report = journey.slo_report(collector)
        self.assertEqual(
            report,
            {
                "observations_recorded": True,
                "bound_to_profile": "a6_mvp_a_reference_v1",
                "extrapolation_forbidden": True,
                "all_slo_ids_present": True,
            },
        )
        self.assertTrue(all(o["profile_id"] == "a6_mvp_a_reference_v1" for o in collector.observations))


if __name__ == "__main__":
    unittest.main()
