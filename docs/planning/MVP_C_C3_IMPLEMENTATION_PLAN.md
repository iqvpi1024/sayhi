# Implementation Plan：C3 Review & Calibration

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-C-C3-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-C-REVIEW-001` |
| Decision | `DEC-MVP-C-REVIEW-001` |
| Contract | `SPEC-C3-REVIEW-001` v0.1 |
| ADR / Architecture | `ADR-0015` / `ARCH-C3-REVIEW-001`（`C3_REVIEW_CALIBRATION_ARCHITECTURE.md`） |
| Suite | `tests/c3_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型；零 schema 变更（ADR-0015）。
- 报告与比较只写 `ledger_records`（record_type=`review_report`/`phase_comparison`）；绝不写 Canonical 层。
- 指标与 delta 为 Canonical payload 的确定性纯函数；不读 Derived 行作为输入。
- 历史版本 append-only 保留；删除只经 ADR-0015 的窄方法 `delete_ledger_record`；重建 metrics 与同 Canonical 时点等价。
- 非法比较（指标集不一致、kind/长度不同、日期倒置、未知窗口）一律显式 `rejected` 且零写入。
- 每个 Task 结束运行定向检查；只有 `C3-TASK-003` 可以运行 C3 official runner。
- 固定 synthetic profile `c3_review_calibration_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `C3-TASK-001` | `reviews.py`：generate/present/rebuild/delete/compare 五入口 + `store.delete_ledger_record` | §2/§3/§5/§6、`C3-001..008` | 五入口语义与合同一致；定向窄测试通过 | `completed`；定向 5/5 passed，回归 362 OK（C3 contract skipped），见 `c3-task001-20260726.json` |
| `C3-TASK-002` | `c3_testing_adapter.py` 与 C3 contract 集成 | §7/§8、`C3-001..010` | adapter 完整实现 protocol；fixture/oracle 不被修改；C3-010 横切通过 | `completed`；contract 10/10 passed（adapter），oracle 一处人工计数修正（见 `c3-task002-20260726.json` notes） |
| `C3-TASK-003` | C3 official runner、existing regression 与 immutable result | §7/§8 | C3 10/10 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `completed`；`c3-20260726.json` 10/10 current/passed，18 validators PASSED，回归 362 OK 0 skip，见 `c3-task003-20260726.json` |
| `C3-TASK-004` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `completed`；Gate Review `C3_REVIEW_GATE_REVIEW_2026-07-26.md` P0=0/P1=0，recovery tag `c3-review-calibration-rp-20260726` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `C3-TASK-001` | `src/noetide_micro/reviews.py`、`store.py`（仅新增 `delete_ledger_record`）、窄范围 tests |
| `C3-TASK-002` | `src/noetide_micro/c3_testing_adapter.py` |
| `C3-TASK-003` | C3 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `C3-TASK-004` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
C3-TASK-001 -> C3-TASK-002 -> C3-TASK-003 -> C3-TASK-004
```

任何 Task 若需要改变 C3 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`C3-TASK-003` 另外执行 C3 official runner、既有 suite validator、全量 semantic regression、privacy boundary scan。未执行 C3 runner 前，C3 只能保持 `not_executed`。
