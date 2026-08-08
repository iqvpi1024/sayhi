"""Noetide product HTTP/API/MCP service for desktop, cloud and phone access."""

from __future__ import annotations

import hmac
import hashlib
import http.server
import ipaddress
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Mapping

from . import __version__ as NOETIDE_VERSION
from .mcp_runtime import CONTRACT_VERSION as MCP_CONTRACT_VERSION, TOOL_DESCRIPTORS as MCP_TOOL_DESCRIPTORS
from .product import NoetideApp, utc_now

JsonObject = dict[str, Any]
APP_HTML_NAME = "webui.html"
_MAX_BODY_BYTES = 1 << 20  # 请求体上限 1 MiB，防止内存耗尽
_LOOPBACK_NAMES = frozenset({"localhost"})
# 标准 MCP 协议 initialize 握手回的 serverInfo 版本:单一来源 = 包 __version__
# (与 pyproject.toml 同步;2026-08-08 起不再单独手工维护)
MCP_SERVER_VERSION = NOETIDE_VERSION


def _split_host(value: str) -> str:
    """去掉 Host/Origin 主机部分的端口，兼容 IPv6 方括号写法。"""
    value = value.strip()
    if value.startswith("["):
        end = value.find("]")
        return value[1:end] if end != -1 else value
    if value.count(":") == 1:
        host, _, port = value.rpartition(":")
        if port.isdigit():
            return host
    return value


