# ADR-0007：A3 实体合并/拆分的审计记录与原子重定向机制

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Slice | `SLICE-MVP-A-ENTITY-MERGE-001` |
| Contract | `SPEC-A3-ENTITY-MERGE-001` |

## 决定

复用现有 Python 标准库 + SQLite runtime 与 ChangeSet Ledger。merge/split 作为显式 ChangeSet 在同一 SQLite 事务内原子发布：source Entity 状态更新、全部受影响引用（relationship_party/state_subject/assertion_subject）重定向与 `merge_records` 表写入同事务提交。`merge_records.pre_merge_references` 以 JSON 数组持久化合并时捕获的全部受影响引用（ref_kind、object_id、field、old_value），是 split compensation 的唯一恢复依据。

## 不采用的方案

- 拆分时不存 pre-merge snapshot、靠"反向推断"恢复引用：无法证明逐字段等价，且合并后新增引用会污染恢复结果。
- 用数据库 trigger 自动重定向：绕过 ChangeSet 边界，产生无用户确认的语义写入。
- 软删除 source Entity 行：违反历史永不删除与可审计要求。
- 独立的图数据库或事件溯源框架：超出固定合成切片范围。

## 后果与验证

- 原子性由现有单事务 + foreign key + `DELETE/FULL` PRAGMA 保证；注入失败时事务整体回滚，无部分重定向。
- `merge_records` 只增不改；split 不删除 merge 记录，历史链完整可审计。
- split 恢复后受影响对象 payload 与合并前逐字段一致，可由 suite 直接断言。
- A3 suite 必须证明：fail closed 集合、原子回滚、逐字段恢复等价、trust/closeness/人格判断不变、三个 Core View 显式 stale 或重建一致。
