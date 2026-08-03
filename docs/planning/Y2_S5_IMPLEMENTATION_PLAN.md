# Y2-S5 MCP Runtime 最小子集 Implementation Plan

## 元信息

- Plan ID: `PLAN-Y2-S5-IMPL-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S5-MCP-RUNTIME-001`
- Contract: `SPEC-Y2S5-MCP-RUNTIME-001` v0.1
- ADR: `ADR-0024`
- Suite: `y2s5_mcp_runtime_v1`（materialized，未执行）

## 1. 任务

1. Y2S5-TASK-001：`src/noetide_micro/mcp_runtime.py`（McpRuntime、McpService、envelope、capability gate、read/propose/append、idempotency、audit、stdlib/loopback 静态扫描）；定向 unit 测试。
2. Y2S5-TASK-002：`src/noetide_micro/y2s5_testing_adapter.py`，完整 adapter protocol，contract 10/10 passed；fixture/oracle 不修改。
3. Y2S5-TASK-003：official runner 同一次 run 10/10 passed/current；manifest 绑定；全量 regression 0 skip；全部 suite validator PASSED。
4. Y2S5-TASK-004：Gate Review（P0=0/P1=0）+ recovery tag `y2s5-mcp-runtime-rp-20260803` 推送，PROJECT_STATE/HANDOFF/矩阵状态同步。

## 2. 规则

- 每轮只执行一张任务卡；不得修改 fixture/oracle 迎合实现；oracle 修正必须单独说明并同步 manifest hash。
- 任何 `not_executed` 不得记为通过；official runner 属 TASK-003，提前执行不算数。
- 网络仅允许本机回环测试；`McpService` 默认且只接受 127.0.0.1。
- 模块只写 Ledger `mcp_audit`/`mcp_idempotency`/`changeset` proposed receipt 与 Source append receipt；不得写 Canonical、不得新增表、不得使用 wall-clock。
