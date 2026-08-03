# Y2-S5 MCP Runtime 最小子集切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-Y2-S5-001` |
| Date | 2026-08-03 |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| Upstream Decision | `DEC-Y2-ENTRY-001` §2.5/§2.6；`DQ-013` 已重开并 decided |
| Current Slice | `SLICE-Y2-S5-MCP-RUNTIME-001` |

## 1. 决定内容

选择本地、最小、只读优先的 MCP runtime 子集作为 Year 2 第五个切片。具体决定：

1. 仅启用 read 与最小 propose/append：`list_resources`、`read_resource`、`propose_changeset`、`record_source`。不启用 controlled mutate、destructive 或任何不可逆动作；`approve_changeset`、`seal_item`、`delete_item` 等请求一律 denied。
2. 每个调用使用 S8 Request/Response Envelope：`request_id`、`contract_version`、`caller_ref`、`purpose`、`capability_ref`、`action`、`scope`、`data_revision_precondition`、`idempotency_key`、`requested_at`；响应明确 authorization、result_status、revision、freshness、answer_status、evidence/missing、receipt 与 payload。
3. capability 显式创建并默认关闭：绑定 `caller_ref`、`purpose`、`tools`、`resource_ids`、`expires_at`、`revoked`；任一维度不匹配、到期或撤销即 denied。
4. 红线/封存舱室 fail closed：Source compartments 含 `health`、`finance`、`relationship`、`sealed` 时，即使 capability 覆盖也 denied，且响应不泄露资源存在性或正文。
5. denied 响应使用 S8 唯一 disclosure profile：revision/freshness/answer/missing/payload=withheld、evidence=[]、receipt=null、error=stable `denied`。
6. `propose_changeset` 只写 Ledger `changeset` 的 proposed receipt，不写 Canonical、不发布、不自动确认；`record_source` 只写 Source append receipt，不写 Canonical。
7. mutating tool 必须携带 `idempotency_key`；同 key 同 payload 重放返回同 receipt，同 key 不同 payload 返回 conflict，不产生重复写。
8. 大文件正文不经 MCP 默认通道；`record_source` 超过上限返回 `large_file_required` 与导入引用要求，不截断伪成功。
9. 运行时只使用 Python 标准库、仅绑定本机回环；不引入 MCP SDK、第三方依赖、账户、真实数据、真实公网调用或 A2A。
10. 所有请求与结果写入 Ledger `mcp_audit`：capability 创建/撤销、allowed/denied/conflict/failed、source appended、changeset proposed、idempotent replay；审计不保存 Source 正文或请求 payload。

## 2. 产品依据

- PRDv06 §19.1-§19.3、§19.5：MCP Resources/Tools、外部 Agent 规则、MCP 开放时机；进入前必须重开 `DQ-013`。
- PRDv06 §24.5：Y2-S5 关键约束为“先重开 `DQ-013`”。
- S8 v0.4：Request/Response Envelope、Tool Classes、状态机、12 条不变量、27 个验收测试定义图纸；本切片只物化其最小可运行子集。
- `DEC-Y2-ENTRY-001` §2.5/§2.6：MCP runtime 排在 Y2-S1/S2/S3 verified 之后，S8 不提前实现；Y2-S5 为最后 Year 2 切片。

## 3. 切片范围

- `src/noetide_micro/mcp_runtime.py`：Request/Response Envelope、capability gate、loopback HTTP JSON-RPC 2.0 包装、read/propose/append 工具、idempotency、审计、stdlib/loopback 静态扫描。
- `src/noetide_micro/y2s5_testing_adapter.py`：临时目录 + 显式合成 fixture + 127.0.0.1 HTTP stub 的 contract adapter。
- Suite：10 场景，覆盖 9 条不变量；全部使用固定合成 profile `y2s5_mcp_runtime_v1`。

## 4. 非目标

- controlled mutate、destructive/irreversible tools、A2A、多 Agent、专业 Agent 市场、账户/认证供应商、真实数据模式、大文件传输总线、同步或云端调用。
- 扩大预授权自动处理范围（`DQ-011` deferred）；`record_source` 只是原始 Source append，不自动解析或生成 Canonical。
- 修改任何已 verified 切片（含 Y2-S1..S4）的 fixture/oracle/result 或业务代码语义。

## 5. 不变量

- `Y2S5-INV-001`：default closed——无有效 capability 即无调用结果，所有请求 denied。
- `Y2S5-INV-002`：envelope & disclosure——每个响应带 S8 envelope；denied 使用唯一 withheld profile。
- `Y2S5-INV-003`：minimal read——read 只返回 capability 允许的最小字段；redacted 不返回正文或越权字段。
- `Y2S5-INV-004`：propose-only——`propose_changeset` 只创建 proposed Ledger receipt，Canonical/revision 不变。
- `Y2S5-INV-005`：append-only——`record_source` 只追加 Source receipt，Canonical/revision 不变。
- `Y2S5-INV-006`：idempotency & conflict——mutating tool 有幂等键；同 key 同 payload 同 receipt，同 key 不同 payload conflict。
- `Y2S5-INV-007`：no irreversible——destructive/不可逆工具不存在且任何请求 denied，`DQ-013` 无例外。
- `Y2S5-INV-008`：no bypass——红线/sealed、未知工具、畸形请求、policy unavailable、大文件正文均 fail closed 或返回导入引用。
- `Y2S5-INV-009`：deterministic/stdlib/loopback/synthetic——fixture clock、stdlib only、127.0.0.1 only、显式合成数据。

## 6. 授权与下一步

本决定授权 S1-S9 SPEC applicability review，随后 slice contract、traceability、ADR、suite 物化、Implementation Plan。不授权业务编码；suite 未执行前不得标记 verified。
