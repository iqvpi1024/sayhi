# Implementation Plan：A6 MVP-A 硬化与本地 Alpha

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-A6-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-A-HARDENING-001` |
| Decision | `DEC-MVP-A-HARDENING-001` |
| Contract | `SPEC-A6-HARDENING-001` v0.1 |
| ADR / Architecture | `ADR-0010` / `ARCH-A6-HARDENING-001` |
| Suite | `tests/a6_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库；不引入第三方依赖、打包器、容器或网络能力。
- 集成执行不削弱、不替代任何已 verified suite 的独立证据；fixture/oracle/scenarios/contract module 物化后冻结，不得为迎合 implementation 修改。
- 壳层错误恢复面只复用已验证核心语义（S3 原子回滚、L2 fallback），不新增恢复语义、不新增绕过 ChangeSet 的写入路径。
- 每个 Task 结束运行定向检查；只有 `A6-TASK-005` 可以运行 A6 official runner。
- 固定 synthetic profile `a6_hardening_v1` 与 Reference Profile `a6_mvp_a_reference_v1`；不触碰真实数据和用户未跟踪目录；`devdata/` 仅合成用途。
- SLO 观测仅记录实际值并绑定 profile，不外推、不用于性能调优承诺。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `A6-TASK-001` | `start.py` D0 入口与错误恢复壳面（runtime 检查、devdata 根、init/migrate、preflight+smoke、`--clean` 前缀校验、db corrupt/unwritable 固定表面） | `A6-013/014/015/018`；`A6-INV-003` | 干净启动 exit 0；损坏库拒绝启动非零退出不静默修复；不可写目录不越界写；`--clean` 只删声明合成根 | `completed`（2026-07-25，`a6-task001-20260725`） |
| `A6-TASK-002` | Alpha 可解释性支撑：数据路径发现、备份+校验清单、导出 Round Trip（复用 CP）、卸载语义（默认保留数据、删除独立确认） | `A6-019/020`；`A6-INV-005` | 备份产物+校验清单可验证；导出 Round Trip 成立；默认卸载不删数据目录 | `completed`（2026-07-25，`a6-task002-20260725`） |
| `A6-TASK-003` | 集成旅程组装支撑：共享 reference profile 系统所需的运行时编排辅助（seed、journey 步骤、conflict probe、merge/split、restricted query、cross-cutting audit 辅助、SLO 计时收集） | `A6-001..012/016/017/021` | 组装辅助只调用已验证核心能力；无新恢复/权限/候选生成语义 | `completed`（2026-07-25，`a6-task003-20260725`） |
| `A6-TASK-004` | `a6_testing_adapter.py` 完整实现 adapter protocol，contract 21/21 passed（adapter） | `A6-001..021` | adapter 完整实现 protocol；fixture/oracle 不被修改；全量 regression 无 skip 无退化 | `pending` |
| `A6-TASK-005` | A6 official runner、existing regression 与 immutable result | `A6-001..021` | 21/21 同一次 run passed/current；环境戳记与 profile 绑定完整；13 个 suite validator PASSED；manifest 正确绑定 result | `pending` |
| `A6-TASK-006` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `A6-TASK-001` | `start.py`、必要的 `store.py` 只读损坏检测窄改动、窄范围 tests |
| `A6-TASK-002` | `src/noetide_micro/alpha_explainability.py`（或并入既有模块的窄辅助）、`cli.py` 窄接线、窄范围 tests |
| `A6-TASK-003` | `src/noetide_micro/a6_journey.py`（编排辅助，只读/委托核心）、窄范围 tests |
| `A6-TASK-004` | `src/noetide_micro/a6_testing_adapter.py`、窄范围 tests |
| `A6-TASK-005` | `docs/testing/results/a6-*.json`、`tests/a6_suite_manifest.json`（仅绑定字段） |
| `A6-TASK-006` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
A6-TASK-001 -> A6-TASK-002 -> A6-TASK-003 -> A6-TASK-004 -> A6-TASK-005 -> A6-TASK-006
```

任何 Task 若需要改变 A6 contract、fixture/oracle/scenarios 的产品语义，停止并回到 Change Control；不得继续下一个 Task。FR-003 生成侧已知限制（合同 §1.1）不得在本切片内被静默补写。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`A6-TASK-005` 另外执行 A6 official runner、其余 12 个 suite validator、全量 semantic regression、privacy boundary scan、环境戳记与 ADR-0010 §5.3 一致性检查。未执行 A6 runner 前，A6 只能保持 `not_executed`。
