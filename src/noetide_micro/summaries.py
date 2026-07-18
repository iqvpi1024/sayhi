"""Fixed deterministic B2 Derived summary projection behavior."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .store import SemanticStore


_POLICY = "b2_deterministic_v1"


class EpisodeSummaryService:
    """Builds B2 Derived projections without exposing them as evidence."""

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now
        self._fail_next_rebuild = False
        self._receipt_index = 0

    def build_for_episode(self, episode_id: str) -> dict[str, Any]:
        episode = self._store.episode_record(episode_id)
        phase_window = {"start": episode["valid_start"], "end": episode["valid_end"]}
        day_window = self._utc_day_window(phase_window["start"])
        projection_ids = [
            self._projection_id("day", episode_id),
            self._projection_id("phase", episode_id),
        ]
        self._build(projection_ids[0], "day_summary", day_window)
        self._build(projection_ids[1], "phase_summary", phase_window)
        revision = self._store.current_revision()
        return {"status": "fresh", "projection_ids": projection_ids, "data_revision": revision, "view_revision": revision}

    def read(self, projection_id: str) -> dict[str, Any]:
        projection = self._store.summary_projection(projection_id)
        current = self._store.current_revision()
        if projection["freshness_status"] == "fresh" and projection["view_revision"] == current:
            return {"status": "fresh", "projection": projection}
        with self._store.transaction():
            self._store.mark_summary_projections_stale(current)
        projection = self._store.summary_projection(projection_id)
        return {"status": projection["freshness_status"], "projection": projection}

    def rebuild_existing(self) -> dict[str, Any]:
        projections = self._store.summary_projections()
        if self._fail_next_rebuild:
            self._fail_next_rebuild = False
            current = self._store.current_revision()
            with self._store.transaction():
                for projection in projections:
                    self._store.replace_summary_projection(
                        projection["projection_id"], projection["projection_kind"], current,
                        projection["view_revision"], "unavailable", projection["dependency_set"],
                        projection["payload"], self._now, _POLICY,
                    )
                    self._store.put_derived_rebuild_receipt(
                        self._receipt_id(projection["projection_id"], current, "failed"), projection["projection_id"],
                        current, "failed", {"reason_code": "summary_rebuild_failed"},
                    )
            return {"status": "unavailable", "reason_code": "summary_rebuild_failed", "data_revision": current}
        for projection in projections:
            self._build(projection["projection_id"], projection["projection_kind"], projection["payload"]["time_window"])
        return {"status": "fresh", "data_revision": self._store.current_revision()}

    def reject_derived_evidence(self, value: Any) -> dict[str, str]:
        if isinstance(value, str) and value.startswith("summary_b2_"):
            return {"status": "rejected", "reason_code": "derived_evidence_forbidden"}
        raise ValueError("direct_source_locator_required")

    def inject_rebuild_failure(self) -> None:
        self._fail_next_rebuild = True

    def _build(self, projection_id: str, projection_kind: str, window: dict[str, str]) -> None:
        current = self._store.current_revision()
        episodes = [episode for episode in self._store.episode_records() if self._overlaps(episode, window)]
        dependencies = {
            "episode_refs": [episode["episode_id"] for episode in episodes],
            "source_refs": [ref for episode in episodes for ref in episode["source_refs"]],
            "data_revision": current,
        }
        payload = {
            "summary_level": "day" if projection_kind == "day_summary" else "phase",
            "time_window": dict(window),
            "summary_text": f"{projection_kind}:{','.join(dependencies['episode_refs']) or 'none'}",
        }
        with self._store.transaction():
            self._store.replace_summary_projection(
                projection_id, projection_kind, current, current, "fresh", dependencies, payload, self._now, _POLICY,
            )
            self._store.put_derived_rebuild_receipt(
                self._receipt_id(projection_id, current, "rebuilt"), projection_id, current, "rebuilt",
                {"generator_policy_id": _POLICY, "dependency_set": dependencies},
            )

    @staticmethod
    def _overlaps(episode: dict[str, Any], window: dict[str, str]) -> bool:
        return episode["valid_start"] < window["end"] and window["start"] < episode["valid_end"]

    @staticmethod
    def _projection_id(level: str, episode_id: str) -> str:
        suffix = episode_id.removeprefix("episode_b2_")
        return f"summary_b2_{level}_{suffix}"

    @staticmethod
    def _utc_day_window(timestamp: str) -> dict[str, str]:
        instant = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(timezone.utc)
        start = instant.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return {"start": start.isoformat().replace("+00:00", "Z"), "end": end.isoformat().replace("+00:00", "Z")}

    def _receipt_id(self, projection_id: str, revision: str, status: str) -> str:
        self._receipt_index += 1
        return f"derived_receipt_{projection_id}_{revision}_{status}_{self._receipt_index:03d}"
