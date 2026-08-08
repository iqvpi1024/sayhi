"""问识海(产品问答)语义测试:诚实回答、零写入、Derived-only 拒绝、路由冒烟。"""

from __future__ import annotations

import contextlib
import hashlib
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from noetide_micro.product import NoetideApp
from noetide_micro.product_server import ProductHttpServer


def _library_digest(app: NoetideApp) -> str:
    """产品库语义无损摘要:权威层快照 + 派生投影 + 候选账本。"""
    material = {
        "snapshot": app.store.portability_snapshot(),
        "projections": app.store.projection_records(),
        "candidates": app.list_candidates(),
    }
    payload = json.dumps(material, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _confirm_assertions(app: NoetideApp) -> list[dict]:
    app.analyze_sources()
    confirmed = []
    for candidate in app.list_candidates():
        if candidate["candidate_kind"] == "assertion":
            confirmed.append(app.confirm_candidate(candidate["candidate_id"]))
    return confirmed


class ProductAskTests(unittest.TestCase):
    def test_answer_with_confirmed_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            ingested = app.ingest_text("小明是识海项目的CEO。")
            confirmed = _confirm_assertions(app)
            self.assertTrue(confirmed)
            result = app.ask("识海项目的 CEO 是谁?")
            self.assertEqual(result["answer_status"], "answered")
            self.assertIn("识海", result["answer_text"])
            self.assertTrue(result["coverage"]["covered"])
            self.assertTrue(result["evidence"])
            entry = result["evidence"][0]
            self.assertEqual(entry["source_id"], ingested["source_id"])
            self.assertEqual(entry["object_id"], confirmed[0]["object_id"])
            self.assertEqual(entry["verified_scope"], "statement_occurrence")
            self.assertIn("statement_occurrence_confirmed", result["coverage"]["reason_codes"])
            self.assertEqual(result["freshness"]["status"], "current")
            self.assertIn("不代表识海核实", result["confidence_note"])
            app.close()

    def test_no_evidence_honest_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("小明是识海项目的CEO。")
            _confirm_assertions(app)
            result = app.ask("火星基地的建设进度如何?")
            self.assertEqual(result["answer_status"], "no_coverage")
            self.assertIn("不知道", result["answer_text"])
            self.assertEqual(result["evidence"], [])
            self.assertEqual(result["coverage"]["covered"], [])
            self.assertTrue(result["coverage"]["not_covered"])
            self.assertEqual(result["freshness"]["status"], "not_applicable")
            app.close()

    def test_empty_question_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            with self.assertRaises(ValueError):
                app.ask("   ")
            app.close()

    def test_ask_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("小明是识海项目的CEO。")
            _confirm_assertions(app)
            before_digest = _library_digest(app)
            before_revision = app.store.current_revision()
            db_path = app.db_path
            before_bytes = hashlib.sha256(db_path.read_bytes()).hexdigest()
            app.ask("识海项目的 CEO 是谁?")
            app.ask("火星基地的建设进度如何?")
            self.assertEqual(_library_digest(app), before_digest)
            self.assertEqual(app.store.current_revision(), before_revision)
            self.assertEqual(hashlib.sha256(db_path.read_bytes()).hexdigest(), before_bytes)
            app.close()

    def test_derived_only_evidence_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            # 有原始资料和 Derived 投影,但没有任何已确认记忆:派生证据不足为凭(AS-008)
            app.ingest_text("小明是识海项目的CEO。")
            self.assertEqual(app.overview()["canonical"], 0)
            result = app.ask("识海项目的 CEO 是谁?")
            self.assertEqual(result["answer_status"], "no_coverage")
            self.assertIn("不知道", result["answer_text"])
            self.assertIn("derived_evidence_forbidden", result["coverage"]["reason_codes"])
            self.assertTrue(
                any("派生" in note for note in result["coverage"]["not_covered"]),
                msg=str(result["coverage"]["not_covered"]),
            )
            app.close()

    def test_api_ask_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("小明是识海项目的CEO。")
            _confirm_assertions(app)
            server = ProductHttpServer(app, ("127.0.0.1", 0))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                port = server.server_address[1]
                payload = json.dumps({"question": "识海项目的 CEO 是谁?"}).encode("utf-8")
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/ask",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                response = json.loads(urllib.request.urlopen(req, timeout=5).read().decode("utf-8"))
                self.assertEqual(response["status"], "ok")
                self.assertEqual(response["data"]["answer_status"], "answered")
                self.assertTrue(response["data"]["evidence"])

                bad = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/ask",
                    data=json.dumps({}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(bad, timeout=5)
                self.assertEqual(caught.exception.code, 400)
                body = json.loads(caught.exception.read().decode("utf-8"))
                self.assertEqual(body["reason"], "question_required")

                with self.assertRaises(urllib.error.HTTPError) as caught_get:
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ask", timeout=5)
                self.assertEqual(caught_get.exception.code, 404)
            finally:
                server.shutdown()
                server.server_close()
                app.close()

    def test_subject_only_match_is_no_coverage(self) -> None:
        """2026-08-08 真实用户测试发现:只命中问题主体的记忆不得作为回答依据。

        “雷军的血型是什么?”不能拿“雷军是劳模”来答——主体相同但谓词无覆盖。
        """
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("雷军被业界公认为劳模,以高强度工作著称。")
            _confirm_assertions(app)
            result = app.ask("雷军的血型是什么?")
            self.assertEqual(result["answer_status"], "no_coverage")
            self.assertIn("不知道", result["answer_text"])
            self.assertEqual(result["evidence"], [])
            app.close()

    def test_entity_memory_can_answer(self) -> None:
        """问识海覆盖已确认的 entity/episode/commitment,不只 assertion。"""
        with tempfile.TemporaryDirectory() as tmp:
            app = NoetideApp(tmp)
            app.ingest_text("小米集团由雷军于2010年创立,2018年在港股上市。")
            app.analyze_sources()
            confirmed = [app.confirm_candidate(c["candidate_id"]) for c in app.list_candidates()]
            self.assertTrue(confirmed)
            result = app.ask("小米是哪一年创立的?")
            self.assertEqual(result["answer_status"], "answered")
            self.assertIn("2010", result["answer_text"])
            app.close()


# -- 本地向量召回(ask_retrieval=embedding) ------------------------------------

_EMBED_GROUPS = ["创立创办成立", "小米", "雷军劳模", "年份"]


def _fake_embed(text: str) -> list[float]:
    """确定性假向量:按语义组计数,同义词(创立/创办)落在同一维度。"""
    return [float(sum(text.count(ch) for ch in group)) for group in _EMBED_GROUPS]


class _FakeEmbedHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        payload = json.dumps({"data": [{"embedding": _fake_embed(text)} for text in body.get("input", [])]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args: object) -> None:
        return


@contextlib.contextmanager
def _embed_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeEmbedHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/v1/chat/completions"
    finally:
        server.shutdown()
        server.server_close()


class EmbeddingRetrievalTests(unittest.TestCase):
    def _app_with_memory(self, tmp: str, endpoint: str) -> NoetideApp:
        app = NoetideApp(tmp)
        app.ingest_text("小米集团由雷军于2010年创立,2018年在港股上市。")
        app.ingest_text("雷军被业界公认为劳模,以高强度工作著称。")
        app.analyze_sources()  # offline 规则提取 + 确认,与检索方式无关
        for candidate in app.list_candidates():
            app.confirm_candidate(candidate["candidate_id"])
        app.update_settings({
            "model_mode": "local",
            "model_endpoint": endpoint,
            "ask_retrieval": "embedding",
        })
        return app

    def test_embedding_recalls_synonym_lexical_misses(self) -> None:
        """"创办年份"字面匹配不到"创立":字面模式诚实 no_coverage,向量模式召回后核对通过。"""
        with tempfile.TemporaryDirectory() as tmp, _embed_server() as endpoint:
            app = self._app_with_memory(tmp, endpoint)
            result = app.ask("小米的创办年份?")
            self.assertEqual(result["answer_status"], "answered")
            self.assertIn("2010", result["answer_text"])
            self.assertEqual(result["coverage"]["retrieval"], "embedding")
            app.update_settings({"ask_retrieval": "lexical"})
            lexical = app.ask("小米的创办年份?")
            self.assertEqual(lexical["answer_status"], "no_coverage")
            self.assertEqual(lexical["coverage"]["retrieval"], "lexical")
            app.close()

    def test_embedding_unavailable_falls_back_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = self._app_with_memory(tmp, "http://127.0.0.1:1/v1/chat/completions")
            result = app.ask("小米的创办年份?")
            self.assertEqual(result["coverage"]["retrieval"], "embedding_unavailable_fallback_lexical")
            self.assertIn(result["answer_status"], ("answered", "no_coverage"))
            app.close()

    def test_embedding_never_used_in_cloud_mode(self) -> None:
        """隐私边界:cloud 模式即使开了 ask_retrieval=embedding 也不用向量——记忆文本不出网。"""
        with tempfile.TemporaryDirectory() as tmp, _embed_server() as endpoint:
            app = self._app_with_memory(tmp, endpoint)
            app.update_settings({"model_mode": "cloud"})
            result = app.ask("小米的创办年份?")
            self.assertEqual(result["coverage"]["retrieval"], "lexical")
            app.close()

if __name__ == "__main__":    unittest.main()
