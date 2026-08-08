"""C5 Markdown+JSON pack rendering, local encrypted backup, restore, and honest deletion receipts.

Encryption note (ADR-0017): the backup cipher is a stdlib-only construction
(PBKDF2-HMAC-SHA256 派生密钥 + sha256 密钥流 XOR + HMAC-SHA256 认证，格式标记 NOBAK2)。
It proves the slice semantics (ciphertext != plaintext, key-sensitive, tamper-evident,
byte-identical restore) and is NOT production cryptography. Production AEAD/KDF
selection is deferred to the D2/D3 decision. 旧版无版本标记的备份格式一律拒绝恢复。
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .portability import PACK_SCHEMA_VERSION, ContextPackError, _json_bytes, _safe_relative, _sha256
from .store import SemanticStore


JsonObject = dict[str, Any]
# receipt 标签与实际构造一致:NOBAK2(PBKDF2-HMAC-SHA256 20 万轮派生 + HMAC-SHA256
# 认证),仍非生产级加密;由 C5-005 oracle 哈希绑定。
ENCRYPTION_LABEL = "nobak2_pbkdf2_hmac_v1"
_BACKUP_MAGIC = b"NOBAK2"  # 备份格式版本标记：PBKDF2 派生 + HMAC 认证
_KDF_ITERATIONS = 200_000
_SALT_LEN = 16
_NONCE_LEN = 16
_TAG_LEN = 32
_BASE_FILES = ("sources.json", "canonical.json", "ledger.json", "README.md")
_MARKDOWN_FILES = ("markdown/sources.md", "markdown/canonical.md", "markdown/ledger.md")
_DELETION_COMPONENTS = (
    "live_source", "canonical_payload", "ledger_payload", "derived_index",
    "cache", "backup", "export_copy", "minimal_audit_proof",
)
_NL = chr(10)


def _render_value(value: Any) -> str:
    if value is None:
        return "(empty)"
    if isinstance(value, (dict, list)):
        return "`" + json.dumps(value, ensure_ascii=False, sort_keys=True) + "`"
    return str(value)


def _render_record(title: str, record: Mapping[str, Any]) -> str:
    lines = [f"## {title}", ""]
    for key in sorted(record):
        lines.append(f"- **{key}**: {_render_value(record[key])}")
    lines.append("")
    return _NL.join(lines)


def render_markdown(snapshot: Mapping[str, Any]) -> dict[str, str]:
    """Deterministic Markdown rendering of the three authoritative layers."""
    sources = sorted(snapshot["sources"], key=lambda r: json.dumps(r, sort_keys=True))
    canonical = sorted(snapshot["canonical"], key=lambda r: json.dumps(r, sort_keys=True))
    ledger = sorted(snapshot["ledger"], key=lambda r: json.dumps(r, sort_keys=True))
    parts = {
        "markdown/sources.md": ["# Sources", ""],
        "markdown/canonical.md": ["# Canonical Objects", ""],
        "markdown/ledger.md": ["# Ledger Records", ""],
    }
    for index, record in enumerate(sources, 1):
        parts["markdown/sources.md"].append(_render_record(f"source-{index}", record))
    for index, record in enumerate(canonical, 1):
        parts["markdown/canonical.md"].append(_render_record(f"canonical-{index}", record))
    for index, record in enumerate(ledger, 1):
        parts["markdown/ledger.md"].append(_render_record(f"ledger-{index}", record))
    return {name: _NL.join(lines).rstrip(_NL) + _NL for name, lines in parts.items()}


def _readme(snapshot: Mapping[str, Any]) -> str:
    lines = [
        "# Noetide Context Pack",
        "",
        "Owner-private synthetic export with Markdown+JSON layers. JSON is authoritative; Markdown is explanatory only.",
        "",
        "- Data revision: `" + str(snapshot["data_revision"]) + "`",
        "- Source records: " + str(len(snapshot["sources"])),
        "- Canonical objects: " + str(len(snapshot["canonical"])),
        "- Ledger records: " + str(len(snapshot["ledger"])),
    ]
    return _NL.join(lines) + _NL

def export_markdown_pack(store: SemanticStore, destination: str | Path, exported_at: str) -> JsonObject:
    """Exports JSON + Markdown pack; read-only on the store (C5-INV-005)."""
    root = Path(destination)
    if root.exists():
        return {"outcome": "rejected", "reason": "pack destination already exists"}
    snapshot = store.portability_snapshot()
    markdown = render_markdown(snapshot)
    root.mkdir(parents=True)
    (root / "markdown").mkdir()
    contents: dict[str, bytes] = {
        "sources.json": _json_bytes({"schema_version": PACK_SCHEMA_VERSION, "records": snapshot["sources"]}),
        "canonical.json": _json_bytes({"schema_version": PACK_SCHEMA_VERSION, "data_revision": snapshot["data_revision"], "objects": snapshot["canonical"]}),
        "ledger.json": _json_bytes({"schema_version": PACK_SCHEMA_VERSION, "records": snapshot["ledger"]}),
        "README.md": _readme(snapshot).encode("utf-8"),
    }
    for name, text in markdown.items():
        contents[name] = text.encode("utf-8")
    entries = []
    for relative in _BASE_FILES + _MARKDOWN_FILES:
        payload = contents[relative]
        target = root / relative
        target.write_bytes(payload)
        entries.append({
            "entry_id": relative,
            "logical_layer": "derived" if relative.endswith(".md") else relative.removesuffix(".json"),
            "content_ref": relative,
            "media_type": "text/markdown" if relative.endswith(".md") else "application/json",
            "byte_length": len(payload),
            "hash_algorithm": "sha256",
            "content_hash": _sha256(payload),
        })
    manifest = {
        "schema_version": PACK_SCHEMA_VERSION,
        "data_revision": snapshot["data_revision"],
        "exported_at": exported_at,
        "export_scope": "owner_private_synthetic",
        "entries": entries,
    }
    (root / "manifest.json").write_bytes(_json_bytes(manifest))
    checksums = "".join(entry["content_hash"] + "  " + entry["content_ref"] + _NL for entry in entries)
    (root / "checksums.sha256").write_text(checksums, encoding="utf-8", newline="\n")
    return {"outcome": "exported", "manifest": manifest}


def verify_pack(root: str | Path, current_revision: str | None = None) -> JsonObject:
    """Validates a Markdown+JSON pack as inert data; fail closed, never writes SQLite."""
    pack_root = Path(root).resolve()
    try:
        manifest = json.loads((pack_root / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schema_version") != PACK_SCHEMA_VERSION or not isinstance(manifest.get("entries"), list):
            return {"status": "rejected_schema"}
        expected_refs = set()
        for entry in manifest["entries"]:
            relative = _safe_relative(entry.get("content_ref", ""))
            expected_refs.add(str(relative))
            target = (pack_root / relative).resolve()
            if pack_root not in target.parents or not target.is_file():
                return {"status": "rejected_hash_mismatch", "detail": "missing " + str(relative)}
            data = target.read_bytes()
            if entry.get("hash_algorithm") != "sha256" or entry.get("byte_length") != len(data) or entry.get("content_hash") != _sha256(data):
                return {"status": "rejected_hash_mismatch", "detail": str(relative)}
        allowed = expected_refs | {"manifest.json", "checksums.sha256"}
        for path in pack_root.rglob("*"):
            if path.is_file():
                relative = path.relative_to(pack_root).as_posix()
                if relative not in allowed:
                    return {"status": "rejected_unknown_file", "detail": relative}
    except (OSError, json.JSONDecodeError, ContextPackError, TypeError):
        return {"status": "rejected_path"}
    revision = manifest["data_revision"]
    relation = "unknown" if current_revision is None else ("current" if revision == current_revision else "historical")
    return {"status": "validated", "data_revision": revision, "pack_relation": relation}


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    blocks = []
    counter = 0
    produced = 0
    while produced < length:
        blocks.append(hashlib.sha256(key + nonce + counter.to_bytes(8, "big")).digest())
        produced += 32
        counter += 1
    return b"".join(blocks)[:length]


def _xor(data: bytes, stream: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, stream))


def _derive_keys(key: str, salt: bytes) -> tuple[bytes, bytes]:
    """PBKDF2-HMAC-SHA256 派生加密密钥与 MAC 密钥，避免直接用口令做密钥流种子。"""
    derived = hashlib.pbkdf2_hmac("sha256", key.encode("utf-8"), salt, _KDF_ITERATIONS, dklen=64)
    return derived[:32], derived[32:]


def create_backup(db_path: str | Path, key: str, backup_path: str | Path, created_at: str) -> JsonObject:
    """Encrypts the DB file into .nobak; read-only on the source (C5-INV-003/005)."""
    db = Path(db_path)
    target = Path(backup_path)
    if target.exists():
        return {"outcome": "rejected", "reason": "backup destination already exists"}
    plaintext = db.read_bytes()
    source_sha = _sha256(plaintext)
    salt = os.urandom(_SALT_LEN)
    nonce = os.urandom(_NONCE_LEN)
    enc_key, mac_key = _derive_keys(key, salt)
    ciphertext = _xor(plaintext, _keystream(enc_key, nonce, len(plaintext)))
    header = _BACKUP_MAGIC + salt + nonce
    tag = hmac.new(mac_key, header + ciphertext, hashlib.sha256).digest()
    payload = header + tag + ciphertext
    target.write_bytes(payload)
    return {
        "outcome": "created",
        "receipt": {
            "backup_id": target.name,
            "source_db_sha256": source_sha,
            "backup_sha256": _sha256(payload),
            "created_at": created_at,
            "encryption": ENCRYPTION_LABEL,
            "key_hint": "c5-synthetic-key-hint",
        },
    }


def restore_backup(backup_path: str | Path, key: str, target_path: str | Path) -> JsonObject:
    """Restores a backup to a NEW target only; wrong key or corruption fails closed (C5-INV-003)."""
    source = Path(backup_path)
    target = Path(target_path)
    if target.exists():
        return {"outcome": "rejected", "reason": "restore target already exists"}
    try:
        payload = source.read_bytes()
        if not payload.startswith(_BACKUP_MAGIC):
            # 旧版无版本标记格式（无 KDF/MAC）一律拒绝，beta 不做兼容
            return {"outcome": "rejected", "reason": "unsupported backup format: pre-NOBAK2 backups cannot be restored"}
        header_len = len(_BACKUP_MAGIC) + _SALT_LEN + _NONCE_LEN
        if len(payload) < header_len + _TAG_LEN:
            return {"outcome": "rejected", "reason": "key mismatch or corrupted backup"}
        salt = payload[len(_BACKUP_MAGIC):len(_BACKUP_MAGIC) + _SALT_LEN]
        nonce = payload[len(_BACKUP_MAGIC) + _SALT_LEN:header_len]
        tag = payload[header_len:header_len + _TAG_LEN]
        ciphertext = payload[header_len + _TAG_LEN:]
        enc_key, mac_key = _derive_keys(key, salt)
        expected_tag = hmac.new(mac_key, payload[:header_len] + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected_tag):
            return {"outcome": "rejected", "reason": "key mismatch or corrupted backup"}
        plaintext = _xor(ciphertext, _keystream(enc_key, nonce, len(ciphertext)))
        target.write_bytes(plaintext)
    except (OSError, ValueError):
        if target.exists():
            target.unlink()
        return {"outcome": "rejected", "reason": "key mismatch or corrupted backup"}
    restored_sha = _sha256(target.read_bytes())
    return {
        "outcome": "restored",
        "receipt": {
            "restore_id": "restore:" + target.name,
            "backup_sha256": _sha256(payload),
            "restored_db_sha256": restored_sha,
            "byte_identical": True,
        },
    }


def build_deletion_receipt(
    target_ref: str,
    requested_at: str,
    policy: Mapping[str, str],
    fail_component: str | None = None,
) -> JsonObject:
    """Honest eight-component deletion receipt (PRD section 534, C5-INV-004)."""
    components: JsonObject = {}
    for name in _DELETION_COMPONENTS:
        if name == fail_component:
            components[name] = "failed"
        elif name == "backup":
            components[name] = policy.get("backup", "pending_expiry")
        elif name == "export_copy":
            components[name] = policy.get("export_copy", "out_of_control")
        elif name == "minimal_audit_proof":
            components[name] = "retained"
        else:
            components[name] = "deleted"
    partial = any(value == "failed" for value in components.values())
    return {
        "receipt_id": "deletion:" + target_ref,
        "target_ref": target_ref,
        "requested_at": requested_at,
        "components": components,
        "overall": "partial_failure" if partial else "deleted",
        "claimed_deleted": not partial,
    }
