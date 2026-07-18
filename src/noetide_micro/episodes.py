"""Fixed synthetic Episode ChangeSet behavior for B2."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
_PROFILE = "b2_episode_summary_v1"


class EpisodeChangeSetService:
    """Publishes one fixture-scoped Episode without using Derived summary data."""

    def __init__(self, store: SemanticStore, now: str) -> None:
        self._store = store
        self._now = now

    def propose(self, candidate: Mapping[str, Any]) -> JsonObject:
        self._validate_candidate(candidate)
        episode_id = candidate["episode_id"]
        changeset_id = f"changeset_b2_{episode_id}"
        existing = self._store.ledger_record(changeset_id)
        if existing is not None:
            return existing
        proposal = {
            "changeset_id": changeset_id,
            "schema_version": "noetide.changeset.v1",
            "base_revision": self._store.current_revision(),
            "actor": "shiling",
            "requested_at": self._now,
            "confirmation_policy": "single_confirmation",
            "status": "proposed",
            "published_revision": None,
            "reversibility": "reversible",
            "proposals": [
                {
                    "proposal_id": f"proposal_b2_{episode_id}",
                    "operation": "add",
                    "target_ref": {"object_type": "episode", "object_id": episode_id},
                    "before_digest": "absent",
                    "after_value": self._episode_payload(candidate, "pending"),
                }
            ],
        }
        with self._store.transaction():
            self._store.put_ledger_record(changeset_id, "changeset", proposal)
        return proposal

    def approve(self, changeset_id: str, actor: str) -> JsonObject:
        changeset = self._required_changeset(changeset_id)
        if actor != "person_alpha":
            raise PermissionError("only the synthetic owner may approve a B2 Episode")
        if changeset["status"] == "approved":
            return changeset
        if changeset["status"] != "proposed":
            raise RuntimeError("only a proposed Episode ChangeSet may be approved")
        approved = copy.deepcopy(changeset)
        approved["status"] = "approved"
        approved["approval"] = {"actor": actor, "recorded_at": self._now}
        with self._store.transaction():
            self._store.replace_ledger_record(changeset_id, approved)
        return approved

    def publish(self, changeset_id: str) -> JsonObject:
        changeset = self._required_changeset(changeset_id)
        if changeset["status"] != "approved":
            raise RuntimeError("only an approved Episode ChangeSet may publish")
        if changeset["base_revision"] != self._store.current_revision():
            return self._fail(changeset, "conflicted", "stale_base_revision")
        proposal = changeset["proposals"][0]
        candidate = proposal["after_value"]
        if self._store.canonical_object_or_none(candidate["episode_id"]) is not None:
            return self._fail(changeset, "conflicted", "episode_already_exists")
        revision = "rev_b2_021"
        published = copy.deepcopy(candidate)
        published["object_revision"] = revision
        published["recorded_at"] = self._now
        published["review_status"] = "user_confirmed"
        receipt = {
            "receipt_id": f"receipt_b2_{candidate['episode_id']}_publish",
            "changeset_id": changeset_id,
            "status": "published",
            "published_revision": revision,
        }
        completed = copy.deepcopy(changeset)
        completed.update({"status": "published", "published_revision": revision, "receipt_id": receipt["receipt_id"]})
        with self._store.transaction():
            self._store.add_revision(revision, self._now)
            self._store.mark_summary_projections_stale(revision)
            self._store.add_canonical_object(candidate["episode_id"], published)
            self._store.replace_evidence_refs(candidate["episode_id"], published["evidence_refs"])
            self._store.put_episode_record(
                candidate["episode_id"], revision, candidate["episode_kind"],
                candidate["valid_time"]["start"], candidate["valid_time"]["end"], self._now,
                candidate["synthetic_profile_id"], candidate["source_refs"],
            )
            self._store.replace_ledger_record(changeset_id, completed, revision)
            self._store.put_ledger_record(receipt["receipt_id"], "receipt", receipt, revision)
            self._store.put_ledger_record(
                f"audit:{changeset_id}:published", "audit_event",
                {"changeset_id": changeset_id, "event_type": "published", "revision": revision}, revision,
            )
        return {"status": "published", "episode_id": candidate["episode_id"], "data_revision": revision}

    def revert(self, changeset_id: str) -> JsonObject:
        changeset = self._required_changeset(changeset_id)
        if changeset["status"] != "published" or self._store.current_revision() != "rev_b2_021":
            raise RuntimeError("Episode compensation requires the current published B2 revision")
        episode_id = changeset["proposals"][0]["after_value"]["episode_id"]
        revision = "rev_b2_022"
        compensation_id = f"changeset_b2_compensation_{episode_id}"
        receipt_id = f"receipt_b2_{episode_id}_revert"
        reverted = copy.deepcopy(changeset)
        reverted.update({"status": "reverted", "rollback_reference": compensation_id})
        compensation = {
            "changeset_id": compensation_id,
            "base_revision": "rev_b2_021",
            "actor": "user",
            "status": "published",
            "published_revision": revision,
            "proposals": [{"operation": "remove", "target_ref": {"object_type": "episode", "object_id": episode_id}}],
        }
        with self._store.transaction():
            self._store.delete_episode_record(episode_id)
            self._store.delete_canonical_object(episode_id)
            self._store.add_revision(revision, self._now)
            self._store.mark_summary_projections_stale(revision)
            self._store.replace_ledger_record(changeset_id, reverted, revision)
            self._store.put_ledger_record(compensation_id, "changeset", compensation, revision)
            self._store.put_ledger_record(receipt_id, "receipt", {"receipt_id": receipt_id, "changeset_id": changeset_id, "status": "published", "published_revision": revision}, revision)
            self._store.put_ledger_record(
                f"audit:{changeset_id}:reverted", "audit_event",
                {"changeset_id": changeset_id, "event_type": "reverted", "revision": revision}, revision,
            )
        return {"status": "reverted", "episode_id": episode_id, "data_revision": revision}

    def _fail(self, changeset: Mapping[str, Any], status: str, reason_code: str) -> JsonObject:
        failed = copy.deepcopy(changeset)
        failed.update({"status": status, "published_revision": None, "failure_reason": reason_code})
        with self._store.transaction():
            self._store.replace_ledger_record(changeset["changeset_id"], failed)
        return {"status": status, "reason_code": reason_code, "data_revision": self._store.current_revision()}

    def _required_changeset(self, changeset_id: str) -> JsonObject:
        changeset = self._store.ledger_record(changeset_id)
        if changeset is None or changeset.get("changeset_id") != changeset_id:
            raise KeyError(changeset_id)
        return changeset

    def _validate_candidate(self, candidate: Mapping[str, Any]) -> None:
        allowed_candidate_fields = {
            "episode_id", "episode_kind", "participant_refs", "valid_time", "source_refs",
            "synthetic_profile_id",
        }
        if set(candidate) != allowed_candidate_fields:
            raise ValueError("fixture_profile_mismatch")
        if candidate.get("synthetic_profile_id") != _PROFILE:
            raise ValueError("synthetic_input_required")
        if candidate.get("episode_kind") not in {"synthetic_relationship_event", "synthetic_project_event"}:
            raise ValueError("episode_kind_invalid")
        if not isinstance(candidate.get("episode_id"), str) or self._store.canonical_object_or_none(candidate["episode_id"]) is not None:
            raise ValueError("episode_id_invalid")
        participants = candidate.get("participant_refs")
        valid_time = candidate.get("valid_time")
        source_refs = candidate.get("source_refs")
        if not isinstance(participants, list) or not participants or not isinstance(valid_time, Mapping) or not isinstance(source_refs, list) or not source_refs:
            raise ValueError("episode_reference_invalid")
        if set(valid_time) != {"start", "end"} or not isinstance(valid_time.get("start"), str) or not isinstance(valid_time.get("end"), str) or valid_time["start"] >= valid_time["end"]:
            raise ValueError("episode_reference_invalid")
        for participant in participants:
            entity = self._store.canonical_object_or_none(participant)
            if entity is None or entity.get("object_type") != "entity":
                raise ValueError("episode_reference_invalid")
        for ref in source_refs:
            if not isinstance(ref, Mapping) or set(ref) != {"source_id", "locator"}:
                raise ValueError("episode_reference_invalid")
            locator = ref.get("locator")
            source = self._store.seeded_source(ref.get("source_id", ""))
            if (
                not isinstance(ref.get("source_id"), str)
                or not isinstance(locator, Mapping)
                or set(locator) != {"scheme", "start_byte", "end_byte_exclusive"}
                or locator.get("scheme") != "text_utf8_byte_range_v1"
                or not isinstance(locator.get("start_byte"), int)
                or not isinstance(locator.get("end_byte_exclusive"), int)
                or locator["start_byte"] < 0
                or locator["start_byte"] >= locator["end_byte_exclusive"]
                or source is None
                or source.get("synthetic") is not True
                or source.get("synthetic_profile_id") != _PROFILE
            ):
                raise ValueError("episode_reference_invalid")

    def _episode_payload(self, candidate: Mapping[str, Any], revision: str) -> JsonObject:
        source_refs = [dict(ref) for ref in candidate["source_refs"]]
        return {
            "episode_id": candidate["episode_id"],
            "object_type": "episode",
            "schema_version": "noetide.semantic.v1",
            "object_revision": revision,
            "owner_ref": "person_alpha",
            "created_at": self._now,
            "created_by": "shiling",
            "sensitivity": "normal",
            "compartments": ["personal"],
            "subject_refs": list(candidate["participant_refs"]),
            "recorder_ref": "person_alpha",
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "episode_kind": candidate["episode_kind"],
            "participant_refs": list(candidate["participant_refs"]),
            "valid_time": dict(candidate["valid_time"]),
            "recorded_at": self._now,
            "source_refs": source_refs,
            "evidence_refs": [
                {"source_id": ref["source_id"], "locator": dict(ref["locator"]), "stance": "supports", "claim_ref": candidate["episode_id"]}
                for ref in source_refs
            ],
            "evidence_status": "present",
            "review_status": "unreviewed",
            "synthetic_profile_id": candidate["synthetic_profile_id"],
        }
