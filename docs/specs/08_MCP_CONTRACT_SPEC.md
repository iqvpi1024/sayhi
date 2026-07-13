# MCP Contract SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-MCP-001` |
| 版本 | `0.1` |
| 状态 | `Approved` |
| 产品基线 | `PRDv04.md` v0.4 |
| 上游 | S1-S7 `Approved` |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_executed=false`、`suite_passed=false` |

本文定义外部能力语义，不选择 MCP SDK、传输、进程模型、认证实现或协议扩展。

## 1. 目标

1. 定义外部 caller 读取、提出、追加和受控修改的最小能力合同。
2. 所有响应携带权限、revision、新鲜度、证据/缺失证据和回执。
3. 禁止 MCP 绕过 ChangeSet、权限或 Source 边界。
4. 禁止 stale/无证据数据驱动不可逆外部行动。
5. 保持大文件传输、内部事件总线与 A2A 在范围外。

依据：PRD §7.3、§10.2、§19、§20 FR-304/306、§21、§25。

## 2. 非目标

- 不把 MCP 作为大文件上传/下载或内部事件总线。
- 不实现 A2A、多 Agent 编排、专业 Agent 市场。
- 不选择 SDK、transport、JSON-RPC 版本或认证供应商。
- 不提供真实数据的 Micro 外部 Agent 接入。
- 不让外部 Agent Verify、解封或默认执行 destructive action。

## 3. 术语

| 术语 | 定义 |
|---|---|
| Resource | 受权限裁剪的只读上下文表示 |
| Tool | 受控动作入口，按 read/propose/append/mutate/destructive 分类 |
| Capability | caller 在 purpose/scope/time 下被授予的资源/动作集合 |
| Response Envelope | 权限、revision、freshness、evidence、result/error 的共同结构 |
| Minimal Context | 完成声明任务所需的最小授权字段集合 |
| Irreversible Action | 外发、删除、支付/提交等不能仅靠本地撤销恢复的行动 |

## 4. 适用范围

Resources：当前状态与新鲜度、人物/关系时间线、Episode/Assertion/证据/CoverageWindow、Goal/Commitment/Decision/Outcome、冲突/待确认/系统健康。

Tools：read、propose、append、controlled mutate、destructive。Micro 不启用 MCP runtime；这里只定义未来接口语义。

## 5. 对象与边界

- Resource 是 Projection/Context Compiler 输出，不是 Canonical 事实源。
- `record_source` 发起 Source Append；大文件本体通过文件系统/导入器，MCP 只传引用和任务。
- propose tool 只创建 Candidate/ChangeSet，不能发布。
- controlled mutate 必须调用 S3/S4 合同。
- Tool response/Agent 文本不能成为 Evidence Ref。

## 6. 字段语义

### 6.1 Request Envelope

```yaml
request_id: stable ID
caller_ref: actor
purpose: declared purpose
capability_ref: grant/capability
action: resource/tool name
scope: object, field, time, compartment
data_revision_precondition: optional
idempotency_key: required for mutating tools
requested_at: timestamp
```

### 6.2 Response Envelope

```yaml
request_id: ID
authorization: allowed | denied | allowed_with_redaction
result_status: ok | accepted | conflict | stale | not_covered | unavailable | failed
data_revision: current canonical revision
view_revision: actual view revision | not_applicable
freshness_status: fresh | stale | updating | unavailable
answer_status: BTE status | not_applicable
evidence_refs: authorized Source refs | []
missing_evidence: boolean or non-leaking reason
receipt_ref: Source/ChangeSet/destructive receipt | null
payload: minimized result | withheld
error: stable non-leaking error | null
```

### 6.3 Tool Classes

| 类别 | 例 | 约束 |
|---|---|---|
| read | `search_context|get_evidence|get_timeline|get_relationship` | 不写入 |
| propose | `propose_changeset|propose_entity_merge|open_decision` | 只建候选/提案 |
| append | `record_source|record_diary|record_outcome` | 原始 Source receipt；语义另走 ChangeSet |
| controlled mutate | `approve_changeset|correct_assertion|revert_changeset` | S3 + 权限 |
| destructive | `seal_item|delete_item|export_sensitive_pack` | owner 强授权、S4 receipt |

### 6.4 Pagination/Continuation

列表资源必须有稳定 `continuation_token`、revision 和排序语义；token 不得扩大权限或跨 revision 静默混页。具体编码后置实现。

## 7. 状态机

```text
received -> authorized | denied
authorized -> executing
executing -> ok | accepted | conflict | stale | unavailable | failed
accepted -> completed | failed (通过 receipt/resource 查询，不改原响应)
```

Mutating tool 的实际 ChangeSet/Source 状态由上游 SPEC 管理。

## 8. 允许与禁止的状态转换

允许：read 返回裁剪数据；propose 返回 proposal ID；append 返回 stored receipt；mutate 返回 ChangeSet receipt；异步 accepted 后查询结果。

禁止：propose 直接 published；Agent 设置 verified；stale 资源执行 irreversible action；denied 响应透露隐藏资源；同 idempotency key 不同 payload；MCP 上传大文件正文作为默认通道。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `MCP-INV-001` | MCP 不能绕过 Source Append/ChangeSet/权限合同 |
| `MCP-INV-002` | 每个响应明确 authorization 与实际 revision |
| `MCP-INV-003` | L2/L3 响应明确 view/freshness，不冒充 current |
| `MCP-INV-004` | stale/unknown/not_covered/denied 不驱动不可逆行动 |
| `MCP-INV-005` | caller 只获得任务所需最小字段 |
| `MCP-INV-006` | denied/redacted 不通过错误、计数、摘要泄露 |
| `MCP-INV-007` | 外部 Agent 不能直接 Verify 个人语义事实 |
| `MCP-INV-008` | mutating tool 有 idempotency 与 receipt |
| `MCP-INV-009` | 大文件本体不经 MCP 默认传输 |
| `MCP-INV-010` | Resource/response 不成为事实证据 |
| `MCP-INV-011` | capability 受 caller/purpose/scope/time 约束 |
| `MCP-INV-012` | A2A/多 Agent 不被 MCP 合同隐式引入 |

## 10. 时间语义

- Request、authorization evaluation、execution、receipt 时间分离。
- 查询可指定 BTE valid/recorded time；响应回显解析后的 scope。
- capability 到期后继续请求必须 deny。
- continuation token 绑定 revision/expiry，过期返回明确 conflict/stale。

## 11. 证据语义

- get_evidence 只返回授权 Source locator 和七维 assessment。
- missing evidence、not covered、unknown、disputed 严格区分。
- Resource、MCP response、Agent 总结不是 Evidence Ref。
- evidence 被裁剪时不能通过数量/错误泄露。

## 12. 权限要求

- 每个调用经过 S4 PolicyRequest；capability 只是授权引用，不是永久信任。
- destructive 默认 deny，必须 owner 明确 scope/purpose/time。
- sealed 资源即使出现在 ID 参数中也不得读取或推断。
- 外发只返回最小 Context，不给完整档案。

## 13. 冲突行为

- revision precondition 过期返回 conflict/current revision，不自动覆盖。
- BTE disputed 返回并列授权证据，不由工具选胜者。
- capability 与 policy 冲突时 deny。
- continuation 跨 revision 返回 restart/conflict，不混合结果。

## 14. 失败与降级

| 失败 | 行为 |
|---|---|
| policy unavailable | deny mutate/destructive；read fail closed |
| L2 unavailable | Canonical fallback 或 unavailable，无旧 current |
| L3 stale | 可返回 stale payload，但 irreversible prohibited |
| model unavailable | read/append/manual ChangeSet 工具继续 |
| large file input | 返回导入引用要求，不截断伪成功 |
| timeout | 明确 accepted/unavailable + receipt/task ref |
| internal error | stable non-leaking error，记录 audit |

## 15. 撤销与审计

- MCP 请求与结果记录 caller、purpose、scope、policy、revision、idempotency 和 receipt。
- 受控变更撤销由 S3，删除/封存由 S4。
- 审计日志不得保存不必要 payload；硬删除后服从 content-free proof。

## 16. 兼容与迁移

- 请求/响应带 contract version。
- 未知 required action/enum fail closed；未知可选字段保留/忽略按版本规则。
- 新工具不能默认继承旧 capability。
- 破坏性变更需新版本和迁移期，不静默改变语义。

## 17. 正例

授权 caller 查询关系时间线：响应返回裁剪 payload、data/view revision、freshness 和 Source evidence；若 View updating，则返回 Canonical fallback 或 unavailable，不返回旧 current。

## 18. 反例

- `propose_changeset` 直接修改 State。
- 工作 caller 从摘要推断 restricted 字段。
- stale 人物卡驱动不可逆外发。
- `record_source` 把解析结果直接写 verified Assertion。
- MCP 作为视频文件传输总线。

## 19. 可执行验收测试

```yaml
suite_id: mcp_contract_v0_1
suite_defined: true
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `MCP-AT-001` | authorized read | 返回最小字段/revisions |
| `MCP-AT-002` | denied read | withheld、无泄露 |
| `MCP-AT-003` | redacted read | 只返回 allowed fields |
| `MCP-AT-004` | stale L2 | fallback/unavailable，不冒充 current |
| `MCP-AT-005` | stale L3 | 明确 stale |
| `MCP-AT-006` | stale 驱动 irreversible | 拒绝 |
| `MCP-AT-007` | not_covered query | 正确 answer status |
| `MCP-AT-008` | disputed query | 并列授权证据 |
| `MCP-AT-009` | Agent verify 请求 | 拒绝 |
| `MCP-AT-010` | propose tool | 只建 proposal |
| `MCP-AT-011` | append tool | Source receipt、Canonical 不变 |
| `MCP-AT-012` | approve tool | 走 ChangeSet receipt |
| `MCP-AT-013` | destructive 无 owner grant | deny |
| `MCP-AT-014` | sealed ID 直查 | deny 且不泄露 |
| `MCP-AT-015` | 同幂等键重放 | 同 receipt，不重复写 |
| `MCP-AT-016` | 同键不同 payload | conflict |
| `MCP-AT-017` | revision precondition stale | conflict/current revision |
| `MCP-AT-018` | continuation 跨 revision | restart/conflict |
| `MCP-AT-019` | 大文件正文请求 | 返回导入引用要求 |
| `MCP-AT-020` | model unavailable | read/append/manual 继续 |
| `MCP-AT-021` | policy unavailable | fail closed |
| `MCP-AT-022` | error response | 非泄露 stable code |
| `MCP-AT-023` | response 作为 evidence | 拒绝 |
| `MCP-AT-024` | fixtures 扫描 | 仅合成数据 |
| `MCP-AT-025` | A2A/未知 Agent 协议尝试调用 | 仍须 capability/policy/ChangeSet，不能旁路 |

不变量覆盖：001→AT010-013/025；002→001/004；003→004/005；004→006-009；005→001/003；006→002/014/022；007→009；008→012/015/016；009→019；010→023；011→013/017/021；012→AT025/静态范围检查。

## 20. 未决问题

本 SPEC 无 blocking open question。SDK、transport、认证、分页 token 编码和错误码载体后置实现 ADR。A2A、专业 Agent 市场、多 Agent 编排保持 deferred；FR-306 在本 SPEC 只获得“不绕过本合同”的未来边界。

## 21. 完成定义

- Resources/Tools、envelope、权限、revision、freshness、idempotency 和失败合同可测试。
- 12 条不变量、25 个测试有映射。
- FR-306 及关联 FR 进入追踪，但无 runtime 实现。
- 未选择 SDK/传输；测试未执行。

当前结论：本 SPEC v0.1 经整体授权于 2026-07-13 标记 `Approved`。允许进入 S9，不授权 A2A、多 Agent 或 MCP runtime 实现。
