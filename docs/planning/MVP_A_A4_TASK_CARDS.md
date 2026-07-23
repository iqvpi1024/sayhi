# A4 任务卡

每张任务卡只允许执行一个 Task；完成后更新 `docs/planning/MVP_A_A4_IMPLEMENTATION_PLAN.md` 的状态列与 `docs/PROJECT_STATE.md`。

## A4-TASK-001：store 只读策略标注与 digest 辅助

- 允许文件：`src/noetide_micro/store.py`、`tests/semantic/test_a4_task_001_store.py`。
- 交付：对象策略标注只读辅助（sensitivity/compartments 提取）；canonical 对象 digest 辅助（零写入前后对比用）。
- 验证：Python import、定向 store tests、PRAGMA 检查、`git diff --check`。
- 禁止：判决器逻辑、adapter、fixture/oracle 修改。

## A4-TASK-002：access_policy.py 纯函数判决器

- 允许文件：`src/noetide_micro/access_policy.py`、`tests/semantic/test_a4_task_002_access_policy.py`。
- 交付：Grant 有效性（caller/purpose/action/scope/时间窗口）；多舱室最严格交集（allow 交集、deny 并集、无法求交 `policy_conflict`）；sealed 排除；未知 caller/purpose/compartment/策略缺失 fail closed；判决零写入。
- 验证：定向 tests 覆盖 A4-001..008 语义、regression 无退化。
- 禁止：adapter、official runner、fixture/oracle 修改、任何持久化。

## A4-TASK-003：a4_testing_adapter.py

- 允许文件：`src/noetide_micro/a4_testing_adapter.py`。
- 交付：完整实现 `tests/runner/a4_access_policy_adapter_protocol.py`；支持 fixture 的 8 个 case（含 replay 与 derived-view 等价查询）。
- 验证：`NOETIDE_A4_ADAPTER` 下 contract 8/8 passed。
- 禁止：修改 fixture/oracle/contract module。

## A4-TASK-004：official runner 与绑定

- 允许文件：`docs/testing/results/a4-*.json`、`tests/a4_suite_manifest.json`（仅绑定字段）。
- 交付：`python -m tests.runner.run_a4_suite --adapter noetide_micro.a4_testing_adapter --output docs/testing/results/a4-<date>.json` 同一次 run 8/8 passed/current；全量 configured-adapter regression；11 个 suite validator；manifest 绑定 current result。
- 禁止：修改 oracle 迎合 implementation。

## A4-TASK-005：Gate Review 与 Recovery Point

- 允许文件：review、状态、trace、release/recovery record。
- 交付：Gate Review P0/P1=0；PROJECT_STATE/矩阵/CURRENT_HANDOFF 同步；recovery tag `a4-access-policy-rp-<date>` 创建并推送。
- 禁止：移动任何既有 tag。
