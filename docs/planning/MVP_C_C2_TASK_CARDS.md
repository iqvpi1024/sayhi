# Task Cards：C2 Hypothesis Lifecycle

> 父计划：`PLAN-MVP-C-C2-IMPL-001`；合同：`SPEC-C2-HYPOTHESIS-001` v0.1；ADR：`ADR-0014`。

## C2-TASK-001：hypotheses.py 生命周期模块

- 交付物：`src/noetide_micro/hypotheses.py`（create_hypothesis / attach_evidence / transition_status / present_hypothesis / attempt_upgrade_to_fact）+ 窄范围定向测试。
- 验收：创建 rev=1 active；证据追加/迁移各递增 revision 并追加 revision_history 与 ledger 收据；未确认/非法引用/非法目标/upgrade 全部 rejected 零写入；display_tone 映射正确；auto_transitions 恒 0。
- 边界：不改 schema、不改 store 公共 API 语义、不实现自动生成。

## C2-TASK-002：c2_testing_adapter.py

- 交付物：`src/noetide_micro/c2_testing_adapter.py`，实现 `tests/runner/c2_hypothesis_adapter_protocol.py`。
- 验收：C2-001..010 contract 全通过（adapter 环境变量下）；fixture/oracle 未被修改；layer_snapshot 覆盖 source/entity/assertion/derived/hypothesis/revision_ledger 六层。

## C2-TASK-003：official runner 与回归

- 交付物：`docs/testing/results/c2-20260726.json`（immutable）、manifest 绑定、验证记录。
- 验收：同一次 run 10/10 passed/current；全量 regression 无 skip 无失败；全部既有 validator 通过；privacy boundary scan 通过。

## C2-TASK-004：Gate Review 与 Recovery Point

- 交付物：Gate Review（P0/P1=0）、PROJECT_STATE/CURRENT_HANDOFF/矩阵状态更新、recovery tag `c2-hypothesis-lifecycle-rp-20260726`、推送。
