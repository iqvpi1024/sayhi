# Implementation Plan：B2 Episode 与分层摘要

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-B-B2-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| Decision | `DEC-MVP-B-EPISODE-SUMMARY-001` |
| Contract | `SPEC-B2-EPISODE-SUMMARY-001` v0.1 |
| ADR / Architecture | `ADR-0004` / `ARCH-B2-EPISODE-SUMMARY-001` |
| Suite | `tests/b2_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型。
- Episode 的 Canonical 写入经现有 ChangeSet 边界；summary 只写 Derived 表，绝不成为 evidence。
- 每个 Task 结束运行定向检查；只有 `B2-TASK-005` 可以运行 B2 official runner。
- 固定 synthetic profile 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `B2-TASK-001` | schema/store 的 Episode 与 Derived summary logical layer | §4、§7、`B2-001/002/005/008` | foreign key、PRAGMA、migration/idempotent seed 行为可测 | `completed` |
| `B2-TASK-002` | `episodes.py` 的 fixed candidate 校验与 ChangeSet publish/revert | §4-§9、`B2-001/002/004/008` | 直接 Source/Entity/time refs 校验；无半写；补偿后历史保留 | `completed`；定向 5/5 passed，见 `b2-task002-6944b22-20260719.json` |
| `B2-TASK-003` | `summaries.py` 的 deterministic projector/reader | §4-§13、`B2-003/004/005/006/007` | fresh/stale/unavailable 与 dependency/rebuild 边界满足合同 | `pending` |
| `B2-TASK-004` | `b2_testing_adapter.py` 与 B2 contract 集成 | §17、`B2-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改 | `pending` |
| `B2-TASK-005` | B2 official runner、existing regression 与 immutable result | §17、§19 | B2 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `B2-TASK-006` | Gate Review、状态/追踪、Recovery Point | Process §6-§7 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `B2-TASK-001` | `src/noetide_micro/schema.sql`、`src/noetide_micro/store.py`、窄范围 store tests |
| `B2-TASK-002` | `src/noetide_micro/episodes.py`、必要 ChangeSet/store glue、窄范围 tests |
| `B2-TASK-003` | `src/noetide_micro/summaries.py`、必要 store glue、窄范围 tests |
| `B2-TASK-004` | `src/noetide_micro/b2_testing_adapter.py` |
| `B2-TASK-005` | B2 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `B2-TASK-006` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
B2-TASK-001 -> B2-TASK-002 -> B2-TASK-003 -> B2-TASK-004 -> B2-TASK-005 -> B2-TASK-006
```

任何 Task 若需要改变 B2 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`B2-TASK-005` 另外执行 B2 official runner、Micro/A1/B1/C1/Synthetic Ingestion/Context Pack validator、全量 semantic regression、privacy boundary scan。未执行 B2 runner 前，B2 只能保持 `not_executed`。
