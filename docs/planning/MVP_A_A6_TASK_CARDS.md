# A6 任务卡（PLAN-MVP-A-A6-IMPL-001）

## A6-TASK-001：start.py D0 入口与错误恢复壳面

- 允许文件：`start.py`、`src/noetide_micro/store.py`（仅损坏检测窄改动）、`tests/semantic/test_a6_task_001_start.py`。
- 交付：`python start.py` 完成 runtime 版本检查（>=3.12）、创建合成数据根（默认 `<repo>/devdata/`，`--data-root` 覆盖）、初始化/迁移数据库并运行最小 preflight+smoke；成功 exit 0 并输出本地访问入口；`--clean` 仅在路径前缀校验通过后删除声明的合成根；数据库损坏时拒绝启动、非零退出、非泄露错误、不静默修复/覆盖原文件；数据目录不可写时非零退出、不越界写。
- 验证：Python import、定向 tests（干净启动/损坏库/不可写目录/clean 前缀校验）、PRAGMA 检查、`git diff --check`。
- 禁止：adapter、journey 编排、fixture/oracle 修改；网络访问；写入声明根以外路径。

## A6-TASK-002：Alpha 可解释性支撑

- 允许文件：`src/noetide_micro/alpha_explainability.py`、`src/noetide_micro/cli.py`（窄接线）、`tests/semantic/test_a6_task_002_explainability.py`。
- 交付：数据路径可发现（输出声明数据根，合成/真实路径分离可验证）；备份产物 + SHA-256 校验清单；导出 Round Trip（复用 Context Pack 已验证能力）；卸载语义探针（默认保留用户数据目录；删除需独立确认并提示备份/导出副本）。
- 验证：Python import、定向 tests、`git diff --check`。
- 禁止：新导出格式、真实数据路径写入、fixture/oracle 修改。

## A6-TASK-003：集成旅程组装支撑

- 允许文件：`src/noetide_micro/a6_journey.py`、`tests/semantic/test_a6_task_003_journey.py`。
- 交付：共享 reference profile 系统的编排辅助：seed 固定合成数据、journey 步骤（record/review/preview/confirm/read_views/receipt/history/revert）、conflict probe、merge/split 循环、restricted query 探针、cross-cutting audit 辅助（trust/closeness/personality/history 不变断言辅助）、SLO 计时收集（绑定 `a6_mvp_a_reference_v1`）；全部只调用已验证核心能力（intake/candidate/changesets/views/answer/access/merge），不新增恢复/权限/候选生成语义。
- 验证：Python import、定向 tests（编排辅助形状与零新语义）、PRAGMA 检查、`git diff --check`。
- 禁止：adapter、修改 fixture/oracle、补写 FR-003 生成侧规则。

## A6-TASK-004：a6_testing_adapter.py

- 允许文件：`src/noetide_micro/a6_testing_adapter.py`、`tests/semantic/test_a6_task_004_adapter.py`。
- 交付：adapter 完整实现 `tests/runner/a6_hardening_adapter_protocol.py`（create_system/run_scenario/layer_snapshot/inject_failure），支持 21 个 case；sandbox 场景使用隔离实例不动共享状态；`NOETIDE_A6_ADAPTER=noetide_micro.a6_testing_adapter` 下 contract 21/21 passed。
- 验证：定向 tests、contract 21/21 passed（adapter）、全量 regression 无 skip 无退化。
- 禁止：修改 fixture/oracle/scenarios/contract module。

## A6-TASK-005：official runner 与绑定

- 允许文件：`docs/testing/results/a6-*.json`、`tests/a6_suite_manifest.json`（仅绑定字段）。
- 交付：`python -m tests.runner.run_a6_suite --adapter noetide_micro.a6_testing_adapter --output docs/testing/results/a6-<date>.json` 同一次 run 21/21 passed/current；环境戳记（platform/python/wall time/monotonic/timezone）与 `a6_mvp_a_reference_v1` 绑定完整且与 ADR-0010 §5.3 一致；全量 configured-adapter regression；13 个 suite validator；manifest 绑定 current result。
- 禁止：修改 oracle 迎合 implementation；跨 profile 外推 SLO 结果。

## A6-TASK-006：Gate Review 与 Recovery Point

- 允许文件：review、状态、trace、release/recovery record。
- 交付：Gate Review P0/P1=0；PROJECT_STATE/矩阵/CURRENT_HANDOFF 同步；recovery tag `a6-hardening-rp-<date>` 创建并推送。
- 禁止：移动任何既有 tag；本任务不决定 Alpha 发布版本号与工件内容（发布门禁单独决定）。
