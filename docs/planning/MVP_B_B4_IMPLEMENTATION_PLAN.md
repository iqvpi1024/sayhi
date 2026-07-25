# Implementation Plan：B4 Reconciliation 与 Semantic Diff

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-B-B4-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-B-RECONCILIATION-001` |
| Decision | `DEC-MVP-B-RECONCILIATION-001` |
| Contract | `SPEC-B4-RECONCILIATION-001` v0.1 |
| ADR / Architecture | `ADR-0011` / `ARCH-B4-RECONCILIATION-001` |
| Suite | `tests/b4_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型/后台调度。
- 对账检测器与 Semantic Diff 只读 Canonical、L2 投影与 revision ledger；绝不写入、修复或持久化派生结果；发现唯一终态 `quarantined_reported`。
- 深度对账逐分区（person_card / relationship_timeline / current_state）复用生产 projector 在隔离临时 store 重建比较；不整图重算、不回写。
- 每个 Task 结束运行定向检查；只有 `B4-TASK-005` 可以运行 B4 official runner。
- 固定 synthetic profile `b4_reconciliation_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `B4-TASK-001` | `reconciliation.py` 增量对账：运行状态机与四类发现检测 | §2.1/§3/§5、`B4-001..005` | 干净 profile 零发现；四类注入各检出且 `disposition=quarantined_reported`；无写入 | `completed`；定向 7/7 passed，见 `b4-task001-20260725.json` |
| `B4-TASK-002` | `reconciliation.py` 深度对账：三分区重建比较 | §2.1/§5/§6、`B4-006/007` | 逐分区 match/mismatch + digest 对；不回写、不整图重算 | `completed`；定向 11/11 passed（含 TASK-001 回归），见 `b4-task002-20260725.json` |
| `B4-TASK-003` | `semantic_diff.py` 查询时字段级 diff | §2.2/§5、`B4-008/009` | create/modify/no_change + before/after；不持久化；digest 前后不变；revision 缺失显式拒绝 | `completed`；定向 7/7 passed，见 `b4-task003-20260725.json` |
| `B4-TASK-004` | `b4_testing_adapter.py` 与 B4 contract 集成 | §7/§8、`B4-001..010` | adapter 完整实现 protocol；fixture/oracle 不被修改；B4-010 横切通过 | `pending` |
| `B4-TASK-005` | B4 official runner、existing regression 与 immutable result | §7/§8 | B4 10/10 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `B4-TASK-006` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `B4-TASK-001` | `src/noetide_micro/reconciliation.py`、窄范围 tests |
| `B4-TASK-002` | `src/noetide_micro/reconciliation.py`、窄范围 tests |
| `B4-TASK-003` | `src/noetide_micro/semantic_diff.py`、窄范围 tests |
| `B4-TASK-004` | `src/noetide_micro/b4_testing_adapter.py` |
| `B4-TASK-005` | B4 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `B4-TASK-006` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
B4-TASK-001 -> B4-TASK-002 -> B4-TASK-003 -> B4-TASK-004 -> B4-TASK-005 -> B4-TASK-006
```

任何 Task 若需要改变 B4 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`B4-TASK-005` 另外执行 B4 official runner、既有 13 套 suite validator、全量 semantic regression、privacy boundary scan。未执行 B4 runner 前，B4 只能保持 `not_executed`。
