# Y2-S1 文件夹导入 Implementation Plan

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-Y2-S1-IMPL-001` |
| Date | 2026-08-01 |
| Slice | `SLICE-Y2-S1-FOLDER-IMPORT-001` |
| Contract | `SPEC-Y2S1-FOLDER-IMPORT-001` v0.1 |
| ADR | `ADR-0020` |
| Suite | `y2s1_folder_import_v1`（materialized，未执行） |

## 1. 任务

| Task | 内容 | 完成条件 |
|---|---|---|
| Y2S1-TASK-001 | `folder_import.py`：枚举/白名单/路径安全/UTF-8/内容寻址导入/报告；store 窄辅助 `source_hashes_by_kind` | 定向测试通过；回归无退化；official suite `not_executed` |
| Y2S1-TASK-002 | `FolderWatcher` 单次 poll + 中断恢复（fail_hook 注入点） | 定向测试通过；回归无退化；official suite `not_executed` |
| Y2S1-TASK-003 | `y2s1_testing_adapter.py`：完整 adapter protocol（临时目录物化、junction/symlink 创建、fail 注入、layer snapshot） | contract 10/10 passed（adapter）；fixture/oracle 未修改 |
| Y2S1-TASK-004 | official runner 同一次 run 10/10 passed/current；manifest 绑定 current result；全量回归 0 skip；全部 suite validator PASSED | immutable result 入库 |
| Y2S1-TASK-005 | Gate Review（P0=0/P1=0）+ recovery tag `y2s1-folder-import-rp-20260801` 推送 | 切片 verified |

## 2. 规则

- 每轮只执行一张任务卡；不得修改 fixture/oracle 迎合实现；oracle 修正必须单独说明并同步 manifest hash。
- 任何 `not_executed` 不得记为通过；official runner 属 TASK-004，提前执行不算数。
