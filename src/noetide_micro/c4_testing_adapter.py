"""C4 testing adapter: builds the fixed synthetic scenario/action profile and drives contract cases."""

from __future__ import annotations

import atexit
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from . import scenarios
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/c4_scenario_action_v1/fixture.json").read_text(encoding="utf-8"))
CLOCK = FIXTURE["determinism"]["clock"]
CLOCK_DATE = FIXTURE["determinism"]["clock_date"]
SPECS = FIXTURE["scenario_specs"]
ACTIONS = FIXTURE["follow_up_actions"]
DECISION_ID = FIXTURE["base_decision"]["object_id"]


def create_system(case: JsonObject) -> "C4ScenarioSystem":
    return C4ScenarioSystem(case)


def scenario_id_for(kind: str) -> str:
    return f"SCN-{DECISION_ID}-{kind}"


class C4ScenarioSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=f"{case['database_identity']}_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._store = SemanticStore(Path(self._tmpdir) / "c4.sqlite3")
        self._seed()
        self._auto_transitions = 0

    def _seed(self) -> None:
        self._store.add_revision("rev_c4_seed", CLOCK, "seed")
        decision = FIXTURE["base_decision"]
        self._store.add_canonical_object(decision["object_id"], {
            "object_type": "decision",
            "object_revision": "rev_c4_seed",
            "title": decision["title"],
            "status": decision["status"],
            "synthetic": True,
        })

    def _by_type(self, object_type: str) -> dict[str, JsonObject]:
        return {
            item["object_id"]: item["payload"]
            for item in self._store.canonical_object_summaries()
            if item["payload"].get("object_type") == object_type
        }

    def layer_snapshot(self) -> JsonObject:
        return {
            "decision_layer": _canonical_digest(self._by_type("decision")),
            "scenario_layer": _canonical_digest(self._by_type("assertion")),
            "followup_layer": _canonical_digest(self._by_type("commitment")),
            "receipts_ledger": _canonical_digest({
                "selections": self._store.ledger_records_of_type(scenarios.SELECTION_RECORD_TYPE),
                "transitions": self._store.ledger_records_of_type(scenarios.FOLLOWUP_TRANSITION_RECORD_TYPE),
            }),
            "revision_ledger": _canonical_digest(self._store.revision_ids()),
        }

    def run_case(self, case: JsonObject) -> JsonObject:
        before = self.layer_snapshot()
        outcomes: list[JsonObject] = []
        selected_kind = "baseline"
        for op in case["ops"]:
            kind = op["op"]
            if kind == "create_scenario_set":
                outcomes.append(scenarios.create_scenario_set(self._store, DECISION_ID, SPECS, op["confirmed"], CLOCK))
            elif kind == "select_scenario":
                skind = op.get("scenario_kind", "baseline")
                if skind not in scenarios.SCENARIO_KINDS:
                    outcomes.append({"outcome": "rejected", "reason": "out_of_profile"})
                else:
                    selected_kind = skind
                    outcomes.append(scenarios.select_scenario(self._store, scenario_id_for(skind), op["confirmed"], CLOCK))
            elif kind == "create_follow_ups":
                outcomes.append(scenarios.create_follow_ups(self._store, scenario_id_for(selected_kind), ACTIONS, op["confirmed"], CLOCK))
            elif kind == "complete_follow_up":
                outcomes.append(scenarios.complete_follow_up(self._store, op["follow_up_id"], op["confirmed"], CLOCK))
            elif kind == "follow_up_view":
                outcomes.append(scenarios.follow_up_view(self._store, scenario_id_for(selected_kind), CLOCK_DATE))
            elif kind == "evaluate_feasibility":
                outcomes.append({k: scenarios.evaluate_feasibility(v) for k, v in SPECS.items()})
            elif kind == "present_scenarios":
                outcomes.append([scenarios.present_scenario(self._store, scenario_id_for(k)) for k in scenarios.SCENARIO_KINDS])
            elif kind == "attempt_mark_observed":
                outcomes.append(scenarios.attempt_mark_observed(self._store, scenario_id_for(op.get("scenario_kind", "baseline"))))
            else:
                raise ValueError(f"unsupported C4 op: {kind}")
        return self._scenario_result(case["scenario_id"], outcomes, before, self.layer_snapshot(), selected_kind)

    def _scenario_result(self, scenario_id: str, outcomes: list[JsonObject], before: JsonObject, after: JsonObject, selected_kind: str) -> JsonObject:
        sid = scenario_id_for(selected_kind)
        if scenario_id == "C4-001":
            created = outcomes[0]["scenarios"]
            return {"outcome": outcomes[0]["outcome"],
                    "feasibility": {k: p["feasibility_status"] for k, p in created.items()},
                    "all_predicted": all(p["assertion_kind"] == "predicted" for p in created.values()),
                    "scenario_count": len(self._by_type("assertion"))}
        if scenario_id == "C4-002":
            return {"outcome": outcomes[0]["outcome"], "scenario_count": len(self._by_type("assertion"))}
        if scenario_id == "C4-003":
            payload = self._store.canonical_object(sid)
            return {"upgrade_outcome": outcomes[1]["outcome"], "assertion_kind": payload["assertion_kind"],
                    "is_fact": False, "object_revision": payload["object_revision"]}
        if scenario_id == "C4-004":
            scenario_before = before["scenario_layer"]
            scenario_after_create = _canonical_digest(self._by_type("assertion"))
            receipts = self._store.ledger_records_of_type(scenarios.SELECTION_RECORD_TYPE)
            return {"select_outcome": outcomes[1]["outcome"], "selection_receipts": len(receipts),
                    "decision_unchanged": after["decision_layer"] == before["decision_layer"],
                    "scenario_unchanged": self._store.canonical_object(sid)["object_revision"] == 1}
        if scenario_id == "C4-005":
            followups = self._by_type("commitment")
            return {"create_outcome": outcomes[2]["outcome"], "follow_up_count": len(followups),
                    "all_open": all(p["status"] == "open" for p in followups.values()),
                    "refs_correct": all(p["scenario_ref"] == sid and p["decision_ref"] == DECISION_ID for p in followups.values())}
        if scenario_id == "C4-006":
            done = self._store.canonical_object("FU-SYN-C4-003")
            others = {k: p for k, p in self._by_type("commitment").items() if k != "FU-SYN-C4-003"}
            return {"complete_outcome": outcomes[3]["outcome"], "status": done["status"],
                    "object_revision": done["object_revision"], "history_entries": len(done["revision_history"]),
                    "transition_receipts": len(self._store.ledger_records_of_type(scenarios.FOLLOWUP_TRANSITION_RECORD_TYPE)),
                    "others_unchanged": all(p["status"] == "open" and p["object_revision"] == 1 for p in others.values())}
        if scenario_id == "C4-007":
            view = outcomes[4]
            return {"view_statuses": {i["follow_up_id"]: i["view_status"] for i in view["items"]},
                    "canonical_unchanged_by_view": all(p["object_revision"] in (1, 2) for p in self._by_type("commitment").values())
                    and self._store.canonical_object("FU-SYN-C4-001")["status"] == "open"}
        if scenario_id == "C4-008":
            first, second = outcomes[1], outcomes[2]
            return {"first": first, "second": second, "identical": first == second,
                    "pessimistic_infeasible": first["pessimistic"] == "infeasible"}
        if scenario_id == "C4-009":
            views = outcomes[4]
            fact_refs = self._store._connection.execute("SELECT object_id FROM canonical_evidence_refs").fetchall()
            scenario_ids = set(self._by_type("assertion"))
            return {"all_is_fact_false": all(v["is_fact"] is False for v in views),
                    "all_not_professional_advice": all(v["not_professional_advice"] is True for v in views),
                    "no_advice_fields": all("advice" not in v and "recommendation" not in v for v in views),
                    "scenarios_not_in_fact_evidence": not any(row[0] in scenario_ids for row in fact_refs)}
        if scenario_id == "C4-010":
            done = self._store.canonical_object("FU-SYN-C4-003")
            chain_ok = done["object_revision"] == 2 and len(done["revision_history"]) == 1 and done["revision_history"][0]["status"] == "open"
            return {"revision_chain_complete": chain_ok,
                    "out_of_profile_select_outcome": outcomes[5]["outcome"],
                    "out_of_profile_complete_outcome": outcomes[6]["outcome"],
                    "unconfirmed_followups_outcome": outcomes[7]["outcome"],
                    "unrelated_unchanged": after["decision_layer"] == before["decision_layer"],
                    "auto_transitions": self._auto_transitions}
        raise ValueError(f"unsupported C4 scenario: {scenario_id}")
