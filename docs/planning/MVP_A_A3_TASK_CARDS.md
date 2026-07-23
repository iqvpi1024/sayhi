# A3 任务卡

每张任务卡只允许执行一个 Task；完成后更新 `docs/planning/MVP_A_A3_IMPLEMENTATION_PLAN.md` 的状态列与 `docs/PROJECT_STATE.md`。

## A3-TASK-001：store merge_records 持久化辅助

- 允许文件：`src/noetide_micro/schema.sql`、`src/noetide_micro/store.py`、`tests/semantic/test_a3_task_001_store.py`。
- 交付：`merge_records` 表（merge_id、source_entity_ref、target_entity_ref、pre_merge_references JSON、published_revision、recorded_at、split_revision nullable）；写入/读取辅助；重复写入同一 merge_id 拒绝（只增不改）。
- 验证：Python import、定向 store tests、PRAGMA 检查、`git diff --check`。
- 禁止：entity_merge 业务逻辑、adapter、fixture/oracle 修改。

## A3-TASK-002：entity_merge.py ChangeSet 服务

- 允许文件：`src/noetide_micro/entity_merge.py`、必要 store glue、`tests/semantic/test_a3_task_002_entity_merge.py`。
- 交付：merge preflight（reason 非空、source!=target、双方 active、同 profile、实体存在）；单事务原子发布（状态更新 + 引用重定向 + merge_record）；可注入 `entity_merge.mid_redirect` 失败点且整体回滚；split preflight（merge_ref 存在、未 split、source 仍 merged）与逐字段恢复；protected layers（trust/closeness/personality）不变断言辅助。
- 验证：定向 tests 覆盖 A3-001/002/004/005/008 语义、regression 无退化。
- 禁止：adapter、official runner、fixture/oracle 修改。

## A3-TASK-003：a3_testing_adapter.py

- 允许文件：`src/noetide_micro/a3_testing_adapter.py`。
- 交付：完整实现 `tests/runner/a3_entity_merge_adapter_protocol.py`（create_system/run_case/layer_snapshot/inject_failure）；支持 fixture 的 8 个 case 与 invalid attempt 集合。
- 验证：`NOETIDE_A3_ADAPTER` 下 contract 8/8 passed。
- 禁止：修改 fixture/oracle/contract module。

## A3-TASK-004：official runner 与绑定

- 允许文件：`docs/testing/results/a3-*.json`、`tests/a3_suite_manifest.json`（仅绑定字段）。
- 交付：`python -m tests.runner.run_a3_suite --adapter noetide_micro.a3_testing_adapter --output docs/testing/results/a3-<date>.json` 同一次 run 8/8 passed/current；全量 configured-adapter regression；10 个 suite validator；manifest 绑定 current result。
- 禁止：修改 oracle 迎合 implementation。

## A3-TASK-005：Gate Review 与 Recovery Point

- 允许文件：review、状态、trace、release/recovery record。
- 交付：Gate Review P0/P1=0；PROJECT_STATE/矩阵/CURRENT_HANDOFF 同步；recovery tag `a3-entity-merge-rp-<date>` 创建并推送。
- 禁止：移动任何既有 tag。
