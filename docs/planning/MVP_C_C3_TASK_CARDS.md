# C3 Review & Calibration Task Cards

Plan：`PLAN-MVP-C-C3-IMPL-001`；Contract：`SPEC-C3-REVIEW-001` v0.1；ADR：`ADR-0015`。

## C3-TASK-001 reviews 模块与 store 窄删除

- 交付：`reviews.py` 五入口（generate_review/present_review/rebuild_review/delete_review/compare_phases）；`store.delete_ledger_record(record_id)`。
- 合同：§2 字段、§3 状态机、§5 不变量、§6 失败语义；窗口半开区间；view_revision=现存最大+1；freshness=窗口输入 digest 纯函数。
- 禁止：Canonical 写入、Derived 输入读取、自动重写历史报告、因果/趋势文案。
- 验证：import/syntax、定向窄测试（窗口归属、计数、stale、版本链、删除重建、非法比较拒绝）、`git diff --check`。

## C3-TASK-002 C3 testing adapter

- 交付：`c3_testing_adapter.py` 实现 `tests/runner/c3_review_adapter_protocol.py`；fixture 播种 + scenario 分发 + layer 快照。
- 合同：§7/§8；C3-001..010 全场景；fixture/oracle 零修改。
- 验证：`NOETIDE_C3_ADAPTER=noetide_micro.c3_testing_adapter python -m unittest tests.semantic.test_c3_review_contract` 10/10。

## C3-TASK-003 official runner 与绑定

- 交付：`python -m tests.runner.run_c3_suite --adapter noetide_micro.c3_testing_adapter --output docs/testing/results/c3-20260726.json`；manifest flags 与哈希绑定；全量回归与 18 validators。
- 禁止：为通过而修改 oracle/fixture。

## C3-TASK-004 Gate Review 与 Recovery Point

- 交付：Gate Review（逐不变量正反证明，P0/P1=0）、矩阵 §4.17 状态、PROJECT_STATE、CURRENT_HANDOFF、PRD hash 校验、recovery tag。
- 顺序：Gate Review 通过后才允许 commit/tag/push。
