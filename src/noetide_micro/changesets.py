"""Atomic publication and stale-base handling for the Micro ChangeSet."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping

from .candidate import CHANGESET_ID, ContactCandidateBuilder
from .store import SemanticStore
from .views import CoreViewProjector


JsonObject = dict[str, Any]
_PROTECTED_PATHS = {
    "relationship.origin",
    "state[relationship.role].value",
    "assertion[relationship.trust].value",
    "assertion[relationship.closeness].value",
    "hypothesis[relationship.personality]",
}


class ChangeSetService:
    """Publishes the approved end/add pair without involving Derived Views."""

    def __init__(self, store: SemanticStore, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now
        self._drafts = ContactCandidateBuilder(store, fixture, now)

    def publish(self, changeset_id: str, idempotency_key: str, failure_points: set[str]) -> JsonObject:
        changeset = self._drafts.get(changeset_id)
        binding_id = _binding_id(changeset_id, idempotency_key)
        existing_binding = self._store.ledger_record(binding_id)
        if existing_binding is not None:
            return self._required_receipt(existing_binding["receipt_id"])
        if changeset["status"] != "approved":
            raise RuntimeError("only an approved ChangeSet may publish")

        observed_revision = self._store.current_revision()
        attempt_id = _attempt_id(changeset_id, idempotency_key)
        self._record_attempt(changeset, attempt_id, idempotency_key, observed_revision)
        if observed_revision != changeset["base_revision"]:
            return self._terminal_failure(
                changeset, binding_id, attempt_id, "conflict", observed_revision, "conflicted"
            )

        preflight_result, terminal_status = self._preflight(changeset)
        if terminal_status is not None:
            return self._terminal_failure(
                changeset,
                binding_id,
                attempt_id,
                preflight_result,
                observed_revision,
                terminal_status,
            )
        self._set_attempt_preflight(attempt_id, "passed", observed_revision)

        try:
            with self._store.transaction():
                # revision 在事务内统一分配(2026-08-08 Change Control:消除硬编码
                # rev_011;fixture 基线 rev_010 时分配结果仍是 rev_011,合同行为不变)
                new_revision = self._store.next_revision()
                self._publish_atomic(changeset, failure_points, new_revision)
                receipt_id = "receipt_publish_001"
                receipt = {
                    "receipt_id": receipt_id,
                    "changeset_id": changeset_id,
                    "publish_attempt_id": attempt_id,
                    "status": "published",
                    "preflight_result": "passed",
                    "published_revision": new_revision,
                    "view_results": [],
                }
                published = copy.deepcopy(changeset)
                published.update(
                    {"status": "published", "published_revision": new_revision, "receipt_id": receipt_id}
                )
                self._store.replace_ledger_record(changeset_id, published, new_revision)
                self._store.put_ledger_record(receipt_id, "receipt", receipt, new_revision)
                self._store.put_ledger_record(
                    "audit:changeset_micro_001:published",
                    "audit_event",
                    {"changeset_id": changeset_id, "event_type": "published", "revision": new_revision},
                    new_revision,
                )
                self._store.put_ledger_record(
                    binding_id, "idempotency", {"changeset_id": changeset_id, "receipt_id": receipt_id}
                )
        except Exception:
            return self._terminal_failure(
                changeset, binding_id, attempt_id, "passed", observed_revision, "failed"
            )

        # L2 projection is rebuildable and intentionally outside the L1 commit boundary.
        view_results = CoreViewProjector(self._store, self._fixture).project(new_revision, failure_points)
        receipt["view_results"] = view_results
        self._store.replace_ledger_record("receipt_publish_001", receipt, new_revision)
        return receipt

    def attempts(self, changeset_id: str) -> list[JsonObject]:
        return self._store.ledger_records_for("publish_attempt", changeset_id)

    def receipt(self, receipt_id: str) -> JsonObject:
        return self._required_receipt(receipt_id)

    def advance_for_test(self) -> JsonObject:
        if self._store.current_revision() != "rev_010":
            raise RuntimeError("test revision advance is only valid from rev_010")
        with self._store.transaction():
            self._store.add_revision("rev_011_test", self._now)
        return {"data_revision": "rev_011_test"}

    def propose_retry(self, changeset_id: str) -> JsonObject:
        original = self._drafts.get(changeset_id)
        if original["status"] not in {"conflicted", "failed"}:
            raise RuntimeError("only a terminal failed ChangeSet may be retried")
        retry_id = "changeset_micro_retry_001"
        existing = self._store.ledger_record(retry_id)
        if existing is not None:
            return existing
        retry = copy.deepcopy(original)
        retry.update(
            {
                "changeset_id": retry_id,
                "base_revision": self._store.current_revision(),
                "status": "proposed",
                "published_revision": None,
                "receipt_id": None,
                "retry_of": changeset_id,
            }
        )
        with self._store.transaction():
            self._store.put_ledger_record(retry_id, "changeset", retry)
        return retry

    def revert(self, changeset_id: str, idempotency_key: str) -> JsonObject:
        binding_id = _binding_id(changeset_id, idempotency_key)
        existing_binding = self._store.ledger_record(binding_id)
        if existing_binding is not None:
            return self._required_receipt(existing_binding["receipt_id"])
        changeset = self._drafts.get(changeset_id)
        if changeset["status"] != "published":
            raise RuntimeError("only a published ChangeSet may be reverted")
        published_revision = changeset["published_revision"]
        if self._store.current_revision() != published_revision:
            raise RuntimeError("compensation requires the published revision as its base")

        receipt_id = "receipt_compensation_001"
        compensation = {
            "changeset_id": "changeset_compensation_001",
            "base_revision": published_revision,
            "retry_of": changeset_id,
            "actor": "user",
            "status": "published",
            "published_revision": None,  # 占位,事务内分配后回填
            "confirmation_policy": "single_confirmation",
            "proposals": [
                {"proposal_id": "compensation_remove_001", "operation": "remove", "target_ref": "state_contact_002"},
                {"proposal_id": "compensation_restore_001", "operation": "correct", "target_ref": "state_contact_001"},
            ],
        }
        with self._store.transaction():
            # 补偿 revision 事务内统一分配(fixture 基线 rev_011 时仍为 rev_012)
            new_revision = self._store.next_revision()
            compensation["published_revision"] = new_revision
            receipt = {
                "receipt_id": receipt_id,
                "changeset_id": changeset_id,
                "compensation_changeset_id": compensation["changeset_id"],
                "status": "published",
                "compensation_revision": new_revision,
                "published_revision": new_revision,
                "view_results": [],
            }
            restored = self._fixture_state("state_contact_001")
            restored["object_revision"] = new_revision
            restored["recorded_at"] = self._now
            restored["recorded_by"] = "user"

            self._store.delete_canonical_object("state_contact_002")
            self._store.replace_canonical_object("state_contact_001", restored)
            self._store.replace_evidence_refs("state_contact_001", restored["evidence_refs"])
            self._store.add_revision(new_revision, self._now)
            reverted = copy.deepcopy(changeset)
            reverted["status"] = "reverted"
            reverted["rollback_reference"] = compensation["changeset_id"]
            self._store.replace_ledger_record(changeset_id, reverted, new_revision)
            self._store.put_ledger_record(compensation["changeset_id"], "changeset", compensation, new_revision)
            self._store.put_ledger_record(receipt_id, "receipt", receipt, new_revision)
            self._store.put_ledger_record(
                "audit:changeset_micro_001:reverted",
                "audit_event",
                {"changeset_id": changeset_id, "event_type": "reverted", "revision": new_revision},
                new_revision,
            )
            self._store.put_ledger_record(
                binding_id, "idempotency", {"changeset_id": changeset_id, "receipt_id": receipt_id}
            )

        receipt["view_results"] = CoreViewProjector(self._store, self._fixture).project(new_revision, set())
        self._store.replace_ledger_record(receipt_id, receipt, new_revision)
        return receipt

    def audit_events(self, changeset_id: str) -> list[JsonObject]:
        return self._store.ledger_records_for("audit_event", changeset_id)

    def _record_attempt(
        self, changeset: Mapping[str, Any], attempt_id: str, idempotency_key: str, observed_revision: str
    ) -> None:
        attempt = {
            "attempt_id": attempt_id,
            "changeset_id": changeset["changeset_id"],
            "idempotency_key_digest": _digest_text(idempotency_key),
            "observed_data_revision": observed_revision,
            "preflight_result": "pending",
            "status": "recorded",
        }
        with self._store.transaction():
            self._store.put_ledger_record(attempt_id, "publish_attempt", attempt)

    def _preflight(self, changeset: Mapping[str, Any]) -> tuple[str, str | None]:
        proposals = changeset.get("proposals")
        if not isinstance(proposals, list) or len(proposals) != 2:
            return "failed", "failed"
        end, add = proposals
        if end.get("operation") != "end" or add.get("operation") != "add":
            return "failed", "failed"
        if set(changeset.get("protected_paths", [])) != _PROTECTED_PATHS:
            return "failed", "failed"
        if end.get("target_ref", {}).get("object_id") != "state_contact_001":
            return "failed", "failed"
        if add.get("target_ref", {}).get("object_id") != "state_contact_002":
            return "failed", "failed"
        try:
            old_state = self._store.canonical_object("state_contact_001")
        except KeyError:
            return "failed", "failed"
        if end.get("before_digest") != _canonical_digest(old_state):
            return "conflict", "conflicted"
        if self._store.canonical_object_or_none("state_contact_002") is not None:
            return "conflict", "conflicted"
        if add.get("before_digest") != "absent":
            return "conflict", "conflicted"
        for proposal in proposals:
            after_value = proposal.get("after_value")
            if not isinstance(after_value, Mapping):
                return "failed", "failed"
            if after_value.get("object_type") != "state":
                return "failed", "failed"
            if after_value.get("state_id") != proposal.get("target_ref", {}).get("object_id"):
                return "failed", "failed"
            subject_ref = after_value.get("subject_ref")
            if isinstance(subject_ref, Mapping):
                if subject_ref.get("object_type") != "relationship":
                    return "failed", "failed"
                relationship_id = subject_ref.get("object_id")
            elif isinstance(subject_ref, str):
                relationship_id = subject_ref
            else:
                return "failed", "failed"
            if not isinstance(relationship_id, str) or self._store.canonical_object_or_none(relationship_id) is None:
                return "failed", "failed"
            for evidence_ref in after_value.get("evidence_refs", []):
                source_id = evidence_ref.get("source_id")
                if not isinstance(source_id, str) or self._store.seeded_source(source_id) is None:
                    return "failed", "failed"
        return "passed", None

    def _set_attempt_preflight(
        self, attempt_id: str, preflight_result: str, observed_revision: str
    ) -> None:
        attempt = self._required_receipt(attempt_id)
        attempt["preflight_result"] = preflight_result
        attempt["observed_data_revision"] = observed_revision
        with self._store.transaction():
            self._store.replace_ledger_record(attempt_id, attempt)

    def _publish_atomic(self, changeset: Mapping[str, Any], failure_points: set[str], new_revision: str) -> None:
        if self._store.current_revision() != changeset["base_revision"]:
            raise RuntimeError("stale base revision")
        old_state = changeset["proposals"][0]["after_value"]
        new_state = changeset["proposals"][1]["after_value"]
        self._store.replace_canonical_object("state_contact_001", old_state)
        self._store.replace_evidence_refs("state_contact_001", old_state["evidence_refs"])
        if "l1.proposal.2" in failure_points:
            raise RuntimeError("injected second proposal failure")
        self._store.add_canonical_object("state_contact_002", new_state)
        self._store.replace_evidence_refs("state_contact_002", new_state["evidence_refs"])
        self._store.add_revision(new_revision, self._now)

    def _terminal_failure(
        self,
        changeset: Mapping[str, Any],
        binding_id: str,
        attempt_id: str,
        preflight_result: str,
        observed_revision: str,
        status: str,
    ) -> JsonObject:
        receipt_id = f"receipt_{status}_{_digest_text(attempt_id)[:12]}"
        receipt = {
            "receipt_id": receipt_id,
            "changeset_id": changeset["changeset_id"],
            "publish_attempt_id": attempt_id,
            "status": status,
            "preflight_result": preflight_result,
            "published_revision": None,
            "view_results": [],
        }
        terminal = copy.deepcopy(changeset)
        terminal.update({"status": status, "published_revision": None, "receipt_id": receipt_id})
        with self._store.transaction():
            attempt = self._required_receipt(attempt_id)
            attempt["preflight_result"] = preflight_result
            attempt["observed_data_revision"] = observed_revision
            self._store.replace_ledger_record(attempt_id, attempt)
            self._store.replace_ledger_record(changeset["changeset_id"], terminal)
            self._store.put_ledger_record(receipt_id, "receipt", receipt)
            self._store.put_ledger_record(
                binding_id,
                "idempotency",
                {"changeset_id": changeset["changeset_id"], "receipt_id": receipt_id},
            )
        return receipt

    def _required_receipt(self, receipt_id: str) -> JsonObject:
        receipt = self._store.ledger_record(receipt_id)
        if receipt is None:
            raise KeyError(receipt_id)
        return receipt

    def _fixture_state(self, state_id: str) -> JsonObject:
        return copy.deepcopy(
            next(
                item
                for item in self._fixture["initial_state"]["canonical_objects"]
                if item.get("state_id") == state_id
            )
        )


def _canonical_digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _binding_id(changeset_id: str, idempotency_key: str) -> str:
    return f"idempotency:{changeset_id}:{_digest_text(idempotency_key)}"


def _attempt_id(changeset_id: str, idempotency_key: str) -> str:
    return f"attempt:{changeset_id}:{_digest_text(idempotency_key)[:16]}"
