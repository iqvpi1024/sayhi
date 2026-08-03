# ADR-0024：Y2-S5 本地 MCP runtime 最小子集实现方案

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0024` |
| Date | 2026-08-03 |
| Status | `Accepted` |
| Slice | `SLICE-Y2-S5-MCP-RUNTIME-001` |
| Contract | `SPEC-Y2S5-MCP-RUNTIME-001` v0.1 |
| Decision | `DEC-Y2-S5-001`；`DQ-013` decided |

## 1. 决策

1. 新模块 `src/noetide_micro/mcp_runtime.py`：`McpRuntime` 实现 S8 Request/Response Envelope、capability gate、read/propose/append、idempotency、审计；`McpService` 用 Python stdlib `http.server` 提供 127.0.0.1 JSON-RPC 2.0 包装。
2. 不引入 MCP SDK、认证供应商或第三方依赖；transport 是“JSON-RPC 2.0 over loopback HTTP”的最小实现，不宣称标准 MCP SDK 兼容。
3. capability 在进程内显式创建，不新增 SQLite 表；每次请求只从 store 读 Source/Projection，写面仅 Ledger `mcp_audit`、`mcp_idempotency`、`changeset` proposed receipt 与 Source append receipt。
4. 不可逆/controlled mutate 工具全部不在 `ENABLED_TOOLS`；请求落到未启用工具即 denied，不实现任何 destructive 分支。
5. denied 响应由单一 `_denied` helper 生成，字段顺序和值固定，防止实现分支产生泄露组合。
6. `record_source` 使用 fixture clock、计算 `content_hash`/`byte_length`，超限返回 `large_file_required`；不保存未授权 payload。
7. 审计使用 `store.put_ledger_record(record_type="mcp_audit")`，只存元数据；`mcp_idempotency` 存 payload hash 与 receipt，不存正文。

## 2. 备选方案与放弃理由

- 直接依赖官方 MCP SDK：放弃。引入第三方依赖违反 `Y2E-INV-005`，且 S8 明示 SDK/transport 后置；最小 loopback HTTP JSON-RPC 2.0 足以证明语义。
- 新增权限 SQLite 表：放弃。Y2-S5 只需证明 capability gate；Ledger 保留 capability 创建/撤销事件，后续真实权限 runtime 可另立 ADR。
- 启用 controlled mutate/destructive：放弃。`DQ-013` 决定无不可逆例外；最小 runtime 不证明或扩大该能力。
- 用文件传输接受大文件正文：放弃。S8 `MCP-INV-009` 禁止；返回导入引用并保持零写。
- 在 store 内直接写 Canonical 演示 propose：放弃。违反 S3 与 Y2-S5-INV-004；只写 Ledger receipt。

## 3. 代价与回退

- 代价：capability 不持久化，进程重启后需重新创建；不会在 official suite 中执行真实 MCP SDK 互操作。
- 回退：删除 `mcp_runtime.py` 与 `y2s5_testing_adapter.py` 即可移除；无 Canonical 写入、无新表迁移。

## 4. 环境

Windows 11 10.0.26200；CPython 3.12.8；stdlib only；runner 阻断外部网络（loopback-only socket guard）；fixture clock；显式合成数据。
