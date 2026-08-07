"""Y2-S3 local Web UI: loopback-only stdlib HTTP server and read/derived API.

The Web module never calls SemanticStore write methods directly. Source intake
delegates to LocalMicroRuntime.intake; canonical writes delegate to the verified
approve/publish/revert path; export is request-time Derived; backup writes only
to the server-configured backup_dir.
"""

from __future__ import annotations

import ast
import hashlib
import http.server
import ipaddress
import json
import os
import re
import secrets
import socket
import sys
import threading
from pathlib import Path
from typing import Any

from .app_shell import FORBIDDEN_WRITE_METHODS, render_impact_preview, render_review
from .pack_backup import create_backup, render_markdown
from .runtime import LocalMicroRuntime, open_runtime

JsonObject = dict[str, Any]

HOME_TITLE = "识海本地整理"
BACKUP_FILENAME = "web_backup_001.nobak"
PUBLISH_KEY = "web_publish_001"
REVERT_KEY = "web_revert_001"
# 备份密钥环境变量名；本切片为合成演示，密钥不再使用源码常量，
# 未设置环境变量时在 backup_dir 下持久化一份随机密钥（.web_backup_key）。
BACKUP_KEY_ENV = "NOETIDE_WEB_BACKUP_KEY"
SOURCE_ID = "src_micro_001"
CHANGESET_ID = "changeset_micro_001"
RECORD_RECEIPT_ID = "receipt_source_micro_001"
PUBLISH_RECEIPT_ID = "receipt_publish_001"
COMPENSATION_RECEIPT_ID = "receipt_compensation_001"
APPROVE_ACTOR = "person_alpha"
EXPORT_FILES = ("markdown/sources.md", "markdown/canonical.md", "markdown/ledger.md")
FORBIDDEN_VISIBLE_TERMS = ("ChangeSet", "Projection", "Revision")

_WRITE_CALL = re.compile(r"\.([a-z_][a-z0-9_]*)\s*\(")
_MALFORMED = object()

_VISIBLE_ACTIONS = (
    ("record", "记录一条示例材料"),
    ("review", "生成整理建议"),
    ("confirm", "确认这次整理"),
    ("views", "查看当前视图"),
    ("revert", "撤销这次整理"),
    ("history", "查看操作历史"),
    ("export", "导出为可读副本"),
    ("backup", "创建本地备份"),
)

