"""Deterministic local folder text import for the Y2-S1 slice (SPEC-Y2S1-FOLDER-IMPORT-001).

Reads `.md`/`.txt` files from a logical root and appends them to the Source Vault
via the existing append-only write path. No semantic inference, no Canonical writes,
no wall-clock: every timestamp comes from the injected `now` or file metadata.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]

ALLOWED_PROFILES = frozenset({"y2s1_folder_import_v1"})
DEFAULT_EXTENSIONS = (".md", ".txt")
SOURCE_KIND = "folder_text_import"
SOURCE_SYSTEM = "folder_importer_v1"


class ProfileRejectedError(ValueError):
    """Raised when the importer is constructed with an unknown profile (fail closed)."""

    def __init__(self, profile: str) -> None:
        super().__init__(f"unknown profile: {profile}")
        self.profile = profile


def _iso_utc(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat()


class FolderImporter:
    """Batch-import text files from one logical root into the Source Vault."""

    def __init__(
        self,
        store: SemanticStore,
        now: str,
        *,
        profile: str = "y2s1_folder_import_v1",
        root_ref: str = "diary_root_v1",
        language: str = "unknown",
        extensions: tuple[str, ...] = DEFAULT_EXTENSIONS,
        fail_hook: Callable[[int], None] | None = None,
    ) -> None:
        if profile not in ALLOWED_PROFILES:
            raise ProfileRejectedError(profile)
        self._store = store
        self._now = now
        self._profile = profile
        self._root_ref = root_ref
        self._language = language
        self._extensions = tuple(ext.lower() for ext in extensions)
        self._fail_hook = fail_hook

    def import_folder(
        self,
        root: Path,
        extra_entries: list[Mapping[str, Any]] | None = None,
    ) -> JsonObject:
        """Import one folder tree; returns a deterministic ImportReport (Derived, not persisted)."""
        root = Path(root)
        report: JsonObject = {
            "files_seen": 0, "stored": 0, "duplicate": 0, "rejected": 0, "skipped": 0,
            "receipts": [], "rejections": [], "skipped_paths": [], "duplicate_of": {},
        }
        scanned = self._scan(root)
        for index, candidate in enumerate(scanned):
            self._run_hook(index)
            self._import_scanned(root, candidate, report)
        for entry in extra_entries or []:
            self._import_explicit(root, entry, report)
        report["skipped_paths"] = sorted(report["skipped_paths"])
        return report

    def _run_hook(self, index: int) -> None:
        if self._fail_hook is not None:
            self._fail_hook(index)

    def _scan(self, root: Path) -> list[Path]:
        """Lexically sorted file candidates; link-to-dir entries are descended once."""
        found: list[Path] = []
        stack: list[Path] = [root]
        seen_dirs: set[str] = set()
        while stack:
            current = stack.pop()
            key = os.path.normcase(str(current))
            if key in seen_dirs:
                continue
            seen_dirs.add(key)
            try:
                entries = sorted(os.scandir(current), key=lambda item: item.name)
            except OSError:
                continue
            for entry in entries:
                entry_path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False) or entry.is_dir(follow_symlinks=True):
                    stack.append(entry_path)
                elif entry.is_file(follow_symlinks=False) or entry.is_file(follow_symlinks=True):
                    found.append(entry_path)
        return sorted(found, key=lambda path: path.relative_to(root).as_posix())

    def _import_scanned(self, root: Path, path: Path, report: JsonObject) -> None:
        relative = path.relative_to(root).as_posix()
        report["files_seen"] += 1
        resolved = path.resolve()
        root_resolved = root.resolve()
        if not self._is_relative_to(resolved, root_resolved):
            self._reject(report, relative, "symlink_escape")
            return
        if path.suffix.lower() not in self._extensions:
            report["skipped"] += 1
            report["skipped_paths"].append(relative)
            return
        self._import_file(path, relative, report)

    def _import_explicit(self, root: Path, entry: Mapping[str, Any], report: JsonObject) -> None:
        raw = str(entry.get("path", ""))
        report["files_seen"] += 1
        kind = str(entry.get("kind", ""))
        if kind == "relative_traversal" or ".." in Path(raw).parts:
            self._reject(report, raw, "path_traversal")
            return
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = Path(entry.get("base", "")) / candidate if entry.get("base") else candidate
        resolved = candidate.resolve()
        if not self._is_relative_to(resolved, root.resolve()):
            self._reject(report, raw, "path_outside_root")
            return
        self._reject(report, raw, "path_outside_root")

    @staticmethod
    def _is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def _reject(self, report: JsonObject, entry: str, failure: str) -> None:
        report["rejected"] += 1
        report["rejections"].append({"entry": entry, "failure": failure})

    def _import_file(self, path: Path, relative: str, report: JsonObject) -> None:
        try:
            payload = path.read_bytes()
        except OSError:
            self._reject(report, relative, "storage_failure")
            return
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            self._reject(report, relative, "invalid_utf8")
            return
        digest = hashlib.sha256(payload).hexdigest()
        source_id = f"src_folder_{digest[:16]}"
        existing = self._store.seeded_source(source_id)
        if existing is not None:
            report["duplicate"] += 1
            report["duplicate_of"][relative] = source_id
            report["receipts"].append({"relative_path": relative, "status": "duplicate", "source_id": source_id})
            return
        source_created_at = _iso_utc(path.stat().st_mtime)
        source: JsonObject = {
            "source_id": source_id,
            "append_receipt_id": f"receipt_{source_id}",
            "source_kind": SOURCE_KIND,
            "source_system": SOURCE_SYSTEM,
            "inline_content": text,
            "content_hash": digest,
            "byte_length": len(payload),
            "source_created_at": source_created_at,
            "ingested_at": self._now,
            "language": self._language,
            "source_timezone": "unknown",
            "locator_scheme": "file_path_v1",
            "locator": {"root_ref": self._root_ref, "relative_path": relative},
            "coverage_window": {
                "start": source_created_at, "end": source_created_at, "continuous": True, "gaps": [],
            },
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared",
            "owner_ref": "synthetic_owner_001",
            "subject_refs": [],
            "recorder_ref": "synthetic_owner_001",
            "sensitivity": "private",
            "compartments": ["personal"],
            "third_party_present": "unknown",
            "retention_policy_ref": "user_controlled_v1",
            "retention_state": "active",
            "review_status": "unreviewed",
        }
        receipt: JsonObject = {
            "receipt_id": f"receipt_{source_id}",
            "source_id": source_id,
            "status": "stored",
            "hash_algorithm": "sha256",
            "content_hash": digest,
            "byte_length": len(payload),
            "media_type": "text/plain; charset=utf-8",
            "ingested_at": self._now,
            "locator_scheme": "file_path_v1",
            "coverage_raw_status": "present",
            "policy_profile_ref": "owner_intake_private_v1",
            "policy_resolution_status": "declared",
            "effective_policy": {"sensitivity": "private", "compartments": ["personal"]},
            "failure": None,
            "actor": SOURCE_SYSTEM,
        }
        try:
            self._store.append_source(source, receipt)
        except sqlite3.Error:
            self._reject(report, relative, "storage_failure")
            return
        report["stored"] += 1
        report["receipts"].append({"relative_path": relative, "status": "stored", "source_id": source_id})


class FolderWatcher:
    """Explicit single-shot poll watcher; no threads, timers or OS events."""

    def __init__(self, importer: FolderImporter) -> None:
        self._importer = importer

    def poll(self, root: Path) -> JsonObject:
        """Import only files whose content hash is not yet in the vault."""
        store = self._importer._store
        seen = store.source_hashes_by_kind(SOURCE_KIND)
        candidates = self._importer._scan(Path(root))
        report: JsonObject = {"stored": 0, "duplicate": 0}
        for index, candidate in enumerate(candidates):
            self._importer._run_hook(index)
            if candidate.suffix.lower() not in self._importer._extensions:
                continue
            resolved = candidate.resolve()
            if not FolderImporter._is_relative_to(resolved, Path(root).resolve()):
                continue
            try:
                payload = candidate.read_bytes()
            except OSError:
                continue
            digest = hashlib.sha256(payload).hexdigest()
            if digest in seen:
                report["duplicate"] += 1
                continue
            sub_report: JsonObject = {
                "files_seen": 0, "stored": 0, "duplicate": 0, "rejected": 0, "skipped": 0,
                "receipts": [], "rejections": [], "skipped_paths": [], "duplicate_of": {},
            }
            self._importer._import_file(candidate, candidate.relative_to(root).as_posix(), sub_report)
            report["stored"] += sub_report["stored"]
            report["duplicate"] += sub_report["duplicate"]
        return report
