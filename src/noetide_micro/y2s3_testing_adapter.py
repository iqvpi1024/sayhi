"""Fixture-scoped Y2-S3 local Web UI contract adapter.

Each system owns a temp data directory, a fresh synthetic runtime, and a real
127.0.0.1 stdlib HTTP server. Contract cases are executed over HTTP, while
layer snapshots prove no forbidden store mutation occurred.
"""

from __future__ import annotations

import copy
import hashlib
import http.client
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .local_web import BACKUP_FILENAME, FORBIDDEN_VISIBLE_TERMS, WebService, static_stdlib_scan, web_write_scan
from .runtime import open_runtime

JsonObject = dict[str, Any]
SOURCE_ID = "src_micro_001"
RECORD_RECEIPT_ID = "receipt_source_micro_001"
PUBLISH_RECEIPT_ID = "receipt_publish_001"
COMPENSATION_RECEIPT_ID = "receipt_compensation_001"
CHANGESET_ID = "changeset_micro_001"
PROTECTED_STATE_KINDS = ("trust", "closeness")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class WebSystem:
    def __init__(self, case: JsonObject) -> None:
        self.case = copy.deepcopy(case)
        self._tmp = Path(tempfile.mkdtemp(prefix="noetide-y2s3-"))
        self.data_dir = self._tmp / "data"
        self.backup_dir = self._tmp / "backups"
        self.data_dir.mkdir()
        self.runtime = open_runtime(self.data_dir)
        self.service = WebService(self.runtime, self.backup_dir, host="127.0.0.1", port=0)
        self._closed = False
        self._export_read_only: bool | None = None
        self._backup_store_read_only: bool | None = None
        self._backup_path_controlled: bool | None = None

    def layer_snapshot(self) -> JsonObject:
        snapshot = self.runtime.store.seed_snapshot()
        objects = snapshot["objects"]
        trust_closeness = {
            oid: payload
            for oid, payload in sorted(objects.items())
            if payload.get("state_kind") in PROTECTED_STATE_KINDS
        }
        personality = {
            oid: payload
            for oid, payload in sorted(objects.items())
            if payload.get("object_type") == "hypothesis"
        }
        return {
            "canonical_objects": _canonical(objects),
            "revisions": self.runtime.revision(),
            "trust_closeness": _canonical(trust_closeness),
            "personality_judgments": _canonical(personality),
            "ledger": _canonical(self.runtime.store.portability_snapshot()["ledger"]),
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.service.close()
        self.runtime.close()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def run_case(self, case: JsonObject) -> JsonObject:
        step_results: JsonObject = {}
        for step in case["steps"]:
            if step == "home":
                step_results["home"] = self._home()
            elif step == "record":
                step_results["record"] = self._record()
            elif step == "review":
                step_results["review"] = self._review()
            elif step == "confirm":
                step_results["confirm"] = self._confirm()
            elif step == "views":
                step_results["views"] = self._views()
            elif step == "history":
                step_results["history"] = self._history()
            elif step == "revert":
                step_results["revert"] = self._revert()
            elif step == "export":
                step_results["export"] = self._export()
            elif step == "backup":
                step_results["backup"] = self._backup()
            elif step == "fail":
                step_results["fail"] = self._fail()
            elif step == "determinism":
                step_results["determinism"] = self._determinism()
            elif step == "audit":
                step_results["audit"] = self._audit()
            else:
                raise KeyError(f"unknown Y2S3 journey step: {step}")
        return {
            "status": "web_case_completed",
            "step_results": step_results,
            "data_revision": self.runtime.revision(),
        }

    def _http_request(
        self,
        method: str,
        path: str,
        body: Any | None = None,
        raw_body: str | None = None,
    ) -> tuple[int, bytes]:
        connection = http.client.HTTPConnection("127.0.0.1", self.service.port, timeout=5)
        try:
            headers = {}
            payload = body
            if raw_body is not None:
                payload = raw_body.encode("utf-8")
                headers["Content-Type"] = "application/json"
            elif body is not None:
                payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                headers["Content-Type"] = "application/json"
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def _json_request(self, method: str, path: str, body: Any | None = None, raw_body: str | None = None) -> JsonObject:
        status, raw = self._http_request(method, path, body=body, raw_body=raw_body)
        payload = json.loads(raw.decode("utf-8"))
        return {"http_status": status, "payload": payload}

    def _home(self) -> JsonObject:
        status, raw = self._http_request("GET", "/")
        html = raw.decode("utf-8")
        title_match = re.search(r"<title>([^<]+)</title>", html)
        title = title_match.group(1) if title_match else ""
        visible = re.findall(r'data-copy="([^"]+)"', html)
        forbidden = any(term in html for term in FORBIDDEN_VISIBLE_TERMS)
        external = bool(
            re.search(r"https?://", html)
            or re.search(r"<script[^>]+src=", html)
            or re.search(r'<link[^>]+href=', html)
        )
        if status != 200:
            raise AssertionError(f"home returned HTTP {status}")
        return {
            "status": "ok",
            "html_title": title,
            "visible_copy": visible,
            "contains_forbidden_visible_terms": forbidden,
            "uses_external_assets": external,
        }

    def _record(self) -> JsonObject:
        result = self._json_request("POST", "/api/record", body={})
        payload = result["payload"]
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("record was rejected")
        return {"status": "ok", "source_id": payload["source_id"], "receipt_id": payload["receipt_id"]}

    def _review(self) -> JsonObject:
        result = self._json_request("POST", "/api/review", body={})
        payload = result["payload"]
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("review was rejected")
        return {"status": "ok", "review": payload["review"], "preview": payload["preview"]}

    def _confirm(self) -> JsonObject:
        result = self._json_request("POST", "/api/confirm", body={})
        payload = result["payload"]
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("confirm was rejected")
        return {
            "status": "ok",
            "publish_status": payload["publish_status"],
            "published_revision": payload["published_revision"],
            "receipt_id": payload["receipt_id"],
        }

    def _views(self) -> JsonObject:
        result = self._json_request("GET", "/api/views")
        payload = result["payload"]
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("views were rejected")
        return {
            "status": "ok",
            "person_card": payload["person_card"],
            "relationship_timeline": payload["relationship_timeline"],
        }

    def _history(self) -> JsonObject:
        result = self._json_request("GET", "/api/history")
        payload = result["payload"]
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("history was rejected")
        return {"status": "ok", "events": payload["events"]}

    def _revert(self) -> JsonObject:
        result = self._json_request("POST", "/api/revert", body={})
        payload = result["payload"]
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("revert was rejected")
        return {
            "status": "ok",
            "revert_status": payload["revert_status"],
            "compensation_revision": payload["compensation_revision"],
            "receipt_id": payload["receipt_id"],
        }

    def _export(self) -> JsonObject:
        before = self._short_layer_snapshot()
        result = self._json_request("GET", "/api/export")
        payload = result["payload"]
        after = self._short_layer_snapshot()
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("export was rejected")
        expected_files = {"markdown/sources.md", "markdown/canonical.md", "markdown/ledger.md"}
        markdown = payload.get("markdown", {})
        if set(payload["files"]) != expected_files:
            raise AssertionError("export file list mismatch")
        if not all(isinstance(markdown.get(name), str) and markdown[name] for name in expected_files):
            raise AssertionError("export markdown content missing")
        self._export_read_only = before == after
        return {
            "status": "ok",
            "data_revision": payload["data_revision"],
            "files": payload["files"],
            "read_only": payload["read_only"],
        }

    def _backup(self) -> JsonObject:
        before = self._short_layer_snapshot()
        result = self._json_request("POST", "/api/backup", body={})
        payload = result["payload"]
        after = self._short_layer_snapshot()
        if result["http_status"] != 200 or payload["status"] != "ok":
            raise AssertionError("backup was rejected")
        backup_file = self.backup_dir / payload["backup_id"]
        self._backup_store_read_only = before == after
        self._backup_path_controlled = (
            backup_file == (self.backup_dir / BACKUP_FILENAME)
            and backup_file.parent == self.backup_dir
            and backup_file.is_file()
        )
        return {
            "status": "ok",
            "backup_id": payload["backup_id"],
            "backup_file_exists": payload["backup_file_exists"],
            "source_db_sha256_matches": payload["source_db_sha256_matches"],
            "created_at": payload["created_at"],
        }

    def _fail(self) -> JsonObject:
        probes = [
            ("GET", "/api/unknown", None, None, 404, "not_found"),
            ("POST", "/api/record", None, "{not-json", 400, "malformed_json"),
            ("POST", "/api/review", {}, None, 409, "record_first"),
            ("POST", "/api/confirm", {}, None, 409, "review_first"),
            ("POST", "/api/revert", {}, None, 409, "confirm_first"),
            ("POST", "/api/backup", {"path": "/tmp/evil"}, None, 409, "path_not_allowed"),
        ]
        before = self.layer_snapshot()
        rejections: list[JsonObject] = []
        for method, path, body, raw_body, expected_status, expected_reason in probes:
            status, raw = self._http_request(method, path, body=body, raw_body=raw_body)
            payload = json.loads(raw.decode("utf-8"))
            if status != expected_status or payload.get("status") != "rejected" or payload.get("reason") != expected_reason:
                raise AssertionError(f"{method} {path} did not fail closed as expected")
            rejections.append(
                {"method": method, "path": path, "http_status": status, "reason": payload["reason"]}
            )
        after = self.layer_snapshot()
        non_loopback_rejected = False
        try:
            WebService(self.runtime, self._tmp / "evil", host="0.0.0.0", port=0, autostart=False)
        except ValueError:
            non_loopback_rejected = True
        return {
            "status": "ok",
            "rejections": rejections,
            "zero_business_write": before == after,
            "non_loopback_rejected": non_loopback_rejected,
        }

    def _determinism(self) -> JsonObject:
        before = self.layer_snapshot()
        other = WebSystem({"scenario_id": "Y2S3-010-other", "steps": []})
        try:
            probes = [
                ("GET", "/", None, None),
                ("GET", "/api/unknown", None, None),
                ("POST", "/api/review", {}, None),
            ]
            self_responses = [self._http_request(method, path, body=body, raw_body=raw) for method, path, body, raw in probes]
            other_responses = [other._http_request(method, path, body=body, raw_body=raw) for method, path, body, raw in probes]
            identical = all(a == b for a, b in zip(self_responses, other_responses))
        finally:
            other.close()
        after = self.layer_snapshot()
        non_loopback_rejected = False
        try:
            WebService(self.runtime, self._tmp / "evil2", host="0.0.0.0", port=0, autostart=False)
        except ValueError:
            non_loopback_rejected = True
        _, forbidden = web_write_scan()
        _, external = static_stdlib_scan()
        fixture = self.runtime.fixture
        return {
            "status": "ok",
            "determinism_byte_identical": identical,
            "non_loopback_rejected": non_loopback_rejected,
            "zero_bypass": forbidden == [],
            "stdlib_only": external == [],
            "synthetic_fixture": fixture.get("synthetic") is True and fixture.get("external_data_used") is not True,
            "canonical_unchanged": after == before,
            "revision_unchanged": after["revisions"] == before["revisions"],
        }

    def _audit(self) -> JsonObject:
        _, forbidden = web_write_scan()
        _, external = static_stdlib_scan()
        fixture = self.runtime.fixture
        result = {
            "zero_bypass": forbidden == [],
            "synthetic_fixture": fixture.get("synthetic") is True and fixture.get("external_data_used") is not True,
            "stdlib_server": external == [],
        }
        if self._export_read_only is not None:
            result["export_store_read_only"] = self._export_read_only
        if self._backup_store_read_only is not None:
            result["backup_store_read_only"] = self._backup_store_read_only
        if self._backup_path_controlled is not None:
            result["backup_path_controlled"] = self._backup_path_controlled
        return result

    def _short_layer_snapshot(self) -> JsonObject:
        return {
            "revision": self.runtime.revision(),
            "canonical": self.runtime.store.canonical_layer_digest(),
            "ledger": _canonical(self.runtime.store.portability_snapshot()["ledger"]),
        }


def create_system(case: JsonObject) -> WebSystem:
    return WebSystem(case)