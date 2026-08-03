# Y2-S5 MCP Runtime 最小子集切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-Y2S5-MCP-RUNTIME-001` |
| 版本 | `0.1` |
| 状态 | `Approved for Y2-S5 slice` |
| 产品基线 | `PRDv06.md` v0.6 |
| 产品决定 | `DEC-Y2-S5-001`；`DQ-013` decided |
| 上游 | S1 v0.7、S2 v0.6、S3 v0.5、S4 v0.5、S5 v0.5、S6 v0.6、S7 v0.4、S8 v0.4、S9 v0.5 |
| 适用范围 | `SLICE-Y2-S5-MCP-RUNTIME-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：证明本地 MCP runtime 最小子集能对外部 caller 提供受控 read/propose/append，默认关闭、最小披露、幂等、审计、红线/sealed fail closed，且不引入任何不可逆动作。

非目标：controlled mutate、destructive、A2A、多 Agent、MCP SDK/认证、账户体系、真实数据模式、大文件传输、同步或云端调用。

## 2. 对象与字段

```yaml
request_envelope:
  contract_version: y2s5-mcp-runtime-v1
  request_id: req_y2s5_<short_hash>
  caller_ref: person_alpha
  purpose: review
  capability_ref: cap_y2s5_<short_hash>
  action: list_resources | read_resource | propose_changeset | record_source
  scope:
    resource_ids: [src_..., person_card, relationship_timeline]
  data_revision_precondition: optional
  idempotency_key: required for mutating tools
  requested_at: ISO-8601 fixture time

capability:
  capability_id: cap_y2s5_<short_hash>
  actor: person_alpha
  purpose: review
  tools: [list_resources, read_resource, propose_changeset, record_source]
  resource_ids: [...]
  resource_fields: optional {read_resource: [metadata] | [metadata, content]}
  expires_at: ISO-8601 fixture time
  revoked: false
  created_at: ISO-8601 fixture time

response_envelope:
  request_id: ID
  authorization: allowed | allowed_with_redaction | denied
  result_status: ok | accepted | conflict | unavailable | failed | denied
  data_revision: actual | withheld
  view_revision: actual | not_applicable | withheld
  freshness_status: fresh | stale | not_applicable | withheld
  answer_status: actual | not_applicable | withheld
  evidence_refs: authorized refs | []
  missing_evidence: boolean | not_applicable | withheld
  receipt_ref: receipt | null
  payload: minimized result | import_reference | withheld
  error: {code, message} | null
