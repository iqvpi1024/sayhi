# A5 任务卡（PLAN-MVP-A-A5-IMPL-001）

## A5-TASK-001：app_shell.py 呈现层纯函数

- 允许文件：`src/noetide_micro/app_shell.py`、`tests/semantic/test_a5_task_001_app_shell.py`。
- 交付：`render_review(changeset) -> nl_review_item`；`render_impact_preview(changeset) -> {will_create, will_modify, views_affected}`；`shell_write_scan() -> (allowed_calls, forbidden_calls)` 静态零绕过扫描辅助（扫描自身模块源码，断言无 store 写方法名）。
- 验证：Python import、定向 tests、PRAGMA 检查、`git diff --check`。
- 禁止：adapter、cli 接线、fixture/oracle 修改。

## A5-TASK-002：cli 接线与 a5_testing_adapter.py

- 允许文件：`src/noetide_micro/cli.py`、`src/noetide_micro/a5_testing_adapter.py`、`tests/semantic/test_a5_task_002_adapter.py`。
- 交付：cli 增加 `guide`（引导旅程）、`receipts`、`history` 命令；adapter 完整实现 `tests/runner/a5_app_shell_adapter_protocol.py`（create_system/run_case/layer_snapshot/inject_failure），支持 8 个 case。
- 验证：定向 tests、`NOETIDE_A5_ADAPTER` 下 contract 可运行。
- 禁止：修改 fixture/oracle/contract module。

## A5-TASK-003：contract 集成验证

- 允许文件：无新实现文件。
- 交付：`NOETIDE_A5_ADAPTER=noetide_micro.a5_testing_adapter` 下 contract 8/8 passed。
- 验证：contract module 全场景通过；回归无退化。
- 禁止：实现变更（如失败回到 TASK-001/002）。

## A5-TASK-004：official runner 与绑定

- 允许文件：`docs/testing/results/a5-*.json`、`tests/a5_suite_manifest.json`（仅绑定字段）。
- 交付：`python -m tests.runner.run_a5_suite --adapter noetide_micro.a5_testing_adapter --output docs/testing/results/a5-<date>.json` 同一次 run 8/8 passed/current；全量 configured-adapter regression；12 个 suite validator；manifest 绑定 current result。
- 禁止：修改 oracle 迎合 implementation。

## A5-TASK-005：Gate Review 与 Recovery Point

- 允许文件：review、状态、trace、release/recovery record。
- 交付：Gate Review P0/P1=0；PROJECT_STATE/矩阵/CURRENT_HANDOFF 同步；recovery tag `a5-app-shell-rp-<date>` 创建并推送。
- 禁止：移动任何既有 tag。