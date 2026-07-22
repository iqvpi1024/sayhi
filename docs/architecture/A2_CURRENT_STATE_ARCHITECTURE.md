# A2 current_state Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-A2-CURRENT-STATE-001` |
| Status | `Accepted` |
| ADR | `ADR-0006` |
| Contract | `SPEC-A2-CURRENT-STATE-001` |

## 分层

```text
Source Vault (合成 Source, 只增)
Canonical Context (entity/relationship/state/assertion + revisions, 仅经 ChangeSet)
Revision Ledger (changeset/receipt/audit, 只增)
Derived Layer
  - projection_rows[view_name=current_state]  (fresh/stale/updating/unavailable)
  - rebuild receipts (非证据)
Read Path: Reader -> fresh 投影 | stale/unavailable 显式标记（不伪装 current）
```

## 数据流

1. Canonical 经既有 ChangeSet 发布新 revision。
2. Projector 以当前 revision + fixture clock 计算当前有效对象集合，写入/替换 `current_state` 投影行并保存 receipt。
3. Reader 仅当 `data_revision == view_revision == 当前 revision` 返回 fresh payload；否则返回显式 stale/unavailable 状态。
4. 删除投影后，Projector 仅从 Canonical 与 Source 重算，payload 逐字段等价。

## 边界

- 无网络、无模型、无后台任务、无 UI、无权限 runtime。
- 投影内容不参与 Canonical 写入、Evidence Ref、Assertion input 或 ChangeSet trigger。
- fixture clock 推进不产生 revision；只有 ChangeSet 能推进全局 revision。