_HOME_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: #f6f7f9; color: #1f2933; font-family: system-ui, "Microsoft YaHei", sans-serif; }
.page { max-width: 860px; margin: 0 auto; padding: 32px 20px 56px; }
header { border-bottom: 1px solid #d9dee3; padding-bottom: 18px; margin-bottom: 24px; }
h1 { margin: 0 0 6px; font-size: 28px; line-height: 1.25; }
header p { margin: 0; color: #52606d; }
.actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
button.action { min-height: 48px; border: 1px solid #b7c3cc; border-radius: 6px; background: #ffffff; color: #102a43; font-size: 15px; cursor: pointer; }
button.action:hover { border-color: #268e8c; background: #f0fbfa; }
.result { margin-top: 24px; border-top: 1px solid #d9dee3; padding-top: 18px; min-height: 72px; color: #3e4c59; line-height: 1.7; }
@media (max-width: 480px) { .actions { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main class="page">
<header><h1>__TITLE__</h1><p>本机离线整理工具</p></header>
<section class="actions" aria-label="常用操作">
__ACTIONS__
</section>
<section class="result" aria-live="polite" id="result"><span id="message">选择上方操作开始。</span></section>
</main>
<script>
const message = document.getElementById("message");
const labels = {"active": "有联系", "no_contact": "无联系"};
async function run(action) {
  const posts = {"record": 1, "review": 1, "confirm": 1, "revert": 1, "backup": 1};
  const init = posts[action]
    ? {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"}
    : {method: "GET"};
  const response = await fetch("/api/" + action, init);
  const data = await response.json();
  if (!response.ok || data.status !== "ok") {
    message.textContent = "操作未完成，请按顺序尝试。";
    return;
  }
  if (action === "record") message.textContent = "已记录一条示例材料";
  if (action === "review") message.textContent = data.review.summary_text + " " + data.preview.impact_text;
  if (action === "confirm") message.textContent = "已确认这次整理";
  if (action === "views") message.textContent = "当前联系状态：" + labels[data.person_card.contact_state] + "；历史记录 " + data.relationship_timeline.history_count + " 条。";
  if (action === "history") message.textContent = data.events.map(function (event) { return event.label; }).join("；");
  if (action === "revert") message.textContent = "已撤销这次整理";
  if (action === "export") message.textContent = "可读副本已生成（" + data.files.length + " 个文件）";
  if (action === "backup") message.textContent = "本地备份已创建";
}
document.querySelectorAll("[data-action]").forEach(function (button) {
  button.addEventListener("click", function () { run(button.getAttribute("data-action")); });
});
</script>
</body>
</html>
"""


def render_home() -> str:
    actions = "\n".join(
        f'<button type="button" class="action" data-action="{name}" data-copy="{label}">{label}</button>'
        for name, label in _VISIBLE_ACTIONS
    )
    return _HOME_TEMPLATE.replace("__TITLE__", HOME_TITLE).replace("__ACTIONS__", actions)


def _validate_loopback_host(host: str) -> None:
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError("local web server requires a literal loopback host") from exc
    if not address.is_loopback:
        raise ValueError("local web server requires a literal loopback host")


class NoetideLocalHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, service: "WebService", server_address: tuple[str, int]) -> None:
        self.service = service
        self._serve_started = threading.Event()
        self.address_family = socket.AF_INET6 if ":" in server_address[0] else socket.AF_INET
        super().__init__(server_address, LocalWebHandler)

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        self._serve_started.set()
        return super().serve_forever(poll_interval)


class LocalWebHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "NoetideLocal"
    sys_version = ""

    def log_message(self, format: str, *args: Any) -> None:
        return None

    def send_response(self, code: int, message: str | None = None) -> None:
        self.log_request(code)
        self.send_response_only(code, message)

    def do_GET(self) -> None:
        self._route("GET")

    def do_POST(self) -> None:
        self._route("POST")

    def _route(self, method: str) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/" and method == "GET":
            body = render_home().encode("utf-8")
            self._send_bytes(200, "text/html; charset=utf-8", body)
            return
        if path.startswith("/api/"):
            action = path[len("/api/"):]
            if method == "GET" and action in ("views", "history", "export"):
                status, payload = self.server.service.handle_get(action)
                self._send_json(status, payload)
                return
            if method == "POST" and action in ("record", "review", "confirm", "revert", "backup"):
                body = self._read_body()
                status, payload = self.server.service.handle_post(action, body)
                self._send_json(status, payload)
                return
        self._send_json(404, {"status": "rejected", "reason": "not_found"})

    def _read_body(self) -> Any:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            return _MALFORMED
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            return _MALFORMED
        raw = self.rfile.read(max(0, length))
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _MALFORMED

    def _send_json(self, status: int, payload: JsonObject) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self._send_bytes(status, "application/json; charset=utf-8", body)

    def _send_bytes(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)


class WebService:
    def __init__(
        self,
        runtime: LocalMicroRuntime,
        backup_dir: str | Path,
        host: str = "127.0.0.1",
        port: int = 0,
        autostart: bool = True,
    ) -> None:
        _validate_loopback_host(host)
        self.runtime = runtime
        self.backup_dir = Path(backup_dir)
        self.host = host
        self.port = port
        self._server: NoetideLocalHTTPServer | None = None
        self._closed = False
        if autostart:
            self.start()

    def start(self) -> None:
        if self._server is not None:
            raise RuntimeError("local web server is already started")
        self._server = NoetideLocalHTTPServer(self, (self.host, self.port))
        self.port = self._server.server_address[1]
        thread = threading.Thread(target=self._serve, name="noetide-local-web-serve", daemon=True)
        thread.start()

    def _serve(self) -> None:
        if self._server is not None:
            self._server.serve_forever(poll_interval=0.05)

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        if self._server is None:
            raise RuntimeError("local web server is not started")
        self._server.serve_forever(poll_interval)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        server = self._server
        if server is None:
            return
        if server._serve_started.is_set():
            server.shutdown()
        server.server_close()
        self._server = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def handle_get(self, action: str) -> tuple[int, JsonObject]:
        if action == "views":
            return self._views()
        if action == "history":
            return self._history()
        if action == "export":
            return self._export()
        return 404, {"status": "rejected", "reason": "not_found"}

    def handle_post(self, action: str, body: Any) -> tuple[int, JsonObject]:
        if body is _MALFORMED:
            return 400, {"status": "rejected", "reason": "malformed_json"}
        if action == "record":
            return self._record()
        if action == "review":
            return self._review()
        if action == "confirm":
            return self._confirm()
        if action == "revert":
            return self._revert()
        if action == "backup":
            return self._backup(body)
        return 404, {"status": "rejected", "reason": "not_found"}

    def _record(self) -> tuple[int, JsonObject]:
        receipt = self.runtime.intake()
        if receipt["status"] not in {"stored", "duplicate"}:
            return 400, {"status": "rejected", "reason": receipt.get("failure", "record_rejected")}
        return 200, {"status": "ok", "source_id": receipt["source_id"], "receipt_id": receipt["receipt_id"]}

    def _review(self) -> tuple[int, JsonObject]:
        if self.runtime.source(SOURCE_ID) is None:
            return 409, {"status": "rejected", "reason": "record_first"}
        try:
            proposal = self.runtime.propose(SOURCE_ID)
            labels = self._participant_labels()
            review = render_review(proposal, labels)
            preview = render_impact_preview(proposal)
        except (KeyError, RuntimeError, ValueError):
            return 409, {"status": "rejected", "reason": "record_first"}
        return 200, {"status": "ok", "review": review, "preview": preview}

    def _confirm(self) -> tuple[int, JsonObject]:
        if self.runtime.changeset(CHANGESET_ID) is None:
            return 409, {"status": "rejected", "reason": "review_first"}
        try:
            self.runtime.approve(CHANGESET_ID, APPROVE_ACTOR)
            receipt = self.runtime.publish(CHANGESET_ID, PUBLISH_KEY)
        except (KeyError, RuntimeError, ValueError):
            return 409, {"status": "rejected", "reason": "review_first"}
        if receipt.get("status") != "published":
            return 409, {"status": "rejected", "reason": "publish_rejected"}
        return 200, {
            "status": "ok",
            "publish_status": receipt["status"],
            "published_revision": receipt["published_revision"],
            "receipt_id": receipt["receipt_id"],
        }

    def _revert(self) -> tuple[int, JsonObject]:
        changeset = self.runtime.changeset(CHANGESET_ID)
        if changeset is None or changeset.get("status") != "published":
            return 409, {"status": "rejected", "reason": "confirm_first"}
        try:
            receipt = self.runtime.revert(CHANGESET_ID, REVERT_KEY)
        except (KeyError, RuntimeError, ValueError):
            return 409, {"status": "rejected", "reason": "confirm_first"}
        if receipt.get("status") != "published":
            return 409, {"status": "rejected", "reason": "revert_rejected"}
        return 200, {
            "status": "ok",
            "revert_status": receipt["status"],
            "compensation_revision": receipt["compensation_revision"],
            "receipt_id": receipt["receipt_id"],
        }

    def _views(self) -> tuple[int, JsonObject]:
        card = self.runtime.view("person_card")["payload"]
        timeline = self.runtime.view("relationship_timeline")["payload"]
        return 200, {
            "status": "ok",
            "person_card": {"contact_state": card["contact_state"]},
            "relationship_timeline": {
                "current_contact_state": timeline["current_contact_state"],
                "history_count": len(timeline["history"]),
            },
        }

    def _history(self) -> tuple[int, JsonObject]:
        events: list[JsonObject] = []
        if self.runtime.store.append_receipt(RECORD_RECEIPT_ID) is not None:
            events.append(
                {
                    "action": "record",
                    "label": "已记录一条示例材料",
                    "source_id": SOURCE_ID,
                    "receipt_id": RECORD_RECEIPT_ID,
                }
            )
        publish_receipt = self.runtime.store.ledger_record(PUBLISH_RECEIPT_ID)
        if publish_receipt is not None and publish_receipt.get("status") == "published":
            events.append(
                {
                    "action": "confirm",
                    "label": "已确认这次整理",
                    "changeset_id": CHANGESET_ID,
                    "receipt_id": PUBLISH_RECEIPT_ID,
                }
            )
        compensation_receipt = self.runtime.store.ledger_record(COMPENSATION_RECEIPT_ID)
        if compensation_receipt is not None and compensation_receipt.get("status") == "published":
            events.append(
                {
                    "action": "revert",
                    "label": "已撤销这次整理",
                    "changeset_id": CHANGESET_ID,
                    "receipt_id": COMPENSATION_RECEIPT_ID,
                }
            )
        return 200, {"status": "ok", "events": events}

    def _export(self) -> tuple[int, JsonObject]:
        snapshot = self.runtime.store.portability_snapshot()
        markdown = render_markdown(snapshot)
        return 200, {
            "status": "ok",
            "data_revision": snapshot["data_revision"],
            "files": list(EXPORT_FILES),
            "markdown": markdown,
            "read_only": True,
        }

    def _backup_key(self) -> str:
        """备份密钥：优先环境变量，否则生成并持久化随机密钥；禁止用源码常量当密钥。"""
        env_key = os.environ.get(BACKUP_KEY_ENV)
        if env_key:
            return env_key
        key_path = self.backup_dir / ".web_backup_key"
        try:
            if key_path.is_file():
                stored = key_path.read_text(encoding="utf-8").strip()
                if stored:
                    return stored
        except OSError:
            pass
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        generated = secrets.token_urlsafe(24)
        key_path.write_text(generated, encoding="utf-8")
        return generated

    def _backup(self, body: Any) -> tuple[int, JsonObject]:
        if not isinstance(body, dict) or body:
            return 409, {"status": "rejected", "reason": "path_not_allowed"}
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / BACKUP_FILENAME
        if backup_path.exists():
            return 409, {"status": "rejected", "reason": "backup_exists"}
        db_path = self.runtime.data_dir / "noetide.sqlite3"
        try:
            result = create_backup(
                db_path,
                key=self._backup_key(),
                backup_path=backup_path,
                created_at=self.runtime.fixture["determinism"]["clock"],
            )
        except OSError:
            return 500, {"status": "rejected", "reason": "backup_failed"}
        if result.get("outcome") != "created":
            return 409, {"status": "rejected", "reason": "backup_rejected"}
        db_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()
        return 200, {
            "status": "ok",
            "backup_id": backup_path.name,
            "backup_file_exists": backup_path.is_file(),
            "source_db_sha256_matches": result["receipt"]["source_db_sha256"] == db_sha,
            "created_at": self.runtime.fixture["determinism"]["clock"],
        }

    def _participant_labels(self) -> list[str]:
        relationship = self.runtime.store.canonical_object("rel_alpha_beta")
        return [
            self.runtime.store.canonical_object(ref)["canonical_label"]
            for ref in relationship["participant_refs"]
        ]


def web_write_scan(module_path: str | Path | None = None) -> tuple[list[str], list[str]]:
    path = Path(module_path) if module_path else Path(__file__).resolve()
    source = path.read_text(encoding="utf-8")
    called = sorted(set(_WRITE_CALL.findall(source)))
    forbidden = [name for name in called if name in FORBIDDEN_WRITE_METHODS]
    allowed = [name for name in called if name not in FORBIDDEN_WRITE_METHODS]
    return allowed, forbidden


def static_stdlib_scan(module_path: str | Path | None = None) -> tuple[list[str], list[str]]:
    path = Path(module_path) if module_path else Path(__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue
            if node.module:
                imported.add(node.module.split(".", 1)[0])
    external = sorted(name for name in imported if name not in sys.stdlib_module_names)
    return sorted(imported), external


def serve_local_web(
    data_dir: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    backup_dir: str | Path | None = None,
) -> int:
    data_root = Path(data_dir)
    runtime = open_runtime(data_root)
    service = WebService(
        runtime,
        backup_dir=Path(backup_dir) if backup_dir is not None else data_root / "backups",
        host=host,
        port=port,
        autostart=False,
    )
    print(f"本地整理服务已启动：http://{host}:{service.port}", flush=True)
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("已停止本地整理服务", file=sys.stderr)
    finally:
        service.close()
        runtime.close()
    return 0