"""Product-level tests for the complete Noetide local application surface."""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from noetide_micro.product import NoetideApp
from noetide_micro.product_server import ProductHttpServer


class NoetideProductTests(unittest.TestCase):
    def test_empty_init_ingest_analyze_confirm_export_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            self.assertEqual(app.overview()["sources"], 0)
            result = app.ingest_text("今天和小明聊了识海项目。我答应下周给一份完整方案。")
            self.assertEqual(result["status"], "stored")
            analysis = app.analyze_sources()
            self.assertGreater(len(analysis["candidates_proposed"]), 0)
            candidates = app.list_candidates()
            self.assertTrue(candidates)
            first = next(item for item in candidates if item["candidate_kind"] == "entity")
            confirmed = app.confirm_candidate(first["candidate_id"])
            self.assertEqual(confirmed["status"], "confirmed")
            self.assertEqual(app.overview()["canonical"], 1)
            exported = app.export_pack()
            self.assertEqual(exported["status"], "ok")
            backup = app.backup()
            self.assertEqual(backup["status"], "ok")
            self.assertTrue(Path(backup["path"]).is_file())
            search = app.search("小明")
            self.assertTrue(search["sources"])
            app.close()

    def test_server_api_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            server = ProductHttpServer(app, ("127.0.0.1", 0))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port = server.server_address[1]
                html = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5).read().decode("utf-8")
                self.assertIn("识海", html)
                payload = json.dumps({"content": "小张要完成识海完整版"}).encode("utf-8")
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/ingest/text",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                response = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))
                self.assertEqual(response["status"], "ok")
                overview = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/overview", timeout=5).read().decode("utf-8"))
                self.assertEqual(overview["data"]["sources"], 1)
            finally:
                server.shutdown()
                server.server_close()
                app.close()

    def test_settings_and_mcp_capability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            settings = app.public_settings()
            self.assertEqual(settings["model_mode"], "offline")
            self.assertTrue(settings["api_token"])
            app.update_settings({"model_mode": "cloud", "model_endpoint": "https://example.com/v1/chat/completions"})
            self.assertEqual(app.public_settings()["model_mode"], "cloud")
            capability = app.default_mcp_capability()
            self.assertEqual(capability["capability_id"], "cap_product_default")
            self.assertIn("read_resource", capability["tools"])
            app.close()


    def test_custom_agent_capability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            server = ProductHttpServer(app, ("127.0.0.1", 0))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port = server.server_address[1]
                payload = json.dumps({"resource_ids": ["src_agent_inbox_001"]}).encode("utf-8")
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/mcp/capability",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                response = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))
                self.assertEqual(response["status"], "ok")
                self.assertTrue(response["capability"]["capability_id"].startswith("cap_agent_"))
                self.assertIn("record_source", response["capability"]["tools"])
            finally:
                server.shutdown()
                server.server_close()
                app.close()

    def test_mcp_list_resources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            result = app.ingest_text("小明这周要完成识海完整版。")
            app.default_mcp_capability()
            response = app.mcp_handle({
                "contract_version": "y2s5-mcp-runtime-v1",
                "request_id": "req_product_001",
                "caller_ref": "local_user",
                "purpose": "personal_memory_read_and_propose",
                "capability_ref": "cap_product_default",
                "scope": {"resource_ids": [result["source_id"]]},
                "requested_at": "2026-08-03T00:00:00+00:00",
                "action": "list_resources",
            })
            self.assertEqual(response["result_status"], "ok")
            self.assertIn(result["source_id"], response["payload"]["resource_ids"])
            app.close()


if __name__ == "__main__":
    unittest.main()
