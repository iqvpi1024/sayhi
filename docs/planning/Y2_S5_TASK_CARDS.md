# Y2-S5 任务卡

## Y2S5-TASK-001：MCP Runtime 核心

- 范围：`src/noetide_micro/mcp_runtime.py`（McpRuntime、McpService、envelope、capability gate、read/propose/append、idempotency、audit、stdlib/loopback 静态扫描）。
- SPEC：`SPEC-Y2S5-MCP-RUNTIME-001` §2-§6；`ADR-0024`。
- 测试：`tests/semantic/test_y2s5_mcp_runtime_unit.py` 定向覆盖 default closed、denied profile、minimal read、propose-only、append-only、idempotency、irreversible denied、large file、endpoint/loopback、stdlib 扫描。
- 完成条件：定向全过；`python -m unittest discover -s tests -t .` 回归无退化（Y2S5 contract 10 skipped 属预期）。

## Y2S5-TASK-002：Testing Adapter

- 范围：`src/noetide_micro/y2s5_testing_adapter.py` 完整实现 `create_system/run_case/layer_snapshot`；临时目录 + fixture source + 127.0.0.1 MCP service；fixture clock；profile fail closed。
- SPEC：合同 §7；adapter protocol。
- 完成条件：contract 10/10 passed（`NOETIDE_Y2S5_ADAPTER=noetide_micro.y2s5_testing_adapter`）；fixture/oracle/manifest 未修改。

## Y2S5-TASK-003：Official Runner 与绑定

- 范围：`python -m tests.runner.run_y2s5_suite --adapter noetide_micro.y2s5_testing_adapter --output docs/testing/results/y2s5-20260803.json`；manifest flags 翻真并绑定 result 哈希；全量 regression（21 个 adapter 环境变量）0 skip；全部 suite validator。
- 完成条件：同一次 run 10/10 passed/current；immutable result 入库。

## Y2S5-TASK-004：Gate Review 与恢复点

- 范围：`docs/reviews/Y2_S5_MCP_RUNTIME_GATE_REVIEW_2026-08-03.md`；annotated tag `y2s5-mcp-runtime-rp-20260803` 推送；PROJECT_STATE/HANDOFF/矩阵 §4.25 状态更新。
- 完成条件：P0=0/P1=0；tag 可解析、远端可验证。
