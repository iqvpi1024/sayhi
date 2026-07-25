# Implementation Plan：A5 自然语言审查与最小可用应用壳

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-A5-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-A-APP-SHELL-001` |
| Decision | `DEC-MVP-A-APP-SHELL-001` |
| Contract | `SPEC-A5-APP-SHELL-001` v0.2 |
| ADR / Architecture | `ADR-0009` / `ARCH-A5-APP-SHELL-001` |
| Suite | `tests/a5_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库；呈现层为纯函数，只读 Candidate Envelope 与 Canonical 对象，不写任何表。
- 壳写路径只调用已验证核心能力（intake/candidate/changesets/views）；壳模块不出现 store 写方法调用。
- 每个 Task 结束运行定向检查；只有 `A5-TASK-004` 可以运行 A5 official runner。
- 固定 synthetic profile `a5_app_shell_v1`；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `A5-TASK-001` | `app_shell.py` 呈现层纯函数（NL review、impact preview、summary line）与零绕过静态扫描辅助 | §2-§5、`A5-002/003/008` | 呈现输出形状确定；壳模块无 store 写调用可静态证明 | `completed`（2026-07-24，`a5-task001-2320515-20260724`） |
| `A5-TASK-002` | 壳命令接线（cli.py 增加 guide/receipts/history 命令）与 `a5_testing_adapter.py` | §3、§7-§8、`A5-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改 | `completed`（2026-07-25，`a5-task002-310bcf2-20260725`） |
| `A5-TASK-003` | A5 contract 集成验证（NOETIDE_A5_ADAPTER 下 8/8） | §7-§8、`A5-001..008` | contract 8/8 passed | `completed`（2026-07-25，`a5-task003-a45a8bd-20260725`） |
| `A5-TASK-004` | A5 official runner、existing regression 与 immutable result | §7-§8 | A5 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `A5-TASK-005` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `A5-TASK-001` | `src/noetide_micro/app_shell.py`、窄范围 tests |
| `A5-TASK-002` | `src/noetide_micro/cli.py`、`src/noetide_micro/a5_testing_adapter.py`、窄范围 tests |
| `A5-TASK-003` | 无新实现文件；仅验证 |
| `A5-TASK-004` | A5 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `A5-TASK-005` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
A5-TASK-001 -> A5-TASK-002 -> A5-TASK-003 -> A5-TASK-004 -> A5-TASK-005
```

任何 Task 若需要改变 A5 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`A5-TASK-004` 另外执行 A5 official runner、其余 11 个 suite validator、全量 semantic regression、privacy boundary scan。未执行 A5 runner 前，A5 只能保持 `not_executed`。