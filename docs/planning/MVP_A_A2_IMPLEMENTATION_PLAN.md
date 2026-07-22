# Implementation Plan：A2 current_state Core View

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-A2-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-A-CURRENT-STATE-001` |
| Decision | `DEC-MVP-A-CURRENT-STATE-001` |
| Contract | `SPEC-A2-CURRENT-STATE-001` v0.1 |
| ADR / Architecture | `ADR-0006` / `ARCH-A2-CURRENT-STATE-001` |
| Suite | `tests/a2_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型/查询引擎。
- `current_state` 只写 Derived projection；Canonical 变更沿用既有 ChangeSet 边界；视图构建不产生新 revision。
- 每个 Task 结束运行定向检查；只有 `A2-TASK-004` 可以运行 A2 official runner。
- 固定 synthetic profile `a2_current_state_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `A2-TASK-001` | store 的 current_state 投影辅助（receipt 表、删除/stale 辅助） | §2、§5、`A2-001/006/007` | receipt 持久化、Derived 删除隔离、PRAGMA 行为可测 | `completed`；定向 5/5 passed，见 `a2-task001-20260722.json` |
| `A2-TASK-002` | `current_state.py` 的 projector/reader（fresh/stale/rebuild/失败降级/不作证） | §2-§7、`A2-001..008` | 当前有效判定确定；stale 不伪装；rebuild 等价；Derived 不作证 | `completed`；定向 6/6 passed，见 `a2-task002-20260722.json` |
| `A2-TASK-003` | `a2_testing_adapter.py` 与 A2 contract 集成 | §7-§8、`A2-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改 | `completed`；contract 8/8 passed（adapter），见 `a2-task003-20260722.json` |
| `A2-TASK-004` | A2 official runner、existing regression 与 immutable result | §7-§8 | A2 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `A2-TASK-005` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `A2-TASK-001` | `src/noetide_micro/schema.sql`、`src/noetide_micro/store.py`、窄范围 store tests |
| `A2-TASK-002` | `src/noetide_micro/current_state.py`、必要 store glue、窄范围 tests |
| `A2-TASK-003` | `src/noetide_micro/a2_testing_adapter.py` |
| `A2-TASK-004` | A2 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `A2-TASK-005` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
A2-TASK-001 -> A2-TASK-002 -> A2-TASK-003 -> A2-TASK-004 -> A2-TASK-005
```

任何 Task 若需要改变 A2 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`A2-TASK-004` 另外执行 A2 official runner、Micro/A1/B1/B2/B3/C1/Synthetic Ingestion/Context Pack validator、全量 semantic regression、privacy boundary scan。未执行 A2 runner 前，A2 只能保持 `not_executed`。
