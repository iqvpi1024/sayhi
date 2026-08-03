# Y2-S5 MCP Runtime 最小子集架构视图

## 元信息

- Architecture ID: `ARCH-Y2S5-MCP-RUNTIME-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S5-MCP-RUNTIME-001`
- ADR: `ADR-0024`
- Contract: `SPEC-Y2S5-MCP-RUNTIME-001` v0.1

## 1. 组件

```text
External caller
  -> McpService（127.0.0.1 HTTP + JSON-RPC 2.0）
  -> McpRuntime.handle_request
       capability gate（default closed / actor / purpose / tools / scope / expiry / revoked）
       red-line & sealed fail closed
       dispatch:
         list_resources -> store.seed_snapshot
         read_resource -> store.seeded_source / projection_row
         propose_changeset -> Ledger changeset proposed receipt
         record_source -> store.append_source + append receipt
       idempotency -> Ledger mcp_idempotency
       audit -> Ledger mcp_audit
       denied/failed envelope helpers
SemanticStore
  source_records / append_receipts / canonical_revisions / projection_rows / ledger_records
```

## 2. 边界

- 写面：`mcp_audit`、`mcp_idempotency`、`changeset` proposed receipt、Source append receipt；无 Canonical 写、无新表。
- 读面：`seed_snapshot()`、`seeded_source()`、`current_revision()`、`canonical_layer_digest()`。
- 失败面：无 capability、越权、红线/sealed、不可逆工具、畸形请求、policy unavailable、大文件正文全部 fail closed 或返回 stable error。
- 时间面：全部使用 fixture clock，无 wall-clock。
- 网络面：HTTP server 只允许 `127.0.0.1`；official runner 使用 loopback-only socket guard。

## 3. 数据流

capability 显式创建 -> caller 发 request -> capability gate -> 若 denied 返回 withheld profile；若 allowed 执行最小工具 -> propose/append 写 Ledger/Source receipt -> `mcp_audit` 记录结果 -> response 返回。任何失败保持 Canonical/revision 不变。

## 4. 测试面

`y2s5_testing_adapter.py` 在临时目录物化 fixture Source，启动 127.0.0.1 MCP service，按 case 创建 capability、发送 JSON-RPC 请求、读取 response、检查 Ledger/Canonical/revision。contract 10 场景覆盖 9 条不变量；determinism、stdlib、loopback 与 synthetic 由 adapter/runner 证明。
