# B4 Reconciliation 与 Semantic Diff Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-B4-RECONCILIATION-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-B-RECONCILIATION-001` |
| ADR | `ADR-0011` |

## 结构

```text
Canonical (objects / assertions / revision ledger)
  |                            |
  | (read-only)                | (read-only snapshot pair)
  v                            v
reconciliation.run_reconciliation      semantic_diff.compute_diff
  |  incremental: 4 finding kinds      |  field-level recursive compare
  |  deep: 3 partition rebuild         v
  |  via production projectors         SemanticDiff (in-memory only,
  v                                    never persisted / evidence)
ReconciliationReport (read-only derived,
quarantined_reported only, no repair write)
```

- 检测器与 diff 模块只读：无 Canonical/L2 写入依赖；fixture 异常注入由测试 adapter 完成。
- 深度对账逐分区（person_card / relationship_timeline / current_state）在隔离临时 store 用生产 projector + 固定 clock 重建，规范化 digest 比较，绝不回写。
- 报告与 diff 是 Derived：不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。
- 对账自身失败返回 unavailable 报告壳，不以空报告冒充无发现。
- 删除/隔离 Derived 不影响 Canonical、Source 与 revision ledger 可读性。
