"""Agent 记忆中枢表面测试:标准 MCP 协议、ask_memory 范围门、提议落候选队列、分析进度。

2026-08-08 真实用户模拟测试遗留改进:任何支持 MCP 的 Agent(Claude Code、Codex 等)
可通过标准协议接入识海;提议必须进入用户可确认的候选队列;ask_memory 只读且
范围限能力令牌授权资料(红线舱室不可见)。
"""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
import urllib.request

from noetide_micro.product import NoetideApp
from noetide_micro.product_server import ProductHttpServer


def _rpc(port: int, body: dict, capability: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if capability:
        headers["X-Noetide-Capability"] = capability
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/mcp",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8"))


def _confirm_all(app: NoetideApp) -> list[dict]:
    app.analyze_sources()
    return [app.confirm_candidate(c["candidate_id"]) for c in app.list_candidates()]


class _ServerCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.app = NoetideApp(self._tmp.name)
        self.server = ProductHttpServer(self.app, ("127.0.0.1", 0))
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.app.close()
        self._tmp.cleanup()


class StandardMcpProtocolTests(_ServerCase):
    def test_initialize_and_tools_list(self) -> None:
        init = _rpc(self.port, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "noetide")
        self.assertIn("tools", init["result"]["capabilities"])
        tools = _rpc(self.port, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in tools["result"]["tools"]}
        self.assertEqual(names, {"list_resources", "read_resource", "ask_memory", "propose_changeset", "record_source"})
        for tool in tools["result"]["tools"]:
            self.assertTrue(tool["description"])
            self.assertIn("inputSchema", tool)
        ping = _rpc(self.port, {"jsonrpc": "2.0", "id": 3, "method": "ping"})
        self.assertEqual(ping["result"], {})
        unknown = _rpc(self.port, {"jsonrpc": "2.0", "id": 4, "method": "prompts/get"})
        self.assertEqual(unknown["error"]["code"], -32601)

    def test_tools_call_unknown_tool_rejected(self) -> None:
        response = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 5, "method": "tools/call",
            "params": {"name": "delete_item", "arguments": {}},
        })
        self.assertEqual(response["error"]["code"], -32601)

    def test_resources_list_and_read(self) -> None:
        ingested = self.app.ingest_text("小明是识海项目的CEO。")
        listed = _rpc(self.port, {"jsonrpc": "2.0", "id": 6, "method": "resources/list"})
        uris = [r["uri"] for r in listed["result"]["resources"]]
        self.assertIn(f"noetide://source/{ingested['source_id']}", uris)
        read = _rpc(self.port, {"jsonrpc": "2.0", "id": 7, "method": "resources/read",
                                "params": {"uri": f"noetide://source/{ingested['source_id']}"}})
        content = read["result"]["contents"][0]
        self.assertFalse(read["result"]["isError"])
        self.assertIn("小明", content["text"])
        denied = _rpc(self.port, {"jsonrpc": "2.0", "id": 8, "method": "resources/read",
                                  "params": {"uri": "noetide://source/src_not_exist"}})
        self.assertTrue(denied["result"]["isError"])

    def test_legacy_shape_still_works(self) -> None:
        ingested = self.app.ingest_text("小明是识海项目的CEO。")
        self.app.default_mcp_capability()
        legacy = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 9, "method": "tools/call",
            "params": {"request": {
                "contract_version": "y2s5-mcp-runtime-v1",
                "request_id": "req_legacy_001",
                "caller_ref": "local_user",
                "purpose": "personal_memory_read_and_propose",
                "capability_ref": "cap_product_default",
                "scope": {"resource_ids": [ingested["source_id"]]},
                "requested_at": "2026-08-08T00:00:00+00:00",
                "action": "list_resources",
            }},
        })
        self.assertEqual(legacy["result"]["result_status"], "ok")


