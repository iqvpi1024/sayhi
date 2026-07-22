# Implementation Plan：B3 Commitment 与 Derived due-status

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-B-B3-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-B-COMMITMENT-001` |
| Decision | `DEC-MVP-B-COMMITMENT-001` |
| Contract | `SPEC-B3-COMMITMENT-001` v0.1 |
| ADR / Architecture | `ADR-0005` / `ARCH-B3-COMMITMENT-001` |
| Suite | `tests/b3_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型/后台调度。
- Commitment 的 Canonical 写入经现有 ChangeSet 边界；due_status 只写 Derived 表，绝不进入 Canonical、Evidence Ref 或 ChangeSet trigger。
- 每个 Task 结束运行定向检查；只有 `B3-TASK-005` 可以运行 B3 official runner。
- 固定 synthetic profile `b3_commitment_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `B3-TASK-001` | schema/store 的 Commitment 与 Derived due projection logical layer | §2、§5、`B3-001/002` | foreign key、PRAGMA、重复初始化行为可测 | `completed`；定向 5/5 passed，见 `b3-task001-20260722.json` |
| `B3-TASK-002` | `commitments.py` 的 fixed candidate 校验与 ChangeSet publish/complete/cancel/revert | §2-§6、`B3-001/002/004/005/006` | direct locator 校验；cancel 必须带原因；无半写；补偿后历史保留 | `pending` |
| `B3-TASK-003` | `due_status.py` 的 deterministic projector/reader | §3-§7、`B3-003/004/007/008` | upcoming/due/overdue/closed 确定性；stale/unavailable；Derived 不作证 | `pending` |
| `B3-TASK-004` | `b3_testing_adapter.py` 与 B3 contract 集成 | §7-§8、`B3-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改 | `pending` |
| `B3-TASK-005` | B3 official runner、existing regression 与 immutable result | §7-§8 | B3 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `B3-TASK-006` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `B3-TASK-001` | `src/noetide_micro/schema.sql`、`src/noetide_micro/store.py`、窄范围 store tests |
| `B3-TASK-002` | `src/noetide_micro/commitments.py`、必要 ChangeSet/store glue、窄范围 tests |
| `B3-TASK-003` | `src/noetide_micro/due_status.py`、必要 store glue、窄范围 tests |
| `B3-TASK-004` | `src/noetide_micro/b3_testing_adapter.py` |
| `B3-TASK-005` | B3 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `B3-TASK-006` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
B3-TASK-001 -> B3-TASK-002 -> B3-TASK-003 -> B3-TASK-004 -> B3-TASK-005 -> B3-TASK-006
```

任何 Task 若需要改变 B3 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`B3-TASK-005` 另外执行 B3 official runner、Micro/A1/B1/B2/C1/Synthetic Ingestion/Context Pack validator、全量 semantic regression、privacy boundary scan。未执行 B3 runner 前，B3 只能保持 `not_executed`。
