"""Private, synthetic Context Pack v1 export and dry-run verification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .store import SemanticStore


PACK_SCHEMA_VERSION = "noetide.context-pack.v1"
_LAYER_FILES = ("sources.json", "canonical.json", "ledger.json", "README.md")


class ContextPackError(ValueError):
    pass


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or "\\" in value or path.is_absolute() or path.drive or any(part in {"", ".", ".."} for part in path.parts):
        raise ContextPackError("unsafe content_ref")
    return path


class ContextPackExporter:
    """Exports canonical layers without mutating the semantic store."""

    def __init__(self, exported_at: str) -> None:
        self.exported_at = exported_at

    def export(self, store: SemanticStore, destination: str | Path) -> dict[str, Any]:
        root = Path(destination)
        if root.exists():
            raise ContextPackError("pack destination already exists")
        snapshot = store.portability_snapshot()
        root.mkdir(parents=True)
        contents = {
            "sources.json": _json_bytes({"schema_version": PACK_SCHEMA_VERSION, "records": snapshot["sources"]}),
            "canonical.json": _json_bytes({"schema_version": PACK_SCHEMA_VERSION, "data_revision": snapshot["data_revision"], "objects": snapshot["canonical"]}),
            "ledger.json": _json_bytes({"schema_version": PACK_SCHEMA_VERSION, "records": snapshot["ledger"]}),
            "README.md": self._readme(snapshot).encode("utf-8"),
        }
        entries = []
        for relative in _LAYER_FILES:
            payload = contents[relative]
            (root / relative).write_bytes(payload)
            entries.append({"entry_id": relative, "logical_layer": "derived" if relative == "README.md" else relative.removesuffix(".json"), "content_ref": relative, "media_type": "text/markdown" if relative.endswith(".md") else "application/json", "byte_length": len(payload), "hash_algorithm": "sha256", "content_hash": _sha256(payload)})
        manifest = {"schema_version": PACK_SCHEMA_VERSION, "data_revision": snapshot["data_revision"], "exported_at": self.exported_at, "export_scope": "owner_private_synthetic", "entries": entries}
        manifest_bytes = _json_bytes(manifest)
        (root / "manifest.json").write_bytes(manifest_bytes)
        checksums = "".join(f"{entry['content_hash']}  {entry['content_ref']}\n" for entry in entries)
        (root / "checksums.sha256").write_text(checksums, encoding="utf-8", newline="\n")
        return manifest

    def _readme(self, snapshot: Mapping[str, Any]) -> str:
        return (
            "# Noetide Context Pack\n\n"
            "This is an owner-private synthetic export. Structured JSON is authoritative; this file is explanatory only.\n\n"
            f"- Data revision: `{snapshot['data_revision']}`\n"
            f"- Source records: {len(snapshot['sources'])}\n"
            f"- Canonical objects: {len(snapshot['canonical'])}\n"
            f"- Ledger records: {len(snapshot['ledger'])}\n"
            "- Derived projections are not evidence and are intentionally excluded.\n"
        )


class ContextPackVerifier:
    """Validates a Pack as inert data and never writes to SQLite."""

    def verify(self, root: str | Path, current_revision: str | None = None) -> dict[str, Any]:
        pack_root = Path(root).resolve()
        try:
            manifest_path = pack_root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("schema_version") != PACK_SCHEMA_VERSION or not isinstance(manifest.get("entries"), list):
                return {"status": "rejected_schema"}
            for entry in manifest["entries"]:
                relative = _safe_relative(entry.get("content_ref", ""))
                target = (pack_root / relative).resolve()
                if pack_root not in target.parents or not target.is_file():
                    return {"status": "rejected_path"}
                data = target.read_bytes()
                if entry.get("hash_algorithm") != "sha256" or entry.get("byte_length") != len(data) or entry.get("content_hash") != _sha256(data):
                    return {"status": "rejected_hash_mismatch"}
            canonical = json.loads((pack_root / "canonical.json").read_text(encoding="utf-8"))
            sources = json.loads((pack_root / "sources.json").read_text(encoding="utf-8"))
            ledger = json.loads((pack_root / "ledger.json").read_text(encoding="utf-8"))
            if not all(isinstance(value, dict) for value in (canonical, sources, ledger)):
                return {"status": "rejected_schema"}
        except (OSError, json.JSONDecodeError, ContextPackError, TypeError):
            return {"status": "rejected_path"}
        revision = manifest["data_revision"]
        relation = "unknown" if current_revision is None else ("current" if revision == current_revision else "historical")
        return {"status": "validated", "data_revision": revision, "pack_relation": relation, "snapshot": {"sources": sources["records"], "canonical": canonical["objects"], "ledger": ledger["records"]}}
