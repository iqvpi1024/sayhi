"""Fixed synthetic entity merge/split ChangeSet behavior for A3 (SPEC-A3-ENTITY-MERGE-001)."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
_PROFILE = "a3_entity_merge_v1"
_PROTECTED_STATE_KINDS = frozenset({"trust", "closeness"})
_CORE_VIEWS = ("person_card", "relationship_timeline", "current_state")


class _InjectedMergeFailure(RuntimeError):
    """Internal failure injected at entity_merge.mid_redirect to prove atomicity."""


class EntityMergeService:
    """Publishes user-confirmed merge/split ChangeSets for the fixed A3 synthetic profile.

    Reference redirection only covers relationship participant_refs and ordinary
    state/assertion subject_ref. trust/closeness states and hypothesis objects
    (personality judgments) are never rewritten by merge or split.
    """

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now
        self._injected_failure: str | None = None

    def inject_failure(self, failure_point: str) -> None:
        if failure_point != "entity_merge.mid_redirect":
            raise ValueError("unknown A3 failure point")
        self._injected_failure = failure_point

    def publish_merge(self, candidate: Mapping[str, Any]) -> JsonObject:
        failure = self._merge_preflight(candidate)
        if failure is not None:
            return failure
        source_ref = candidate["source_entity_ref"]
        target_ref = candidate["target_entity_ref"]
        affected = self._affected_references(source_ref)
        merge_id = f"merge_{source_ref}_{target_ref}"
        base_revision = self._store.current_revision()
        changeset_id = f"changeset_a3_merge_{source_ref}_{target_ref}"
        revision = self._next_revision()
        pre_merge_references = [
            {
                "ref_kind": entry["ref_kind"],
                "object_id": entry["object_id"],
                "field": entry["field"],
                "old_value": copy.deepcopy(entry["old_value"]),
            }
            for entry in affected
        ]
        try:
            with self._store.transaction():
                self._store.add_revision(revision, self._now)
                source = self._store.canonical_object(source_ref)
                updated_source = copy.deepcopy(source)
                updated_source["identity_status"] = "merged"
                updated_source["merged_into"] = target_ref
                updated_source["object_revision"] = revision
                self._store.replace_canonical_object(source_ref, updated_source)
                for index, entry in enumerate(affected):
                    if index == 1 and self._injected_failure == "entity_merge.mid_redirect":
                        raise _InjectedMergeFailure("injected at entity_merge.mid_redirect")
                    payload = self._store.canonical_object(entry["object_id"])
                    updated = copy.deepcopy(payload)
                    updated[entry["field"]] = self._redirected_value(entry, source_ref, target_ref)
                    updated["object_revision"] = revision
                    self._store.replace_canonical_object(entry["object_id"], updated)
                self._store.put_merge_record(
                    merge_id, source_ref, target_ref, pre_merge_references,
                    revision, self._now, _PROFILE,
                )
                self._write_changeset(changeset_id, "merge", candidate, revision, base_revision)
                self._store.mark_all_projections_stale(revision)
        except _InjectedMergeFailure:
            return {"status": "failed", "reason_code": "merge_redirect_failed", "data_revision": self._store.current_revision()}
        record = self._store.merge_record(merge_id)
        return {
            "status": "merge_published",
            "source_entity_ref": source_ref,
            "target_entity_ref": target_ref,
            "source_identity_status": self._store.canonical_object(source_ref)["identity_status"],
            "merged_into": self._store.canonical_object(source_ref)["merged_into"],
            "redirected_references": len(record["pre_merge_references"]),
            "merge_record_complete": record["pre_merge_references"] == pre_merge_references,
            "data_revision": self._store.current_revision(),
        }

    def publish_split(self, proposal: Mapping[str, Any]) -> JsonObject:
        failure = self._split_preflight(proposal)
        if failure is not None:
            return failure
        merge_ref = proposal["merge_ref"]
        record = self._store.merge_record(merge_ref)
        source_ref = record["source_entity_ref"]
        split_id = f"split_{merge_ref}"
        base_revision = self._store.current_revision()
        changeset_id = f"changeset_a3_split_{merge_ref}"
        revision = self._next_revision()
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            for entry in record["pre_merge_references"]:
                payload = self._store.canonical_object(entry["object_id"])
                updated = copy.deepcopy(payload)
                updated[entry["field"]] = copy.deepcopy(entry["old_value"])
                updated["object_revision"] = revision
                self._store.replace_canonical_object(entry["object_id"], updated)
            source = self._store.canonical_object(source_ref)
            restored_source = copy.deepcopy(source)
            restored_source["identity_status"] = "active"
            restored_source.pop("merged_into", None)
            restored_source["object_revision"] = revision
            self._store.replace_canonical_object(source_ref, restored_source)
            self._store.put_split_record(split_id, merge_ref, revision, self._now)
            self._write_changeset(changeset_id, "split", proposal, revision, base_revision)
            self._store.mark_all_projections_stale(revision)
        field_equivalent = all(
            self._store.canonical_object(entry["object_id"])[entry["field"]] == entry["old_value"]
            for entry in record["pre_merge_references"]
        )
        source_after = self._store.canonical_object(source_ref)
        return {
            "status": "split_published",
            "source_entity_ref": source_ref,
            "source_identity_status": source_after["identity_status"],
            "merged_into_cleared": "merged_into" not in source_after,
            "references_restored": len(record["pre_merge_references"]),
            "field_equivalent_to_pre_merge": field_equivalent,
            "data_revision": self._store.current_revision(),
        }

    def audit_events(self) -> list[str]:
        events: list[tuple[str, str]] = []
        for record in self._store.merge_records():
            events.append((record["published_revision"], "merge_published"))
        for record in self._store.split_records():
            events.append((record["published_revision"], "split_published"))
        events.sort(key=lambda item: item[0])
        return [name for _, name in events]

    def core_view_statuses(self) -> JsonObject:
        statuses: JsonObject = {}
        for view_name in _CORE_VIEWS:
            try:
                statuses[view_name] = self._store.projection_record(view_name)["freshness_status"]
            except KeyError:
                statuses[view_name] = "unavailable"
        return statuses

    def _affected_references(self, source_ref: str) -> list[JsonObject]:
        affected: list[JsonObject] = []
        for object_id, payload in sorted(self._store.seed_snapshot()["objects"].items()):
            if payload.get("synthetic_profile_id", _PROFILE) != _PROFILE:
                continue
            object_type = payload.get("object_type")
            if object_type == "relationship":
                participants = payload.get("participant_refs")
                if isinstance(participants, list) and source_ref in participants:
                    affected.append({
                        "ref_kind": "relationship_party",
                        "object_id": object_id,
                        "field": "participant_refs",
                        "old_value": copy.deepcopy(participants),
                    })
            elif object_type in ("state", "assertion"):
                if object_type == "state" and payload.get("state_kind") in _PROTECTED_STATE_KINDS:
                    continue
                if payload.get("subject_ref") == source_ref:
                    affected.append({
                        "ref_kind": "state_subject" if object_type == "state" else "assertion_subject",
                        "object_id": object_id,
                        "field": "subject_ref",
                        "old_value": source_ref,
                    })
        return affected

    def _redirected_value(self, entry: Mapping[str, Any], source_ref: str, target_ref: str) -> Any:
        if entry["field"] == "participant_refs":
            return [target_ref if value == source_ref else value for value in entry["old_value"]]
        return target_ref
    def _merge_preflight(self, candidate: Mapping[str, Any]) -> JsonObject | None:
        reason = candidate.get("reason")
        if not isinstance(reason, str) or not reason:
            return self._closed("merge_reason_required")
        source_ref = candidate.get("source_entity_ref")
        target_ref = candidate.get("target_entity_ref")
        if source_ref == target_ref:
            return self._closed("merge_source_equals_target")
        if candidate.get("synthetic_profile_id") != _PROFILE:
            return self._closed("unexpected_synthetic_profile")
        for ref in (source_ref, target_ref):
            entity = self._store.canonical_object_or_none(ref) if isinstance(ref, str) else None
            if entity is None or entity.get("object_type") != "entity":
                return self._closed("merge_entity_not_found")
        for ref, code in ((source_ref, "merge_source_not_active"), (target_ref, "merge_target_not_active")):
            if self._store.canonical_object(ref).get("identity_status", "active") != "active":
                return self._closed(code)
        return None

    def _split_preflight(self, proposal: Mapping[str, Any]) -> JsonObject | None:
        merge_ref = proposal.get("merge_ref")
        if not isinstance(merge_ref, str) or not merge_ref:
            return self._closed("merge_ref_required")
        record = self._store.merge_record_or_none(merge_ref)
        if record is None:
            return self._closed("merge_ref_not_found")
        if self._store.split_record_for_merge(merge_ref) is not None:
            return self._closed("merge_already_split")
        if proposal.get("synthetic_profile_id", _PROFILE) != _PROFILE:
            return self._closed("unexpected_synthetic_profile")
        reason = proposal.get("reason")
        if not isinstance(reason, str) or not reason:
            return self._closed("split_reason_required")
        source = self._store.canonical_object(record["source_entity_ref"])
        if source.get("identity_status") != "merged":
            return self._closed("merge_source_not_merged")
        return None

    def _closed(self, reason_code: str) -> JsonObject:
        return {"status": "failed", "reason_code": reason_code, "data_revision": self._store.current_revision()}

    def _write_changeset(self, changeset_id: str, operation: str, proposal: Mapping[str, Any], revision: str, base_revision: str) -> None:
        payload = {
            "changeset_id": changeset_id,
            "schema_version": "noetide.changeset.v1",
            "base_revision": base_revision,
            "actor": "shiling",
            "requested_at": self._now,
            "confirmation_policy": "single_confirmation",
            "status": "published",
            "approval": {"actor": "synthetic_user", "recorded_at": self._now},
            "published_revision": revision,
            "reversibility": "reversible",
            "proposals": [dict(proposal, operation=operation)],
        }
        self._store.put_ledger_record(changeset_id, "changeset", payload, revision)
        receipt = {
            "receipt_id": f"receipt_a3_{changeset_id}",
            "changeset_id": changeset_id,
            "status": "published",
            "published_revision": revision,
        }
        self._store.put_ledger_record(receipt["receipt_id"], "receipt", receipt, revision)
        self._store.put_ledger_record(
            f"history:{changeset_id}:published", "a3_history",
            {"changeset_id": changeset_id, "status": "published", "published_revision": revision}, revision,
        )

    def _next_revision(self) -> str:
        # 委托给 store 的全局分配器:遇到 rev_c1_* 等非数值 revision 跳过而非崩溃
        return self._store.next_revision()
