# A4 查询层权限与舱室强制执行切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-A4-ACCESS-POLICY-001` |
| 版本 | `0.1` |
| 状态 | `Approved for A4 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-A-ACCESS-POLICY-001` |
| 上游 | S1 v0.6、S3 v0.4、S4 v0.4、S6 v0.5 |
| 适用范围 | `SLICE-MVP-A-ACCESS-POLICY-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：证明固定合成单用户本地调用者的查询在身份、目的、舱室、字段和时间约束下被查询层强制执行——`allow`（全部请求字段）、`allow_with_redaction`（过滤后字段子集）或 `deny`（非泄露原因码）；多策略取最严格交集；任何未知或冲突默认拒绝；判决零写入。

非目标：多用户、家庭授权、托管人、数字遗产、sealed 紧急恢复（`DQ-003/004/009` deferred）、Grant 管理 UI、策略编辑器、外部 Agent/MCP runtime、真实数据。

## 2. 对象与字段

```yaml
access_request:
  caller_ref: synthetic caller ID
  purpose: synthetic_review | synthetic_export | unknown purpose string
  action: read | search | summarize
  resource_refs: [object IDs]
  field_paths: [requested field paths]
  authorization_refs: [grant IDs]
  requested_at: RFC3339 UTC instant
  synthetic_profile_id: a4_access_policy_v1

grant (固定合成授权, fixture 给定):
  grant_id: stable ID
  caller_ref: caller ID
  purpose: purpose string
  actions: [action]
  resource_refs: [object IDs]
  allowed_fields: [field paths]
  denied_fields: [field paths]
  valid_from / valid_until: RFC3339 UTC instant
  synthetic_profile_id: a4_access_policy_v1

policy_decision (请求时 Derived, 不持久化):
  decision: allow | allow_with_redaction | deny
  allowed_fields: [field paths]
  denied_fields: [requested field paths only]
  reason_code: closed enum
  policy_revision: a4_policy_v1
```

`reason_code ∈ {none, grant_expired, grant_scope_mismatch, unknown_caller, unknown_purpose, unknown_compartment, policy_missing, policy_conflict, sealed_excluded, field_denied}`。`denied_fields` 只回显 caller 自己请求的 field paths，不附加任何对象存在性或内容信息。

对象标注使用 S1 Policy Subject 字段：`sensitivity ∈ {normal, private, restricted, sealed}`、`compartments`（一项或多项）、`owner_ref`。

## 3. 判定规则

1. 无明确允许即拒绝：请求的 caller/purpose/action/resource/field 必须被至少一个有效 Grant 覆盖，且不被任何适用策略禁止。
2. Grant 有效性：`caller_ref`、`purpose`、`action`、`resource_refs` 全部匹配，且 `requested_at ∈ [valid_from, valid_until]`；任一不匹配或过期即无效。
3. 字段集：allowed 取所有适用策略的交集，denied 取并集；`allow_with_redaction` = 请求字段中仅子集通过；`deny` = 无任何字段可返回或策略显式拒绝。
4. 多舱室对象应用所有舱室策略的最严格交集；无法安全求交时 `policy_conflict` 拒绝。
5. `sensitivity=sealed` 的对象从 read/search/summarize 全部排除：`sealed_excluded`。
6. 未知 caller、未知 purpose、未知 compartment、策略缺失均 fail closed，对应固定 reason_code。
7. 时间求值只使用请求的 `requested_at` 与 Grant 的固定窗口；不读取系统时钟。

## 4. 时间、证据与权限

- 固定 A4 clock 只出现在 fixture；判决用 `requested_at` 与 Grant 窗口比较，不产生 Canonical revision。
- PolicyDecision 是请求时 Derived，不持久化、不作 Evidence Ref、Assertion input 或 ChangeSet trigger。
- Derived View（current_state 等）内容不得作为权限证据绕过判决；经视图发起的等价查询适用同一判决。
- A4 不实现 Grant 生命周期管理；Grant 全部由 fixture 给定。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `A4-INV-001` | 无明确允许即拒绝；未知 caller/purpose/compartment/策略缺失均 fail closed。 |
| `A4-INV-002` | 多舱室/多策略取最严格交集；allow 字段交集、deny 字段并集；无法求交默认拒绝。 |
| `A4-INV-003` | 拒绝响应只含 `decision/reason_code/denied_fields(请求回显)`，不泄露被拒内容、存在性侧信道或证据计数。 |
| `A4-INV-004` | 判决零写入：不产生 Canonical revision、不修改任何 Canonical 对象、trust/closeness/人格判断不变。 |
| `A4-INV-005` | `sealed` 对象从 read/search/summarize 全部排除。 |
| `A4-INV-006` | Grant 过期或 caller/purpose/action/scope 任一不匹配即无效，不得用缓存判决猜测。 |
| `A4-INV-007` | Derived View 内容不得作为权限证据；判决结果不是事实证据。 |

## 6. 失败、撤销与审计

- 判决器内部失败：fail closed 返回 `deny`（`policy_missing`），不得返回部分字段。
- 字段裁剪失败：不返回任何 payload，按 `deny` 处理。
- 判决无撤销语义（无写入）；审计仅记录非泄露 reason_code 分布，不记录被拒内容。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `A4-001` | owner caller、匹配 purpose/action、有效 Grant、normal 对象 | 请求全部字段 | `allow`，返回全部请求字段 |
| `A4-002` | restricted 对象，Grant 只覆盖字段子集 | 请求超集字段 | `allow_with_redaction`，allowed 为子集、denied 回显请求余量 |
| `A4-003` | 多舱室对象 [personal, health]，策略冲突或无法求交 | 查询 | 最严格交集；无法求交 `policy_conflict` 拒绝 |
| `A4-004` | Grant 已过期或 purpose/action/scope 不匹配 | 查询 | `deny`（`grant_expired`/`grant_scope_mismatch`），无字段返回 |
| `A4-005` | 未知 caller / 未知 purpose / 未知 compartment / 策略缺失 | 查询 | 全部 `deny`，对应固定 reason_code，无字段返回 |
| `A4-006` | `sealed` 对象 | read/search/summarize | `deny`（`sealed_excluded`），无字段返回 |
| `A4-007` | 执行 A4-001..006 全部查询后 | 检查 revision、Canonical 对象、trust/closeness/人格判断 | 全部不变，无新 revision |
| `A4-008` | 经 Derived View 内容发起等价查询 / 检查 deny 响应形状 | 判决与响应 | 判决一致；deny 响应只含合同字段，无泄漏 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `A4-001..008` passed result 存在，且所有 `A4-INV-*` 有正/反证明时，A4 才能标记 `verified`。未执行时必须保持 `not_executed`。
