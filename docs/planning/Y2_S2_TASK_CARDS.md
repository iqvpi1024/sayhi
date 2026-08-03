# Y2-S2 任务卡

## Y2S2-TASK-001：模型能力核心

- 范围：`src/noetide_micro/model_capability.py`（后端接口、FixtureModelBackend、LocalHttpBackend、ModelCurator、VersionRegistry、CandidateRegistry、异常）；仅复用现有 `SemanticStore` 读/ledger 原语，不新增 SQLite 表。
- SPEC：`SPEC-Y2S2-LOCAL-MODEL-001` §2-§6/§8；`ADR-0021` §1.1-1.7。
- 测试：`tests/semantic/test_y2s2_model_capability_unit.py` 定向覆盖四类候选、畸形输出、注入免疫、红线、版本与确认边界。
- 完成条件：定向全过；`python -m unittest discover -s tests -t .` 回归无退化（Y2S2 contract 10 skipped 属预期）。

## Y2S2-TASK-002：Testing Adapter

- 范围：`src/noetide_micro/y2s2_testing_adapter.py` 完整实现 `create_system/run_case/layer_snapshot`；临时目录物化 fixture source；fixture/local_http/cloud 探针；stub HTTP 服务；fixture clock；profile fail closed。
- SPEC：合同 §7；adapter protocol。
- 完成条件：contract 10/10 passed（`NOETIDE_Y2S2_ADAPTER=noetide_micro.y2s2_testing_adapter`）；fixture/oracle/manifest 未修改。

## Y2S2-TASK-003：Official Runner 与绑定

- 范围：`python -m tests.runner.run_y2s2_suite --adapter noetide_micro.y2s2_testing_adapter --output docs/testing/results/y2s2-20260803.json`；manifest flags 翻真并绑定 result 哈希；全量 regression（18 个 adapter 环境变量）0 skip；全部 suite validator。
- 完成条件：同一次 run 10/10 passed/current；immutable result 入库。

## Y2S2-TASK-004：Gate Review 与恢复点

- 范围：`docs/reviews/Y2_S2_LOCAL_MODEL_GATE_REVIEW_2026-08-03.md`；annotated tag `y2s2-local-model-rp-20260803` 推送；PROJECT_STATE/HANDOFF/矩阵 §4.22 状态更新。
- 完成条件：P0=0/P1=0；tag 可解析、远端可验证。