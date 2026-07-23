# Implementation Plan：A4 查询层权限与舱室强制执行

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-A4-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-A-ACCESS-POLICY-001` |
| Decision | `DEC-MVP-A-ACCESS-POLICY-001` |
| Contract | `SPEC-A4-ACCESS-POLICY-001` v0.1 |
| ADR / Architecture | `ADR-0008` / `ARCH-A4-ACCESS-POLICY-001` |
| Suite | `tests/a4_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库；判决器为纯函数，只读对象策略标注，不写任何表。
- PolicyDecision 不持久化；Grant 由 fixture 注入；时间求值只比较 `requested_at` 与 Grant 固定窗口。
- 每个 Task 结束运行定向检查；只有 `A4-TASK-004` 可以运行 A4 official runner。
- 固定 synthetic profile `a4_access_policy_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `A4-TASK-001` | store 只读策略标注与 digest 辅助 | §2、`A4-001/007` | 对象标注只读可测；digest 前后一致可断言 | `done` (2026-07-24) |
| `A4-TASK-002` | `access_policy.py` 纯函数判决器（Grant 有效性、交集/并集、sealed、fail closed、零写入） | §2-§6、`A4-001..008` | 全部 reason_code 与字段集确定；判决不产生 revision | `done` (2026-07-24) |
| `A4-TASK-003` | `a4_testing_adapter.py` 与 A4 contract 集成 | §7-§8、`A4-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改 | `pending` |
| `A4-TASK-004` | A4 official runner、existing regression 与 immutable result | §7-§8 | A4 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `A4-TASK-005` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `A4-TASK-001` | `src/noetide_micro/store.py`（只读辅助）、窄范围 store tests |
| `A4-TASK-002` | `src/noetide_micro/access_policy.py`、窄范围 tests |
| `A4-TASK-003` | `src/noetide_micro/a4_testing_adapter.py` |
| `A4-TASK-004` | A4 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `A4-TASK-005` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
A4-TASK-001 -> A4-TASK-002 -> A4-TASK-003 -> A4-TASK-004 -> A4-TASK-005
```

任何 Task 若需要改变 A4 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`A4-TASK-004` 另外执行 A4 official runner、其余 10 个 suite validator、全量 semantic regression、privacy boundary scan。未执行 A4 runner 前，A4 只能保持 `not_executed`。
