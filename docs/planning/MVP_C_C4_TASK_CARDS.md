# C4 Scenario & Action Task Cards

Plan：`PLAN-MVP-C-C4-IMPL-001`；Contract：`SPEC-C4-SCENARIO-001` v0.1；ADR：`ADR-0016`。

## C4-TASK-001 scenarios 模块

- 交付：`scenarios.py` 七入口（create_scenario_set/select_scenario/create_follow_ups/complete_follow_up/follow_up_view/present_scenario/attempt_mark_observed）。
- 合同：§2 字段、§3 状态机、§5 不变量、§6 失败语义；feasibility 纯函数；missed Derived 纯计算；全部 confirmed-only。
- 禁止：自动生成、评分算法、建议文案、Canonical 自动写入、未确认写入。
- 验证：import/syntax、定向窄测试（创建/拒绝/选择/跟进/完成/missed/呈现/upgrade 拒绝）、`git diff --check`。

## C4-TASK-002 C4 testing adapter

- 交付：`c4_testing_adapter.py` 实现 `tests/runner/c4_scenario_adapter_protocol.py`；fixture 播种 + scenario 分发 + layer 快照。
- 合同：§7/§8；C4-001..010 全场景；fixture/oracle 零修改。
- 验证：`NOETIDE_C4_ADAPTER=noetide_micro.c4_testing_adapter python -m unittest tests.semantic.test_c4_scenario_contract` 10/10。

## C4-TASK-003 official runner 与绑定

- 交付：`python -m tests.runner.run_c4_suite --adapter noetide_micro.c4_testing_adapter --output docs/testing/results/c4-20260726.json`；manifest flags 与哈希绑定；全量回归与 19 validators。
- 禁止：为通过而修改 oracle/fixture。

## C4-TASK-004 Gate Review 与 Recovery Point

- 交付：Gate Review（逐不变量正反证明，P0/P1=0）、矩阵 §4.18 状态、PROJECT_STATE、CURRENT_HANDOFF、PRD hash 校验、recovery tag。
- 顺序：Gate Review 通过后才允许 commit/tag/push。
