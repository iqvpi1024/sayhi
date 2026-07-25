"""C2 testing adapter: builds the fixed synthetic hypothesis profile and drives contract cases."""

from __future__ import annotations

import atexit
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .hypotheses import (
    TRANSITION_RECORD_TYPE,
    attach_evidence,
    attempt_upgrade_to_fact,
    create_hypothesis,
    present_hypothesis,
    transition_status,
)
from .store import SemanticStore, _canonical_digest


JsonObject = dict[str, Any]
ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "tests/fixtures/c2_hypothesis_v1/fixture.json").read_text(encoding="utf-8"))
SEED = FIXTURE["hypothesis_seed"]
CLOCK = FIXTURE["determinism"]["clock"]
HYPOTHESIS_ID = SEED["hypothesis_id"]


def create_system(case: JsonObject) -> "C2HypothesisSystem":
    return C2HypothesisSystem(case)


class C2HypothesisSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix=f"{case['database_identity']}_")
        atexit.register(shutil.rmtree, self._tmpdir, True)
        self._store = SemanticStore(Path(self._tmpdir) / "c2.sqlite3")
        self._seed()
        self._auto_transitions = 0

    def _seed(self) -> None:
        store = self._store
        store.add_revision("rev_c2_seed", CLOCK, "seed")
        for source in FIXTURE["base_sources"]:
            store.append_source(
                {
                    "source_id": source["source_id"],
                    "append_receipt_id": f"receipt_{source['source_id']}",
                    "source_kind": source["source_kind"],
                    "content_hash": hashlib.sha256(source["text"].encode("utf-8")).hexdigest(),
                    "text": source["text"],
                    "synthetic": True,
                },
                {"receipt_id": f"receipt_{source['source_id']}", "source_id": source["source_id"], "status": "stored", "actor": "c2_fixture_seed"},
            )
        for entity in FIXTURE["base_entities"]:
            store.add_canonical_object(
                entity["entity_id"],
                {"object_type": "entity", "object_revision": "rev_c2_seed", "entity_kind": entity["entity_kind"], "display_name": entity["display_name"], "synthetic": True},
            )

    def _objects_by_type(self) -> dict[str, JsonObject]:
        grouped: dict[str, JsonObject] = {}
        for item in self._store.canonical_object_summaries():
            grouped.setdefault(item["payload"]["object_type"], {})[item["object_id"]] = item["payload"]
        return grouped

    def layer_snapshot(self) -> JsonObject:
        store = self._store
        grouped = self._objects_by_type()
        source_ids = sorted(s["source_id"] for s in FIXTURE["base_sources"])
        return {
            "source_layer": _canonical_digest({sid: store.seeded_source(sid) for sid in source_ids}),
            "entity_layer": _canonical_digest(grouped.get("entity", {})),
            "assertion_layer": _canonical_digest(grouped.get("assertion", {})),
            "derived_layer": _canonical_digest(store.projection_records()),
            "hypothesis_layer": _canonical_digest(grouped.get("hypothesis", {})),
            "revision_ledger": _canonical_digest({"revisions": store.revision_ids(), "receipts": store.ledger_records_of_type(TRANSITION_RECORD_TYPE)}),
        }

    def _payload(self, hypothesis_id: str = HYPOTHESIS_ID) -> JsonObject:
        payload = self._store.canonical_object_or_none(hypothesis_id)
        if payload is None:
            raise KeyError(hypothesis_id)
        return payload

    def _status(self, hypothesis_id: str) -> str | None:
        payload = self._store.canonical_object_or_none(hypothesis_id)
        return payload["status"] if payload else None

    def _receipts(self, kind: str | None = None) -> list[JsonObject]:
        records = [r for r in self._store.ledger_records_of_type(TRANSITION_RECORD_TYPE) if r["hypothesis_id"] == HYPOTHESIS_ID]
        return [r for r in records if kind is None or r["kind"] == kind]

    def _fact_evidence_source_ids(self) -> set[str]:
        rows = self._store._connection.execute(
            "SELECT cer.source_id FROM canonical_evidence_refs cer "
            "JOIN canonical_objects co ON co.object_id = cer.object_id "
            "WHERE co.object_type = 'assertion'"
        ).fetchall()
        return {row[0] for row in rows}

    def run_case(self, case: JsonObject) -> JsonObject:
        before = self.layer_snapshot()
        outcomes: JsonObject = {}
        for op in case["ops"]:
            kind = op["op"]
            hypothesis_id = op.get("hypothesis_id", HYPOTHESIS_ID)
            pre_status = self._status(hypothesis_id) if hypothesis_id == HYPOTHESIS_ID else None
            if kind == "create_hypothesis":
                result = create_hypothesis(self._store, SEED, op["evidence"], confirmed=op["confirmed"], at=op["at"])
                outcomes["create_outcome"] = result["outcome"]
            elif kind == "attach_evidence":
                result = attach_evidence(self._store, hypothesis_id, op, confirmed=op["confirmed"], at=op["at"])
                if not op["confirmed"]:
                    outcomes["unconfirmed_attach_outcome"] = result["outcome"]
                elif op["source_id"].startswith("DERIVED:"):
                    outcomes["illegal_derived_ref_outcome"] = result["outcome"]
                elif op["source_id"].endswith("MISSING"):
                    outcomes["illegal_missing_source_outcome"] = result["outcome"]
                else:
                    outcomes["attach_outcome"] = result["outcome"]
            elif kind == "transition_status":
                result = transition_status(self._store, hypothesis_id, op["to_status"], op["reason"], confirmed=op["confirmed"], at=op["at"])
                if not op["confirmed"]:
                    outcomes["unconfirmed_transition_outcome"] = result["outcome"]
                elif hypothesis_id != HYPOTHESIS_ID:
                    outcomes["out_of_profile_outcome"] = result["outcome"]
                else:
                    outcomes["transition_outcome"] = result["outcome"]
            elif kind == "present":
                outcomes["present"] = present_hypothesis(self._store, hypothesis_id)
            elif kind == "upgrade_to_fact":
                pre_layers = self.layer_snapshot()
                result = attempt_upgrade_to_fact(self._store, hypothesis_id)
                post_layers = self.layer_snapshot()
                outcomes["upgrade_outcome"] = result["outcome"]
                outcomes["writes_during_upgrade"] = 0 if (pre_layers["hypothesis_layer"], pre_layers["revision_ledger"]) == (post_layers["hypothesis_layer"], post_layers["revision_ledger"]) else 1
            else:
                raise ValueError(f"unsupported C2 op: {kind}")
            if hypothesis_id == HYPOTHESIS_ID and kind not in ("create_hypothesis",):
                post_status = self._status(hypothesis_id)
                if pre_status != post_status and not (kind == "transition_status" and op["confirmed"]):
                    self._auto_transitions += 1
        return self._assemble(case["scenario_id"], outcomes, before)

    def _history_statuses(self) -> list[str]:
        return [entry["status"] for entry in self._payload()["revision_history"]]

    def _assemble(self, scenario_id: str, outcomes: JsonObject, before: JsonObject) -> JsonObject:
        payload = self._payload()
        present = outcomes.get("present") or present_hypothesis(self._store, HYPOTHESIS_ID)
        after = self.layer_snapshot()
        if scenario_id == "C2-001":
            return {
                "create_outcome": outcomes["create_outcome"],
                "status": payload["status"],
                "object_revision": payload["object_revision"],
                "evidence_for": len(payload["evidence_for"]),
                "evidence_against": len(payload["evidence_against"]),
                "valid_scope": payload["valid_scope"],
                "hypothesis_kind": payload["hypothesis_kind"],
                "in_assertion_layer": HYPOTHESIS_ID in self._objects_by_type().get("assertion", {}),
            }
        if scenario_id == "C2-002":
            return {
                "attach_outcome": outcomes["attach_outcome"],
                "status": payload["status"],
                "object_revision": payload["object_revision"],
                "evidence_for": len(payload["evidence_for"]),
                "history_entries": len(payload["revision_history"]),
            }
        if scenario_id == "C2-003":
            return {
                "attach_outcome": outcomes["attach_outcome"],
                "status": payload["status"],
                "evidence_against": len(payload["evidence_against"]),
                "auto_transitions": self._auto_transitions,
            }
        if scenario_id == "C2-004":
            return {
                "transition_outcome": outcomes["transition_outcome"],
                "status": payload["status"],
                "display_tone": present["display_tone"],
                "object_revision": payload["object_revision"],
                "history_statuses": self._history_statuses(),
                "transition_receipts": len(self._receipts("transition")),
            }
        if scenario_id == "C2-005":
            history = payload["revision_history"]
            return {
                "status": payload["status"],
                "display_tone": present["display_tone"],
                "evidence_against": len(payload["evidence_against"]),
                "object_revision": payload["object_revision"],
                "history_statuses": self._history_statuses(),
                "all_history_readable": len(history) == payload["object_revision"] - 1
                and all("status" in entry and "object_revision" in entry for entry in history),
            }
        if scenario_id == "C2-006":
            return {
                "display_tone": present["display_tone"],
                "is_fact": present["is_fact"],
                "in_fact_evidence_set": bool(
                    {ref["source_id"] for ref in payload["evidence_for"] + payload["evidence_against"]} & self._fact_evidence_source_ids()
                ),
                "certain_tone_used": present["display_tone"] in ("certain", "factual"),
                "assertion_layer_unchanged": after["assertion_layer"] == before["assertion_layer"],
            }
        if scenario_id == "C2-007":
            return {
                "upgrade_outcome": outcomes["upgrade_outcome"],
                "writes_during_upgrade": outcomes["writes_during_upgrade"],
                "status": payload["status"],
                "object_revision": payload["object_revision"],
            }
        if scenario_id == "C2-008":
            return {
                "final_status": payload["status"],
                "object_revision": payload["object_revision"],
                "transition_receipts": len(self._receipts("transition")),
                "history_statuses": self._history_statuses(),
                "no_deletions": len(self._receipts()) == 9 and len(payload["revision_history"]) == 8,
            }
        if scenario_id == "C2-009":
            return {
                "unconfirmed_attach_outcome": outcomes["unconfirmed_attach_outcome"],
                "unconfirmed_transition_outcome": outcomes["unconfirmed_transition_outcome"],
                "status": payload["status"],
                "object_revision": payload["object_revision"],
                "evidence_for": len(payload["evidence_for"]),
                "evidence_against": len(payload["evidence_against"]),
                "auto_transitions": self._auto_transitions,
            }
        if scenario_id == "C2-010":
            history = payload["revision_history"]
            current = "active"
            chain_complete = True
            for entry in history:
                if entry["status"] != current:
                    chain_complete = False
                    break
                if entry.get("change") == "transition":
                    current = entry["to_status"]
            chain_complete = chain_complete and current == payload["status"] and len(history) == payload["object_revision"] - 1
            all_refs = payload["evidence_for"] + payload["evidence_against"] + payload["evidence_contextual"]
            return {
                "revision_chain_complete": chain_complete,
                "all_evidence_sources_exist": all(self._store.seeded_source(ref["source_id"]) is not None for ref in all_refs),
                "illegal_missing_source_outcome": outcomes["illegal_missing_source_outcome"],
                "illegal_derived_ref_outcome": outcomes["illegal_derived_ref_outcome"],
                "out_of_profile_outcome": outcomes["out_of_profile_outcome"],
                "unrelated_canonical_unchanged": after["entity_layer"] == before["entity_layer"] and after["assertion_layer"] == before["assertion_layer"],
                "auto_transitions": self._auto_transitions,
                "final_status": payload["status"],
                "object_revision": payload["object_revision"],
            }
        raise ValueError(f"unsupported C2 scenario: {scenario_id}")
