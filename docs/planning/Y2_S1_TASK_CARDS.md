# Y2-S1 任务卡

## Y2S1-TASK-001：FolderImporter 核心

- 范围：`src/noetide_micro/folder_import.py`（枚举、白名单、路径 resolve 复检、UTF-8 校验、内容寻址 source_id、逐文件 append_source、ImportReport）；`src/noetide_micro/store.py` 仅加 `source_hashes_by_kind` 窄读辅助。
- SPEC：`SPEC-Y2S1-FOLDER-IMPORT-001` §2/§3/§5；`ADR-0020` §1.1-1.5。
- 测试：`tests/semantic/test_y2s1_task_001_importer.py` 定向覆盖 stored/duplicate/skipped/rejected 四终态与确定性。
- 完成条件：定向全过；`python -m unittest discover -s tests -t .` 回归无退化（contract 10 skipped 属预期）。

## Y2S1-TASK-002：Watcher 与中断恢复

- 范围：`FolderWatcher.poll`（seen 集从 store 重建、只导入新增）；`fail_hook` 注入点；重跑收敛。
- SPEC：合同 §2.4/§3/§6；`ADR-0020` §1.5-1.6。
- 测试：`tests/semantic/test_y2s1_task_002_watcher.py`。
- 完成条件：定向全过；回归无退化。

## Y2S1-TASK-003：Testing Adapter

- 范围：`src/noetide_micro/y2s1_testing_adapter.py` 完整实现 `create_system/run_case/layer_snapshot`；临时目录物化 fixture 库；junction（Linux symlink / Windows mklink /J fallback）；fail_at_index 注入；profile fail closed。
- SPEC：合同 §7；adapter protocol。
- 完成条件：contract 10/10 passed（`NOETIDE_Y2S1_ADAPTER=noetide_micro.y2s1_testing_adapter`）；fixture/oracle/manifest 未修改。

## Y2S1-TASK-004：Official Runner 与绑定

- 范围：`python -m tests.runner.run_y2s1_suite --adapter noetide_micro.y2s1_testing_adapter --output docs/testing/results/y2s1-20260801.json`；manifest flags 翻真并绑定 result 哈希；全量回归（17 个 adapter 环境变量）0 skip；全部 suite validator。
- 完成条件：同一次 run 10/10 passed/current；immutable result 入库。

## Y2S1-TASK-005：Gate Review 与恢复点

- 范围：`docs/reviews/Y2_S1_FOLDER_IMPORT_GATE_REVIEW_2026-08-01.md`；annotated tag `y2s1-folder-import-rp-20260801` 推送；PROJECT_STATE/HANDOFF/矩阵 §4.21 状态更新。
- 完成条件：P0=0/P1=0；tag 可解析、远端可验证。
