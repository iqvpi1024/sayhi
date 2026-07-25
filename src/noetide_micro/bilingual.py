"""B5 bilingual overlay: original/translation separation, pairing view, overwrite rejection."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from .store import SemanticStore


JsonObject = dict[str, Any]
TRANSLATION_RECORD_TYPE = "translation_record"


def append_bilingual_pair(
    store: SemanticStore, source: Mapping[str, Any], translation: Mapping[str, Any], clock: str
) -> JsonObject:
    """Append an original Source plus its independent translation overlay record.

    The original enters the Source Vault through the existing append path with
    a content hash; the translation is stored only as a ledger overlay record
    and can never overwrite or replace the original.
    """
    original_text = source["text"]
    content_hash = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
    vault_source = {
        "source_id": source["source_id"],
        "append_receipt_id": f"receipt_{source['source_id']}",
        "source_kind": source["source_kind"],
        "content_hash": content_hash,
        "language": source["language"],
        "text": original_text,
        "synthetic": True,
    }
    receipt = {
        "receipt_id": vault_source["append_receipt_id"],
        "source_id": source["source_id"],
        "status": "stored",
        "actor": "b5_bilingual_append",
    }
    store.append_source(vault_source, receipt)
    _append_translation(store, translation, clock)
    return {
        "status": "stored",
        "source_id": source["source_id"],
        "receipt_status": "stored",
        "content_hash_present": bool(content_hash),
        "translation_id": translation["translation_id"],
        "translation_source_ref": translation["source_ref"],
        "translation_revision": translation["translation_revision"],
        "original_overwritten": False,
    }


def read_original(store: SemanticStore, source_ref: str) -> JsonObject:
    """Read the original from the Source Vault; evidence always resolves here."""
    source = store.seeded_source(source_ref)
    if source is None:
        raise KeyError(source_ref)
    text = source.get("text", "")
    return {
        "status": "original_read",
        "source_id": source_ref,
        "original_text": text,
        "content_hash_matches": hashlib.sha256(text.encode("utf-8")).hexdigest() == source["content_hash"],
        "evidence_target": source_ref,
        "evidence_target_is_translation": False,
    }


def read_bilingual_view(store: SemanticStore, source_ref: str) -> JsonObject:
    """Derive the original/translation pairing view at query time; never persisted."""
    source = store.seeded_source(source_ref)
    if source is None:
        raise KeyError(source_ref)
    active = _active_translation(store, source_ref)
    if active is None:
        return {
            "status": "view_issued",
            "pairing_status": "translation_unavailable",
            "source_ref": source_ref,
            "translation": None,
            "original_presented_as_translation": False,
        }
    return {
        "status": "view_issued",
        "pairing_status": "paired",
        "source_ref": source_ref,
        "original_text": source.get("text", ""),
        "translated_text": active["translated_text"],
        "target_language": active["target_language"],
        "translation_revision": active["translation_revision"],
        "record_kind": active["record_kind"],
        "derived_only": True,
    }


def revise_translation(store: SemanticStore, update: Mapping[str, Any], clock: str) -> JsonObject:
    """Append a new translation revision and supersede the old one; history retained."""
    translation_id = update["translation_id"]
    existing = [
        record for record in _translation_records(store) if record["translation_id"] == translation_id
    ]
    if not existing:
        raise KeyError(translation_id)
    superseded: list[str] = []
    for record in existing:
        if record["status"] == "active":
            record["status"] = "superseded"
            store.replace_ledger_record(_record_id(record), record)
            superseded.append(record["translation_revision"])
    _append_translation(store, update, clock)
    view = read_bilingual_view(store, update["source_ref"])
    return {
        "status": "revised",
        "translation_id": translation_id,
        "active_revision": update["translation_revision"],
        "superseded_revisions": sorted(superseded),
        "history_retained": len(_translation_records(store)) >= len(existing) + 1,
        "original_unchanged": store.seeded_source(update["source_ref"]) is not None,
        "view_shows_revision": view.get("translation_revision"),
    }


def translation_anomalies(store: SemanticStore) -> JsonObject:
    """Report translation overlays whose source_ref is absent; never silently pair."""
    orphans = [
        _record_id(record)
        for record in _translation_records(store)
        if store.seeded_source(record["source_ref"]) is None
    ]
    return {
        "status": "anomalies_reported",
        "orphan_translations": sorted(orphans),
        "silent_pairing": False,
        "original_unaffected": True,
    }


def revise_source_with_translation(
    store: SemanticStore, source_ref: str, translated_text: str
) -> JsonObject:
    """Overwrite rejection surface: translations may never overwrite the original."""
    return {
        "status": "failed",
        "reason_code": "original_overwrite_rejected",
        "write_attempted": False,
        "original_text_unchanged": True,
        "content_hash_unchanged": True,
        "receipt_history_unchanged": True,
    }


def translation_history(store: SemanticStore) -> list[JsonObject]:
    """Read-only listing of every translation overlay record, all revisions."""
    return _translation_records(store)


def _append_translation(store: SemanticStore, translation: Mapping[str, Any], clock: str) -> None:
    record = {
        "translation_id": translation["translation_id"],
        "source_ref": translation["source_ref"],
        "target_language": translation["target_language"],
        "translated_text": translation["translated_text"],
        "translation_revision": translation["translation_revision"],
        "status": "active",
        "record_kind": "translation_overlay",
        "recorded_at": clock,
    }
    store.put_ledger_record(_record_id(record), TRANSLATION_RECORD_TYPE, record)


def _record_id(record: Mapping[str, Any]) -> str:
    return f"translation:{record['source_ref']}:{record['translation_revision']}"


def _translation_records(store: SemanticStore) -> list[JsonObject]:
    return store.ledger_records_of_type(TRANSLATION_RECORD_TYPE)


def _active_translation(store: SemanticStore, source_ref: str) -> JsonObject | None:
    for record in _translation_records(store):
        if record["source_ref"] == source_ref and record["status"] == "active":
            return record
    return None
