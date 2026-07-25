# Implementation Plan：B6 Shadow Migration 与压测消歧传播

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-B-B6-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-B-SHADOW-MIGRATION-001` |
| Decision | `DEC-MVP-B-SHADOW-MIGRATION-001` |
| Contract | `SPEC-B6-SHADOW-MIGRATION-001` v0.1 |
| ADR / Architecture | `ADR-0013` / `ARCH-B6-MIGRATION-001`（`B6_SHADOW_MIGRATION_ARCHITECTURE.md`） |
| Suite | `tests/b6_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型。
- 原始库物理只读：影子为文件级副本；失败影子只能 discarded；迁移不打开原始库写事务。
- 计数断言全部为确定性计数；不做 wall-clock SLO；候选绝不自动合并。
- 每个 Task 结束运行定向检查；只有 `B6-TASK-004` 可以运行 B6 official runner。
- 固定 synthetic profile `b6_shadow_migration_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `B6-TASK-001` | `shadow_migration.py`：文件级影子副本、v1->v2 变换、故障注入、迁移后对账 | §2.1/§3/§6、`B6-001..004/008/009` | 三分区 match；transform_log 计数确定；故障零部分写入；历史随迁移完整 | `completed`；定向 9/9 passed（含 TASK-002），见 `b6-task001-20260725.json` |
| `B6-TASK-002` | `disambiguation.py`：候选扫描、合并传播、批量处理 | §2.2/§2.3/§5、`B6-005..007` | 候选对 12 且全 proposed；传播 2 计数确定；batches=3 processed=12 可复现 | `completed`；定向 9/9 passed（含 TASK-001），见 `b6-task002-20260725.json` |
| `B6-TASK-003` | `b6_testing_adapter.py` 与 B6 contract 集成 | §7/§8、`B6-001..010` | adapter 完整实现 protocol；fixture/oracle 不被修改；B6-010 横切通过 | `pending` |
| `B6-TASK-004` | B6 official runner、existing regression 与 immutable result | §7/§8 | B6 10/10 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `B6-TASK-005` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `B6-TASK-001` | `src/noetide_micro/shadow_migration.py`、窄范围 tests |
| `B6-TASK-002` | `src/noetide_micro/disambiguation.py`、窄范围 tests |
| `B6-TASK-003` | `src/noetide_micro/b6_testing_adapter.py` |
| `B6-TASK-004` | B6 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `B6-TASK-005` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
B6-TASK-001 -> B6-TASK-002 -> B6-TASK-003 -> B6-TASK-004 -> B6-TASK-005
```

任何 Task 若需要改变 B6 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`B6-TASK-004` 另外执行 B6 official runner、既有 suite validator、全量 semantic regression、privacy boundary scan。未执行 B6 runner 前，B6 只能保持 `not_executed`。
