# Implementation Plan：C2 Hypothesis Lifecycle

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-C-C2-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-C-HYPOTHESIS-001` |
| Decision | `DEC-MVP-C-HYPOTHESIS-001` |
| Contract | `SPEC-C2-HYPOTHESIS-001` v0.1 |
| ADR / Architecture | `ADR-0014` / `ARCH-C2-HYPOTHESIS-001`（`C2_HYPOTHESIS_LIFECYCLE_ARCHITECTURE.md`） |
| Suite | `tests/c2_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型；零 schema 变更（ADR-0014）。
- 所有规范写入必须显式 `confirmed=True`；未确认/非法引用/非法状态目标一律显式 `rejected` 且零写入。
- 模块内不存在任何自动状态迁移代码路径；`auto_transitions` 恒为 0。
- 状态迁移只追加（revision_history + canonical_revisions + ledger 收据），永不删除。
- 每个 Task 结束运行定向检查；只有 `C2-TASK-004` 可以运行 C2 official runner。
- 固定 synthetic profile `c2_hypothesis_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `C2-TASK-001` | `hypotheses.py`：创建、证据追加、状态迁移、呈现、upgrade 拒绝 | §2/§3/§5/§6、`C2-001..009` | 五个入口语义与合同一致；定向窄测试通过 | `completed`；定向 9/9 passed，回归 347 OK（C2 contract skipped），见 `c2-task001-20260726.json` |
| `C2-TASK-002` | `c2_testing_adapter.py` 与 C2 contract 集成 | §7/§8、`C2-001..010` | adapter 完整实现 protocol；fixture/oracle 不被修改；C2-010 横切通过 | `completed`；contract 10/10 passed（adapter），回归 347 OK 0 skip，见 `c2-task002-20260726.json` |
| `C2-TASK-003` | C2 official runner、existing regression 与 immutable result | §7/§8 | C2 10/10 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `completed`；`c2-20260726.json` 10/10 current/passed，17 validators PASSED，回归 347 OK 0 skip，见 `c2-task003-20260726.json` |
| `C2-TASK-004` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `completed`；Gate Review `C2_HYPOTHESIS_GATE_REVIEW_2026-07-26.md` P0=0/P1=0，recovery tag `c2-hypothesis-lifecycle-rp-20260726` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `C2-TASK-001` | `src/noetide_micro/hypotheses.py`、窄范围 tests |
| `C2-TASK-002` | `src/noetide_micro/c2_testing_adapter.py` |
| `C2-TASK-003` | C2 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `C2-TASK-004` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
C2-TASK-001 -> C2-TASK-002 -> C2-TASK-003 -> C2-TASK-004
```

任何 Task 若需要改变 C2 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`C2-TASK-003` 另外执行 C2 official runner、既有 suite validator、全量 semantic regression、privacy boundary scan。未执行 C2 runner 前，C2 只能保持 `not_executed`。
