# Y2-S3 本地 Web UI Implementation Plan

## 元信息

- Plan ID: `PLAN-Y2-S3-IMPL-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S3-LOCAL-WEB-UI-001`
- Contract: `SPEC-Y2S3-LOCAL-WEB-UI-001` v0.1
- ADR: `ADR-0022`
- Suite: `y2s3_local_web_ui_v1`（materialized，未执行）

## 1. 任务

1. Y2S3-TASK-001：`src/noetide_micro/local_web.py`（回环 HTTP 服务、HTML 页面、API 路由、导出/备份入口）、`runtime.store` 只读访问辅助与 `cli.py web` 命令；定向 unit 测试。
2. Y2S3-TASK-002：`src/noetide_micro/y2s3_testing_adapter.py`，完整 adapter protocol，contract 10/10 passed；fixture/oracle 不修改。
3. Y2S3-TASK-003：official runner 同一次 run 10/10 passed/current；manifest 绑定；全量 regression 0 skip；全部 suite validator PASSED。
4. Y2S3-TASK-004：Gate Review（P0=0/P1=0）+ recovery tag `y2s3-local-web-ui-rp-20260803` 推送，PROJECT_STATE/HANDOFF/矩阵状态同步。

## 2. 规则

- 每轮只执行一张任务卡；不得修改 fixture/oracle 迎合实现；oracle 修正必须单独说明并同步 manifest hash。
- 任何 `not_executed` 不得记为通过；official runner 属 TASK-003，提前执行不算数。
- 网络仅允许本机回环；不得调用云端、不得引入第三方依赖、不得使用 wall-clock。
- Web 模块不得直接调用 store 写方法；导出只读；备份只写服务配置的 `backup_dir`。