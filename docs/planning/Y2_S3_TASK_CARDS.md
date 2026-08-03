# Y2-S3 任务卡

## Y2S3-TASK-001：本地 Web 服务核心

- 范围：`src/noetide_micro/local_web.py`（`ThreadingHTTPServer`、回环绑定、HTML 页面、API 路由、export/backup 入口）、`runtime.store` 只读访问辅助、`cli.py web` 命令。
- SPEC：`SPEC-Y2S3-LOCAL-WEB-UI-001` §2-§5/§7；`ADR-0022`。
- 测试：`tests/semantic/test_y2s3_local_web_ui_unit.py` 定向覆盖回环绑定、页面语言、路由、导出只读、备份路径约束、静态零绕过。
- 完成条件：定向全过；`python -m unittest discover -s tests -t .` 回归无退化（Y2S3 contract 10 skipped 属预期）。

## Y2S3-TASK-002：Testing Adapter

- 范围：`src/noetide_micro/y2s3_testing_adapter.py` 完整实现 `create_system/run_case/layer_snapshot`；临时目录 + 127.0.0.1 stub server；HTTP 请求执行固定旅程；export/backup 断言；fixture clock；profile fail closed。
- SPEC：合同 §7；adapter protocol。
- 完成条件：contract 10/10 passed（`NOETIDE_Y2S3_ADAPTER=noetide_micro.y2s3_testing_adapter`）；fixture/oracle/manifest 未修改。

## Y2S3-TASK-003：Official Runner 与绑定

- 范围：`python -m tests.runner.run_y2s3_suite --adapter noetide_micro.y2s3_testing_adapter --output docs/testing/results/y2s3-20260803.json`；manifest flags 翻真并绑定 result 哈希；全量 regression（19 个 adapter 环境变量）0 skip；全部 suite validator。
- 完成条件：同一次 run 10/10 passed/current；immutable result 入库。

## Y2S3-TASK-004：Gate Review 与恢复点

- 范围：`docs/reviews/Y2_S3_LOCAL_WEB_UI_GATE_REVIEW_2026-08-03.md`；annotated tag `y2s3-local-web-ui-rp-20260803` 推送；PROJECT_STATE/HANDOFF/矩阵 §4.23 状态更新。
- 完成条件：P0=0/P1=0；tag 可解析、远端可验证。