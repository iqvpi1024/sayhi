# Implementation Plan：A3 实体合并候选与拆分回滚

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-A3-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-A-ENTITY-MERGE-001` |
| Decision | `DEC-MVP-A-ENTITY-MERGE-001` |
| Contract | `SPEC-A3-ENTITY-MERGE-001` v0.1 |
| ADR / Architecture | `ADR-0007` / `ARCH-A3-ENTITY-MERGE-001` |
| Suite | `tests/a3_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型。
- merge/split 只经既有 ChangeSet 边界在单事务内原子发布；`merge_records` 只增不改。
- 每个 Task 结束运行定向检查；只有 `A3-TASK-004` 可以运行 A3 official runner。
- 固定 synthetic profile `a3_entity_merge_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `A3-TASK-001` | store 的 merge_records 持久化辅助（表、写入/读取、只增不改） | §2、§6、`A3-001/006` | merge_record 原子写入、完整读取、PRAGMA 行为可测 | `completed`；定向 5/5 passed，regression 156 OK（8 A3 contract skipped） |
| `A3-TASK-002` | `entity_merge.py`：merge/split ChangeSet 服务（preflight、原子重定向、split 等价恢复、fail closed） | §2-§7、`A3-001..008` | 原子性可注入失败证明；split 逐字段恢复等价；trust/closeness/人格不变 | `completed`；定向 5/5 passed，regression 161 OK（8 A3 contract skipped） |
| `A3-TASK-003` | `a3_testing_adapter.py` 与 A3 contract 集成 | §8-§9、`A3-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改 | `completed`；contract 8/8 passed（adapter），regression 169 OK 无 skip |
| `A3-TASK-004` | A3 official runner、existing regression 与 immutable result | §8-§9 | A3 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `completed`；`a3-20260724.json` 8/8 current/passed，regression 169 OK |
| `A3-TASK-005` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `completed`；Gate Review P0=0/P1=0，见 `docs/reviews/A3_ENTITY_MERGE_GATE_REVIEW_2026-07-24.md` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `A3-TASK-001` | `src/noetide_micro/schema.sql`、`src/noetide_micro/store.py`、窄范围 store tests |
| `A3-TASK-002` | `src/noetide_micro/entity_merge.py`、必要 store glue、窄范围 tests |
| `A3-TASK-003` | `src/noetide_micro/a3_testing_adapter.py` |
| `A3-TASK-004` | A3 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `A3-TASK-005` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
A3-TASK-001 -> A3-TASK-002 -> A3-TASK-003 -> A3-TASK-004 -> A3-TASK-005
```

任何 Task 若需要改变 A3 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`A3-TASK-004` 另外执行 A3 official runner、Micro/A1/B1/B2/B3/C1/A2/Synthetic Ingestion/Context Pack validator、全量 semantic regression、privacy boundary scan。未执行 A3 runner 前，A3 只能保持 `not_executed`。
