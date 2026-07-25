"""C3 testing adapter: builds the fixed synthetic review/calibration profile and drives contract cases."""

from __future__ import annotations

import atexit
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from . import reviews
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/c3_review_calibration_v1/fixture.json").read_text(encoding="utf-8"))
CLOCK = FIXTURE["determinism"]["clock"]
WINDOWS = FIXTURE["windows"]
METRIC_SET_ID = FIXTURE["metric_set_id"]


def create_system(case: JsonObject) -> "C3ReviewSystem":
    return C3ReviewSystem(case)


class C3ReviewSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=f"{case['database_identity']}_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._store = SemanticStore(Path(self._tmpdir) / "c3.sqlite3")
        self._seed()
        self._canonical_writes_from_review_ops = 0

    def _seed(self) -> None:
        self._store.add_revision("rev_c3_seed", CLOCK, "seed")
        for item in FIXTURE["profile_objects"]:
            payload = {k: v for k, v in item.items() if k != "object_id"}
            payload["object_revision"] = "rev_c3_seed"
            payload["synthetic"] = True
            self._store.add_canonical_object(item["object_id"], payload)

    def _canonical_objects(self) -> dict[str, JsonObject]:
        return {item["object_id"]: item["payload"] for item in self._store.canonical_object_summaries()}

    def layer_snapshot(self) -> JsonObject:
        return {
            "canonical_layer": _canonical_digest(self._canonical_objects()),
            "derived_ledger": _canonical_digest({
                "reviews": self._store.ledger_records_of_type(reviews.REVIEW_RECORD_TYPE),
                "comparisons": self._store.ledger_records_of_type(reviews.COMPARISON_RECORD_TYPE),
            }),
            "revision_ledger": _canonical_digest(self._store.revision_ids()),
        }

    def _window(self, ref: Any) -> JsonObject | None:
        if isinstance(ref, str):
            window = WINDOWS.get(ref)
            return dict(window) if window else None
        if isinstance(ref, dict):
            return dict(ref)
        return None

    def _run_review_op(self, op: JsonObject) -> JsonObject:
        kind = op["op"]
        if kind == "compare_phases":
            window_a = self._window(op["window_a"])
            window_b = self._window(op["window_b"])
            if window_a is None or window_b is None:
                return {"outcome": "rejected", "reason": "out_of_profile"}
            return reviews.compare_phases(self._store, window_a, window_b, op.get("metric_set_id", ""), CLOCK)
        window = self._window(op.get("window"))
        if window is None:
            return {"outcome": "rejected", "reason": "out_of_profile"}
        args = (window["review_kind"], window["window_start"], window["window_end"])
        if kind == "generate_review":
            return reviews.generate_review(self._store, *args, generated_at=CLOCK)
        if kind == "present_review":
            return reviews.present_review(self._store, *args)
        if kind == "rebuild_review":
            return reviews.rebuild_review(self._store, *args, generated_at=CLOCK)
        if kind == "delete_review":
            return reviews.delete_review(self._store, *args)
        raise ValueError(f"unsupported C3 review op: {kind}")

    def run_case(self, case: JsonObject) -> JsonObject:
        before = self.layer_snapshot()
        outcomes: list[JsonObject] = []
        for op in case["ops"]:
            kind = op["op"]
            if kind == "inject_episode":
                self._store.add_canonical_object(
                    op["episode_id"],
                    {"object_type": "episode", "object_revision": "rev_c3_seed",
                     "occurred_on": op["occurred_on"], "synthetic": True},
                )
                outcomes.append({"outcome": "injected"})
                continue
            pre = self.layer_snapshot()["canonical_layer"]
            outcomes.append(self._run_review_op(op))
            if self.layer_snapshot()["canonical_layer"] != pre:
                self._canonical_writes_from_review_ops += 1
        return self._scenario_result(case["scenario_id"], outcomes, before, self.layer_snapshot())

    def _reports(self, window: JsonObject | None = None) -> list[JsonObject]:
        records = self._store.ledger_records_of_type(reviews.REVIEW_RECORD_TYPE)
        if window is None:
            return records
        return [r for r in records if r["review_kind"] == window["review_kind"]
                and r["window_start"] == window["window_start"] and r["window_end"] == window["window_end"]]

    def _scenario_result(self, scenario_id: str, outcomes: list[JsonObject], before: JsonObject, after: JsonObject) -> JsonObject:
        canonical_unchanged = after["canonical_layer"] == before["canonical_layer"]
        derived_unchanged = after["derived_ledger"] == before["derived_ledger"]
        w1, w2, m1, y1 = (self._window(name) for name in ("W1", "W2", "M1", "Y1"))

        if scenario_id == "C3-001":
            report = outcomes[0]["report"]
            presented = reviews.present_review(self._store, w1["review_kind"], w1["window_start"], w1["window_end"])
            return {"outcome": outcomes[0]["outcome"], "review_kind": report["review_kind"], "metrics": report["metrics"],
                    "freshness": presented["freshness"], "view_revision": report["view_revision"],
                    "derived_only": report["derived_only"], "canonical_unchanged": canonical_unchanged}
        if scenario_id == "C3-002":
            monthly = outcomes[0]["report"]["metrics"]
            yearly = outcomes[1]["report"]["metrics"]
            w1_metrics = outcomes[2]["report"]["metrics"]
            w2_metrics = outcomes[3]["report"]["metrics"]
            boundary = "W2_only" if ("2026-07-13" not in self._days(w1)) and w2_metrics["episodes"] > w1_metrics["episodes"] else "wrong"
            return {"monthly_metrics": monthly, "yearly_metrics": yearly,
                    "boundary_episode_window": boundary, "canonical_unchanged": canonical_unchanged}
        if scenario_id == "C3-003":
            stored = self._reports(w1)
            presented = outcomes[2]
            return {"freshness": presented["freshness"],
                    "report_metrics_unchanged": stored[0]["metrics"] == outcomes[0]["report"]["metrics"],
                    "stored_metrics": stored[0]["metrics"], "view_revision": stored[0]["view_revision"]}
        if scenario_id == "C3-004":
            stored = sorted(self._reports(w1), key=lambda r: r["view_revision"])
            presented = outcomes[3]
            rebuilt = outcomes[2]["report"]
            return {"view_revision": rebuilt["view_revision"], "freshness": presented["freshness"],
                    "metrics": rebuilt["metrics"],
                    "v1_preserved": len(stored) == 2 and stored[0]["view_revision"] == 1,
                    "v1_metrics": stored[0]["metrics"] if stored else None}
        if scenario_id == "C3-005":
            deleted_metrics = outcomes[1]["deleted_metrics"]
            rebuilt = outcomes[2]["report"]
            return {"rebuild_metrics_equal": rebuilt["metrics"] == deleted_metrics,
                    "rebuilt_metrics": rebuilt["metrics"], "view_revision": rebuilt["view_revision"],
                    "canonical_unchanged": canonical_unchanged}
        if scenario_id == "C3-006":
            comparison = outcomes[0]["comparison"]
            return {"outcome": outcomes[0]["outcome"], "deltas": comparison["deltas"],
                    "derived_only": comparison["derived_only"], "canonical_unchanged": canonical_unchanged}
        if scenario_id == "C3-007":
            return {"outcome": outcomes[0]["outcome"],
                    "comparison_records": len(self._store.ledger_records_of_type(reviews.COMPARISON_RECORD_TYPE)),
                    "canonical_unchanged": canonical_unchanged, "derived_unchanged": derived_unchanged}
        if scenario_id == "C3-008":
            return {"kind_mismatch_outcome": outcomes[0]["outcome"], "inverted_window_outcome": outcomes[1]["outcome"],
                    "comparison_records": len(self._store.ledger_records_of_type(reviews.COMPARISON_RECORD_TYPE)),
                    "derived_unchanged": derived_unchanged}
        if scenario_id == "C3-009":
            report = outcomes[0]["report"]
            comparison = outcomes[1]["comparison"]
            payloads = json.dumps(list(self._canonical_objects().values()), sort_keys=True)
            current_counts = reviews._compute_metrics(reviews._window_inputs(self._store, w1["window_start"], w1["window_end"]))["hypothesis_status_counts"]
            return {"derived_not_referenced_by_canonical": "review:" not in payloads and "comparison:" not in payloads,
                    "hypothesis_counts_match_snapshot": report["metrics"]["hypothesis_status_counts"] == current_counts,
                    "derived_only_flags": bool(report["derived_only"] and comparison["derived_only"])}
        if scenario_id == "C3-010":
            presented = reviews.present_review(self._store, w1["review_kind"], w1["window_start"], w1["window_end"])
            remaining = {oid: p for oid, p in self._canonical_objects().items() if oid != "EP-SYN-C3-NEW1"}
            return {"version_chain": presented["version_chain"],
                    "out_of_profile_outcome": outcomes[4]["outcome"],
                    "unrelated_canonical_unchanged": _canonical_digest(remaining) == before["canonical_layer"],
                    "canonical_writes_from_review_ops": self._canonical_writes_from_review_ops}
        raise ValueError(f"unsupported C3 scenario: {scenario_id}")

    def _days(self, window: JsonObject) -> set[str]:
        inputs = reviews._window_inputs(self._store, window["window_start"], window["window_end"])
        return {p["occurred_on"] for p in inputs["episodes"].values()}
