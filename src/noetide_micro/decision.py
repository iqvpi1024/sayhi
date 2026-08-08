"""Decision object for MVP-C C1.

``decide``/``close``/``set_predicted_outcome`` 是纯内存转换(不写库),用于
构造待发布对象;持久化走 ``*_persisted`` 变体——它们复用同一校验,然后经
c1.py 的 add-only ChangeSet 语义(``C1ChangeSetService.publish_revision``)
把状态变更落成新 revision 的 Canonical 对象:只追加新 revision/changeset
账本行与 payload 内 revision_history,不改写历史。
"""

from __future__ import annotations

import copy
from typing import Any, Mapping

from .c1 import C1ChangeSetService

JsonObject = dict[str, Any]


class DecisionService:
    """Create and transition Decision objects; persistence goes through the C1 ChangeSet path."""

    def __init__(self, store: Any, fixture: Mapping[str, Any], now: str) -> None:
        self._store = store
        self._fixture = fixture
        self._now = now

    def create(
        self,
        decision_id: str,
        question: str,
        options: list[str],
        constraints: list[str],
        assumptions: list[str],
        choice: str | None = None,
    ) -> JsonObject:
        """Create a Decision object. If choice is provided, status is 'decided'."""
        if not question or not options or (choice is not None and choice not in options):
            raise ValueError("invalid_decision_choice")
        decision = {
            "decision_id": decision_id,
            "object_type": "decision",
            "schema_version": "noetide.semantic.v1",
            "object_revision": "rev_001",
            "owner_ref": "person_alpha",
            "created_at": self._now,
            "created_by": "user",
            "sensitivity": "private",
            "compartments": ["personal"],
            "subject_refs": ["person_alpha"],
            "recorder_ref": "person_alpha",
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "question": question,
            "options": options,
            "constraints": constraints,
            "assumptions": assumptions,
            "choice": choice,
            "status": "decided" if choice else "open",
            "evidence_refs": [],
            "evidence_status": "missing",
            "review_status": "confirmed" if choice else "unconfirmed",
            "predicted_outcome": None,
            "actual_outcome_ref": None,
        }
        return decision

    def decide(self, decision: JsonObject, choice: str) -> JsonObject:
        """Record a choice for an open Decision."""
        if decision["status"] != "open":
            raise RuntimeError("only an open Decision may be decided")
        if choice not in decision["options"]:
            raise ValueError("choice must be one of the options")
        updated = copy.deepcopy(decision)
        updated["choice"] = choice
        updated["status"] = "decided"
        updated["review_status"] = "confirmed"
        updated["object_revision"] = "rev_002"
        return updated

    def close(self, decision: JsonObject) -> JsonObject:
        """Close a decided Decision."""
        if decision["status"] != "decided":
            raise RuntimeError("only a decided Decision may be closed")
        updated = copy.deepcopy(decision)
        updated["status"] = "closed"
        updated["object_revision"] = "rev_003"
        return updated

    def set_predicted_outcome(self, decision: JsonObject, predicted: str) -> JsonObject:
        """Set a predicted outcome without writing it as actual."""
        updated = copy.deepcopy(decision)
        updated["predicted_outcome"] = predicted
        return updated

    def _load_persisted(self, decision_id: str) -> JsonObject:
        current = self._store.canonical_object_or_none(decision_id)
        if current is None or current.get("object_type") != "decision":
            raise ValueError("c1_decision_not_persisted")
        return current

    def _persist_transition(self, current: JsonObject, updated: JsonObject, change: str, actor: str) -> JsonObject:
        history = list(current.get("revision_history", []))
        history.append({
            "object_revision": current["object_revision"],
            "status": current["status"],
            "at": self._now,
            "change": change,
        })
        updated["revision_history"] = history
        writer = C1ChangeSetService(self._store, self._now)
        return writer.publish_revision(current["decision_id"], updated, actor, "correct")

    def decide_persisted(self, decision_id: str, choice: str, actor: str = "user") -> JsonObject:
        """Persisted variant of ``decide``: appends a new revision via C1 ChangeSet."""
        current = self._load_persisted(decision_id)
        updated = self.decide(current, choice)
        return self._persist_transition(current, updated, "decide", actor)

    def close_persisted(self, decision_id: str, actor: str = "user") -> JsonObject:
        """Persisted variant of ``close``: appends a new revision via C1 ChangeSet."""
        current = self._load_persisted(decision_id)
        updated = self.close(current)
        return self._persist_transition(current, updated, "close", actor)

    def set_predicted_outcome_persisted(self, decision_id: str, predicted: str, actor: str = "user") -> JsonObject:
        """Persisted variant of ``set_predicted_outcome``: appends a new revision via C1 ChangeSet."""
        current = self._load_persisted(decision_id)
        updated = self.set_predicted_outcome(current, predicted)
        return self._persist_transition(current, updated, "set_predicted_outcome", actor)