```

## 3. 判定规则

1. capability 默认关闭：没有匹配且未到期、未撤销的 capability 时，请求 denied。
2. capability 必须匹配 `caller_ref`、`purpose`、`action`、`scope.resource_ids` 与 `expires_at`；`requested_at > expires_at` 或 `revoked=true` 即 denied。
3. `health`、`finance`、`relationship`、`sealed` 红线舱室 fail closed：即使 capability 覆盖，请求也 denied，响应不泄露正文或资源存在性。
4. denied 响应必须精确使用 withheld profile：revision/freshness/answer/missing/payload=withheld、evidence=[]、receipt=null、error=stable `denied`。
5. `list_resources` 只返回 capability 内的 source ids 与 view names；`read_resource` 只返回 capability 允许的字段，未授权字段不返回。
6. `propose_changeset` 只写 Ledger `changeset` proposed receipt，不写 Canonical、不发布、不自动确认。
7. `record_source` 只写 Source append receipt；超过 `max_source_bytes` 时返回 `large_file_required`，不截断。
8. mutating tool 必须带 `idempotency_key`；同 key 同 payload 返回同 receipt，同 key 不同 payload 返回 conflict。
9. 所有请求与结果写入 Ledger `mcp_audit`；审计不保存 Source 正文或请求 payload。
10. 本切片不提供 irreversible tool；`approve_changeset`、`seal_item`、`delete_item`、`export_sensitive_pack` 等一律 denied。

## 4. 时间、证据与权限

- 全部产品时间来自 fixture clock；不读 wall-clock。
- `data_revision` 使用 store 当前 Canonical revision；view 使用 projection 的 view revision/freshness。
- MCP response 不是 Evidence Ref；`evidence_refs` 只引用 Source 定位。
- 本切片不开放真实数据；fixture 全部显式合成。
- 审计只记录 request metadata、action、capability、receipt 与内部拒绝原因，不记录 payload/正文。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `Y2S5-INV-001` | default closed——无有效 capability 即无调用结果。 |
| `Y2S5-INV-002` | envelope & disclosure——每个响应带 S8 envelope；denied 使用唯一 withheld profile。 |
| `Y2S5-INV-003` | minimal read——read 只返回 capability 允许的最小字段；redacted 不返回正文或越权字段。 |
| `Y2S5-INV-004` | propose-only——`propose_changeset` 只创建 proposed Ledger receipt，Canonical/revision 不变。 |
| `Y2S5-INV-005` | append-only——`record_source` 只追加 Source receipt，Canonical/revision 不变。 |
| `Y2S5-INV-006` | idempotency & conflict——mutating tool 有幂等键；同 key 同 payload 同 receipt，同 key 不同 payload conflict。 |
| `Y2S5-INV-007` | no irreversible——destructive/不可逆工具不存在且任何请求 denied，`DQ-013` 无例外。 |
| `Y2S5-INV-008` | no bypass——红线/sealed、未知工具、畸形请求、policy unavailable、大文件正文均 fail closed 或返回导入引用。 |
| `Y2S5-INV-009` | deterministic/stdlib/loopback/synthetic——fixture clock、stdlib only、127.0.0.1 only、显式合成数据。 |

## 6. 失败、撤销与审计

- 拒绝原因使用内部封闭枚举：`no_capability`、`capability_expired`、`capability_revoked`、`purpose_mismatch`、`actor_mismatch`、`tool_not_granted`、`scope_mismatch`、`red_line_denied`、`irreversible_disabled`、`policy_unavailable`、`invalid_payload`。
- 内部拒绝原因可写入 `mcp_audit`，但响应永远使用唯一 `denied` profile，不得把原因映射到响应 error 文本。
- `result_status=failed` 只用于协议/工具错误，如 `invalid_request`、`invalid_payload`、`resource_not_found`、`large_file_required`、`conflict`。
- capability 撤销后后续请求立即 denied；已生成的 propose/append receipt 不自动进入 Canonical。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `Y2S5-001` | 有效 capability / list + authorized read | `list_resources` ok；`read_resource` ok，返回最小 fields/revisions；Canonical/revision 不变 |
| `Y2S5-002` | 无 capability 或越权 read | 每个响应为精确 denied profile；无 payload/evidence/revision 泄露 |
| `Y2S5-003` | capability 只授 metadata / 请求 content；sealed ID 直查 | 普通源返回 allowed_with_redaction 且无 content；sealed 返回 denied profile |
| `Y2S5-004` | capability 授 propose_changeset / 候选引用授权 Source | accepted，receipt_ref 为 changeset_id，Ledger status=proposed，Canonical/revision 不变 |
| `Y2S5-005` | capability 授 record_source / 合成 Source | accepted，receipt_ref 为 append receipt，Source 已存储，Canonical/revision 不变 |
| `Y2S5-006` | 同 key 同 payload 重放 / 同 key 不同 payload | 同 receipt 不重复写；不同 payload conflict，不新增写 |
| `Y2S5-007` | 过期 revision precondition / 当前 precondition | 过期返回 conflict/current revision 且不写；当前返回 accepted |
| `Y2S5-008` | `approve_changeset`/`seal_item`/`delete_item` 请求携带 verified | 全部 denied profile；零 changeset/source 写；`DQ-013` 无例外 |
| `Y2S5-009` | 畸形请求、未知工具、policy unavailable、超限大文件正文 | 分别返回 stable failed/denied/import_reference；零 Canonical 写 |
| `Y2S5-010` | 横切 / 两个独立系统 | 同输入同输出；HTTP server 只允许 127.0.0.1；stdlib scan 无外部依赖；fixture 显式合成 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `Y2S5-001..010` passed result 存在，且所有 `Y2S5-INV-*` 有正/反证明时，Y2-S5 才能标记 `verified`。未执行时必须保持 `not_executed`。
