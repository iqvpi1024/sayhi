"""产品层 LLM 提供商适配、结构化提取解析与 docx 导入的语义测试。

使用 127.0.0.1 假 HTTP 服务器验证三种 provider 的请求形状与响应解析;
全部数据均为显式合成数据,不访问外网。
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from noetide_micro import llm_providers
from noetide_micro.folder_import import FolderImporter
from noetide_micro.product import NoetideApp


class _FakeProviderHandler(BaseHTTPRequestHandler):
    """记录请求形状并按类属性返回固定响应的假提供商。"""

    captured: list[dict] = []
    response_status = 200
    response_payload: dict = {}

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw)
        except ValueError:
            body = raw
        type(self).captured.append({
            "method": "POST",
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
        })
        payload = json.dumps(type(self).response_payload).encode("utf-8")
        self.send_response(type(self).response_status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args: object) -> None:
        return


@contextlib.contextmanager
def fake_server(payload: dict, status: int = 200):
    """启动 loopback 假提供商,产出 (captured 列表, base_url)。"""
    _FakeProviderHandler.captured = []
    _FakeProviderHandler.response_payload = payload
    _FakeProviderHandler.response_status = status
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeProviderHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield _FakeProviderHandler.captured, f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def _make_docx(paragraphs: list[str]) -> bytes:
    """现场造一个最小 docx:仅含 word/document.xml 的 zip。"""
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs)
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>'
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", document)
    return buffer.getvalue()


def _header(request: dict, name: str) -> str | None:
    """大小写不敏感地取请求头(urllib 会对头名做 capitalize)。"""
    for key, value in request["headers"].items():
        if key.lower() == name.lower():
            return value
    return None


_MESSAGES = [
    {"role": "system", "content": "只输出 JSON。"},
    {"role": "user", "content": "材料:小明是识海项目的创始人。"},
]


class ProviderShapeTests(unittest.TestCase):
    def test_openai_compatible_request_shape_and_response(self) -> None:
        with fake_server({"choices": [{"message": {"content": "[]"}}]}) as (captured, base):
            out = llm_providers.chat_completion(
                "openai_compatible", base + "/v1/chat/completions", "sk-synthetic-KEY", "my-model", _MESSAGES, timeout=5,
            )
        self.assertEqual(out, "[]")
        self.assertEqual(len(captured), 1)
        request = captured[0]
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["path"], "/v1/chat/completions")
        self.assertEqual(_header(request, "Authorization"), "Bearer sk-synthetic-KEY")
        self.assertEqual(request["body"]["model"], "my-model")
        self.assertEqual(request["body"]["messages"][0]["role"], "system")

    def test_anthropic_request_shape_and_response(self) -> None:
        payload = {"content": [{"type": "text", "text": "[{\"object_type\":\"entity\"}]"}]}
        with fake_server(payload) as (captured, base):
            out = llm_providers.chat_completion(
                "anthropic", base + "/v1/messages", "sk-ant-synthetic", "claude-test", _MESSAGES, timeout=5,
            )
        self.assertEqual(out, '[{"object_type":"entity"}]')
        request = captured[0]
        self.assertEqual(request["path"], "/v1/messages")
        self.assertEqual(_header(request, "x-api-key"), "sk-ant-synthetic")
        self.assertEqual(_header(request, "anthropic-version"), "2023-06-01")
        self.assertIsNone(_header(request, "Authorization"))
        body = request["body"]
        self.assertEqual(body["model"], "claude-test")
        self.assertEqual(body["max_tokens"], 1024)
        # system 是顶层字段,messages 里不允许 system 角色
        self.assertEqual(body["system"], "只输出 JSON。")
        self.assertEqual([m["role"] for m in body["messages"]], ["user"])

    def test_gemini_request_shape_and_response(self) -> None:
        payload = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
        with fake_server(payload) as (captured, base):
            out = llm_providers.chat_completion(
                "gemini", base + "/v1beta/models/{model}:generateContent", "goog-synthetic", "gemini-x", _MESSAGES, timeout=5,
            )
        self.assertEqual(out, "ok")
        request = captured[0]
        # {model} 模板在发送前替换为实际模型名
        self.assertEqual(request["path"], "/v1beta/models/gemini-x:generateContent")
        self.assertEqual(_header(request, "x-goog-api-key"), "goog-synthetic")
        body = request["body"]
        self.assertEqual(body["contents"][0]["role"], "user")
        self.assertEqual(body["contents"][0]["parts"][0]["text"], _MESSAGES[1]["content"])
        self.assertEqual(body["system_instruction"]["parts"][0]["text"], "只输出 JSON。")

    def test_api_key_never_in_error_message(self) -> None:
        secret = "sk-secret-UNITTEST-KEY"
        with fake_server({"error": "boom"}, status=500) as (_, base):
            with self.assertRaises(llm_providers.ProviderCallError) as ctx:
                llm_providers.chat_completion(
                    "openai_compatible", base + "/v1/chat/completions", secret, "m", _MESSAGES, timeout=5,
                )
        self.assertNotIn(secret, str(ctx.exception))

    def test_provider_presets_and_resolution(self) -> None:
        self.assertEqual(llm_providers.default_endpoint("deepseek"), "https://api.deepseek.com/v1/chat/completions")
        self.assertEqual(llm_providers.default_model("moonshot"), "moonshot-v1-8k")
        self.assertEqual(llm_providers.resolve_provider("anthropic")["adapter"], "anthropic")
        # 未知值 fail-closed 到 openai_compatible 且无默认端点
        unknown = llm_providers.resolve_provider("no-such-provider")
        self.assertEqual(unknown["adapter"], "openai_compatible")
        self.assertEqual(unknown["endpoint"], "")
        with self.assertRaises(llm_providers.ProviderCallError):
            llm_providers.chat_completion("custom", "", "", "", _MESSAGES, timeout=1)


class ExtractionParserTests(unittest.TestCase):
    SOURCE = "小明是识海项目的创始人。我答应下周提交方案。"

    def _entry(self, **overrides: object) -> dict:
        entry = {
            "object_type": "entity",
            "label": "小明",
            "summary": "小明是识海项目的创始人",
            "evidence_quote": "小明是识海项目的创始人",
        }
        entry.update(overrides)
        return entry

    def test_fenced_json_accepted(self) -> None:
        raw = "```json\n" + json.dumps([self._entry()], ensure_ascii=False) + "\n```"
        entries, stats = llm_providers.parse_extraction_output(raw, self.SOURCE)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["label"], "小明")
        self.assertIsNone(stats["error"])

    def test_noisy_text_around_json_accepted(self) -> None:
        raw = "好的,提取结果如下:\n" + json.dumps([self._entry()], ensure_ascii=False) + "\n希望对你有帮助。"
        entries, stats = llm_providers.parse_extraction_output(raw, self.SOURCE)
        self.assertEqual(len(entries), 1)
        self.assertEqual(stats["parsed"], 1)

    def test_fabricated_evidence_dropped_and_counted(self) -> None:
        raw = json.dumps([
            self._entry(),
            self._entry(label="编造者", evidence_quote="原文里根本没有这句话"),
        ], ensure_ascii=False)
        entries, stats = llm_providers.parse_extraction_output(raw, self.SOURCE)
        self.assertEqual(len(entries), 1)
        self.assertEqual(stats["dropped_fabricated_evidence"], 1)

    def test_bad_json_fails_closed(self) -> None:
        entries, stats = llm_providers.parse_extraction_output("完全不是 JSON 的输出", self.SOURCE)
        self.assertEqual(entries, [])
        self.assertEqual(stats["error"], "invalid_json")

    def test_object_type_whitelist_enforced(self) -> None:
        raw = json.dumps([self._entry(object_type="unknown_kind")], ensure_ascii=False)
        entries, stats = llm_providers.parse_extraction_output(raw, self.SOURCE)
        self.assertEqual(entries, [])
        self.assertEqual(stats["dropped_invalid"], 1)


class ProductProviderWiringTests(unittest.TestCase):
    def test_settings_provider_roundtrip_and_key_privacy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            public = app.public_settings()
            self.assertEqual(public["model_provider"], "openai_compatible")
            self.assertEqual(public["model_name"], "")
            app.update_settings({"model_provider": "anthropic", "model_api_key": "sk-secret-SETTINGS"})
            public = app.public_settings()
            self.assertEqual(public["model_provider"], "anthropic")
            # api_key 只回 *_set 布尔,永不回明文
            self.assertTrue(public["model_api_key_set"])
            self.assertNotIn("model_api_key", public)
            app.close()

    def test_local_mode_extraction_end_to_end(self) -> None:
        source_text = "小明是识海项目的创始人。我答应下周提交方案。"
        model_output = "```json\n" + json.dumps([
            {"object_type": "entity", "label": "小明", "summary": "小明是识海项目的创始人", "evidence_quote": "小明是识海项目的创始人"},
            {"object_type": "commitment", "label": "提交方案", "summary": "我答应下周提交方案", "evidence_quote": "我答应下周提交方案"},
            {"object_type": "entity", "label": "编造者", "summary": "不存在的人", "evidence_quote": "原文里根本没有这句话"},
        ], ensure_ascii=False) + "\n```"
        with tempfile.TemporaryDirectory() as tmp:
            with fake_server({"choices": [{"message": {"content": model_output}}]}) as (captured, base):
                app = NoetideApp(tmp)
                app.update_settings({
                    "model_mode": "local",
                    "model_provider": "openai_compatible",
                    "model_endpoint": base + "/v1/chat/completions",
                    "model_name": "test-model",
                })
                stored = app.ingest_text(source_text)
                analysis = app.analyze_sources()
            try:
                self.assertEqual(analysis["rejected_outputs"], [])
                proposed = analysis["candidates_proposed"]
                # 编造证据的候选被丢弃,只有两条进入候选
                self.assertEqual(len(proposed), 2)
                self.assertEqual(sorted(item["candidate_kind"] for item in proposed), ["commitment", "entity"])
                stats = analysis["extraction_stats"][stored["source_id"]]
                self.assertEqual(stats["dropped_fabricated_evidence"], 1)
                # 候选仍是 propose-only,等待人确认
                self.assertTrue(all(item["status"] == "proposed" for item in proposed))
                # 发送的请求带结构化提取系统提示与原文材料
                sent = captured[0]["body"]
                self.assertEqual(sent["model"], "test-model")
                self.assertIn("只输出 JSON", sent["messages"][0]["content"])
                self.assertIn(source_text, sent["messages"][1]["content"])
            finally:
                app.close()

    def test_api_key_not_in_product_failure_reason(self) -> None:
        secret = "sk-secret-PRODUCT-KEY"
        with tempfile.TemporaryDirectory() as tmp:
            with fake_server({"error": "boom"}, status=500) as (_, base):
                app = NoetideApp(tmp)
                app.update_settings({
                    "model_mode": "local",
                    "model_endpoint": base + "/v1/chat/completions",
                    "model_api_key": secret,
                })
                app.ingest_text("今天和小明聊了识海项目。")
                analysis = app.analyze_sources()
            try:
                self.assertEqual(analysis["candidates_proposed"], [])
                reason = analysis["rejected_outputs"][0]["reason"]
                self.assertTrue(reason.startswith("model_call_failed:"))
                self.assertNotIn(secret, reason)
            finally:
                app.close()

    def test_red_line_source_denied_on_cloud_without_grant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            # 命中财务红线关键词,source 带 finance compartment
            app.ingest_text("我的工资和存款记录,每月余额明细。")
            app.update_settings({
                "model_mode": "cloud",
                "model_provider": "openai",
                "model_endpoint": "https://example.invalid/v1/chat/completions",
                "model_api_key": "sk-secret-CLOUD-KEY",
            })
            analysis = app.analyze_sources()
            try:
                self.assertEqual(analysis["candidates_proposed"], [])
                reasons = [item["reason"] for item in analysis["rejected_outputs"]]
                self.assertEqual(reasons, ["cloud_denied:red_line_denied"])
                # 红线 source 在创建任何 grant 之前即拒绝,不留授权记录
                self.assertEqual(app.store.ledger_records_of_type("product_cloud_grant"), [])
                audits = app.store.ledger_records_of_type("cloud_audit")
                self.assertTrue(any(
                    record.get("event_type") == "send_denied" and record.get("reason") == "red_line_denied"
                    for record in audits
                ))
            finally:
                app.close()

    def test_offline_role_relation_and_year_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("王丽是星河项目的创始人。公司在2020年成立。")
            analysis = app.analyze_sources()
            try:
                proposed = analysis["candidates_proposed"]
                entities = {
                    (item["payload"].get("entity_kind"), item["payload"].get("canonical_label"))
                    for item in proposed if item["candidate_kind"] == "entity"
                }
                self.assertIn(("person", "王丽"), entities)
                self.assertIn(("project", "星河项目"), entities)
                relations = [
                    item for item in proposed
                    if item["candidate_kind"] == "assertion" and item["payload"].get("predicate") == "创始人"
                ]
                self.assertTrue(relations)
                self.assertEqual(relations[0]["payload"]["subject_ref"], "王丽")
                episodes = [item for item in proposed if item["candidate_kind"] == "episode"]
                self.assertTrue(any(item["payload"]["valid_time"]["value"] == "2020年" for item in episodes))
            finally:
                app.close()


class DocxImportTests(unittest.TestCase):
    def test_ingest_folder_docx_and_broken_docx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "inbox"
            root.mkdir()
            (root / "notes.md").write_text("普通笔记。", encoding="utf-8")
            (root / "report.docx").write_bytes(_make_docx(["第一段文字。", "第二段文字。"]))
            (root / "broken.docx").write_bytes(b"this is not a zip at all")
            app = NoetideApp(Path(tmp) / "data")
            report = app.ingest_folder(root)
            try:
                self.assertEqual(report["stored"], 2)
                self.assertEqual(report["rejected"], 1)
                self.assertEqual(report["rejections"][0]["failure"], "docx_unreadable")
                source = app.get_source(next(
                    item["source_id"] for item in report["receipts"]
                    if item["relative_path"] == "report.docx"
                ))
                self.assertIn("第一段文字。", source["content"])
                self.assertIn("第二段文字。", source["content"])
                # w:p 分段映射为换行
                self.assertIn("\n", source["content"])
            finally:
                app.close()

    def test_folder_importer_docx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "vault_in"
            root.mkdir()
            (root / "diary.docx").write_bytes(_make_docx(["识海导入测试段落。"]))
            (root / "junk.docx").write_bytes(b"\xff\xfe not zip")
            app = NoetideApp(Path(tmp) / "data")
            importer = FolderImporter(app.store, "2026-08-07T00:00:00+00:00")
            report = importer.import_folder(root)
            try:
                self.assertEqual(report["stored"], 1)
                self.assertEqual(report["rejected"], 1)
                self.assertEqual(report["rejections"][0]["failure"], "docx_unreadable")
                source_id = report["receipts"][0]["source_id"]
                source = app.get_source(source_id)
                self.assertIn("识海导入测试段落。", source["inline_content"])
            finally:
                app.close()


if __name__ == "__main__":
    unittest.main()
