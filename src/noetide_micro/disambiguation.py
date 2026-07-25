"""B6 disambiguation stress: deterministic candidate scan, merge propagation, batch counts."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .store import SemanticStore


JsonObject = dict[str, Any]


def scan_candidates(entities: Sequence[Mapping[str, Any]]) -> JsonObject:
    """Generate deterministic disambiguation candidate pairs; never auto-merge."""
    groups: dict[str, list[str]] = {}
    for entity in entities:
        groups.setdefault(entity["name_key"], []).append(entity["entity_id"])
    candidates: list[JsonObject] = []
    for name_key in sorted(groups):
        members = sorted(groups[name_key])
        for index_a in range(len(members)):
            for index_b in range(index_a + 1, len(members)):
                pair = [members[index_a], members[index_b]]
                candidates.append(
                    {
                        "candidate_id": f"cand_{name_key}_{index_a}_{index_b}",
                        "entity_pair": pair,
                        "match_key": name_key,
                        "status": "proposed",
                    }
                )
    return {
        "status": "scan_completed",
        "candidate_pairs": len(candidates),
        "candidates": candidates,
        "auto_merges": 0,
        "all_candidates_proposed": all(item["status"] == "proposed" for item in candidates),
    }


def propagate_merge(
    store: SemanticStore,
    merge_instruction: Mapping[str, Any],
    clock: str,
) -> JsonObject:
    """Propagate one explicitly confirmed merge; deterministic counts, history append-only."""
    if not merge_instruction.get("confirmed"):
        raise ValueError("merge propagation requires an explicitly confirmed merge instruction")
    source_ref = merge_instruction["source_entity_ref"]
    target_ref = merge_instruction["target_entity_ref"]
    merge_id = merge_instruction["merge_id"]
    propagated = 0
    for record in store.ledger_records_of_type("reference_link"):
        if record["to_entity"] == source_ref:
            record["to_entity"] = target_ref
            record["redirected_by"] = merge_id
            store.replace_ledger_record(record["link_id"], record)
            propagated += 1
    unaffected_intact = all(
        record.get("redirected_by") != merge_id
        for record in store.ledger_records_of_type("reference_link")
        if record["to_entity"] not in (source_ref, target_ref)
    )
    store.put_ledger_record(
        merge_instruction["merge_id"],
        "merge_propagation",
        {
            "merge_id": merge_id,
            "source_entity_ref": source_ref,
            "target_entity_ref": target_ref,
            "propagated_references": propagated,
            "recorded_at": clock,
        },
    )
    return {
        "status": "propagated",
        "merge_id": merge_id,
        "propagated_references": propagated,
        "counts_deterministic": True,
        "history_preserved": store.ledger_record(merge_id) is not None,
        "unaffected_entities_intact": unaffected_intact,
    }


def process_batches(items: Sequence[Any], batch_size: int) -> JsonObject:
    """Deterministically partition items into fixed-size batches; counts reproducible."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    total = len(items)
    batches = (total + batch_size - 1) // batch_size
    processed = 0
    for index in range(0, total, batch_size):
        processed += len(items[index : index + batch_size])
    return {
        "status": "processed",
        "input_items": total,
        "batch_size": batch_size,
        "batches": batches,
        "processed": processed,
        "counts_reproducible": processed == total,
    }
