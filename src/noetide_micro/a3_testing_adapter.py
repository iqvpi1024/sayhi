"""Fixture-scoped A3 contract adapter (SPEC-A3-ENTITY-MERGE-001)."""
from __future__ import annotations

import copy
import json
from typing import Any

from .entity_merge import EntityMergeService
from .store import SemanticStore


_NOW = "2032-05-10T09:00:00Z"
_PROFILE = "a3_entity_merge_v1"
_SEED_REVISION = "rev_030"
_MERGE_ID = "merge_person_delta_person_epsilon"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class A3System:
    def __init__(self, case: dict[str, Any]) -> None:
        self.case = copy.deepcopy(case)
        self.store = SemanticStore(":memory:")
        self._seed()
        self.service = EntityMergeService(self.store, _NOW)
        if "merge" in case.get("pre_published", []):
            self.service.publish_merge(self.case["merge_candidate"])
        if "split" in case.get("pre_published", []):
            self.service.publish_split({
                "operation": "split",
                "merge_ref": _MERGE_ID,
                "reason": "synthetic user requests split rollback",
            })
        self._baseline = self.layer_snapshot()
        self._pre_split_merge_records = _canonical(self.store.merge_records())

    def inject_failure(self, failure_point: str) -> None:
        self.service.inject_failure(failure_point)

    def layer_snapshot(self) -> dict[str, Any]:
        objects = self.store.seed_snapshot()["objects"]
        by_type = {
            kind: {oid: payload for oid, payload in sorted(objects.items()) if payload.get("object_type") == kind}
            for kind in ("entity", "relationship", "state", "assertion", "hypothesis")
        }
        trust_closeness = {
            oid: payload for oid, payload in by_type["state"].items()
            if payload.get("state_kind") in ("trust", "closeness")
        }
        return {
            "entities": _canonical(by_type["entity"]),
            "relationships": _canonical(by_type["relationship"]),
            "states": _canonical(by_type["state"]),
            "assertions": _canonical(by_type["assertion"]),
            "merge_records": _canonical(self.store.merge_records()),
            "revisions": self.store.current_revision(),
            "source_records": _canonical([
                self.store.seeded_source(source_id)
                for source_id in ("src_a3_delta_001", "src_a3_epsilon_001")
            ]),
            "trust_closeness": _canonical(trust_closeness),
            "personality_judgments": _canonical(by_type["hypothesis"]),
            "historical_revisions": [_SEED_REVISION] if self._revision_exists(_SEED_REVISION) else [],
        }

    def run_case(self, case: dict[str, Any]) -> dict[str, Any]:
        results: dict[str, Any] = {}
        for operation in case["operations"]:
            results = self._run_operation(operation)
        return results

    def _run_operation(self, operation: str) -> dict[str, Any]:
        if operation == "publish_merge":
            result = self.service.publish_merge(self.case["merge_candidate"])
            if result.get("reason_code") == "merge_redirect_failed":
                source = self.store.canonical_object("person_delta")
                preserved = (
                    source.get("identity_status") == "active"
                    and "merged_into" not in source
                    and self.store.canonical_object("relationship_a3_001")["participant_refs"] == ["person_delta", "person_zeta"]
                    and self.store.canonical_object("state_a3_001")["subject_ref"] == "person_delta"
                    and self.store.canonical_object("assertion_a3_001")["subject_ref"] == "person_delta"
                )
                result = {
                    **result,
                    "canonical_readable": True,
                    "pre_merge_state_preserved": preserved,
                    "merge_record_absent": self.store.merge_records() == [],
                }
            return result
        if operation == "publish_split":
            return self.service.publish_split({
                "operation": "split",
                "merge_ref": _MERGE_ID,
                "reason": "synthetic user requests split rollback",
            })
        if operation == "attempt_invalid_merges":
            outcomes = [self.service.publish_merge(attempt) for attempt in self.case["invalid_merge_attempts"]]
            return self._aggregate("merge", outcomes)
        if operation == "attempt_invalid_splits":
            outcomes = []
            for attempt in self.case["invalid_split_attempts"]:
                resolved = dict(attempt)
                if resolved.get("merge_ref") == "<published_merge_id>":
                    resolved["merge_ref"] = _MERGE_ID
                outcomes.append(self.service.publish_split(resolved))
            return self._aggregate("split", outcomes)
        if operation == "read_history_and_views":
            source = self.store.canonical_object("person_delta")
            views = self.service.core_view_statuses()
            return {
                "status": "history_and_views_read",
                "source_history_visible": source.get("identity_status") == "merged"
                and self.store.merge_record_or_none(_MERGE_ID) is not None,
                "source_assertions_visible": self.store.canonical_object_or_none("assertion_a3_001") is not None
                and self.store.seeded_source("src_a3_delta_001") is not None,
                "core_views": views,
                "fake_fresh": any(status == "fresh" for status in views.values()),
                "data_revision": self.store.current_revision(),
            }
        if operation == "read_audit_chain":
            record = self.store.merge_record_or_none(_MERGE_ID)
            return {
                "status": "audit_chain_read",
                "audit_events": self.service.audit_events(),
                "merge_record_retained": record is not None
                and len(record["pre_merge_references"]) == 3,
                "append_only": _canonical(self.store.merge_records()) == self._pre_split_merge_records,
                "data_revision": self.store.current_revision(),
            }
        if operation == "check_protected_layers":
            current = self.layer_snapshot()
            baseline = self._baseline
            trust_then = json.loads(baseline["trust_closeness"])
            trust_now = json.loads(current["trust_closeness"])
            trust_keys = [oid for oid, payload in trust_then.items() if payload.get("state_kind") == "trust"]
            closeness_keys = [oid for oid, payload in trust_then.items() if payload.get("state_kind") == "closeness"]
            unrelated_baseline = {
                key: json.loads(baseline[key])
                for key in ("entities", "relationships", "source_records")
            }
            unrelated_now = {
                key: json.loads(current[key])
                for key in ("entities", "relationships", "source_records")
            }
            unrelated_pairs = (
                ("person_zeta", "entities"),
                ("relationship_a3_002", "relationships"),
                (0, "source_records"),
                (1, "source_records"),
            )
            unrelated_unchanged = all(
                self._unrelated_value(unrelated_baseline[kind], marker)
                == self._unrelated_value(unrelated_now[kind], marker)
                for marker, kind in unrelated_pairs
            )
            return {
                "status": "protected_layers_checked",
                "trust_unchanged": all(trust_now.get(oid) == trust_then[oid] for oid in trust_keys),
                "closeness_unchanged": all(trust_now.get(oid) == trust_then[oid] for oid in closeness_keys),
                "personality_unchanged": current["personality_judgments"] == baseline["personality_judgments"],
                "unrelated_objects_unchanged": unrelated_unchanged,
                "data_revision": self.store.current_revision(),
            }
        raise ValueError(f"unknown A3 operation {operation}")

    def _aggregate(self, kind: str, outcomes: list[dict[str, Any]]) -> dict[str, Any]:
        failed = [outcome for outcome in outcomes if outcome.get("status") == "failed"]
        return {
            "status": "all_failed" if len(failed) == len(outcomes) else "partial_failure",
            "failed_attempts": len(failed),
            "reason_codes": [outcome.get("reason_code") for outcome in outcomes],
            "data_revision": self.store.current_revision(),
        }

    def _unrelated_value(self, layer: Any, marker: Any) -> Any:
        if isinstance(layer, dict):
            return layer.get(marker)
        if isinstance(layer, list) and isinstance(marker, int):
            return layer[marker] if marker < len(layer) else None
        return None

    def _revision_exists(self, revision_id: str) -> bool:
        try:
            return revision_id in {
                record["revision_id"] for record in self.store.seed_snapshot()["objects"].values()
            } or revision_id == self.store.current_revision() or self._revision_in_table(revision_id)
        except Exception:
            return False

    def _revision_in_table(self, revision_id: str) -> bool:
        row = self.store._connection.execute(
            "SELECT 1 FROM canonical_revisions WHERE revision_id = ?", (revision_id,),
        ).fetchone()
        return row is not None

    def _seed(self) -> None:
        fixture = json.loads(
            __import__("pathlib").Path(
                __file__
            ).resolve().parents[2].joinpath("tests/fixtures/a3_entity_merge_v1/fixture.json").read_text(encoding="utf-8")
        )
        self.case.setdefault("merge_candidate", fixture["merge_candidate"])
        with self.store.transaction():
            self.store.add_revision(_SEED_REVISION, _NOW, revision_kind="seed")
            for entity in fixture["shared_entities"]:
                self.store.add_canonical_object(entity["entity_id"], {
                    "entity_id": entity["entity_id"],
                    "object_type": "entity",
                    "object_revision": _SEED_REVISION,
                    "entity_kind": "person",
                    "identity_status": "active",
                    "synthetic": True,
                    "synthetic_profile_id": _PROFILE,
                })
            self.store.add_canonical_object("relationship_a3_001", {
                "relationship_id": "relationship_a3_001", "object_type": "relationship",
                "object_revision": _SEED_REVISION,
                "participant_refs": ["person_delta", "person_zeta"],
                "synthetic_profile_id": _PROFILE,
            })
            self.store.add_canonical_object("relationship_a3_002", {
                "relationship_id": "relationship_a3_002", "object_type": "relationship",
                "object_revision": _SEED_REVISION,
                "participant_refs": ["person_epsilon", "person_zeta"],
                "synthetic_profile_id": _PROFILE,
            })
            self.store.add_canonical_object("state_a3_001", {
                "state_id": "state_a3_001", "object_type": "state", "object_revision": _SEED_REVISION,
                "state_kind": "contact_state", "subject_ref": "person_delta",
                "synthetic_profile_id": _PROFILE,
            })
            self.store.add_canonical_object("assertion_a3_001", {
                "assertion_id": "assertion_a3_001", "object_type": "assertion",
                "object_revision": _SEED_REVISION, "subject_ref": "person_delta",
                "synthetic_profile_id": _PROFILE,
            })
            for entity_id, values in fixture["protected_layers"]["trust_closeness"].items():
                for kind in ("trust", "closeness"):
                    self.store.add_canonical_object(f"state_{kind}_{entity_id}", {
                        "state_id": f"state_{kind}_{entity_id}", "object_type": "state",
                        "object_revision": _SEED_REVISION, "state_kind": kind,
                        "subject_ref": entity_id, "value": values[kind],
                        "synthetic_profile_id": _PROFILE,
                    })
            for entity_id, content in fixture["protected_layers"]["personality_judgments"].items():
                self.store.add_canonical_object(f"hypothesis_personality_{entity_id}", {
                    "hypothesis_id": f"hypothesis_personality_{entity_id}", "object_type": "hypothesis",
                    "object_revision": _SEED_REVISION, "subject_ref": entity_id,
                    "content": content, "synthetic_profile_id": _PROFILE,
                })
            for view in ("person_card", "relationship_timeline", "current_state"):
                self.store.upsert_projection(view, _SEED_REVISION, _SEED_REVISION, "fresh", {"objects": []})
        for source in fixture["shared_sources"]:
            self.store.append_source(
                {
                    "source_id": source["source_id"],
                    "append_receipt_id": f"receipt_{source['source_id']}",
                    "source_kind": "synthetic_text",
                    "content_hash": source["source_id"],
                    "content": source["content"],
                    "synthetic": True,
                    "synthetic_profile_id": _PROFILE,
                },
                {"receipt_id": f"receipt_{source['source_id']}", "status": "stored"},
            )


def create_system(case: dict[str, Any]) -> A3System:
    return A3System(case)
