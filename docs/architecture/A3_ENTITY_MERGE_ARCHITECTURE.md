# A3 Entity Merge/Split Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-A3-ENTITY-MERGE-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-A-ENTITY-MERGE-001` |
| ADR | `ADR-0007` |

```text
fixed synthetic merge/split proposal
  -> Entity Merge ChangeSet service
  -> single SQLite transaction:
       source identity_status=merged + merged_into
       + reference redirection (relationship_party/state_subject/assertion_subject)
       + merge_records (pre_merge_references)
  -> Canonical + Revision Ledger
  -> Core Views (person card / relationship timeline / current_state): stale or rebuilt

split compensation:
  -> new ChangeSet reading merge_records.pre_merge_references
  -> single transaction restoring original references + source identity_status=active
```

- ChangeSet service 是唯一 Canonical 写入入口；无 trigger、无后台任务。
- `merge_records` 是审计组成部分，只增不改，不作 Evidence Ref 替代。
- split 恢复等价以逐字段 payload 断言为准；合并后新增引用不属于恢复范围。
- 任何 fail closed 路径不产生 revision、不产生 `merge_records` 行。
