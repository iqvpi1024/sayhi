"""Atomic publication and stale-base handling for the Micro ChangeSet."""

from __future__ import annotations

import copy
import hashlib
from typing import Any, Callable, Mapping

from .candidate import CHANGESET_ID, ContactCandidateBuilder
from .store import SemanticStore
from .views import CoreViewProjector


JsonObject = dict[str, Any]


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
        if observed_revision != changeset["base_revision"]:
            return self._terminal_failure(
                changeset, binding_id, attempt_id, "conflict", observed_revision, "conflicted"
            )

        attempt = {
            "attempt_id": attempt_id,
            "changeset_id": changeset_id,
            "idempotency_key_digest": _digest_text(idempotency_key),
            "observed_data_revision": observed_revision,
            "preflight_result": "passed",
            "status": "recorded",
        }
        self._store.put_ledger_record(attempt_id, "publish_attempt", attempt)
        try:
            with self._store.transaction():
                self._publish_atomic(changeset, failure_points)
        except Exception:
            return self._terminal_failure(
                changeset, binding_id, attempt_id, "failed", observed_revision, "failed"
            )

        receipt_id = "receipt_publish_001"
        receipt = {
            "receipt_id": receipt_id,
            "changeset_id": changeset_id,
            "publish_attempt_id": attempt_id,
            "status": "published",
            "preflight_result": "passed",
            "published_revision": "rev_011",
            "view_results": [],
        }
        published = copy.deepcopy(changeset)
        published.update({"status": "published", "published_revision": "rev_011", "receipt_id": receipt_id})
        with self._store.transaction():
            self._store.replace_ledger_record(changeset_id, published, "rev_011")
            self._store.put_ledger_record(receipt_id, "receipt", receipt, "rev_011")
            self._store.put_ledger_record(
                "audit:changeset_micro_001:published",
                "audit_event",
                {"changeset_id": changeset_id, "event_type": "published", "revision": "rev_011"},
                "rev_011",
            )
            self._store.put_ledger_record(
                binding_id, "idempotency", {"changeset_id": changeset_id, "receipt_id": receipt_id}
            )
        view_results = CoreViewProjector(self._store, self._fixture).project("rev_011", failure_points)
        receipt["view_results"] = view_results
        self._store.replace_ledger_record(receipt_id, receipt, "rev_011")
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
        self._store.put_ledger_record(retry_id, "changeset", retry)
        return retry

    def revert(self, changeset_id: str, idempotency_key: str) -> JsonObject:
        changeset = self._drafts.get(changeset_id)
        if changeset["status"] != "published":
            raise RuntimeError("only a published ChangeSet may be reverted")
        if self._store.current_revision() != "rev_011":
            raise RuntimeError("compensation requires the published revision as its base")
        receipt_id = "receipt_compensation_001"
        existing = self._store.ledger_record(receipt_id)
        if existing is not None:
            return existing
        restored = copy.deepcopy(self._fixture_state("state_contact_001"))
        restored["object_revision"] = "rev_012"
        restored["recorded_at"] = self._now
        restored["recorded_by"] = "user"
        compensation = {
            "changeset_id": "changeset_compensation_001",
            "base_revision": "rev_011",
            "retry_of": changeset_id,
            "actor": "user",
            "status": "published",
            "published_revision": "rev_012",
            "confirmation_policy": "single_confirmation",
            "proposals": [
                {"proposal_id": "compensation_remove_001", "operation": "remove", "target_ref": "state_contact_002"},
                {"proposal_id": "compensation_restore_001", "operation": "correct", "target_ref": "state_contact_001"},
            ],
        }
        receipt = {
            "receipt_id": receipt_id,
            "changeset_id": changeset_id,
            "compensation_changeset_id": compensation["changeset_id"],
            "status": "published",
            "compensation_revision": "rev_012",
            "published_revision": "rev_012",
            "view_results": [],
        }
        with self._store.transaction():
            self._store.delete_canonical_object("state_contact_002")
            self._store.replace_canonical_object("state_contact_001", restored)
            self._store.replace_evidence_refs("state_contact_001", restored["evidence_refs"])
            self._store.add_revision("rev_012", self._now)
            reverted = copy.deepcopy(changeset)
            reverted["status"] = "reverted"
            reverted["rollback_reference"] = compensation["changeset_id"]
            self._store.replace_ledger_record(changeset_id, reverted, "rev_012")
            self._store.put_ledger_record(compensation["changeset_id"], "changeset", compensation, "rev_012")
            self._store.put_ledger_record(receipt_id, "receipt", receipt, "rev_012")
            self._store.put_ledger_record(
                "audit:changeset_micro_001:reverted",
                "audit_event",
                {"changeset_id": changeset_id, "event_type": "reverted", "revision": "rev_012"},
                "rev_012",
            )
        receipt["view_results"] = CoreViewProjector(self._store, self._fixture).project("rev_012", set())
        self._store.replace_ledger_record(receipt_id, receipt, "rev_012")
        return receipt

    def audit_events(self, changeset_id: str) -> list[JsonObject]:
        return self._store.ledger_records_for("audit_event", changeset_id)

    def _publish_atomic(self, changeset: Mapping[str, Any], failure_points: set[str]) -> None:
        if self._store.current_revision() != changeset["base_revision"]:
            raise RuntimeError("stale base revision")
        proposals = changeset["proposals"]
        old_state = proposals[0]["after_value"]
        new_state = proposals[1]["after_value"]
        self._store.replace_canonical_object("state_contact_001", old_state)
        self._store.replace_evidence_refs("state_contact_001", old_state["evidence_refs"])
        if "l1.proposal.2" in failure_points:
            raise RuntimeError("injected second proposal failure")
        self._store.add_canonical_object("state_contact_002", new_state)
        self._store.replace_evidence_refs("state_contact_002", new_state["evidence_refs"])
        self._store.add_revision("rev_011", self._now)

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
        attempt = self._store.ledger_record(attempt_id)
        if attempt is None:
            attempt = {
                "attempt_id": attempt_id,
                "changeset_id": changeset["changeset_id"],
                "idempotency_key_digest": _digest_text(binding_id),
                "observed_data_revision": observed_revision,
                "preflight_result": preflight_result,
                "status": "recorded",
            }
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
            if self._store.ledger_record(attempt_id) is None:
                self._store.put_ledger_record(attempt_id, "publish_attempt", attempt)
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


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _binding_id(changeset_id: str, idempotency_key: str) -> str:
    return f"idempotency:{changeset_id}:{_digest_text(idempotency_key)}"


def _attempt_id(changeset_id: str, idempotency_key: str) -> str:
    return f"attempt:{changeset_id}:{_digest_text(idempotency_key)[:16]}"
