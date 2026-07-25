# B6 Shadow Migration 与压测消歧传播 Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-B6-SHADOW-MIGRATION-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-B-SHADOW-MIGRATION-001` |
| ADR | `ADR-0013` |

```text
original SQLite (read-only, never opened for write)
  -> file copy -> shadow SQLite
       -> v1_to_v2 deterministic transform (batched, transform_log counts)
       -> B4 deep reconciliation on shadow (3 partitions match/mismatch)
       -> reconciled | failed -> discarded
synthetic similar entities
  -> disambiguation.scan_candidates (name_key groups, C(n,2) pairs, all proposed, auto_merges=0)
explicit merge instruction
  -> disambiguation.propagate_merge (deterministic reference counts, history append-only)
bulk synthetic items
  -> disambiguation.process_batches (fixed batch_size, deterministic counts)
```

- 原始库物理只读：影子是文件级副本，失败可整体丢弃。
- 影子与压测报告是 Derived：不作 Canonical 证据。
- 未确认候选不因压力自动合并；bitemporal 历史随迁移逐条保留。
