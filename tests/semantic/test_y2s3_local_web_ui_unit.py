"""Focused unit tests for Y2-S3 local Web UI boundaries."""

from __future__ import annotations

import http.client
import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.local_web import (
    FORBIDDEN_VISIBLE_TERMS,
    HOME_TITLE,
    WebService,
    static_stdlib_scan,
    web_write_scan,
)
from noetide_micro.runtime import open_runtime


class Y2S3LocalWebUiUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.runtime = open_runtime(self.root / "data")
        self.service = WebService(self.runtime, self.root / "backups", host="127.0.0.1", port=0)

    def tearDown(self) -> None:
        self.service.close()
        self.runtime.close()
        self._tmp.cleanup()

    def request(self, method: str, path: str, body: object | None = None, raw: str | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", self.service.port, timeout=5)
        try:
            payload = None
            headers = {}
            if raw is not None:
                payload = raw.encode("utf-8")
                headers["Content-Type"] = "application/json"
            elif body is not None:
                payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                headers["Content-Type"] = "application/json"
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            data = response.read()
            if not data:
                return response.status, None
            try:
                return response.status, json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                return response.status, data.decode("utf-8")
        finally:
            connection.close()

    def test_non_loopback_host_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WebService(self.runtime, self.root / "backups2", host="0.0.0.0", port=0, autostart=False)

    def test_home_page_uses_daily_copy_and_no_external_assets(self) -> None:
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        html = body if isinstance(body, str) else ""
        self.assertIn(HOME_TITLE, html)
        for label in ("记录一条示例材料", "生成整理建议", "确认这次整理", "查看当前视图", "撤销这次整理", "查看操作历史", "导出为可读副本", "创建本地备份"):
            self.assertIn(label, html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn('<link rel="stylesheet"', html)
        self.assertFalse(any(term in html for term in FORBIDDEN_VISIBLE_TERMS))

    def test_full_journey_over_http(self) -> None:
        status, record = self.request("POST", "/api/record", {})
        self.assertEqual(status, 200)
        self.assertEqual(record["receipt_id"], "receipt_source_micro_001")
        status, review = self.request("POST", "/api/review", {})
        self.assertEqual(status, 200)
        self.assertEqual(review["review"]["candidate_ref"], "changeset_micro_001")
        status, confirm = self.request("POST", "/api/confirm", {})
        self.assertEqual(status, 200)
        self.assertEqual(confirm["published_revision"], "rev_011")
        status, views = self.request("GET", "/api/views")
        self.assertEqual(status, 200)
        self.assertEqual(views["person_card"]["contact_state"], "no_contact")
        self.assertEqual(views["relationship_timeline"]["history_count"], 2)
        status, history = self.request("GET", "/api/history")
        self.assertEqual(status, 200)
        self.assertEqual([event["action"] for event in history["events"]], ["record", "confirm"])
        status, revert = self.request("POST", "/api/revert", {})
        self.assertEqual(status, 200)
        self.assertEqual(revert["compensation_revision"], "rev_012")
        status, views = self.request("GET", "/api/views")
        self.assertEqual(status, 200)
        self.assertEqual(views["person_card"]["contact_state"], "active")
        self.assertEqual(views["relationship_timeline"]["history_count"], 1)

    def test_rejections_are_zero_write(self) -> None:
        before = self.runtime.store.canonical_layer_digest()
        revision = self.runtime.revision()
        status, payload = self.request("GET", "/api/unknown")
        self.assertEqual((status, payload["status"], payload["reason"]), (404, "rejected", "not_found"))
        status, payload = self.request("POST", "/api/record", raw="{not-json")
        self.assertEqual((status, payload["status"], payload["reason"]), (400, "rejected", "malformed_json"))
        status, payload = self.request("POST", "/api/review", {})
        self.assertEqual((status, payload["status"], payload["reason"]), (409, "rejected", "record_first"))
        status, payload = self.request("POST", "/api/confirm", {})
        self.assertEqual((status, payload["status"], payload["reason"]), (409, "rejected", "review_first"))
        status, payload = self.request("POST", "/api/revert", {})
        self.assertEqual((status, payload["status"], payload["reason"]), (409, "rejected", "confirm_first"))
        status, payload = self.request("POST", "/api/backup", {"path": "C:/evil"})
        self.assertEqual((status, payload["status"], payload["reason"]), (409, "rejected", "path_not_allowed"))
        self.assertEqual(self.runtime.store.canonical_layer_digest(), before)
        self.assertEqual(self.runtime.revision(), revision)

    def test_export_is_read_only_and_backup_path_is_controlled(self) -> None:
        for action in ("record", "review", "confirm", "revert"):
            status, _ = self.request("POST", f"/api/{action}", {})
            self.assertEqual(status, 200)
        before = self.runtime.store.canonical_layer_digest()
        revision = self.runtime.revision()
        status, export = self.request("GET", "/api/export")
        self.assertEqual(status, 200)
        self.assertEqual(set(export["files"]), {"markdown/sources.md", "markdown/canonical.md", "markdown/ledger.md"})
        self.assertTrue(all(export["markdown"][name].startswith("# ") for name in export["files"]))
        self.assertEqual(self.runtime.store.canonical_layer_digest(), before)
        self.assertEqual(self.runtime.revision(), revision)
        status, backup = self.request("POST", "/api/backup", {})
        self.assertEqual(status, 200)
        self.assertTrue(backup["backup_file_exists"])
        self.assertTrue(backup["source_db_sha256_matches"])
        self.assertTrue((self.root / "backups" / "web_backup_001.nobak").is_file())
        self.assertEqual(self.runtime.store.canonical_layer_digest(), before)
        self.assertEqual(self.runtime.revision(), revision)

    def test_web_write_scan_finds_no_forbidden_store_calls(self) -> None:
        _, forbidden = web_write_scan()
        self.assertEqual(forbidden, [])

    def test_static_stdlib_scan_finds_no_external_modules(self) -> None:
        _, external = static_stdlib_scan()
        self.assertEqual(external, [])


if __name__ == "__main__":
    unittest.main()