def _is_loopback_host(value: str) -> bool:
    host = _split_host(value).lower()
    if host in _LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class ProductHttpHandler(http.server.BaseHTTPRequestHandler):
    server_version = "NoetideProduct"

    def _json(self, status: int, payload: Any, extra_headers: Mapping[str, str] | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> Any:
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            return {"_malformed": True}
        if length < 0 or length > _MAX_BODY_BYTES:
            return {"_too_large": True}
        raw = self.rfile.read(max(0, length))
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {"_malformed": True}

    def _remote_mode(self) -> bool:
        settings = self.server.app.public_settings()
        return bool(settings.get("remote_access")) and bool(settings.get("api_token"))

    def _request_origin_allowed(self) -> bool:
        """回环服务只接受回环 Host/Origin；remote_access+token 模式下放宽，由令牌认证兜底。"""
        if self._remote_mode():
            return True
        host = self.headers.get("Host") or ""
        if not host or not _is_loopback_host(host):
            return False
        origin = self.headers.get("Origin")
        if origin:
            origin_host = urllib.parse.urlparse(origin).hostname or ""
            if not _is_loopback_host(origin_host):
                return False
        return True

    def _authorized(self) -> bool:
        settings = self.server.app.public_settings()
        if not settings.get("remote_access"):
            return True
        token = settings.get("api_token") or ""
        if not token:
            return False
        header = self.headers.get("Authorization") or ""
        return hmac.compare_digest(header, "Bearer " + token) or hmac.compare_digest(header, "Token " + token)

    def _route_api(self, method: str, path: str, body: Any) -> tuple[int, JsonObject]:
        app = self.server.app
        if path == "/api/health":
            return 200, {"status": "ok", "app": "noetide", "version": "1.0"}
        if path == "/" or path.startswith("/static/"):
            return 404, {"status": "rejected", "reason": "not_found"}
        if not self._authorized():
            return 401, {"status": "rejected", "reason": "unauthorized"}
        parsed = urllib.parse.urlparse(path)
        path_only = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        segments = [seg for seg in path_only.split("/") if seg]
        try:
            if method == "GET":
                if path_only == "/api/overview":
                    return 200, {"status": "ok", "data": app.overview()}
                if path_only == "/api/sources":
                    return 200, {"status": "ok", "sources": app.list_sources()}
                if path_only == "/api/objects":
                    object_type = query.get("type", [None])[0]
                    return 200, {"status": "ok", "objects": app.list_objects(object_type)}
                if path_only == "/api/candidates":
                    status = query.get("status", [None])[0]
                    return 200, {"status": "ok", "candidates": app.list_candidates(status)}
                if path_only == "/api/search":
                    return 200, {"status": "ok", "data": app.search(query.get("q", [""])[0])}
                if path_only == "/api/timeline":
                    return 200, {"status": "ok", "timeline": app.timeline()}
                if path_only == "/api/settings":
                    return 200, {"status": "ok", "settings": app.public_settings()}
                if path_only == "/api/mcp":
                    return 200, {"status": "ok", "capabilities": app.mcp_capabilities(), "tools": MCP_TOOL_DESCRIPTORS}
                if path_only == "/api/analyze/status":
                    return 200, {"status": "ok", "data": app.analysis_status()}
                if len(segments) == 3 and segments[0] == "api" and segments[1] == "sources":
                    source = app.get_source(segments[2])
                    return (200, {"status": "ok", "source": source}) if source else (404, {"status": "rejected", "reason": "source_not_found"})
                if len(segments) == 3 and segments[0] == "api" and segments[1] == "objects":
                    obj = app.get_object(segments[2])
                    return (200, {"status": "ok", "object": obj}) if obj else (404, {"status": "rejected", "reason": "object_not_found"})
            elif method == "POST":
                if path_only == "/api/ingest/text":
                    if not isinstance(body, dict) or not isinstance(body.get("content"), str):
                        return 400, {"status": "rejected", "reason": "content_required"}
                    result = app.ingest_text(body["content"], body.get("title"), body.get("source_kind"))
                    return 200, {"status": "ok", "data": result}
                if path_only == "/api/ingest/folder":
                    if not isinstance(body, dict) or not isinstance(body.get("path"), str):
                        return 400, {"status": "rejected", "reason": "path_required"}
                    result = app.ingest_folder(body["path"])
                    return 200, {"status": "ok", "data": result}
                if path_only == "/api/analyze":
                    source_ids = body.get("source_ids") if isinstance(body, dict) else None
                    result = app.start_analysis(source_ids)
                    return 200, {"status": "ok", "data": result}
                if path_only == "/api/ask":
                    if not isinstance(body, dict) or not isinstance(body.get("question"), str) or not body["question"].strip():
                        return 400, {"status": "rejected", "reason": "question_required"}
                    return 200, {"status": "ok", "data": app.ask(body["question"])}
                if path_only == "/api/export":
                    return 200, {"status": "ok", "data": app.export_pack()}
                if path_only == "/api/backup":
                    key = body.get("key") if isinstance(body, dict) else None
                    return 200, {"status": "ok", "data": app.backup(key)}
                if path_only == "/api/import":
                    if not isinstance(body, dict) or not isinstance(body.get("path"), str):
                        return 400, {"status": "rejected", "reason": "path_required"}
                    return 200, {"status": "ok", "data": app.import_pack(body["path"])}
                if path_only == "/api/restore":
                    if not isinstance(body, dict) or not isinstance(body.get("path"), str) or not isinstance(body.get("key"), str):
                        return 400, {"status": "rejected", "reason": "path_and_key_required"}
                    return 200, {"status": "ok", "data": app.restore_backup(body["path"], body["key"])}
                if path_only == "/api/settings":
                    if not isinstance(body, dict):
                        return 400, {"status": "rejected", "reason": "settings_required"}
                    return 200, {"status": "ok", "settings": app.update_settings(body)}
                if path_only == "/api/mcp/capability":
                    body = body or {}
                    if isinstance(body.get("spec"), dict):
                        return 200, {"status": "ok", "capability": app.create_mcp_capability(body["spec"])}
                    return 200, {"status": "ok", "capability": app.create_agent_capability(body.get("resource_ids"))}
                if len(segments) == 4 and segments[0] == "api" and segments[1] == "candidates" and segments[3] == "confirm":
                    return 200, {"status": "ok", "candidate": app.confirm_candidate(segments[2], (body or {}).get("actor") or "local_user")}
                if len(segments) == 4 and segments[0] == "api" and segments[1] == "candidates" and segments[3] == "reject":
                    return 200, {"status": "ok", "candidate": app.reject_candidate(segments[2], (body or {}).get("actor") or "local_user")}
            return 404, {"status": "rejected", "reason": "not_found"}
        except (KeyError, ValueError, RuntimeError, OSError) as exc:
            # 细节只进 stderr，不把内部异常信息回给客户端
            print(f"识海 API 请求处理失败：{exc}", file=sys.stderr)
            return 400, {"status": "rejected", "reason": "request_failed"}

    def do_GET(self) -> None:
        if not self._request_origin_allowed():
            self._json(403, {"status": "rejected", "reason": "forbidden_origin"})
            return
        if self.path == "/" or self.path == "/index.html":
            html_path = Path(__file__).with_name(APP_HTML_NAME)
            if not html_path.exists():
                self._json(500, {"status": "rejected", "reason": "web_ui_missing"})
                return
            self._html(html_path.read_bytes())
            return
        status, payload = self._route_api("GET", self.path, None)
        self._json(status, payload)

    def do_POST(self) -> None:
        if not self._request_origin_allowed():
            self._json(403, {"status": "rejected", "reason": "forbidden_origin"})
            return
        body = self._read_body()
        if isinstance(body, dict) and body.get("_too_large"):
            self._json(413, {"status": "rejected", "reason": "body_too_large"})
            return
        if isinstance(body, dict) and body.get("_malformed"):
            self._json(400, {"status": "rejected", "reason": "malformed_json"})
            return
        if self.path == "/mcp":
            if not self._authorized():
                self._json(401, {"jsonrpc": "2.0", "id": body.get("id") if isinstance(body, dict) else None, "error": {"code": -32001, "message": "unauthorized"}})
                return
            if isinstance(body, dict) and isinstance(body.get("params"), dict) and isinstance(body["params"].get("request"), dict):
                # 遗留合同形状(params.request)原样保留,内部工具与测试继续可用
                result = self.server.app.mcp_handle(body["params"]["request"], body["params"].get("payload"))
                self._json(200, {"jsonrpc": "2.0", "id": body.get("id"), "result": result})
                return
            if isinstance(body, dict) and isinstance(body.get("method"), str):
                # 标准 MCP 协议(initialize/tools/list/tools/call/resources/*),
                # 主流 Agent(Claude Code、Codex 等)可直接把 /mcp 配为 MCP server
                self._handle_standard_mcp(body)
                return
            self._json(400, {"jsonrpc": "2.0", "id": body.get("id") if isinstance(body, dict) else None, "error": {"code": -32602, "message": "invalid params"}})
            return
        status, payload = self._route_api("POST", self.path, body)
        self._json(status, payload)

    # -- 标准 MCP 协议层(initialize/tools/list/tools/call/resources/*) --------

    def _handle_standard_mcp(self, body: JsonObject) -> None:
        method = body.get("method")
        msg_id = body.get("id")
        params = body.get("params") if isinstance(body.get("params"), dict) else {}
        if method == "initialize":
            self._json(200, {"jsonrpc": "2.0", "id": msg_id, "result": {
                "protocolVersion": str(params.get("protocolVersion") or "2024-11-05"),
                "capabilities": {"tools": {"listChanged": False}, "resources": {"listChanged": False}},
                "serverInfo": {"name": "noetide", "version": MCP_SERVER_VERSION},
                "instructions": (
                    "识海 Noetide:本地优先的个人记忆中枢。ask_memory 用自然语言查询用户"
                    "已确认的记忆(只读、有证据才答、绝不编造);propose_changeset 提议新记忆,"
                    "由用户在网页上确认后生效;read_resource 读取授权范围内的原始资料。"
                    "默认使用本地默认能力令牌;限定范围时用 X-Noetide-Capability 请求头"
                    "指定 capability_id。"
                ),
            }})
            return
        if method == "ping" or (isinstance(method, str) and method.startswith("notifications/")):
            self._json(200, {"jsonrpc": "2.0", "id": msg_id, "result": {}})
            return
        if method == "tools/list":
            self._json(200, {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": MCP_TOOL_DESCRIPTORS}})
            return
        if method == "resources/list":
            internal = self._standard_call("list_resources", {})
            resource_ids = ((internal.get("payload") or {}).get("resource_ids") or []) if isinstance(internal.get("payload"), dict) else []
            self._json(200, {"jsonrpc": "2.0", "id": msg_id, "result": {
                "resources": [
                    {"uri": f"noetide://source/{sid}", "name": str(sid), "mimeType": "text/plain"}
                    for sid in resource_ids
                ],
            }})
            return
        if method == "resources/read":
            uri = str(params.get("uri") or "")
            prefix = "noetide://source/"
            if not uri.startswith(prefix):
                self._json(200, {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": "unknown resource uri"}})
                return
            internal = self._standard_call("read_resource", {"resource_id": uri[len(prefix):]})
            denied = internal.get("result_status") != "ok"
            text = json.dumps(internal.get("payload"), ensure_ascii=False) if not denied else json.dumps(
                {"denied": (internal.get("error") or {}).get("code")}, ensure_ascii=False)
            self._json(200, {"jsonrpc": "2.0", "id": msg_id, "result": {
                "contents": [{"uri": uri, "mimeType": "application/json", "text": text}],
                "isError": denied,
            }})
            return
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
            known = {tool["name"] for tool in MCP_TOOL_DESCRIPTORS}
            if name not in known:
                self._json(200, {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "unknown tool"}})
                return
            internal = self._standard_call(str(name), arguments)
            denied = internal.get("result_status") not in ("ok", "accepted")
            self._json(200, {"jsonrpc": "2.0", "id": msg_id, "result": {
                "content": [{"type": "text", "text": json.dumps(internal, ensure_ascii=False)}],
                "isError": denied,
            }})
            return
        self._json(200, {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "method not found"}})

    def _standard_call(self, action: str, arguments: Mapping[str, Any]) -> JsonObject:
        """把标准 MCP 调用翻译为内部能力令牌合同:默认本地默认令牌,
        或用 X-Noetide-Capability 请求头指定限定范围的令牌。"""
        app = self.server.app
        capability_id = self.headers.get("X-Noetide-Capability") or ""
        if capability_id:
            capability = next((item for item in app.mcp_capabilities() if item.get("capability_id") == capability_id), None)
            if capability is None:
                return {"result_status": "denied", "error": {"code": "unknown_capability", "message": "unknown capability"}, "payload": "withheld"}
        else:
            capability = app.default_mcp_capability()
        scope_ids = list(capability.get("resource_ids") or [])
        payload: JsonObject = {}
        if action == "read_resource":
            scope_ids = [str(arguments.get("resource_id") or "")]
            payload = {"resource_id": arguments.get("resource_id"), "fields": arguments.get("fields")}
        elif action == "ask_memory":
            payload = {"question": arguments.get("question")}
        elif action == "propose_changeset":
            payload = {"candidate": arguments.get("candidate")}
        elif action == "record_source":
            payload = {"source": arguments.get("source")}
        idem = arguments.get("idempotency_key")
        if not isinstance(idem, str) or not idem:
            # 缺省幂等键按内容哈希派生:网络重试/Agent 重复调用不产生重复写入
            idem = "std_" + hashlib.sha256(
                json.dumps({"action": action, "arguments": dict(arguments)}, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()[:16]
        request = {
            "contract_version": MCP_CONTRACT_VERSION,
            "request_id": "mcp_std_" + idem,
            "caller_ref": capability["actor"],
            "purpose": capability["purpose"],
            "capability_ref": capability["capability_id"],
            "scope": {"resource_ids": scope_ids},
            "requested_at": utc_now(),
            "action": action,
            "idempotency_key": idem,
        }
        return app.mcp_handle(request, payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


class ProductHttpServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, app: NoetideApp, server_address: tuple[str, int]) -> None:
        self.app = app
        super().__init__(server_address, ProductHttpHandler)


def serve_product(
    data_dir: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    settings_path: str | Path | None = None,
) -> int:
    app = NoetideApp(data_dir, settings_path=settings_path)
    if not _is_loopback_host(host):
        settings = app.public_settings()
        if not (settings.get("remote_access") and settings.get("api_token")):
            # 绑定非回环地址会暴露到局域网/公网，必须显式开启 remote_access 并配置 token
            print("拒绝启动：绑定非回环地址需在设置中开启 remote_access 并配置 api_token", file=sys.stderr)
            app.close()
            return 2
    server = ProductHttpServer(app, (host, port))
    actual_port = server.server_address[1]
    print(f"识海已启动：http://{host}:{actual_port}", flush=True)
    print(f"数据目录：{app.data_dir}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("识海已停止", file=sys.stderr)
    finally:
        server.server_close()
        app.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="noetide-product")
    parser.add_argument("--data-dir", default=None, help="data directory")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--settings-path", default=None)
    args = parser.parse_args(argv)
    data_dir = args.data_dir or (Path.home() / ".noetide" / "data")
    return serve_product(data_dir, host=args.host, port=args.port, settings_path=args.settings_path)


if __name__ == "__main__":
    raise SystemExit(main())
