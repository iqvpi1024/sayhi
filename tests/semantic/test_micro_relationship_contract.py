from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/fixture.json"
ORACLE_PATH = ROOT / "tests/fixtures/micro_relationship_v1/oracles.json"
RUN_ROOT = ROOT / "tmp/micro-runs"


def scenario(scenario_id: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorate(method: Callable[..., Any]) -> Callable[..., Any]:
        setattr(method, "_noetide_scenario_id", scenario_id)
        return method

    return decorate


def canonical_digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class MicroRelationshipContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.oracles = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
        adapter_name = os.environ.get("NOETIDE_MICRO_ADAPTER")
        if not adapter_name:
            raise RuntimeError("NOETIDE_MICRO_ADAPTER is required")
        cls.adapter = importlib.import_module(adapter_name)
        if not callable(getattr(cls.adapter, "create_system", None)):
            raise TypeError(f"{adapter_name} must expose create_system(fixture, data_root)")

    def setUp(self) -> None:
        RUN_ROOT.mkdir(parents=True, exist_ok=True)
        self._temp = tempfile.TemporaryDirectory(prefix="noetide-micro-", dir=RUN_ROOT)
        self.addCleanup(self._temp.cleanup)
        self.system = self._create_system("primary")

    def _create_system(self, name: str) -> Any:
        data_root = Path(self._temp.name) / name
        data_root.mkdir(parents=True, exist_ok=False)
        return self.adapter.create_system(copy.deepcopy(self.fixture), data_root)

    def _intake(self, system: Any | None = None) -> dict[str, Any]:
        target = system or self.system
        return target.intake(copy.deepcopy(self.fixture["intake_request"]))

    def _propose(self, system: Any | None = None) -> dict[str, Any]:
        target = system or self.system
        self._intake(target)
        return target.propose_contact_changeset("src_micro_001")

    def _publish(self, system: Any | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
        target = system or self.system
        changeset = self._propose(target)
        target.approve_changeset(changeset["changeset_id"], "person_alpha")
        receipt = target.publish_changeset(
            changeset["changeset_id"], f"publish-{changeset['changeset_id']}"
        )
        return changeset, receipt

    def _object_map(self, snapshot: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        objects = snapshot["objects"]
        self.assertIsInstance(objects, dict)
        return objects

    def _protected_snapshot(self, system: Any | None = None) -> dict[str, dict[str, str]]:
        target = system or self.system
        objects = self._object_map(target.canonical_snapshot())
        protected_ids = self.fixture["protected_semantics"]["object_ids"]
        self.assertTrue(protected_ids)
        result: dict[str, dict[str, str]] = {}
        for object_id in protected_ids:
            self.assertIn(object_id, objects)
            payload = objects[object_id]
            result[object_id] = {
                "object_revision": payload["object_revision"],
                "digest": canonical_digest(payload),
            }
        return result

    @scenario("MM-001")
    def test_mm_001_source_append(self) -> None:
        before = self.system.canonical_snapshot()
        receipt = self._intake()
        self.assertEqual(receipt, self.fixture["expected_append_receipt"])
        expected_source = next(
            item
            for item in self.fixture["source_records"]
            if item["source_id"] == "src_micro_001"
        )
        self.assertEqual(self.system.get_source("src_micro_001"), expected_source)
        source_bytes = expected_source["inline_content"].encode("utf-8")
        self.assertEqual(len(source_bytes), 58)
        self.assertEqual(hashlib.sha256(source_bytes).hexdigest(), expected_source["content_hash"])
        self.assertEqual(expected_source["locator"], {"start_byte": 0, "end_byte_exclusive": 58})
        self.assertEqual(self.system.canonical_snapshot(), before)

    @scenario("MM-002")
    def test_mm_002_allowlisted_proposal(self) -> None:
        changeset = self._propose()
        self.assertEqual(changeset["status"], "proposed")
        self.assertEqual([p["operation"] for p in changeset["proposals"]], ["end", "add"])
        self.assertEqual(changeset["proposals"][1]["after_value"]["value"], "no_contact")
        self.assertEqual(
            changeset["proposals"][1]["after_value"]["valid_time"]["start"]["value"],
            "2031-09-01T00:00:00+08:00",
        )
        self.assertEqual(
            changeset["trigger_sources"],
            [
                {
                    "source_id": "src_micro_001",
                    "locator": {
                        "scheme": "text_utf8_byte_range_v1",
                        "start_byte": 0,
                        "end_byte_exclusive": 58,
                    },
                }
            ],
        )
        self.assertEqual(
            sorted(changeset["impact_set"]["derived_views"]),
            ["person_card", "relationship_timeline"],
        )
        forbidden = (
            "relationship.origin",
            "relationship.role",
            "relationship.trust",
            "relationship.closeness",
            "personality",
            "entity.identity",
        )
        targets = json.dumps(changeset["proposals"], ensure_ascii=False)
        self.assertFalse(any(path in targets for path in forbidden))

    @scenario("MM-003")
    def test_mm_003_unconfirmed_is_not_published(self) -> None:
        before = self.system.canonical_snapshot()
        changeset = self._propose()
        preview = self.system.preview_changeset(changeset["changeset_id"])
        self.assertEqual(preview["confirmation_policy"], "single_confirmation")
        self.assertEqual(self.system.canonical_snapshot(), before)
        for name in ("person_card", "relationship_timeline"):
            view = self.system.read_core_view(name, "session-mm003")
            self.assertEqual(view["data_revision"], "rev_010")
            self.assertEqual(view["view_revision"], "rev_010")
            self.assertEqual(view["freshness_status"], "fresh")
        self.assertEqual(self.system.get_changeset(changeset["changeset_id"])["status"], "proposed")

    @scenario("MM-004")
    def test_mm_004_atomic_publish_and_failure(self) -> None:
        changeset, receipt = self._publish()
        self.assertEqual(receipt["status"], "published")
        self.assertEqual(receipt["preflight_result"], "passed")
        self.assertEqual(receipt["published_revision"], "rev_011")
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_011")
        self.assertEqual(
            self.system.query_relationship_contact("2031-08-31T23:59:59+08:00")["value"],
            "active",
        )
        current = self.system.query_relationship_contact("2031-09-01T00:00:00+08:00")
        self.assertEqual(current["value"], "no_contact")
        self.assertEqual(current["recorded_at"], "2031-10-15T02:00:00Z")
        attempts = self.system.get_publish_attempts(changeset["changeset_id"])
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["preflight_result"], "passed")

        failed = self._create_system("l1-failure")
        failed_changeset = self._propose(failed)
        failed.approve_changeset(failed_changeset["changeset_id"], "person_alpha")
        failed.inject_failure("l1.proposal.2")
        failed_receipt = failed.publish_changeset(
            failed_changeset["changeset_id"], "publish-l1-failure"
        )
        self.assertEqual(failed_receipt["status"], "failed")
        self.assertIsNone(failed_receipt["published_revision"])
        self.assertEqual(failed.canonical_snapshot()["data_revision"], "rev_010")
        self.assertEqual(
            failed.query_relationship_contact("2031-09-01T00:00:00+08:00")["value"],
            "active",
        )

    @scenario("MM-005")
    def test_mm_005_core_views_share_revision(self) -> None:
        self._publish()
        card = self.system.read_core_view("person_card", "session-mm005")
        timeline = self.system.read_core_view("relationship_timeline", "session-mm005")
        for view in (card, timeline):
            self.assertEqual(view["data_revision"], "rev_011")
            self.assertEqual(view["view_revision"], "rev_011")
            self.assertEqual(view["freshness_status"], "fresh")
        self.assertEqual(card["payload"]["contact_state"], "no_contact")
        self.assertEqual(timeline["payload"]["current_contact_state"], "no_contact")
        self.assertIn("active", [item["value"] for item in timeline["payload"]["history"]])

    @scenario("MM-006")
    def test_mm_006_historical_state_and_evidence(self) -> None:
        self._publish()
        before = self.system.query_relationship_contact("2031-08-31T23:59:59+08:00")
        after = self.system.query_relationship_contact("2031-09-01T00:00:00+08:00")
        self.assertEqual(before["value"], "active")
        self.assertEqual(after["value"], "no_contact")
        self.assertEqual({r["source_id"] for r in before["evidence_refs"]}, {"src_history_001"})
        self.assertEqual({r["source_id"] for r in after["evidence_refs"]}, {"src_micro_001"})
        objects = self._object_map(self.system.canonical_snapshot())
        self.assertEqual(objects["rel_alpha_beta"]["origin"], "project_peer")
        self.assertEqual(objects["state_role_001"]["value"], "peer")

    @scenario("MM-007")
    def test_mm_007_protected_semantics_unchanged(self) -> None:
        before_snapshot = self.system.canonical_snapshot()
        before_objects = self._object_map(before_snapshot)
        before_ids = set(before_objects)
        before_protected = self._protected_snapshot()
        self._publish()
        after_objects = self._object_map(self.system.canonical_snapshot())
        self.assertTrue(before_ids.issubset(set(after_objects)))
        self.assertEqual(before_protected, self._protected_snapshot())
        self.assertEqual(after_objects["rel_alpha_beta"]["origin"], "project_peer")
        self.assertEqual(after_objects["state_role_001"]["value"], "peer")
        serialized = json.dumps(after_objects, ensure_ascii=False)
        for forbidden in self.oracles["forbidden_change_oracle"]["forbidden_new_predicates"]:
            self.assertNotIn(forbidden, serialized)

    @scenario("MM-008")
    def test_mm_008_whole_changeset_revert(self) -> None:
        protected = self._protected_snapshot()
        changeset, _ = self._publish()
        revert = self.system.revert_changeset(changeset["changeset_id"], "revert-mm008")
        self.assertEqual(revert["status"], "published")
        self.assertEqual(revert["compensation_revision"], "rev_012")
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_012")
        self.assertEqual(
            self.system.query_relationship_contact("2031-10-15T02:00:00Z")["value"],
            "active",
        )
        for name in ("person_card", "relationship_timeline"):
            view = self.system.read_core_view(name, "session-mm008")
            self.assertEqual(view["data_revision"], "rev_012")
            self.assertEqual(view["view_revision"], "rev_012")
        event_types = {
            event["event_type"]
            for event in self.system.list_audit_events(changeset["changeset_id"])
        }
        self.assertTrue({"published", "reverted"}.issubset(event_types))
        self.assertEqual(protected, self._protected_snapshot())

    @scenario("MM-009")
    def test_mm_009_stale_base_conflict_and_idempotency(self) -> None:
        changeset = self._propose()
        self.system.approve_changeset(changeset["changeset_id"], "person_alpha")
        advanced = self.system.advance_revision_for_test()
        self.assertNotEqual(advanced["data_revision"], "rev_010")
        first = self.system.publish_changeset(changeset["changeset_id"], "stale-mm009")
        second = self.system.publish_changeset(changeset["changeset_id"], "stale-mm009")
        self.assertEqual(first["status"], "conflicted")
        self.assertIsNone(first["published_revision"])
        self.assertEqual(first["publish_attempt_id"], second["publish_attempt_id"])
        self.assertEqual(first["receipt_id"], second["receipt_id"])
        self.assertEqual(
            self.system.get_changeset(changeset["changeset_id"])["status"], "conflicted"
        )
        retry = self.system.propose_retry(changeset["changeset_id"])
        self.assertNotEqual(retry["changeset_id"], changeset["changeset_id"])
        self.assertEqual(retry["retry_of"], changeset["changeset_id"])

    @scenario("MM-010")
    def test_mm_010_l2_failure_is_safe_and_reconcilable(self) -> None:
        changeset = self._propose()
        self.system.approve_changeset(changeset["changeset_id"], "person_alpha")
        self.system.inject_failure("projection.person_card")
        receipt = self.system.publish_changeset(changeset["changeset_id"], "publish-mm010")
        self.assertEqual(receipt["published_revision"], "rev_011")
        failed_view = self.system.read_core_view("person_card", "session-mm010")
        self.assertEqual(failed_view["data_revision"], "rev_011")
        if failed_view.get("payload") is not None:
            self.assertEqual(failed_view["payload"]["contact_state"], "no_contact")
            self.assertEqual(failed_view["source"], "canonical_fallback")
        else:
            self.assertIn(failed_view["freshness_status"], {"updating", "unavailable"})
        self.assertFalse(
            failed_view.get("payload", {}).get("contact_state") == "active"
            and failed_view.get("freshness_status") == "fresh"
        )
        self.assertTrue(
            any(
                item["target"] == "person_card" and item["result"] == "failed"
                for item in receipt["view_results"]
            )
        )
        self.system.reconcile_views()
        self.assertEqual(self.system.canonical_snapshot()["data_revision"], "rev_011")
        for name in ("person_card", "relationship_timeline"):
            view = self.system.read_core_view(name, "session-mm010-reconciled")
            self.assertEqual(view["view_revision"], "rev_011")
            self.assertEqual(view["freshness_status"], "fresh")
