# Y2-S5 MCP Runtime 最小子集 SPEC Applicability Review

| 字段 | 值 |
|---|---|
| Review ID | `Y2S5-SPEC-APPLICABILITY-001` |
| Date | 2026-08-03 |
| Slice | `SLICE-Y2-S5-MCP-RUNTIME-001` |
| Decision | `DEC-Y2-S5-001` |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| 结论 | `pass_with_slice_contract_required` |

## 1. 审查范围

按 `DEC-Y2-S5-001` §6 授权，复核 S1（Semantic Object Model v0.7）、S2（Bitemporal & Evidence v0.6）、S3（ChangeSet & Consistency v0.5）、S4（Privacy & Access Policy v0.5）、S5（Shiling Policy v0.5）、S6（Semantic Test Harness v0.6）、S7（Storage, Index & Portability v0.4）、S8（MCP Contract v0.4）、S9（Ingestion & Migration v0.5）。

## 2. 逐份结论

### S1 Semantic Object Model v0.7：`pass`

- MCP Resource 是 Source/Projection 的受控读取表示，不新增核心对象。
- `propose_changeset` 只携带候选载荷，不把 MCP 响应写成 Canonical 对象。

### S2 Bitemporal & Evidence v0.6：`pass_with_slice_contract_required`

- 响应必须区分 data/view revision、freshness 与 evidence/missing；MCP response 不得成为 Evidence Ref。
- 缺口：切片级 read_resource 的字段裁剪、view freshness 与 source evidence 组合需由 slice contract §6/§7 闭合。

### S3 ChangeSet & Consistency v0.5：`pass_with_slice_contract_required`

- `propose_changeset` 只写 Ledger proposed receipt；不写 Canonical、不发布。
- 缺口：idempotency 同 key 不同 payload 的 conflict 与 revision precondition 需由 slice contract §3/§7 闭合。

### S4 Privacy & Access Policy v0.5：`pass_with_slice_contract_required`

- capability 绑定 caller/purpose/tools/resource scope/time；denied 使用 withheld profile。
- 缺口：MCP capability 的默认关闭、撤销、红线/sealed fail closed 与审计边界需由 slice contract §3/§5/§6 闭合。

### S5 Shiling Policy v0.5：`pass`

- 外部 Agent 不能 Verify；propose 候选保持 unconfirmed；MCP response 不自动升格事实。
- 本切片不改变确认、发布或 review_status 语义。

### S6 Semantic Test Harness v0.6：`pass_with_slice_contract_required`

- 固定合成、离线、确定性、loopback runner 与既有 suite 一致。
- 缺口：10 场景的 manifest/oracle/adapter protocol 与 HTTP transport guard 由 slice contract §8 闭合。

### S7 Storage, Index & Portability v0.4：`pass_with_slice_contract_required`

- MCP 只读 store 的 source/projection；写面仅 Ledger `mcp_audit`/`changeset`/`mcp_idempotency` 与 Source append receipt。
- 缺口：审计记录是否进入私有导出、payload 不落审计的具体字段需由 slice contract §6 闭合。

### S8 MCP Contract v0.4：`pass_with_slice_contract_required`

- S8 是图纸合同；Y2-S5 只实现其最小可运行子集，不实现 SDK、认证、A2A、大文件或 destructive。
- 缺口：最小工具集、capability 字段、HTTP loopback 包装与 10 个切片验收测试由 slice contract 闭合。

### S9 Ingestion & Migration v0.5：`pass`

- `record_source` 只是原始 Source append；大文件正文要求导入引用，不替代既有导入器。
- 本切片不新增迁移格式或真实数据合同。

## 3. 结论与条件

`pass_with_slice_contract_required`：基础 SPEC 不阻碍切片，但七个缺口必须由 `SPEC-Y2S5-MCP-RUNTIME-001` 显式闭合后才可物化 suite 或编码。禁止 slice contract 扩张到 irreversible tools、A2A、账户、真实数据、第三方依赖或大文件传输。