class AskMemoryToolTests(_ServerCase):
    def test_ask_memory_answered_with_confirmed_memory(self) -> None:
        self.app.ingest_text("小米集团由雷军于2010年创立,2018年在港股上市。")
        _confirm_all(self.app)
        response = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 10, "method": "tools/call",
            "params": {"name": "ask_memory", "arguments": {"question": "小米是哪一年创立的?"}},
        })
        self.assertFalse(response["result"]["isError"])
        internal = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(internal["answer_status"], "answered")
        self.assertIn("2010", internal["payload"]["answer_text"])

    def test_ask_memory_honest_no_coverage(self) -> None:
        self.app.ingest_text("小明是识海项目的CEO。")
        _confirm_all(self.app)
        response = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 11, "method": "tools/call",
            "params": {"name": "ask_memory", "arguments": {"question": "火星基地建设进度如何?"}},
        })
        internal = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(internal["answer_status"], "no_coverage")
        self.assertIn("不知道", internal["payload"]["answer_text"])

    def test_ask_memory_scope_excludes_red_line(self) -> None:
        """红线舱室(健康关键词命中)的记忆对 Agent 不可见,即使已确认;本机网页仍可见。"""
        red = self.app.ingest_text("我的病历记录:2026年体检一切正常。")
        normal = self.app.ingest_text("小米集团由雷军于2010年创立。")
        self.assertIn("health", self.app.get_source(red["source_id"]).get("compartments") or [])
        _confirm_all(self.app)
        # Agent 路径:默认令牌含全部 source,但红线舱室在 ask 层被过滤
        response = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 12, "method": "tools/call",
            "params": {"name": "ask_memory", "arguments": {"question": "体检结果如何?"}},
        })
        internal = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(internal["answer_status"], "no_coverage")
        self.assertEqual(internal["payload"]["evidence"], [])
        # 限定范围令牌:只授权 normal 资料,问小米可答
        cap = self.app.create_agent_capability([normal["source_id"]])
        scoped = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 13, "method": "tools/call",
            "params": {"name": "ask_memory", "arguments": {"question": "小米是哪一年创立的?"}},
        }, capability=cap["capability_id"])
        scoped_internal = json.loads(scoped["result"]["content"][0]["text"])
        self.assertEqual(scoped_internal["answer_status"], "answered")
        unknown_cap = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 14, "method": "tools/call",
            "params": {"name": "ask_memory", "arguments": {"question": "小米?"}},
        }, capability="cap_not_exist")
        self.assertTrue(unknown_cap["result"]["isError"])

    def test_ask_memory_empty_question_failed(self) -> None:
        response = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 15, "method": "tools/call",
            "params": {"name": "ask_memory", "arguments": {"question": "  "}},
        })
        internal = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(internal["result_status"], "failed")


class ProposeLandsInQueueTests(_ServerCase):
    def test_propose_changeset_appears_in_candidate_queue(self) -> None:
        ingested = self.app.ingest_text("小米集团由雷军于2010年创立。")
        cap = self.app.create_agent_capability([ingested["source_id"]])
        candidate = {
            "candidate_kind": "entity",
            "payload": {"entity_kind": "person", "canonical_label": "老王", "aliases": ["老王"], "summary": "对话中提到老王"},
            "evidence_refs": [{"source_id": ingested["source_id"]}],
        }
        response = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 16, "method": "tools/call",
            "params": {"name": "propose_changeset", "arguments": {"candidate": candidate}},
        }, capability=cap["capability_id"])
        self.assertFalse(response["result"]["isError"])
        internal = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(internal["result_status"], "accepted")
        # 落队列:网页 /api/candidates 可见,来源标注为 mcp-agent
        queued = [c for c in self.app.list_candidates() if c["payload"].get("canonical_label") == "老王"]
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0]["status"], "proposed")
        self.assertTrue(queued[0]["model_or_rule_version"].startswith("mcp-agent:"))
        self.assertTrue(queued[0]["mcp_changeset_id"])
        # 幂等:同内容重复提议不重复入队
        again = _rpc(self.port, {
            "jsonrpc": "2.0", "id": 17, "method": "tools/call",
            "params": {"name": "propose_changeset", "arguments": {"candidate": candidate}},
        }, capability=cap["capability_id"])
        self.assertFalse(again["result"]["isError"])
        self.assertEqual(len([c for c in self.app.list_candidates() if c["payload"].get("canonical_label") == "老王"]), 1)
        # 用户在网页上确认后成为正式记忆
        confirmed = self.app.confirm_candidate(queued[0]["candidate_id"])
        self.assertEqual(confirmed["status"], "confirmed")
        obj = self.app.get_object(confirmed["object_id"])
        self.assertIsNotNone(obj)
        self.assertEqual(obj["object_type"], "entity")
        self.assertEqual(obj["canonical_label"], "老王")


class AnalysisProgressTests(unittest.TestCase):
    def test_background_analysis_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("小明是识海项目的CEO。")
            started = app.start_analysis()
            self.assertTrue(started["started"])
            deadline = time.time() + 15
            status = app.analysis_status()
            while status["running"] and time.time() < deadline:
                time.sleep(0.05)
                status = app.analysis_status()
            self.assertFalse(status["running"])
            self.assertEqual(status["total"], 1)
            self.assertEqual(status["done"], 1)
            self.assertIsNone(status["error"])
            self.assertGreaterEqual(status["candidates"], 1)
            self.assertTrue(status["finished_at"])
            self.assertTrue(app.list_candidates())
            app.close()

    def test_already_running_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app._analysis_progress["running"] = True
            result = app.start_analysis()
            self.assertFalse(result["started"])
            self.assertEqual(result["reason"], "already_running")
            app.close()


if __name__ == "__main__":
    unittest.main()
