# B3 Commitment Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-B3-COMMITMENT-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-B-COMMITMENT-001` |
| ADR | `ADR-0005` |

```text
fixed synthetic candidate
  -> Commitment ChangeSet service
  -> Canonical Commitment + Revision Ledger
  -> DueStatus projector (fixed clock)
  -> Derived reader
```

- ChangeSet service 是唯一 Canonical 写入入口。
- Projector 不写 Canonical，不读取 summary/receipt 作事实，不触发通知或外部行动。
- Reader 返回 fresh、stale 或 unavailable；不得把旧 due-status 伪装为当前。
- 删除 Derived 只影响 projection/receipt，Canonical、Source 和 Ledger 保持可读。
