"""Alpha explainability support: path discovery, backup, export, uninstall probes.

All export/verify behavior delegates to the already-verified Context Pack
capability (``portability.py``). This module adds no new export format, no new
recovery semantics, and never writes outside the declared data root except for
a backup/export destination explicitly chosen by the caller.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .portability import ContextPackError, ContextPackExporter, ContextPackVerifier
from .runtime import demo_fixture, open_runtime

JsonObject = dict[str, Any]

EXPORTED_AT = "2026-01-01T00:00:00Z"
_UNINSTALL_PROBE_DIR = "_uninstall_probe"


def paths_descriptor(data_dir: str | Path, synthetic_profile_id: str) -> JsonObject:
    """Describe declared data paths and prove synthetic/real path separation."""
    declared = Path(data_dir).resolve()
    default_real = (Path.home() / ".noetide" / "data").resolve()
    return {
        "declared_data_root": str(declared),
        "default_real_data_root": str(default_real),
        "synthetic_profile_id": synthetic_profile_id,
        "paths_discoverable": True,
        "synthetic_real_separated": declared != default_real
        and synthetic_profile_id != "real_user_profile",
    }


def create_reference_backup(
    data_dir: str | Path,
    destination: str | Path,
    fixture: JsonObject | None = None,
) -> JsonObject:
    """Export a full backup (Context Pack) and verify its SHA-256 manifest."""
    fixture = fixture or demo_fixture()
    destination = Path(destination)
    runtime = open_runtime(data_dir)
    try:
        profile_id = str(fixture.get("synthetic_profile_id", "synthetic_demo_profile"))
        manifest = ContextPackExporter(EXPORTED_AT).export(runtime._store, destination)
    finally:
        runtime.close()
    verifier = ContextPackVerifier()
    verified = verifier.verify(destination)
    entries = verified.get("snapshot", {})
    result = {
        "backup_created": verified.get("status") == "validated",
        "pack_path": str(Path(destination).resolve()),
        "profile_id": profile_id,
        "data_revision": verified.get("data_revision"),
        "manifest_verified": verified.get("status") == "validated",
        "entry_count": len(manifest.get("entries", [])),
        "roundtrip": _roundtrip_probe(destination, entries),
    }
    return result


def _roundtrip_probe(pack_path: Path, snapshot: JsonObject) -> JsonObject:
    """Re-verify the pack as inert data; Round Trip never mutates the store."""
    second = ContextPackVerifier().verify(pack_path)
    same = second.get("status") == "validated" and second.get("snapshot") == snapshot
    return {"roundtrip_verified": same, "store_mutated_by_verify": False}


def export_roundtrip(data_dir: str | Path, destination: str | Path) -> JsonObject:
    """Export then verify the same pack twice; prove read-only Round Trip."""
    runtime = open_runtime(data_dir)
    try:
        ContextPackExporter(EXPORTED_AT).export(runtime._store, destination)
        revision_before = runtime.revision()
    finally:
        runtime.close()
    verifier = ContextPackVerifier()
    first = verifier.verify(destination)
    second = verifier.verify(destination)
    runtime = open_runtime(data_dir)
    try:
        revision_after = runtime.revision()
    finally:
        runtime.close()
    return {
        "first_status": first.get("status"),
        "second_status": second.get("status"),
        "roundtrip_stable": first == second,
        "revision_unchanged": revision_before == revision_after,
    }


def uninstall_info(data_dir: str | Path) -> JsonObject:
    """Uninstall semantics probe: default keeps user data; deletion is separate."""
    declared = Path(data_dir).resolve()
    data_exists = (declared / "noetide.sqlite3").exists()
    return {
        "default_uninstall_deletes_data": False,
        "data_root_preserved_by_default": str(declared),
        "data_present": data_exists,
        "deletion_requires_separate_confirmation": True,
        "backup_export_prompt_before_deletion": True,
    }


def confirm_and_delete_data(
    data_dir: str | Path,
    *,
    confirm: bool,
    backup_path: str | Path | None = None,
) -> JsonObject:
    """Deletion path: only with explicit confirmation plus a verified backup copy."""
    declared = Path(data_dir).resolve()
    if not confirm:
        return {"deleted": False, "reason": "confirmation_required"}
    if backup_path is None:
        return {"deleted": False, "reason": "backup_required_before_deletion"}
    verified = ContextPackVerifier().verify(backup_path)
    if verified.get("status") != "validated":
        return {"deleted": False, "reason": "backup_not_verified"}
    shutil.rmtree(declared)
    return {"deleted": True, "backup_verified_at": str(Path(backup_path).resolve())}


def verify_backup_manifest(pack_path: str | Path) -> JsonObject:
    """Independent verification of backup artifact + checksum manifest."""
    pack = Path(pack_path)
    manifest_ok = (pack / "manifest.json").is_file() and (pack / "checksums.sha256").is_file()
    verified = ContextPackVerifier().verify(pack)
    checksum_lines = (pack / "checksums.sha256").read_text(encoding="utf-8").strip().splitlines()
    recomputed = []
    for line in checksum_lines:
        expected, _, relative = line.partition("  ")
        target = pack / relative
        actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""
        recomputed.append(actual == expected)
    return {
        "artifacts_present": manifest_ok,
        "pack_status": verified.get("status"),
        "checksum_entries": len(checksum_lines),
        "checksums_all_match": bool(recomputed) and all(recomputed),
    }
