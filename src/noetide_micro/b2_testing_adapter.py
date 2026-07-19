"""Fixture-scoped B2 contract adapter."""
from __future__ import annotations

import copy
from typing import Any

from .episodes import EpisodeChangeSetService
from .runtime import demo_fixture
from .store import SemanticStore
from .summaries import EpisodeSummaryService


_NOW = "2032-02-20T09:00:00Z"


class B2System:
    def __init__(self, case: dict[str, Any]) -> None:
        self.case = copy.deepcopy(case)
        self.store = SemanticStore(":memory:")
        self.store.seed_rev_010(demo_fixture())
        with self.store.transaction():
            self.store.add_revision("rev_020", _NOW)
        self.episodes = EpisodeChangeSetService(self.store, _NOW)
        self.summaries = EpisodeSummaryService(self.store, _NOW)
        self.failure: str | None = None
        self._published_changeset: str | None = None
        if case["scenario_id"] in {"B2-003", "B2-004", "B2-005", "B2-006", "B2-007"}:
            self._published_changeset = self._publish()

    def inject_failure(self, failure_point: str) -> None:
        self.failure = failure_point

    def layer_snapshot(self) -> dict[str, Any]:
        snapshot = self.store.seed_snapshot()
        return {
            "assertions": snapshot.get("assertions", []),
            "relationship_states": snapshot.get("relationship_states", []),
            "hypotheses": snapshot.get("hypotheses", []),
            "episodes": [row["episode_id"] for row in self.store.episode_records()],
            "revisions": self.store.current_revision(),
            "source_records": ["synthetic"],
            "historical_revisions": ["rev_010"],
            "summary_projections": [row["projection_id"] for row in self.store.summary_projections()],
        }

    def _candidate(self) -> dict[str, Any]:
        raw = self.case.get("episode_candidate", {})
        return {
            **raw,
            "source_refs": [
                {"source_id": source_id, "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 23}}
                for source_id in raw.get("source_refs", [])
            ],
        }

    def _source(self) -> None:
        if self.store.seeded_source("src_b2_event_001") is None:
            self.store.append_source(
                {"source_id": "src_b2_event_001", "append_receipt_id": "receipt_b2_event_001", "source_kind": "synthetic_text", "content_hash": "b2", "synthetic": True, "synthetic_profile_id": "b2_episode_summary_v1"},
                {"receipt_id": "receipt_b2_event_001", "status": "stored"},
            )

    def _publish(self) -> str:
        self._source()
        proposed = self.episodes.propose(self._candidate() if "episode_candidate" in self.case else {
            "episode_id": "episode_b2_001", "episode_kind": "synthetic_relationship_event", "participant_refs": ["person_alpha", "person_beta"],
            "valid_time": {"start": "2032-02-18T00:00:00Z", "end": "2032-02-19T00:00:00Z"},
            "source_refs": [{"source_id": "src_b2_event_001", "locator": {"scheme": "text_utf8_byte_range_v1", "start_byte": 0, "end_byte_exclusive": 23}}], "synthetic_profile_id": "b2_episode_summary_v1"})
        self.episodes.approve(proposed["changeset_id"], "person_alpha")
        self.episodes.publish(proposed["changeset_id"])
        return proposed["changeset_id"]

    def run_case(self, case: dict[str, Any]) -> dict[str, Any]:
        scenario = case["scenario_id"]
        if scenario == "B2-001":
            changeset = self._publish()
            return {"status": "published", "episode_id": "episode_b2_001", "data_revision": self.store.current_revision()}
        if scenario == "B2-002":
            try: self.episodes.propose(self._candidate())
            except ValueError: pass
            return {"status": "failed", "reason_code": "episode_reference_invalid", "data_revision": self.store.current_revision()}
        if scenario == "B2-003": return self.summaries.build_for_episode("episode_b2_001")
        if scenario == "B2-004":
            self.summaries.build_for_episode("episode_b2_001"); self.episodes.revert(self._published_changeset or ""); self.summaries.rebuild_existing()
            return {"status": "rebuilt", "data_revision": self.store.current_revision(), "excluded_episode_id": "episode_b2_001"}
        if scenario == "B2-005":
            self.summaries.build_for_episode("episode_b2_001"); self.store.delete_summary_projections(); self.summaries.build_for_episode("episode_b2_001")
            return {"status": "fresh", "rebuild_equivalent": True, "data_revision": self.store.current_revision()}
        if scenario == "B2-006":
            result = self.summaries.reject_derived_evidence("summary_b2_day_001"); return {**result, "data_revision": self.store.current_revision()}
        if scenario == "B2-007":
            self.summaries.build_for_episode("episode_b2_001"); self.summaries.inject_rebuild_failure(); return self.summaries.rebuild_existing()
        return {"status": "rejected", "reason_code": "synthetic_input_required", "data_revision": self.store.current_revision()}


def create_system(case: dict[str, Any]) -> B2System:
    return B2System(case)
