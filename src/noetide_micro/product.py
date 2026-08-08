"""Noetide product runtime: installable local memory application.

Additive product facade over the existing semantic store and MCP runtime.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import secrets
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from . import llm_providers
from .answers import AnswerEvaluator
from .cloud_model import CloudGate
from .folder_import import extract_docx_text
from .mcp_runtime import McpRuntime, SUPPORTED_PROFILE as MCP_PROFILE
from .model_capability import RED_LINE_COMPARTMENTS
from .pack_backup import create_backup, export_markdown_pack, restore_backup
from .portability import ContextPackVerifier
from .store import SemanticStore

JsonObject = dict[str, Any]
MAX_SOURCE_BYTES = 1_000_000
FOLDER_EXTENSIONS = (".md", ".txt", ".json", ".csv", ".docx")
CANDIDATE_KINDS = ("entity", "assertion", "commitment", "episode")
SETTINGS_KEYS = (
    "model_mode", "model_provider", "model_endpoint", "model_api_key", "model_name",
    "remote_access", "remote_host", "port", "api_token", "backup_key", "language",
)
# 产品云端通路复用 Y2-S4 CloudGate:授权门 + 红线门 + 预览门 + 审计账本。
CLOUD_PURPOSE = "organize"
CLOUD_ACTOR = "local_user"
CLOUD_GRANT_RECORD_TYPE = "product_cloud_grant"
CLOUD_GRANT_EXPIRES_AT = "2099-12-31T23:59:59+00:00"
# 最小确定性红线启发式:命中健康/财务关键词的 source 额外标注红线 compartment,
# CloudGate 对红线 compartment 一律拒绝发送(red_line_denied)。
_RED_LINE_KEYWORDS = {
    "health": ("病历", "体检", "诊断", "症状", "用药", "医疗", "疾病"),
    "finance": ("工资", "存款", "债务", "借款", "欠款", "余额", "账单"),
}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _source_content(source: Mapping[str, Any]) -> str:
    value = source.get("content")
    if isinstance(value, str):
        return value
    value = source.get("inline_content")
    return str(value or "")


def _classify_compartments(content: str) -> list[str]:
    """确定性红线标注:健康/财务关键词命中即附加对应红线 compartment。"""
    compartments = ["personal"]
    for compartment in sorted(_RED_LINE_KEYWORDS):
        if any(keyword in content for keyword in _RED_LINE_KEYWORDS[compartment]):
            compartments.append(compartment)
    return compartments


def _is_loopback_host(host: str | None) -> bool:
    if not host:
        return False
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _snippet(text: str, needle: str, radius: int = 80) -> str:
    if not needle:
        return text[:160]
    pos = text.lower().find(needle.lower())
    if pos < 0:
        return text[:160]
    start = max(0, pos - radius)
    end = min(len(text), pos + len(needle) + radius)
    prefix = "..." if start else ""
    suffix = "..." if end < len(text) else ""
    return prefix + text[start:end].replace("\n", " ").strip() + suffix


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。！？!?；;\n]+", text) if part.strip()]

class NoetideApp:
    """Product-level facade over the existing SemanticStore and MCP runtime."""

    def __init__(
        self,
        data_dir: str | Path,
        settings_path: str | Path | None = None,
        now: str | None = None,
    ) -> None:
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path = Path(settings_path).resolve() if settings_path else (self.data_dir / "settings.json")
        self._now = now or utc_now()
        self._store = SemanticStore(self.data_dir / "noetide.sqlite3", check_same_thread=False)
        self._ensure_initialized()
        self._settings = self._load_settings()
        self._mcp = McpRuntime(self._store, self._now, profile=MCP_PROFILE, policy_available=True)

    def close(self) -> None:
        self._store.close()

    @property
    def store(self) -> SemanticStore:
        return self._store

    @property
    def db_path(self) -> Path:
        return self.data_dir / "noetide.sqlite3"

    def _ensure_initialized(self) -> None:
        try:
            self._store.current_revision()
        except RuntimeError:
            self._store.add_revision("rev_000", self._now, "seed")
            self._store.upsert_projection(
                "product_overview",
                "rev_000",
                "rev_000",
                "fresh",
                {"revision": "rev_000", "initialized_at": self._now},
            )
            self._store.put_ledger_record(
                "product_init_000",
                "product_event",
                {"event_type": "product_initialized", "recorded_at": self._now, "data_dir": str(self.data_dir)},
            )
        existing = {record["view_name"] for record in self._store.projection_records()}
        if "product_overview" not in existing:
            revision = self._store.current_revision()
            self._store.upsert_projection("product_overview", revision, revision, "fresh", {"revision": revision})

    def _next_revision(self) -> str:
        # 委托给 store 的全局分配器:非 rev_NNN 格式(如 rev_c1_*)跳过而非崩溃
        return self._store.next_revision()

    def _refresh_projection(self) -> None:
        revision = self._store.current_revision()
        self._store.upsert_projection(
            "product_overview",
            revision,
            revision,
            "fresh",
            self._overview_payload(),
        )
        self.default_mcp_capability()

    def _overview_payload(self) -> JsonObject:
        snapshot = self._store.portability_snapshot()
        candidates = self.list_candidates()
        return {
            "revision": snapshot["data_revision"],
            "sources": len(snapshot["sources"]),
            "canonical": len(snapshot["canonical"]),
            "candidates_pending": sum(1 for item in candidates if item.get("status") == "proposed"),
            "candidates_confirmed": sum(1 for item in candidates if item.get("status") == "confirmed"),
            "updated_at": self._now,
        }

    def _default_settings(self) -> JsonObject:
        return {
            "model_mode": "offline",
            "model_provider": "openai_compatible",
            "model_endpoint": "",
            "model_api_key": "",
            "model_name": "",
            "remote_access": False,
            "remote_host": "127.0.0.1",
            "port": 8765,
            "api_token": "",
            "backup_key": "",
            "language": "zh-CN",
        }

    def _load_settings(self) -> JsonObject:
        defaults = self._default_settings()
        loaded: JsonObject = {}
        if self.settings_path.exists():
            try:
                parsed = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(parsed, dict):
                    loaded = {key: value for key, value in parsed.items() if key in SETTINGS_KEYS}
            except (OSError, json.JSONDecodeError):
                loaded = {}
        merged = {**defaults, **loaded}
        if not merged.get("backup_key"):
            merged["backup_key"] = "noetide-local-" + secrets.token_urlsafe(12)
        if not merged.get("api_token"):
            merged["api_token"] = secrets.token_urlsafe(24)
        self._settings = merged
        self._save_settings()
        return merged

    def _save_settings(self) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(
            json.dumps(self._settings, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def public_settings(self) -> JsonObject:
        public: JsonObject = {}
        for key, value in self._settings.items():
            if key == "model_api_key":
                public[key + "_set"] = bool(value)
            elif key == "backup_key":
                public[key + "_set"] = bool(value)
            elif key == "api_token":
                public[key] = value
            else:
                public[key] = value
        return public

    def update_settings(self, partial: Mapping[str, Any]) -> JsonObject:
        for key, value in partial.items():
            if key not in SETTINGS_KEYS:
                continue
            if key == "api_token" and value is True:
                self._settings[key] = secrets.token_urlsafe(24)
                continue
            if key == "model_api_key" and not isinstance(value, str):
                continue
            self._settings[key] = value
        self._save_settings()
        return self.public_settings()

    # -- ingestion -----------------------------------------------------------

    def _source_payload(self, source_id: str, content: str, title: str, source_kind: str, now: str, locator: JsonObject) -> JsonObject:
        return {
            "source_id": source_id,
            "append_receipt_id": f"receipt_{source_id}",
            "source_kind": source_kind,
            "content_hash": _sha256(content),
            "content": content,
            "inline_content": content,
            "title": title,
            "byte_length": len(content.encode("utf-8")),
            "source_created_at": now,
            "ingested_at": now,
            "locator_scheme": locator.get("scheme", "inline_v1"),
            "locator": locator,
            "coverage_window": {"start": now, "end": now, "continuous": True, "gaps": []},
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared",
            "owner_ref": "local_user",
            "recorder_ref": "local_user",
            "sensitivity": "private",
            "compartments": _classify_compartments(content),
            "third_party_present": "unknown",
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "review_status": "unreviewed",
            "source_timezone": "local",
        }

    def _receipt(self, source: Mapping[str, Any], now: str) -> JsonObject:
        return {
            "receipt_id": source["append_receipt_id"],
            "source_id": source["source_id"],
            "status": "stored",
            "hash_algorithm": "sha256",
            "content_hash": source["content_hash"],
            "byte_length": source["byte_length"],
            "media_type": "text/plain; charset=utf-8",
            "ingested_at": now,
            "locator_scheme": source.get("locator_scheme", "inline_v1"),
            "coverage_raw_status": "present",
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared",
            "effective_policy": {"sensitivity": "private", "compartments": list(source.get("compartments") or ["personal"])},
            "failure": None,
            "actor": "local_user",
        }

    def ingest_text(self, content: str, title: str | None = None, source_kind: str = "note") -> JsonObject:
        content = str(content or "").strip()
        if not content:
            raise ValueError("empty_content")
        if len(content.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise ValueError("content_too_large")
        now = utc_now()
        digest = _sha256(content)
        source_id = "src_p_" + digest[:16]
        existing = self._store.seeded_source(source_id)
        if existing is not None:
            return {"status": "duplicate", "source_id": source_id, "receipt_id": existing.get("append_receipt_id")}
        first_line = next((line.strip() for line in content.splitlines() if line.strip()), content[:60])
        label = title or first_line[:80]
        source = self._source_payload(
            source_id, content, label, f"product_{source_kind}", now,
            {"scheme": "inline_v1", "title": label},
        )
        self._store.append_source(source, self._receipt(source, now))
        self._refresh_projection()
        return {"status": "stored", "source_id": source_id, "receipt_id": source["append_receipt_id"], "title": label}

    def ingest_folder(self, folder_path: str | Path) -> JsonObject:
        root = Path(folder_path).resolve()
        if not root.is_dir():
            raise ValueError("folder_not_found")
        now = utc_now()
        report: JsonObject = {
            "files_seen": 0, "stored": 0, "duplicate": 0, "rejected": 0, "skipped": 0,
            "receipts": [], "rejections": [], "skipped_paths": [],
        }
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_file():
                continue
            report["files_seen"] += 1
            relative = candidate.relative_to(root).as_posix()
            try:
                resolved = candidate.resolve()
            except OSError:
                report["rejected"] += 1
                report["rejections"].append({"entry": relative, "failure": "path_unresolved"})
                continue
            if not _is_within(resolved, root):
                report["rejected"] += 1
                report["rejections"].append({"entry": relative, "failure": "symlink_escape"})
                continue
            if candidate.suffix.lower() not in FOLDER_EXTENSIONS:
                report["skipped"] += 1
                report["skipped_paths"].append(relative)
                continue
            if candidate.suffix.lower() == ".docx":
                try:
                    text = extract_docx_text(candidate.read_bytes())
                except (OSError, ValueError):
                    # 损坏或非 docx 内容:fail-closed 拒绝该文件并计数,不中断整个导入
                    report["rejected"] += 1
                    report["rejections"].append({"entry": relative, "failure": "docx_unreadable"})
                    continue
            else:
                try:
                    text = candidate.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    report["rejected"] += 1
                    report["rejections"].append({"entry": relative, "failure": "unreadable_or_invalid_utf8"})
                    continue
            digest = _sha256(text)
            source_id = "src_p_" + digest[:16]
            existing = self._store.seeded_source(source_id)
            if existing is not None:
                report["duplicate"] += 1
                report["receipts"].append({"relative_path": relative, "status": "duplicate", "source_id": source_id})
                continue
            source = self._source_payload(
                source_id, text, relative, "product_folder", now,
                {"scheme": "file_path_v1", "root_ref": str(root), "relative_path": relative},
            )
            self._store.append_source(source, self._receipt(source, now))
            report["stored"] += 1
            report["receipts"].append({"relative_path": relative, "status": "stored", "source_id": source_id})
        self._refresh_projection()
        return report

    # -- analysis ------------------------------------------------------------

    def list_sources(self) -> list[JsonObject]:
        return [
            {
                "source_id": source["source_id"],
                "source_kind": source.get("source_kind"),
                "title": source.get("title") or source_id_title(source),
                "byte_length": source.get("byte_length"),
                "ingested_at": source.get("ingested_at"),
                "content_hash": source.get("content_hash"),
                "preview": _source_content(source)[:160],
            }
            for source in self._store.portability_snapshot()["sources"]
        ]

    def get_source(self, source_id: str) -> JsonObject | None:
        source = self._store.seeded_source(source_id)
        return dict(source) if source is not None else None

    def analyze_sources(self, source_ids: Iterable[str] | None = None) -> JsonObject:
        if source_ids is None:
            sources = [
                source for source in self._store.portability_snapshot()["sources"]
                if not self._has_candidates(source["source_id"])
            ]
        else:
            ids = [str(item) for item in source_ids]
            sources = [
                source for source in self._store.portability_snapshot()["sources"]
                if source["source_id"] in ids
            ]
        candidates: list[JsonObject] = []
        rejected: list[JsonObject] = []
        extraction_stats: JsonObject = {}
        seen_ids = [source["source_id"] for source in sources]
        mode = self._settings.get("model_mode", "offline")
        for source in sources:
            if mode == "offline":
                items = self._offline_items(source)
                failure = None
                stats: JsonObject = {}
            else:
                items, failure, stats = self._model_items(source)
            if stats:
                extraction_stats[source["source_id"]] = stats
            if failure:
                rejected.append({"source_id": source["source_id"], "reason": failure})
                continue
            for item in items:
                candidate = self._persist_candidate(item, source)
                if candidate is not None:
                    candidates.append(candidate)
        self._refresh_projection()
        result: JsonObject = {
            "batch_id": "batch_p_" + _sha256(_canonical_json({"mode": mode, "sources": seen_ids}))[:16],
            "mode": mode,
            "sources_seen": seen_ids,
            "candidates_proposed": candidates,
            "rejected_outputs": rejected,
        }
        if extraction_stats:
            # 提取统计(含编造证据丢弃计数)随批次返回,供界面诚实呈现
            result["extraction_stats"] = extraction_stats
        return result

    def _has_candidates(self, source_id: str) -> bool:
        return any(
            any(ref.get("source_id") == source_id for ref in candidate.get("evidence_refs", []))
            for candidate in self.list_candidates()
        )

    def _offline_items(self, source: Mapping[str, Any]) -> list[JsonObject]:
        text = _source_content(source)
        items: list[JsonObject] = []
        for sentence in _split_sentences(text):
            for label in _find_persons(sentence):
                items.append({"candidate_kind": "entity", "payload": {"entity_kind": "person", "canonical_label": label, "aliases": [label], "summary": sentence}})
            for label in _find_projects(sentence):
                items.append({"candidate_kind": "entity", "payload": {"entity_kind": "project", "canonical_label": label, "aliases": [label], "summary": sentence}})
            for person, org, role in _find_role_relations(sentence):
                # 人物-项目关系("X 是 Y 的 CEO/创始人/CTO"):人物、项目各一条实体,关系一条断言
                items.append({"candidate_kind": "entity", "payload": {"entity_kind": "person", "canonical_label": person, "aliases": [person], "summary": sentence}})
                items.append({"candidate_kind": "entity", "payload": {"entity_kind": "project", "canonical_label": org, "aliases": [org], "summary": sentence}})
                items.append({"candidate_kind": "assertion", "payload": {"assertion_kind": "personal_statement", "canonical_text": sentence, "subject_ref": person, "predicate": role, "object_ref": org, "summary": sentence}})
            if _is_commitment(sentence):
                items.append({"candidate_kind": "commitment", "payload": {"commitment_kind": "personal_commitment", "statement": sentence, "due_text": _find_due_text(sentence), "responsible_ref": "local_user"}})
            if _is_episode(sentence):
                items.append({"candidate_kind": "episode", "payload": {"episode_kind": "personal_event", "title": sentence[:60], "summary": sentence, "valid_time": _find_time(sentence)}})
            if _is_assertion(sentence):
                items.append({"candidate_kind": "assertion", "payload": {"assertion_kind": "personal_statement", "canonical_text": sentence, "subject_ref": _assertion_subject(sentence), "predicate": _assertion_predicate(sentence), "object_ref": None, "summary": sentence}})
            if len(items) >= 40:
                break
        return items

    def _model_items(self, source: Mapping[str, Any]) -> tuple[list[JsonObject], str | None, JsonObject]:
        provider = str(self._settings.get("model_provider") or "openai_compatible").strip()
        # endpoint 为空时回落到提供商预置缺省端点(如 anthropic/gemini 官方地址)
        endpoint = str(self._settings.get("model_endpoint") or "").strip() or llm_providers.default_endpoint(provider)
        if not endpoint:
            return [], "model_endpoint_missing", {}
        parsed = urllib.parse.urlparse(endpoint)
        mode = self._settings.get("model_mode")
        if mode == "local":
            if parsed.scheme != "http":
                return [], "local_endpoint_must_be_http", {}
            if not _is_loopback_host(parsed.hostname):
                return [], "local_endpoint_must_be_loopback", {}
        if mode == "cloud" and parsed.scheme != "https":
            return [], "cloud_endpoint_must_be_https", {}
        gate: CloudGate | None = None
        grant_ref = ""
        preview_id: str | None = None
        if mode == "cloud":
            gate, grant_ref, preview_id, failure = self._cloud_authorize(source, endpoint)
            if failure is not None:
                return [], failure, {}
        source_text = _source_content(source)
        api_key = str(self._settings.get("model_api_key") or "").strip()
        model = str(self._settings.get("model_name") or "").strip()
        messages = [
            {"role": "system", "content": llm_providers.EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": llm_providers.build_extraction_prompt(source_text)},
        ]
        try:
            raw = llm_providers.chat_completion(provider, endpoint, api_key, model, messages, timeout=15)
        except Exception as exc:
            message = str(exc)
            if api_key:
                # 双保险:适配层已脱敏,这里再确保 api_key 不进失败原因/审计
                message = message.replace(api_key, "***")
            if gate is not None:
                self._cloud_audit_send(gate, "send_failed", source, grant_ref, preview_id, "transport_failed")
            return [], "model_call_failed:" + message, {}
        entries, stats = llm_providers.parse_extraction_output(raw, source_text)
        if stats.get("error"):
            if gate is not None:
                self._cloud_audit_send(gate, "send_failed", source, grant_ref, preview_id, "invalid_output")
            return [], "invalid_model_output:" + str(stats["error"]), stats
        valid = [self._candidate_from_extraction(entry) for entry in entries]
        if gate is not None:
            self._cloud_audit_send(gate, "send_succeeded", source, grant_ref, preview_id, None)
        return valid, None, stats

    @staticmethod
    def _candidate_from_extraction(entry: Mapping[str, Any]) -> JsonObject:
        """把结构化提取条目映射为既有候选结构(candidate_kind + payload,propose-only)。"""
        object_type = str(entry.get("object_type"))
        label = str(entry.get("label") or "").strip()
        summary = str(entry.get("summary") or "").strip() or label
        quote = str(entry.get("evidence_quote") or "").strip()
        if object_type == "project":
            kind = "entity"
            payload: JsonObject = {"entity_kind": "project", "canonical_label": label or summary[:60], "aliases": [label] if label else [], "summary": summary}
        elif object_type == "commitment":
            kind = "commitment"
            payload = {"commitment_kind": "personal_commitment", "statement": summary, "due_text": "", "responsible_ref": "local_user", "summary": summary}
        elif object_type == "event":
            kind = "episode"
            payload = {"episode_kind": "personal_event", "title": (label or summary)[:60], "summary": summary, "valid_time": {"kind": "unknown", "value": None}}
        elif object_type == "assertion":
            kind = "assertion"
            payload = {"assertion_kind": "personal_statement", "canonical_text": summary, "subject_ref": None, "predicate": None, "object_ref": None, "summary": summary}
        else:
            kind = "entity"
            payload = {"entity_kind": "person", "canonical_label": label or summary[:60], "aliases": [label] if label else [], "summary": summary}
        # evidence_quote 已通过原文子串校验,随 payload 留存供人审核(不改变候选结构)
        payload["evidence_quote"] = quote
        return {"candidate_kind": kind, "payload": payload}

    def _cloud_authorize(
        self, source: Mapping[str, Any], endpoint: str
    ) -> tuple[CloudGate, str, str | None, str | None]:
        """云端发送前的授权门 + 红线门 + 预览门(复用 Y2-S4 CloudGate 合同)。

        用户显式配置 cloud endpoint+key 即视为授权:为此生成并持久化一份
        bounded grant(仅覆盖该 source、purpose=organize、仅 personal 舱室),
        grant/preview/send 全过程审计落 cloud_audit 账本;红线 compartment
        的 source 一律 red_line_denied,不发送。
        """
        now = utc_now()
        gate = CloudGate(self._store, now)
        for record in self._store.ledger_records_of_type(CLOUD_GRANT_RECORD_TYPE):
            grant = record.get("grant")
            if isinstance(grant, Mapping):
                gate.restore_grant(grant)
        source_id = source["source_id"]
        preview = gate.build_preview([source_id], CLOUD_PURPOSE, CLOUD_ACTOR, now)
        preview_id = preview["preview_id"]
        if set(source.get("compartments") or []) & RED_LINE_COMPARTMENTS:
            # 红线舱室在创建任何 grant 之前即拒绝,不为红线内容留存授权记录
            gate._audit("send_denied", {
                "actor": CLOUD_ACTOR, "purpose": CLOUD_PURPOSE,
                "preview_id": preview_id, "source_ids": [source_id],
                "reason": "red_line_denied",
            })
            return gate, "", preview_id, "cloud_denied:red_line_denied"
        grant_id = "grant_product_" + _sha256(_canonical_json({
            "actor": CLOUD_ACTOR, "purpose": CLOUD_PURPOSE,
            "endpoint": endpoint, "sources": [source_id],
        }))[:16]
        if self._store.ledger_record(grant_id) is None:
            # grant 创建与持久化是一个原子单元(审计行与 grant 记录同生共死)
            with self._store.transaction():
                grant = gate.create_grant({
                    "grant_id": grant_id,
                    "actor": CLOUD_ACTOR,
                    "purpose": CLOUD_PURPOSE,
                    "compartments": ["personal"],
                    "source_scope": {"source_ids": [source_id]},
                    "expires_at": CLOUD_GRANT_EXPIRES_AT,
                    "created_at": now,
                })
                self._store.put_ledger_record(grant_id, CLOUD_GRANT_RECORD_TYPE, {
                    "grant_id": grant_id, "grant": grant,
                    "endpoint": endpoint, "recorded_at": now,
                })
        grant_refs, reasons = gate.evaluate_batch([source_id], CLOUD_PURPOSE, CLOUD_ACTOR, now)
        if reasons[0]:
            gate._audit("send_denied", {
                "actor": CLOUD_ACTOR, "purpose": CLOUD_PURPOSE,
                "preview_id": preview_id, "source_ids": [source_id],
                "reason": reasons[0],
            })
            return gate, "", preview_id, "cloud_denied:" + reasons[0]
        gate._audit("send_allowed", {
            "actor": CLOUD_ACTOR, "purpose": CLOUD_PURPOSE,
            "grant_ref": grant_refs[0], "preview_id": preview_id,
            "source_ids": [source_id],
        })
        return gate, grant_refs[0], preview_id, None

    def _cloud_audit_send(
        self,
        gate: CloudGate,
        event_type: str,
        source: Mapping[str, Any],
        grant_ref: str,
        preview_id: str | None,
        reason: str | None,
    ) -> None:
        payload: JsonObject = {
            "actor": CLOUD_ACTOR, "purpose": CLOUD_PURPOSE,
            "grant_ref": grant_ref, "preview_id": preview_id,
            "source_ids": [source["source_id"]],
        }
        if reason:
            payload["reason"] = reason
        gate._audit(event_type, payload)

    def _persist_candidate(self, item: Mapping[str, Any], source: Mapping[str, Any]) -> JsonObject | None:
        kind = item.get("candidate_kind")
        payload = item.get("payload")
        if kind not in CANDIDATE_KINDS or not isinstance(payload, dict):
            return None
        evidence_refs = [{
            "source_id": source["source_id"],
            "locator": source.get("locator", {}),
            "stance": "supports",
            "claim_ref": f"{source['source_id']}:content",
        }]
        material = {"candidate_kind": kind, "payload": payload, "evidence_refs": evidence_refs}
        candidate_id = "cand_p_" + _sha256(_canonical_json(material))[:16]
        existing = self._store.ledger_record(candidate_id)
        if existing is not None:
            return existing
        candidate: JsonObject = {
            "candidate_id": candidate_id,
            "candidate_kind": kind,
            "payload": payload,
            "evidence_refs": evidence_refs,
            "review_status": "unconfirmed",
            "status": "proposed",
            "model_or_rule_version": self._model_version_label(),
            "created_at": self._now,
        }
        self._store.put_ledger_record(candidate_id, "product_candidate", candidate, revision_id=self._store.current_revision())
        return candidate

    def _model_version_label(self) -> str:
        """候选 provenance 用的版本标签:显式 model_name 优先,其次离线规则/提供商缺省模型。"""
        configured = str(self._settings.get("model_name") or "").strip()
        if configured:
            return configured
        if self._settings.get("model_mode") == "offline":
            return "offline-rule-v1"
        return llm_providers.default_model(str(self._settings.get("model_provider") or "")) or "provider-default"

    def list_candidates(self, status: str | None = None) -> list[JsonObject]:
        candidates = self._store.ledger_records_of_type("product_candidate")
        return [item for item in candidates if status is None or item.get("status") == status]

    def confirm_candidate(self, candidate_id: str, actor: str = "local_user") -> JsonObject:
        candidate = self._store.ledger_record(candidate_id)
        if candidate is None or candidate.get("candidate_kind") not in CANDIDATE_KINDS:
            raise KeyError(candidate_id)
        if candidate.get("status") == "confirmed":
            return candidate
        now = utc_now()
        with self._store.transaction():
            base_revision = self._store.current_revision()
            new_revision = self._store.next_revision()
            object_payload = self._build_object(candidate, new_revision, actor, now)
            object_id = object_payload["object_id"]
            published_revision: str | None = None
            if self._store.canonical_object_or_none(object_id) is None:
                self._store.add_revision(new_revision, now, "changeset")
                self._store.add_canonical_object(object_id, object_payload)
                self._store.replace_evidence_refs(object_id, candidate["evidence_refs"])
                self._store.put_ledger_record(
                    "changeset_" + candidate_id,
                    "product_changeset",
                    {
                        "changeset_id": "changeset_" + candidate_id,
                        "candidate_ref": candidate_id,
                        "object_ref": object_id,
                        "base_revision": base_revision,
                        "published_revision": new_revision,
                        "status": "published",
                        "actor": actor,
                        "recorded_at": now,
                    },
                    revision_id=new_revision,
                )
                self._store.mark_all_projections_stale(new_revision)
                published_revision = new_revision
            candidate["status"] = "confirmed"
            candidate["confirmed_at"] = now
            candidate["object_id"] = object_id
            # 对象已存在(去重路径)时不产生新 revision,账本行不引用未发布的 revision
            self._store.replace_ledger_record(candidate_id, candidate, revision_id=published_revision)
        self._refresh_projection()
        return candidate

    def reject_candidate(self, candidate_id: str, actor: str = "local_user") -> JsonObject:
        candidate = self._store.ledger_record(candidate_id)
        if candidate is None:
            raise KeyError(candidate_id)
        candidate["status"] = "rejected"
        candidate["rejected_at"] = utc_now()
        candidate["rejected_by"] = actor
        self._store.replace_ledger_record(candidate_id, candidate)
        self._refresh_projection()
        return candidate

    def _build_object(self, candidate: Mapping[str, Any], new_revision: str, actor: str, now: str) -> JsonObject:
        kind = candidate["candidate_kind"]
        payload = dict(candidate.get("payload") or {})
        evidence_refs = list(candidate.get("evidence_refs") or [])
        base = {
            "object_revision": new_revision,
            "created_at": now,
            "created_by": actor,
            "recorded_at": now,
            "recorded_by": actor,
            "owner_ref": "local_user",
            "sensitivity": "private",
            "compartments": ["personal"],
            "synthetic": False,
            "evidence_refs": evidence_refs,
        }
        if kind == "entity":
            label = str(payload.get("canonical_label") or "未命名主体")
            object_id = "entity_p_" + _sha256(label)[:12]
            body = {
                "object_type": "entity",
                "object_id": object_id,
                "entity_kind": payload.get("entity_kind") or "person",
                "canonical_label": label,
                "aliases": payload.get("aliases") or [label],
                "summary": payload.get("summary") or "",
            }
        elif kind == "assertion":
            text = str(payload.get("canonical_text") or payload.get("summary") or "未命名断言")
            object_id = "assertion_p_" + _sha256(text)[:12]
            body = {
                "object_type": "assertion",
                "object_id": object_id,
                "assertion_kind": payload.get("assertion_kind") or "personal_statement",
                "canonical_text": text,
                "subject_ref": payload.get("subject_ref"),
                "predicate": payload.get("predicate"),
                "object_ref": payload.get("object_ref"),
                "summary": payload.get("summary") or text,
            }
        elif kind == "commitment":
            text = str(payload.get("statement") or payload.get("summary") or "未命名承诺")
            object_id = "commitment_p_" + _sha256(text)[:12]
            body = {
                "object_type": "commitment",
                "object_id": object_id,
                "commitment_kind": payload.get("commitment_kind") or "personal_commitment",
                "statement": text,
                "due_text": payload.get("due_text") or "",
                "responsible_ref": payload.get("responsible_ref") or "local_user",
                "status": "open",
                "summary": payload.get("summary") or text,
            }
        elif kind == "episode":
            text = str(payload.get("title") or payload.get("summary") or "未命名事件")
            object_id = "episode_p_" + _sha256(text)[:12]
            body = {
                "object_type": "episode",
                "object_id": object_id,
                "episode_kind": payload.get("episode_kind") or "personal_event",
                "title": text,
                "summary": payload.get("summary") or text,
                "valid_time": payload.get("valid_time") or {"kind": "unknown", "value": None},
            }
        else:
            raise ValueError("unsupported candidate_kind")
        body.update(base)
        body["object_id"] = object_id
        return body

    # -- reading -------------------------------------------------------------

    def list_objects(self, object_type: str | None = None) -> list[JsonObject]:
        summaries = self._store.canonical_object_summaries()
        return [item for item in summaries if object_type is None or item.get("object_type") == object_type]

    def get_object(self, object_id: str) -> JsonObject | None:
        return self._store.canonical_object_or_none(object_id)

    def overview(self) -> JsonObject:
        payload = self._overview_payload()
        payload["recent_sources"] = self.list_sources()[-8:][::-1]
        payload["recent_objects"] = self.list_objects()[-8:][::-1]
        payload["candidates"] = self.list_candidates()[-12:][::-1]
        return payload

    def search(self, query: str) -> JsonObject:
        needle = str(query or "").strip()
        source_matches: list[JsonObject] = []
        object_matches: list[JsonObject] = []
        if needle:
            for source in self._store.portability_snapshot()["sources"]:
                text = _source_content(source)
                title = str(source.get("title") or source_id_title(source))
                if needle.lower() in text.lower() or needle.lower() in title.lower():
                    source_matches.append({
                        "source_id": source["source_id"],
                        "title": title,
                        "snippet": _snippet(text, needle),
                        "ingested_at": source.get("ingested_at"),
                    })
            for summary in self._store.canonical_object_summaries():
                payload_text = json.dumps(summary.get("payload", {}), ensure_ascii=False)
                if needle.lower() in payload_text.lower():
                    object_matches.append(summary)
        return {"query": needle, "sources": source_matches[:50], "objects": object_matches[:50]}

    def timeline(self, limit: int = 50) -> list[JsonObject]:
        events: list[JsonObject] = []
        for source in self._store.portability_snapshot()["sources"]:
            events.append({
                "kind": "source",
                "id": source["source_id"],
                "title": source.get("title") or source_id_title(source),
                "at": source.get("ingested_at") or source.get("source_created_at"),
                "summary": _source_content(source)[:120],
            })
        for summary in self._store.canonical_object_summaries():
            payload = summary["payload"]
            events.append({
                "kind": summary["object_type"],
                "id": summary["object_id"],
                "title": payload.get("canonical_label") or payload.get("title") or payload.get("statement") or summary["object_id"],
                "at": payload.get("recorded_at") or payload.get("created_at"),
                "summary": str(payload.get("summary") or "")[:120],
            })
        events = [event for event in events if event.get("at")]
        events.sort(key=lambda item: str(item["at"]), reverse=True)
        return events[:limit]

    # -- 问识海(只读问答) ---------------------------------------------------

    def ask(self, question: str) -> JsonObject:
        """诚实问答:只基于已确认记忆+原文证据,调用 answers.py 语义层逐条核对。

        无证据时明确回答"不知道/没有覆盖",绝不编造;本方法是只读操作,零写入。
        """
        question = str(question or "").strip()
        if not question:
            raise ValueError("empty_question")
        now = utc_now()
        snapshot = self._store.portability_snapshot()
        sources = list(snapshot["sources"])
        canonical = list(snapshot["canonical"])
        source_by_id = {source["source_id"]: source for source in sources}

        # 产品断言适配为 AnswerEvaluator 合同形状;无法安全适配的一律不参与回答
        adapted = [
            item for item in (self._ask_adapt_assertion(obj) for obj in canonical)
            if item is not None
        ]
        evaluator = self._ask_evaluator(adapted, sources, now)

        terms = _ask_terms(question)
        scored = sorted(
            ((_ask_score(item, terms), item) for item in adapted),
            key=lambda pair: (-pair[0], str(pair[1]["assertion_id"])),
        )
        relevant = [item for score, item in scored if score > 0][:8]

        verified: list[tuple[JsonObject, JsonObject]] = []
        rejected: list[tuple[JsonObject, JsonObject]] = []
        for item in relevant:
            answer = evaluator.evaluate(self._ask_query(item, question))
            if answer.get("answer_status") == "verified":
                verified.append((item, answer))
            else:
                rejected.append((item, answer))

        # 负向探针:没有可核对的陈述时,让语义层给出诚实的拒绝原因(如 AS-008 仅派生证据)
        probe = None
        if not verified:
            probe = evaluator.evaluate({
                "query_id": "ask_probe_" + _sha256(question)[:16],
                "claim_ref": "product.free_text:" + _sha256(question)[:12],
                "subject_ref": "local_user",
                "predicate": "product.free_text_query",
                "verification_scope": "statement_occurrence",
                "valid_time": "current",
                "coverage_window_refs": [],
            })

        reason_codes: set[str] = set()
        for _, answer in verified + rejected:
            reason_codes.update(answer.get("reason_codes") or [])
        if probe is not None:
            reason_codes.update(probe.get("reason_codes") or [])

        evidence: list[JsonObject] = []
        seen_evidence: set[tuple[str, str]] = set()
        for item, answer in verified:
            for ref in answer.get("evidence_refs") or []:
                source_id = ref.get("source_id")
                key = (str(item["assertion_id"]), str(source_id))
                if key in seen_evidence:
                    continue
                seen_evidence.add(key)
                source = source_by_id.get(source_id)
                evidence.append({
                    "object_id": item["assertion_id"],
                    "object_type": "assertion",
                    "text": item["canonical_text"],
                    "source_id": source_id,
                    "source_title": (source.get("title") if source else None) or str(source_id),
                    "claim_ref": item["evidence_refs"][0].get("claim_ref"),
                    "verified_scope": answer.get("verification_scope"),
                })

        covered = [item["canonical_text"] for item, _ in verified]
        not_covered: list[str] = []
        for item, answer in rejected:
            codes = answer.get("reason_codes") or []
            not_covered.append(
                "相关记忆「" + item["canonical_text"][:40] + "」未作为回答依据:"
                + _ask_reason_text(codes)
            )
        if probe is not None:
            not_covered.extend(_ask_reason_text([code]) for code in (probe.get("reason_codes") or []))
        if not verified:
            # 原始资料命中但未经确认的内容不算证据,只提示数量,不展示内容
            unconfirmed_hits = sum(
                1 for source in sources
                if any(term in _source_content(source).lower() for term in terms)
            )
            if unconfirmed_hits:
                not_covered.append(f"{unconfirmed_hits} 份原始资料含有相关文本,但尚未确认,未作为回答依据")
        not_covered.append("本次回答不覆盖:未确认的候选、未导入识海的内容")

        if verified:
            lines = "\n".join(f"{index}. {text}" for index, text in enumerate(covered, 1))
            answer_text = "根据你已确认的记忆(仅核对“资料中确实这样记录”,不代表内容必然为真):\n" + lines
            answer_status = "answered"
        else:
            answer_text = "我不知道。已确认的记忆中没有证据覆盖这个问题,识海不会编造回答。"
            answer_status = "no_coverage"

        return {
            "question": question,
            "answer_status": answer_status,
            "answer_text": answer_text,
            "coverage": {
                "covered": covered,
                "not_covered": not_covered,
                "searched": {
                    "confirmed_assertions": len(adapted),
                    "confirmed_objects": len(canonical),
                    "sources": len(sources),
                },
                "reason_codes": sorted(reason_codes),
            },
            "evidence": evidence,
            "freshness": self._ask_freshness(evidence, source_by_id),
            "confidence_note": (
                f"回答基于 {len(verified)} 条已确认记忆、{len(evidence)} 条原文证据;"
                "核对范围为陈述发生(statement_occurrence),不代表识海核实了内容真实性。"
                if verified else
                "未找到证据时识海固定回答不知道;未确认的资料与派生视图不作为回答依据。"
            ),
            "evaluated_at": now,
        }

    @staticmethod
    def _ask_adapt_assertion(obj: Mapping[str, Any]) -> JsonObject | None:
        """把已确认的 canonical 断言适配为 AnswerEvaluator 的 fixture 合同形状。

        关键语义映射(诚实,不改 answers.py):
        - assertion_kind=reported + 查询范围 statement_occurrence:产品断言只声称
          "资料中确实出现过这条陈述",不声称它是世界事实;
        - review_status=confirmed:对象能进入 canonical 层,前提就是候选已被用户确认;
        - claim_ref 细化为 source:subject:predicate:同一来源同一主体同一谓词的
          不同取值才会被判为冲突(AS-004),避免不同陈述被误报冲突。
        """
        if obj.get("object_type") != "assertion":
            return None
        text = str(obj.get("canonical_text") or obj.get("summary") or "").strip()
        evidence_refs = [
            dict(ref) for ref in obj.get("evidence_refs") or []
            if isinstance(ref, Mapping) and ref.get("source_id")
        ]
        if not text or not evidence_refs:
            return None
        subject_ref = str(obj.get("subject_ref") or "local_user")
        predicate = str(obj.get("predicate") or ("product.statement:" + str(obj.get("object_id"))))
        source_id = str(evidence_refs[0]["source_id"])
        claim_ref = f"{source_id}:{subject_ref}:{predicate}"
        for ref in evidence_refs:
            ref["claim_ref"] = claim_ref
        return {
            "object_type": "assertion",
            "assertion_id": obj.get("object_id"),
            "object_revision": obj.get("object_revision"),
            "subject_ref": subject_ref,
            "predicate": predicate,
            "value": text,
            "assertion_kind": "reported",
            "review_status": "confirmed",
            "perspective_ref": subject_ref,
            "valid_time": {
                "start": _ask_z_time(obj.get("recorded_at") or obj.get("created_at")),
                "end": "unbounded",
                "bounds": "[)",
            },
            "evidence_refs": evidence_refs,
            "canonical_text": text,
            "object_ref": obj.get("object_ref"),
            "summary": obj.get("summary") or text,
        }

    def _ask_evaluator(self, adapted: list[JsonObject], sources: list[JsonObject], now: str) -> AnswerEvaluator:
        # 产品库的 Derived 投影映射为 derived_inputs:仅派生证据时语义层拒绝回答(AS-008);
        # 产品不按谓词维护覆盖窗口,coverage_window_refs 恒为空,覆盖度声明由产品侧自行给出
        initial = {
            "data_revision": self._store.current_revision(),
            "canonical_objects": adapted,
            "coverage_windows": [],
            "source_records": [
                {"source_id": source["source_id"], "source_created_at": source.get("source_created_at")}
                for source in sources
            ],
            "derived_inputs": [
                {"projection_ref": record["view_name"]}
                for record in self._store.projection_records()
            ],
            "candidates": [],
            "freshness_policies": [],
        }
        return AnswerEvaluator(self._store, {"initial_state": initial}, now)

    @staticmethod
    def _ask_query(item: Mapping[str, Any], question: str) -> JsonObject:
        return {
            "query_id": "ask_" + _sha256(question + str(item["assertion_id"]))[:16],
            "claim_ref": str(item["evidence_refs"][0]["claim_ref"]),
            "subject_ref": str(item["subject_ref"]),
            "predicate": str(item["predicate"]),
            "verification_scope": "statement_occurrence",
            "valid_time": "current",
            "coverage_window_refs": [],
        }

    @staticmethod
    def _ask_freshness(evidence: list[JsonObject], source_by_id: Mapping[str, Any]) -> JsonObject:
        """时效诚实声明:只报告证据时间,不发明过期政策替你下判断。"""
        if not evidence:
            return {"status": "not_applicable", "newest_evidence_at": None, "oldest_evidence_at": None,
                    "note": "没有证据,无所谓时效"}
        times = []
        for entry in evidence:
            source = source_by_id.get(entry.get("source_id"))
            if not source:
                continue
            stamp = _ask_z_time(source.get("source_created_at")) or _ask_z_time(source.get("ingested_at"))
            if stamp:
                times.append(stamp)
        if not times:
            return {"status": "unknown", "newest_evidence_at": None, "oldest_evidence_at": None,
                    "note": "证据缺少可解析的时间,时效未知"}
        return {"status": "current", "newest_evidence_at": max(times), "oldest_evidence_at": min(times),
                "note": "识海只报告证据时间,不替你判断内容是否过期"}

    # -- export / import -----------------------------------------------------

    def export_pack(self, destination: str | Path | None = None) -> JsonObject:
        if destination is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = self.data_dir / "exports" / f"pack_{stamp}"
        manifest = export_markdown_pack(self._store, Path(destination), utc_now())
        return {"status": "ok" if manifest.get("outcome") != "rejected" else "rejected", "path": str(Path(destination).resolve()), "manifest": manifest}

    def backup(self, key: str | None = None) -> JsonObject:
        key = key or self._settings.get("backup_key") or "noetide-local"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.data_dir / "backups" / f"noetide_{stamp}.nobak"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        result = create_backup(self.db_path, key, backup_path, utc_now())
        return {"status": "ok" if result.get("outcome") == "created" else "rejected", "path": str(backup_path.resolve()), "backup": result, "key_hint": "stored in local settings"}

    def restore_backup(self, backup_path: str | Path, key: str) -> JsonObject:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.data_dir / "restored" / f"restored_{stamp}.sqlite3"
        return restore_backup(Path(backup_path), key, target)

    def import_pack(self, pack_path: str | Path) -> JsonObject:
        verified = ContextPackVerifier().verify(str(pack_path))
        if verified.get("status") != "validated":
            return {"status": "rejected", "reason": verified.get("status", "invalid_pack")}
        snapshot = verified.get("snapshot") or {}
        report: JsonObject = {
            "sources_imported": 0, "sources_duplicate": 0,
            "canonical_imported": 0, "canonical_duplicate": 0, "ledger_imported": 0,
        }
        # 整个导入是一个原子单元:任一记录失败即整体回滚,不留半导入状态
        with self._store.transaction():
            for source in snapshot.get("sources", []):
                source_id = source.get("source_id")
                if not source_id or self._store.seeded_source(source_id) is not None:
                    report["sources_duplicate"] += 1
                    continue
                source = dict(source)
                source.setdefault("append_receipt_id", f"receipt_{source_id}")
                self._store.append_source(source, {
                    "receipt_id": source["append_receipt_id"], "source_id": source_id,
                    "status": "stored", "actor": "pack_import",
                })
                report["sources_imported"] += 1
            for obj in snapshot.get("canonical", []):
                object_id = obj.get("object_id")
                if not object_id or self._store.canonical_object_or_none(object_id) is not None:
                    report["canonical_duplicate"] += 1
                    continue
                payload = dict(obj)
                payload.setdefault("object_revision", self._store.current_revision())
                self._store.add_canonical_object(object_id, payload)
                if isinstance(payload.get("evidence_refs"), list):
                    self._store.replace_evidence_refs(object_id, payload["evidence_refs"])
                report["canonical_imported"] += 1
            for record in snapshot.get("ledger", []):
                record_id = record.get("record_id")
                if not record_id or self._store.ledger_record(record_id) is not None:
                    continue
                self._store.put_ledger_record(record_id, record.get("record_type") or "product_event", record.get("payload") or record)
                report["ledger_imported"] += 1
        self._refresh_projection()
        return report

    # -- MCP / agent surface -------------------------------------------------

    def mcp_handle(self, request: Mapping[str, Any], payload: Mapping[str, Any] | None = None) -> JsonObject:
        return self._mcp.handle_request(request, payload)

    def create_mcp_capability(self, spec: Mapping[str, Any]) -> JsonObject:
        return self._mcp.create_capability(spec)

    def mcp_capabilities(self) -> list[JsonObject]:
        return self._mcp.capabilities()

    def default_mcp_capability(self) -> JsonObject:
        source_ids = [source["source_id"] for source in self._store.portability_snapshot()["sources"]][:50]
        if not source_ids:
            source_ids = ["src_product_empty"]
        existing = next((item for item in self._mcp.capabilities() if item.get("capability_id") == "cap_product_default"), None)
        if existing is not None and set(existing.get("resource_ids") or []) == set(source_ids):
            return existing
        return self._mcp.create_capability({
            "capability_id": "cap_product_default",
            "actor": "local_user",
            "purpose": "personal_memory_read_and_propose",
            "tools": ["list_resources", "read_resource", "propose_changeset", "record_source"],
            "resource_ids": source_ids,
            "resource_fields": {"read_resource": ["metadata", "content"]},
            "expires_at": "2099-12-31T23:59:59+00:00",
        })

    def create_agent_capability(self, resource_ids: Iterable[str] | None = None) -> JsonObject:
        ids = [str(item).strip() for item in (resource_ids or []) if str(item).strip()]
        if not ids:
            return self.default_mcp_capability()
        capability_id = "cap_agent_" + _sha256(_canonical_json(ids))[:12]
        return self.create_mcp_capability({
            "capability_id": capability_id,
            "actor": "local_user",
            "purpose": "personal_memory_read_and_propose",
            "tools": ["list_resources", "read_resource", "propose_changeset", "record_source"],
            "resource_ids": ids,
            "resource_fields": {"read_resource": ["metadata", "content"]},
            "expires_at": "2099-12-31T23:59:59+00:00",
        })


def source_id_title(source: Mapping[str, Any]) -> str:
    return "来源 " + str(source.get("source_id", "")).replace("src_p_", "").replace("src_", "")[:12]


def _find_persons(text: str) -> list[str]:
    found: list[str] = []
    patterns = (
        r"(?:我叫|我是|我的名字是|对方叫|他叫|她叫)([A-Za-z\u4e00-\u9fff]{1,20})",
        r"(?:和|跟|与|向)([A-Za-z\u4e00-\u9fff]{1,12})(?:说|聊|沟通|商量|见面|约|合作|联系|对接)",
        r"([A-Za-z\u4e00-\u9fff]{1,12})(?:说|提到|告诉我|跟我讲|答复|回复)",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            label = match.group(1).strip()
            if len(label) >= 2 and label not in found:
                found.append(label)
    return found


def _find_projects(text: str) -> list[str]:
    found: list[str] = []
    patterns = (
        r"(?:项目|工作|方案|任务|产品|平台|课题)[：:\s]*([^，。;；\n]{1,30})",
        r"([^，。;；\n]{1,24})(?:项目|工作|方案|任务|产品|平台|课题)",
    )
    bad_prefixes = ("我答应", "我决定", "我们决定", "我计划", "今天", "昨天", "上周", "下周", "我们要", "我需要", "他答应", "她答应")
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            label = match.group(1).strip(" ，。、")
            if not label or label in found:
                continue
            if any(label.startswith(prefix) for prefix in bad_prefixes):
                continue
            found.append(label)
    return found[:6]


def _find_role_relations(text: str) -> list[tuple[str, str, str]]:
    """人物-项目关系模式:"X 是 Y 的(CEO|创始人|联合创始人|CTO)" -> (人, 组织, 角色)。"""
    found: list[tuple[str, str, str]] = []
    pattern = r"([A-Za-z一-鿿]{2,12})是([^，。;；\n]{1,24}?)的(联合创始人|创始人|CEO|CTO)"
    for match in re.finditer(pattern, text):
        person, org, role = match.group(1).strip(), match.group(2).strip(" ，。、"), match.group(3)
        if org and (person, org, role) not in found:
            found.append((person, org, role))
    return found


def _is_commitment(text: str) -> bool:
    return bool(re.search(r"(答应|承诺|保证|约好|决定|会尽快|稍后|明天|下周|月底|本周|后天|周五|周一)", text))


def _find_due_text(text: str) -> str:
    match = re.search(r"(明天|下周|月底|本周|后天|周五|周一|\d{1,2}月\d{1,2}日|[0-9]{4}-[0-9]{2}-[0-9]{2})", text)
    return match.group(1) if match else ""


def _is_episode(text: str) -> bool:
    return bool(re.search(r"(今天|昨天|前天|上周|刚才|下午|上午|晚上|早上|[0-9]{4}年|[0-9]{1,2}月[0-9]{1,2}日|[0-9]{4}-[0-9]{2}-[0-9]{2})", text))


def _find_time(text: str) -> JsonObject:
    # 裸年份("X 在 2020 年")也算事件时间,排在完整日期之后避免截断长匹配
    match = re.search(r"([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}年|今天|昨天|上周|明天)", text)
    return {"kind": "unknown", "value": match.group(1) if match else None}


def _is_assertion(text: str) -> bool:
    return bool(re.search(r"(认为|觉得|决定|发现|确认|其实|一直是|已经是|并不是|很重要|不同意|同意)", text))


def _assertion_subject(text: str) -> str | None:
    match = re.search(r"(?:我觉得|我认为|他|她|我们|对方|客户|团队|项目)([^，。]{0,20})", text)
    if match:
        return match.group(1).strip() or "local_user"
    return "local_user"


def _assertion_predicate(text: str) -> str:
    match = re.search(r"(认为|觉得|决定|发现|确认|很重要|不同意|同意)", text)
    return match.group(1) if match else "陈述"


# -- 问识海辅助 -------------------------------------------------------------

# 问题里的通用疑问成分不参与证据匹配
_ASK_STOPWORDS = frozenset({
    "什么", "怎么", "怎样", "如何", "为什么", "为何", "多少", "哪些", "哪个", "谁",
    "哪里", "哪儿", "吗", "呢", "吧", "的", "了", "是", "有", "没有", "是不是",
    "有没有", "我", "我们", "你", "您", "他", "她", "它", "在", "和", "跟", "与",
    "请", "请问", "一下", "告诉", "告诉我", "知道", "时候", "能否", "可否",
})

# answers.py reason_code 的中文诚实说明(未列出的原样展示,不粉饰)
_ASK_REASON_TEXT = {
    "unresolved_conflict": "存在相互冲突的陈述,识海不替你裁决",
    "evidence_outside_freshness_window": "证据超出时效窗口",
    "derived_evidence_forbidden": "仅有派生视图(投影)相关内容,派生证据不足为凭",
    "fictional_evidence_excluded": "虚构内容不作为证据",
    "unreviewed_candidate_present": "相关候选尚未确认,不作为证据",
    "world_claim_not_verified": "识海只核对记录中是否这样写过,不验证其是否为真",
    "no_matching_assertion": "已确认记忆中没有可核对的陈述",
    "coverage_sufficient_no_safe_conclusion": "覆盖充分但得不出安全结论",
    "claim_ref_mismatch": "证据与问题对不上",
    "no_coverage_window": "没有覆盖窗口信息",
}


def _ask_reason_text(codes: Iterable[str]) -> str:
    return ";".join(_ASK_REASON_TEXT.get(code, code) for code in codes) or "未通过证据核对"


def _ask_terms(question: str) -> list[str]:
    """确定性分词:英文/数字整词 + 中文整串与 2-gram,去停用词,保序去重。"""
    terms: list[str] = []
    for token in re.findall(r"[A-Za-z0-9_]+|[一-鿿]+", question.lower()):
        if re.fullmatch(r"[一-鿿]+", token):
            if len(token) >= 2:
                terms.append(token)
            terms.extend(token[index:index + 2] for index in range(len(token) - 1))
        elif len(token) >= 2:
            terms.append(token)
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        if term not in _ASK_STOPWORDS and term not in seen:
            seen.add(term)
            unique.append(term)
    return unique


def _ask_score(item: Mapping[str, Any], terms: list[str]) -> int:
    haystack = " ".join(
        str(item.get(key) or "")
        for key in ("canonical_text", "summary", "subject_ref", "object_ref", "predicate")
    ).lower()
    return sum(1 for term in terms if term in haystack)


def _ask_z_time(value: Any) -> str:
    """把 ISO 时间规范为 answers.py 冲突检测可解析的 '%Y-%m-%dT%H:%M:%SZ';失败返回 'unbounded'。"""
    if not isinstance(value, str) or not value:
        return "unbounded"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "unbounded"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
