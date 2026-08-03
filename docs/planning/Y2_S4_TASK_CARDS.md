# Y2-S4 任务卡

## Y2S4-TASK-001：云端授权门与编排器核心

- 范围：`src/noetide_micro/cloud_model.py`（CloudGate、脱敏 preview、Ledger audit、CloudFixtureBackend、CloudHttpBackend、CloudModelCurator、stdlib 静态扫描）。
- SPEC：`SPEC-Y2S4-CLOUD-MODEL-001` §2-§6；`ADR-0023`。
- 测试：`tests/semantic/test_y2s4_cloud_model_unit.py` 定向覆盖默认关闭、红线、授权匹配、preview、审计、版本、endpoint 校验、静态扫描。
- 完成条件：定向全过；`python -m unittest discover -s tests -t .` 回归无退化（Y2S4 contract 10 skipped 属预期）。

## Y2S4-TASK-002：Testing Adapter

- 范围：`src/noetide_micro/y2s4_testing_adapter.py` 完整实现 `create_system/run_case/layer_snapshot`；临时目录 + fixture source + loopback stub；fixture clock；profile fail closed。
- SPEC：合同 §7；adapter protocol。
- 完成条件：contract 10/10 passed（`NOETIDE_Y2S4_ADAPTER=noetide_micro.y2s4_testing_adapter`）；fixture/oracle/manifest 未修改。

## Y2S4-TASK-003：Official Runner 与绑定

- 范围：`python -m tests.runner.run_y2s4_suite --adapter noetide_micro.y2s4_testing_adapter --output docs/testing/results/y2s4-20260803.json`；manifest flags 翻真并绑定 result 哈希；全量 regression（20 个 adapter 环境变量）0 skip；全部 suite validator。
- 完成条件：同一次 run 10/10 passed/current；immutable result 入库。

## Y2S4-TASK-004：Gate Review 与恢复点

- 范围：`docs/reviews/Y2_S4_CLOUD_MODEL_GATE_REVIEW_2026-08-03.md`；annotated tag `y2s4-cloud-model-rp-20260803` 推送；PROJECT_STATE/HANDOFF/矩阵 §4.24 状态更新。
- 完成条件：P0=0/P1=0；tag 可解析、远端可验证。
