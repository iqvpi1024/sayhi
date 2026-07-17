# MVP-A Answer Safety 验收合同

## 0. 状态

```yaml
contract_id: ACCEPT-MVP-A-AS-001
slice_id: SLICE-MVP-A-ANSWER-SAFETY-001
product_baseline: PRDv05.md v0.5
decision_ref: DEC-MVP-A-AS-001
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

本文定义 A1 的 exact 合同；尚无 manifest、fixture、oracle、runner 或实现。Markdown 完成不等于 suite materialized 或 passed。

## 1. 目标

证明一个固定合成查询可以根据 Canonical evidence、CoverageWindow、review status、valid time 和显式 freshness policy，诚实返回一个且仅一个六态 Answer Status，并保持查询完全只读。

## 2. 非目标

- 通用自然语言问答、搜索、RAG、LLM 或模型置信度。
- 权限 runtime、MCP、外部 Agent 或跨舱室推断。
- 冲突裁决、用户修正、ChangeSet 发布或撤销。
- Canonical `value=unknown`、`BTE-AT-038` 或 `DQ-012` 裁决。
- View 投影、UI、安装包、导出或迁移。

## 3. 固定对象与查询边界

Fixture 只使用中性合成 ID：

```yaml
owner_ref: synthetic_owner_001
subject_ref: synthetic_subject_001
query_id: query_answer_safety_001
query_claim: synthetic_claim_001
business_clock: fixed UTC timestamp
authorized_profile: owner_local_private_v1
```

禁止使用真实姓名、地址、组织、电话、邮箱、凭据、债务、健康或亲密关系数据。

所有 case 必须从独立的初始 snapshot 创建，不能把上一个 case 的结果作为下一个 case 的事实输入。Expected oracle 必须来自本合同和 Approved SPEC，不能从 evaluator actual 生成。

## 4. AnswerEnvelope 最小字段

每个成功的事实型查询至少返回：

```yaml
answer_status: verified | unconfirmed | disputed | not_covered | stale | unknown
answer_value: value | null | withheld
verification_scope: record_accuracy | statement_occurrence | viewpoint | world_claim | null
valid_time: requested + resolved scope
recorded_as_of: requested snapshot | current
evaluated_at: fixture clock
evidence_refs: authorized direct Source locators | []
coverage: relevant windows + gaps
reason_codes: [stable code]
data_revision: current canonical revision
assessment_policy_ref: versioned policy | not_applicable
```

非 `verified` 回答使用 `verification_scope=null`；不得添加 S2 枚举外值或写入 Canonical。

## 5. 场景

### AS-001：观点范围可 Verified

Given：存在 `assertion_kind=opinion`、`review_status=confirmed`、明确 `perspective_ref` 和直接 Source locator；查询 scope 为 `viewpoint`。

When：计算 AnswerEnvelope。

Then：

- `answer_status=verified`。
- `verification_scope=viewpoint`。
- `answer_value` 只表达“该主体持有该观点”。
- 同一记录不得被用来返回 world claim verified。
- Assertion kind 继续为 opinion，Canonical 不变。

### AS-002：陈述发生与世界事实分离

Given：存在 confirmed reported Assertion 与直接 Source。

When：分别查询 `statement_occurrence` 和 `world_claim`。

Then：前者可按合同 `verified`；后者不得因同一次确认自动 verified，若覆盖充分且无其他证据则为 `unknown`。

### AS-003：未审候选只能 Unconfirmed

Given：覆盖充分，存在可见但未审 Candidate；Canonical 无对应 confirmed claim。

When：查询该 claim。

Then：`answer_status=unconfirmed`，候选可在 reason 中引用但不得出现在 Canonical evidence refs，`data_revision` 不变。

### AS-004：冲突必须 Disputed

Given：同 subject/predicate/perspective、重叠 valid time 的两个不兼容 Assertion，各自有独立直接 Source；无用户裁决。

When：查询该 claim。

Then：

- `answer_status=disputed`、`answer_value=null`。
- 并列返回两方授权 evidence、valid time 和 perspective。
- 不按 recorded_at、数量、模型 confidence 或文案长度选胜者。
- 不创建冲突裁决或 Canonical revision。

### AS-005：覆盖不足必须 Not Covered

Given：CoverageWindow 从目标查询时间之后才开始，或 `continuous=unknown` 且零结果。

When：查询目标时间是否发生事件。

Then：`answer_status=not_covered`，coverage 显示起点/gap；不得返回 verified negative、unknown 或 no-event。

### AS-006：显式当前性要求产生 Stale

Given：当前查询只有一条可用证据；显式 fixture policy 声明当前性窗口，该证据已超期；无冲突、无 candidate、覆盖充分。

When：在 fixture clock 计算回答。

Then：`answer_status=stale`，返回 `assessment_policy_ref`、`evaluated_at` 和证据时间。用同一证据查询匹配的历史 valid time 时不得仅因年龄返回 stale。

### AS-007：覆盖充分但无法判断为 Unknown

Given：覆盖充分、无 candidate、无冲突、无满足验证规则的直接证据，且不是 freshness failure。

When：查询 claim。

Then：`answer_status=unknown`、`answer_value=null`、evidence refs 为空或只含非决定性直接上下文；不得写 Canonical unknown State。

### AS-008：Derived 不得作证

Given：唯一“证据”来自人物卡、旧 AnswerEnvelope、摘要或 receipt。

When：评估 claim。

Then：在覆盖充分且没有其他直接证据时返回 `answer_status=unknown` 并包含 `derived_evidence_forbidden`；Canonical evidence refs 为空，Derived payload 不被复制为 Source。

### AS-009：Fictional 保持隔离

Given：存在 confirmed `assertion_kind=fictional`，内容表面与查询 claim 一致。

When：查询现实 world claim。

Then：不得 verified；fictional Assertion 保持原类型，不进入现实 evidence。覆盖充分且无现实证据时返回 unknown。

### AS-010：查询严格只读且确定

Given：任一 AS-001..009 case 的独立 snapshot。

When：以相同 fixture clock、query 和 policy 重放两次。

Then：除明确排除的运行元数据外 AnswerEnvelope 语义相同；`data_revision`、Canonical/Ledger payload digest、Source count 和 Projection rows 均不变；无网络或工作区外读取。

### AS-011：结果写入失败不能发布 Pass

Given：所有语义断言通过，但 Verification Result 输出被注入失败。

When：runner 完成。

Then：suite 不得设置 passed，不得留下指向缺失/部分 artifact 的 current result；失败 run 信息保留为 failed/errored 证据。

## 6. 全局不变量

| ID | 断言 |
|---|---|
| `AS-INV-001` | 每个事实型回答恰有一个六态主状态 |
| `AS-INV-002` | verified scope 不扩大到未确认 world claim |
| `AS-INV-003` | not_covered、unknown、unconfirmed、stale、disputed 不互换 |
| `AS-INV-004` | Derived View、旧回答、摘要和 receipt 不作事实 Evidence |
| `AS-INV-005` | 冲突证据并列，不自动选胜者 |
| `AS-INV-006` | Answer freshness 与 View freshness 分离 |
| `AS-INV-007` | fictional/opinion/reported 内容类型不因查询改变 |
| `AS-INV-008` | 查询不写 Source、Canonical、Ledger 或 Projection |
| `AS-INV-009` | fixture、result 和日志仅含合成数据且不访问网络 |
| `AS-INV-010` | required result 只能来自同一次 current run |

## 7. Exact Required Mapping

以下是 A1 required upstream Test Ref 的唯一权威集合：

```yaml
answer_safety_required_contract_slices:
  AS-001: [SOM-AT-008, BTE-AT-020]
  AS-002: [BTE-AT-021]
  AS-003: [BTE-AT-024]
  AS-004: [SOM-AT-021, BTE-AT-030]
  AS-005: [BTE-AT-012, BTE-AT-013]
  AS-006: [BTE-AT-026, BTE-AT-027]
  AS-007: [BTE-AT-025]
  AS-008: [SOM-AT-009, BTE-AT-034, SIP-AT-006]
  AS-009: [SOM-AT-018]
  AS-010: [HTH-AT-006, HTH-AT-007, HTH-AT-008, HTH-AT-009, HTH-AT-013]
  AS-011: [HTH-AT-002, HTH-AT-019, HTH-AT-020, HTH-AT-023]
```

去重后为 24 个 upstream refs，另加 11 个 `AS-*` 场景，共 35 个 required result IDs。任何增删必须先更新本合同、Matrix 和 applicability review；不得因 SPEC 中还有其他测试而隐式扩大 required 集。

## 8. Suite 物化门禁

只有同时存在以下内容才可设置 `suite_materialized=true`：

- 独立 A1 manifest，绑定 PRD/Decision/SPEC/ADR/Trace。
- 固定合成 fixture、六态 case、CoverageWindow 和显式 freshness policy。
- 字段级 expected/forbidden oracle，不从实现生成。
- runner contract、adapter protocol、11 个可执行场景与结果 schema。
- required/optional/deferred 分类、artifact raw-byte hash 和隐私扫描。
- 旧 Micro suite 保持独立，不修改其 expected 来适配 A1。

## 9. 当前结论

`suite_defined=true`，`suite_materialized=false`，`suite_executed=false`，`suite_passed=false`。Trace 与 ADR 已完成；下一步只执行 `PLAN-MVP-A-AS-SUITE-001` 的 `AS-PRE-001` 物化固定合成 fixture/oracle，不得开始 A1 业务代码。
