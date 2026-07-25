# Implementation Plan：C4 Scenario & Action

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-C-C4-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-C-SCENARIO-001` |
| Decision | `DEC-MVP-C-SCENARIO-001` |
| Contract | `SPEC-C4-SCENARIO-001` v0.1 |
| ADR / Architecture | `ADR-0016` / `ARCH-C4-SCENARIO-001`（`C4_SCENARIO_ACTION_ARCHITECTURE.md`） |
| Suite | `tests/c4_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型；零 schema 变更（ADR-0016）。
- 所有写入入口必须显式 `confirmed=True`；未确认/非法引用/未选择即跟进一律显式 `rejected` 且零写入。
- 情景 `assertion_kind` 恒 `predicted`；feasibility 为声明约束的确定性纯函数；不生成建议文案。
- 跟进历史只追加（revision_history + ledger 收据）；`missed` 只 Derived 纯计算。
- 每个 Task 结束运行定向检查；只有 `C4-TASK-003` 可以运行 C4 official runner。
- 固定 synthetic profile `c4_scenario_action_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `C4-TASK-001` | `scenarios.py` 七入口（create/select/follow-ups/complete/view/present/upgrade-reject） | §2/§3/§5/§6、`C4-001..009` | 七入口语义与合同一致；定向窄测试通过 | `completed`；定向 5/5 passed，见 `c4-task001-20260726.json` |
| `C4-TASK-002` | `c4_testing_adapter.py` 与 C4 contract 集成 | §7/§8、`C4-001..010` | adapter 完整实现 protocol；fixture/oracle 不被修改；C4-010 横切通过 | `completed`；contract 10/10 passed（adapter），oracle 两处 forbidden_mutations 设计修正（见 `c4-task002-20260726.json` notes） |
| `C4-TASK-003` | C4 official runner、existing regression 与 immutable result | §7/§8 | C4 10/10 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `completed`；`c4-20260726.json` 10/10 current/passed，19 validators PASSED，回归 377 OK 0 skip，见 `c4-task003-20260726.json` |
| `C4-TASK-004` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `completed`；Gate Review `C4_SCENARIO_GATE_REVIEW_2026-07-26.md` P0=0/P1=0，recovery tag `c4-scenario-action-rp-20260726` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `C4-TASK-001` | `src/noetide_micro/scenarios.py`、窄范围 tests |
| `C4-TASK-002` | `src/noetide_micro/c4_testing_adapter.py` |
| `C4-TASK-003` | C4 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `C4-TASK-004` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
C4-TASK-001 -> C4-TASK-002 -> C4-TASK-003 -> C4-TASK-004
```

任何 Task 若需要改变 C4 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`C4-TASK-003` 另外执行 C4 official runner、既有 suite validator、全量 semantic regression、privacy boundary scan。未执行 C4 runner 前，C4 只能保持 `not_executed`。
