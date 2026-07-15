# Micro-MVP Given/When/Then 验收场景

## 1. 测试状态

| 字段 | 值 |
|---|---|
| `suite_id` | `micro_mvp_relationship_state_v3` |
| `product_baseline` | `PRDv05.md` v0.5 |
| `suite_defined` | `true` |
| `suite_materialized` | `false` |
| `suite_executed` | `false` |
| `suite_passed` | `false` |
| 数据类型 | 全合成 fixture |
| 外部网络 | 禁止 |
| 真实个人数据 | 禁止 |

依据 PRD v0.5 §6.14 和 §22.1，本文只定义验收场景。尚无实现和测试运行器，因此不得描述为通过。

## 2. 验收范围

本套件只证明 PRD §24.1 和 §26 Case A 的一条链路：

```text
synthetic text Source
  -> Shiling proposal
  -> user approval
  -> atomic RelationshipState publication
  -> person card + relationship timeline read new revision
  -> historical relationship retained
  -> trust/closeness/personality untouched
  -> whole ChangeSet revert
  -> both Core Views consistent again
```

不覆盖：通用 NLP、模糊时间解析、实体消歧、提醒、Commitment、冲突来源、CoverageWindow、权限舱室、外部 Agent、连接器、同步、财务、健康、决策和迁移。依据 PRD §24.1、§24.7。

## 3. 固定合成 Fixture

### 3.1 时钟

```text
now = 2031-10-15T02:00:00Z
source_timezone = Asia/Shanghai
transition_at = 2031-09-01T00:00:00+08:00
```

测试必须使用固定时钟，禁止读取运行机器当前时间作为业务输入。

### 3.2 Source

```yaml
source_policy_profile:
  policy_profile_ref: owner_intake_private_v1
  sensitivity_floor: private
  default_compartments: [personal]
  retention_policy_ref: user_controlled_v1
  direct_owner_recorder_fallback: owner_ref
  unresolved_subject_access: owner_intake_only
intake_request:
  intake_id: intake_micro_001
  source_kind: synthetic_text
  source_system: synthetic_fixture
  inline_content: "从2031年9月1日起，我不再与 person_beta 联系。"
  source_created_at: unknown
  language: zh-CN
  source_timezone: Asia/Shanghai
  declared_media_type: text/plain; charset=utf-8
  content_hash: 53bbc4541a77a435f5401b459d1d3e2c21af7a343931341c6db498c28880013c
  owner_ref: person_alpha
  policy_profile_ref: owner_intake_private_v1
  recorder_ref: person_alpha
  declared_subject_refs: [person_alpha, person_beta]
  declared_third_party_present: true
  declared_compartments: [personal]
  sensitivity_hint: private
expected_append_receipt:
  receipt_id: receipt_micro_001
  intake_id: intake_micro_001
  source_id: src_micro_001
  status: stored
  hash_algorithm: sha256
  byte_length: 58
  media_type: text/plain; charset=utf-8
  ingested_at: 2031-10-15T02:00:00Z
  locator_scheme: text_utf8_byte_range_v1
  coverage_raw_status: absent
  policy_profile_ref: owner_intake_private_v1
  policy_resolution_status: declared
  effective_policy:
    owner_ref: person_alpha
    recorder_ref: person_alpha
    subject_refs: [person_alpha, person_beta]
    sensitivity: private
    compartments: [personal]
    third_party_present: true
    retention_policy_ref: user_controlled_v1
    retention_state: active
  failure: null
  actor: user
expected_source:
  source_id: src_micro_001
  source_kind: synthetic_text
  source_system: synthetic_fixture
  content_ref: fixture://micro/src_micro_001.txt
  content_hash: 53bbc4541a77a435f5401b459d1d3e2c21af7a343931341c6db498c28880013c
  source_created_at: unknown
  ingested_at: 2031-10-15T02:00:00Z
  language: zh-CN
  source_timezone: Asia/Shanghai
  locator_scheme: text_utf8_byte_range_v1
  append_receipt_id: receipt_micro_001
  policy_profile_ref: owner_intake_private_v1
  policy_resolution_status: declared
  owner_ref: person_alpha
  subject_refs: [person_alpha, person_beta]
  recorder_ref: person_alpha
  sensitivity: private
  compartments: [personal]
  third_party_present: true
  retention_policy_ref: user_controlled_v1
  retention_state: active
  locator:
    start_byte: 0
    end_byte_exclusive: 58

historical_source_fixture:
  inline_content: "从2030年1月1日起，我与 person_beta 保持联系。"
  expected_source:
    source_id: src_history_001
    source_kind: synthetic_text
    source_system: synthetic_fixture
    content_ref: fixture://micro/src_history_001.txt
    content_hash: 34cdc57abf184dbbd8951ca148b6d4b92b9ceecf455ef0bb55cff63be9f043b1
    byte_length: 58
    source_created_at: 2030-01-01T00:00:00+08:00
    ingested_at: 2030-01-01T00:05:00+08:00
    language: zh-CN
    source_timezone: Asia/Shanghai
    locator_scheme: text_utf8_byte_range_v1
    append_receipt_id: receipt_history_001
    policy_profile_ref: owner_intake_private_v1
    policy_resolution_status: declared
    owner_ref: person_alpha
    subject_refs: [person_alpha, person_beta]
    recorder_ref: person_alpha
    sensitivity: private
    compartments: [personal]
    third_party_present: true
    retention_policy_ref: user_controlled_v1
    retention_state: active
    locator:
      start_byte: 0
      end_byte_exclusive: 58
```

两个 locator 都是各自原始 UTF-8 字节序列上的零基半开区间，并分别绑定自身 hash；字符数、UTF-16 code unit 或渲染后文本偏移均不是本 fixture 的 locator。新 proposal 必须回指 `src_micro_001`；旧 `active` State 必须回指独立的 `src_history_001`，两份证据不得互换。Source policy 字段只由显式 Intake 声明和固定 profile 产生，不从正文同步解析。依据 PRD v0.5 §6.2-§6.3、§7.2、§17、§19.4；S1 v0.5 §6.2；S4 v0.4 §6.6；S9 v0.4 §6.1。

### 3.3 初始 Canonical State

```yaml
data_revision: rev_010
entities:
  - entity_id: person_alpha
    object_type: entity
    entity_kind: person
    schema_version: noetide.semantic.v1
    object_revision: rev_001
    owner_ref: person_alpha
    created_at: 2030-01-01T00:00:00+08:00
    created_by: user
    sensitivity: private
    compartments: [personal]
    subject_refs: [person_alpha]
    third_party_present: false
    recorder_ref: person_alpha
    retention_policy_ref: user_controlled_v1
    retention_state: active
    extensions: {}
    identity_status: active
  - entity_id: person_beta
    object_type: entity
    entity_kind: person
    schema_version: noetide.semantic.v1
    object_revision: rev_002
    owner_ref: person_alpha
    created_at: 2030-01-01T00:00:00+08:00
    created_by: user
    sensitivity: private
    compartments: [personal]
    subject_refs: [person_beta]
    third_party_present: true
    recorder_ref: person_alpha
    retention_policy_ref: user_controlled_v1
    retention_state: active
    extensions: {}
    identity_status: active
relationship:
  relationship_id: rel_alpha_beta
  object_type: relationship
  schema_version: noetide.semantic.v1
  object_revision: rev_003
  owner_ref: person_alpha
  created_at: 2030-01-01T00:00:00+08:00
  created_by: user
  sensitivity: private
  compartments: [personal]
  subject_refs: [person_alpha, person_beta]
  third_party_present: true
  recorder_ref: person_alpha
  retention_policy_ref: user_controlled_v1
  retention_state: active
  extensions: {}
  participant_refs: [person_alpha, person_beta]
  origin: project_peer
  evidence_refs: []
  evidence_status: missing
  identity_status: active
relationship_role_state:
  object_type: state
  state_id: state_role_001
  schema_version: noetide.semantic.v1
  object_revision: rev_004
  owner_ref: person_alpha
  created_at: 2030-01-01T00:00:00+08:00
  created_by: user
  sensitivity: private
  compartments: [personal]
  subject_refs: [person_alpha, person_beta]
  third_party_present: true
  recorder_ref: person_alpha
  retention_policy_ref: user_controlled_v1
  retention_state: active
  extensions: {}
  state_kind: relationship.role
  subject_ref: rel_alpha_beta
  value: peer
  valid_time:
    kind: interval
    start: {boundary_kind: known, value: 2030-01-01T00:00:00+08:00, precision: instant, certainty: exact, timezone: Asia/Shanghai, resolution_status: confirmed}
    end: {boundary_kind: unbounded, value: null, precision: unknown, certainty: unknown, timezone: not_applicable, resolution_status: confirmed}
    bounds: "[)"
  recorded_at: 2030-01-01T00:00:00+08:00
  recorded_by: user
  evidence_refs: []
  evidence_status: missing
  review_status: confirmed
relationship_state:
  object_type: state
  state_id: state_contact_001
  schema_version: noetide.semantic.v1
  object_revision: rev_005
  owner_ref: person_alpha
  created_at: 2030-01-01T00:10:00+08:00
  created_by: user
  sensitivity: private
  compartments: [personal]
  subject_refs: [person_alpha, person_beta]
  third_party_present: true
  recorder_ref: person_alpha
  retention_policy_ref: user_controlled_v1
  retention_state: active
  extensions: {}
  state_kind: relationship.contact
  subject_ref: rel_alpha_beta
  value: active
  valid_time:
    kind: interval
    start: {boundary_kind: known, value: 2030-01-01T00:00:00+08:00, precision: instant, certainty: exact, timezone: Asia/Shanghai, resolution_status: confirmed}
    end: {boundary_kind: unbounded, value: null, precision: unknown, certainty: unknown, timezone: not_applicable, resolution_status: confirmed}
    bounds: "[)"
  recorded_at: 2030-01-01T00:10:00+08:00
  recorded_by: user
  evidence_refs:
    - source_id: src_history_001
      locator: {scheme: text_utf8_byte_range_v1, start_byte: 0, end_byte_exclusive: 58}
      stance: supports
      claim_ref: state_contact_001
  evidence_status: present
  review_status: confirmed
trust_assertion:
  assertion_id: assertion_trust_001
  object_type: assertion
  schema_version: noetide.semantic.v1
  object_revision: rev_006
  owner_ref: person_alpha
  created_at: 2030-02-01T00:00:00+08:00
  created_by: user
  sensitivity: private
  compartments: [personal]
  subject_refs: [person_alpha, person_beta]
  third_party_present: true
  recorder_ref: person_alpha
  retention_policy_ref: user_controlled_v1
  retention_state: active
  extensions: {}
  subject_ref: rel_alpha_beta
  predicate: relationship.trust_assessment
  value: synthetic_trust_baseline
  assertion_kind: opinion
  perspective_ref: person_alpha
  evidence_refs: []
  evidence_status: missing
  review_status: confirmed
  recorded_at: 2030-02-01T00:00:00+08:00
closeness_assertion:
  assertion_id: assertion_closeness_001
  object_type: assertion
  schema_version: noetide.semantic.v1
  object_revision: rev_007
  owner_ref: person_alpha
  created_at: 2030-02-01T00:00:00+08:00
  created_by: user
  sensitivity: private
  compartments: [personal]
  subject_refs: [person_alpha, person_beta]
  third_party_present: true
  recorder_ref: person_alpha
  retention_policy_ref: user_controlled_v1
  retention_state: active
  extensions: {}
  subject_ref: rel_alpha_beta
  predicate: relationship.closeness_assessment
  value: synthetic_closeness_baseline
  assertion_kind: opinion
  perspective_ref: person_alpha
  evidence_refs: []
  evidence_status: missing
  review_status: confirmed
  recorded_at: 2030-02-01T00:00:00+08:00
personality_hypothesis_sentinel:
  hypothesis_id: hypothesis_personality_sentinel_001
  object_type: hypothesis
  schema_version: noetide.semantic.v1
  object_revision: rev_008
  owner_ref: person_alpha
  created_at: 2030-02-01T00:00:00+08:00
  created_by: user
  sensitivity: private
  compartments: [personal]
  subject_refs: [person_alpha]
  third_party_present: false
  recorder_ref: person_alpha
  retention_policy_ref: user_controlled_v1
  retention_state: active
  extensions: {fixture_role: read_only_protected_sentinel}
  statement: synthetic_personality_pattern_sentinel
  scope_ref: rel_alpha_beta
  evidence_for: []
  evidence_against: []
  status: active
protected_semantics:
  trust_assertions: [assertion_trust_001]
  closeness_assertions: [assertion_closeness_001]
  personality_hypotheses: [hypothesis_personality_sentinel_001]
core_views:
  person_card:
    data_revision: rev_010
    view_revision: rev_010
    contact_state: active
  relationship_timeline:
    data_revision: rev_010
    view_revision: rev_010
    current_contact_state: active
```

`RelationshipState` 已根据 `BQ-001` 裁决为 `State(state_kind=relationship.contact)`；物理 Schema 仍由后续实现 ADR 决定。

`trust_assertion`、`closeness_assertion` 和 `personality_hypothesis_sentinel` 都是只读初始 Canonical seed。runner 必须在 proposal 前记录三者各自的 stable ID、集合成员、`object_revision` 与规范 payload digest，并在 publish、L2 收敛和 revert 后逐项比较。空集合、只比较数量或忽略 sentinel payload 都不能满足 protected-change oracle。该 sentinel 不进入 Shiling 输入，不授权 Hypothesis 生成、修改、查询能力或生命周期实现。

### 3.4 允许与禁止变化

允许 proposal 触达的语义：

```text
state[relationship.contact].value
state[relationship.contact].valid_time
recorded_at
trigger_sources
impact_set.person_card
impact_set.relationship_timeline
```

禁止被该输入自动或连带修改的语义：

```text
relationship.origin
state[relationship.role].value
assertion[relationship.trust].value
assertion[relationship.closeness].value
hypothesis[relationship.personality]
entity identity
unrelated canonical objects
```

依据 PRD §6.6-§6.7、§13.3、§24.1、§26 Case A。

## 4. 场景

### MM-001：合成文本保留为可定位 Source

关联需求：FR-001、FR-002。

Given：系统处于 `rev_010`，输入 `src_micro_001`，且 Source 内容被明确标记为 synthetic data。

When：系统接受该文本输入。

Then：

- 返回可验证的 Source receipt，不得静默丢失输入。
- Source 保留原文、语言、时区和稳定 locator。
- 尚未生成用户确认前，不改变 `rev_010` 的 Relationship 当前状态。
- 后续 proposal 的 `trigger_sources` 必须引用 `src_micro_001` 和同一 locator。
- Source Append 使用独立审计 receipt，不要求 ChangeSet；任何由 Source 产生的 Canonical 语义写入必须经过 ChangeSet。
- Source 的 owner/recorder/subject/third-party/sensitivity/compartment/retention 字段与 expected receipt 完全匹配固定 Intake 声明和 `owner_intake_private_v1` profile；正文不参与 policy 初始化。

依据：PRD §7.2、§18.2、§20 FR-001/FR-002、§21.1、§25.2。

### MM-002：识灵只提出允许的联系状态候选

关联需求：FR-003、FR-005。

Given：`src_micro_001` 已可定位，两个 Entity 和 Relationship 已存在且无歧义。

When：识灵处理该 Source。

Then：

- 生成一个 `status=proposed` 的 ChangeSet。
- proposal 表达从 `transition_at` 起查询当前联系状态应为 `no_contact`。
- proposal 保留此前 `active` 状态的历史有效期，不执行 in-place overwrite。
- `trigger_sources` 只包含原始 Source 证据，不引用人物卡、关系时间线、摘要或缓存作为事实证据。
- 新 `no_contact` State 的 `evidence_status=present`，且其 `evidence_refs` 只指向上述 58-byte Source locator。
- `impact_set` 的 Derived View 子集必须且只能列出人物卡和关系时间线；Canonical contact State 目标另行完整列出。
- 影响预览明确列出所有“允许变化”和“禁止变化”。
- `trust`、`closeness`、`origin`、`role` 和人格 Hypothesis 不出现在写 proposal 中。

依据：PRD §6.3、§6.6-§6.7、§11、§13.3、§18.3-§18.4、§24.1、§26 Case A。

### MM-003：未确认候选不能改变 Canonical 或 Core View

关联需求：FR-004、FR-005。

Given：MM-002 产生 `status=proposed` 的 ChangeSet，当前为 `rev_010`。

When：用户只查看影响预览，尚未确认。

Then：

- `data_revision` 仍为 `rev_010`。
- Canonical 当前 `contact_state` 仍为 `active`。
- 人物卡和关系时间线仍读取 `rev_010`。
- Agent 或查询不能把 proposal 当成已确认事实；若展示候选，必须标识为未确认。

依据：PRD §6.1、§6.7、§11.1-§11.3、§18.4、§19.3。

### MM-004：一次确认触发原子 L1 发布

关联需求：FR-004、FR-007。

Given：ChangeSet 的 `base_revision=rev_010`，proposal 已通过用户单次确认，且当前 revision 仍为 `rev_010`。

When：系统发布该 ChangeSet。

Then：

- 发布要么完整成功，要么完整失败，不存在只结束 `active` 而没有建立 `no_contact` 的半状态。
- 成功时只产生一个新的 `published_revision`，记为 `rev_011`。
- 在 `transition_at` 之前的有效时间查询返回 `active`；从 `transition_at` 起的查询返回 `no_contact`。
- `recorded_at=now`，不得伪装为系统在 `transition_at` 已经知道该事实。
- preflight attempt 必须先持久化；全部复检通过后 ChangeSet 才从 approved 进入 publishing。
- receipt 列出规范变更、受影响 Core View 和各项传播结果。
- 失败时不增加 revision，`rev_010` 继续完整可读，并返回失败回执。

依据：PRD §9.1、§10.2、§11、§21.1、§25.2、§26 Case A。

### MM-005：人物卡与关系时间线读取同一新 revision

关联需求：FR-006。

Given：MM-004 已成功发布 `rev_011`。

When：同一用户会话读取人物卡和关系时间线。

Then：

- 两个视图都返回 `view_revision=rev_011`，并标明对应 `data_revision=rev_011`。
- 人物卡当前联系状态为 `no_contact`。
- 关系时间线当前联系状态为 `no_contact`，并保留之前 `active` 的历史段。
- 不允许一个视图返回 `rev_011`、另一个把 `rev_010` 冒充当前值。
- 发布响应构成同会话 Publish Barrier；5 秒是单独测量的 SLO，不允许在窗口内把旧值标成 current。

依据：PRD §6.9、§10.1-§10.3、§21.2、§24.1、§26 Case A。

### MM-006：Historical State 不被 Current State 覆盖

关联需求：FR-009。

Given：当前 revision 为 `rev_011`。

When：分别查询 `transition_at` 之前和之后的 Relationship 状态。

Then：

- `transition_at` 之前的查询返回 `active`。
- `transition_at` 及之后的当前查询返回 `no_contact`。
- 两次查询都能回到对应 State revision 与各自独立的 Source evidence：旧 `active` 只引用 `src_history_001`，新 `no_contact` 只引用 `src_micro_001`；不得把新 Source 反向绑定为旧状态证据。ChangeSet 只提供发布审计链，不能充当事实 Evidence Ref。
- 历史 `origin=project_peer` 和 `role=peer` 始终保留。
- 不允许用 `no_contact` 覆盖或删除旧 `active` 记录。

依据：PRD §6.6、§9.1、§12.2、§13.2-§13.3、§24.1。

### MM-007：禁止变化字段保持字节级或语义级不变

关联需求：FR-003、FR-004、FR-006。

Given：保存 `rev_010` 中禁止变化路径的 canonical serialization 或等价稳定 digest；trust/closeness/personality 三个集合均为非空，且包含固定 stable ID。

When：完成 MM-004 和 MM-005。

Then：

- `origin`、`role`、非空 trust/closeness opinion Assertion 集合、只读 `personality_hypotheses` sentinel 与发布前语义相等。
- `assertion_trust_001`、`assertion_closeness_001`、`hypothesis_personality_sentinel_001` 的成员关系、stable ID、`object_revision` 和规范 payload digest 分别不变；空集合结果不得被接受为通过。
- 不新增“低信任”“关系疏远”“回避型人格”等 Assertion/Hypothesis。
- 不修改两个 Entity 的 identity。
- 不修改任何无依赖对象的 revision；若系统采用全局 revision，必须证明其语义 payload 未变。

依据：PRD §6.7、§12.2、§13.3-§13.4、§24.1、§26 Case A。

### MM-008：撤销整个 ChangeSet 后 Core View 恢复一致

关联需求：FR-007。

Given：ChangeSet 已发布为 `rev_011`，人物卡和关系时间线均已对齐 `rev_011`。

When：用户对该已发布 ChangeSet 执行一次整包撤销。

Then：

- 撤销通过审计可见的修订表达，不擦除 `rev_011` 和原 ChangeSet 历史。
- 当前 Canonical 的联系状态恢复为发布前等价语义 `active`。
- 补偿 ChangeSet 以 `rev_011` 为 base，成功时产生可区分的 `rev_012`；不得把全局 revision 指针退回 `rev_010`。
- 人物卡和关系时间线都读取同一撤销后 revision，并显示当前 `active`。
- 默认关系时间线不得继续把已撤销的 `no_contact` 当作有效事实；审计入口仍可查看该发布与撤销。
- `origin`、`role`、`trust`、`closeness` 和人格 Hypothesis 继续不变。
- receipt 明确列出已恢复、已重建、失败和跳过项。

依据：PRD §11.2-§11.3、§12.3、§20 FR-007、§22.2、§24.1、§26 Case A。

### MM-009：stale base revision 必须拒绝且不能半发布

关联需求：FR-004。

Given：一个 ChangeSet 的 `base_revision=rev_010`，但当前 Canonical 已由另一合法变更推进到不同 revision。

When：尝试发布该旧 ChangeSet。

Then：

- 系统不得静默覆盖新 revision。
- Publish Attempt 先持久化并记录 `observed_data_revision`、`preflight_result=conflict`、稳定 reason 和 receipt。
- 原 ChangeSet 从 `approved` 合法进入终态 `conflicted`，不得进入 `publishing`；`published_revision` 为空，不产生部分 RelationshipState。
- 同一 idempotency key + 同一 payload 重放返回同一 attempt/receipt，不新增 attempt 或 revision。
- 重新基于 current revision 只能创建新 `changeset_id`，并用 `retry_of` 引用原 conflicted ChangeSet；不得执行 `conflicted -> publishing`。
- 人物卡和关系时间线继续对应发布前的当前 revision。

依据：PRD v0.5 §11.2、§12.1、§21.1、§25.2；S3 v0.4 §6.5、§7.1-§7.2、§13-§14。

### MM-010：L2 传播失败不能把旧值冒充最新

关联需求：FR-006、FR-105 的最小失败切片。

Given：L1 已成功发布 `rev_011`，并注入一个人物卡或关系时间线投影更新失败。

When：用户在同一会话读取失败的 Core View。

Then：

- 系统不得返回 `rev_010` 的 `active` 并将其标为当前。
- 允许的安全结果只有：直接从 Canonical 读取 `rev_011`；或返回无旧 payload 的明确 `updating/unavailable` 状态。
- 响应包含 `data_revision=rev_011`、实际 `view_revision` 和非 fresh 状态。
- receipt 和失败队列记录未完成传播；成功视图不能掩盖失败视图。
- 修复后两个 Core View 必须收敛到 `rev_011`，且无需再次修改 Canonical。

依据：PRD §10.2、§14.3、§21.1-§21.2、§25.2。

## 5. 全局不变量 Oracle

每个场景执行后都必须检查：

| Oracle ID | 断言 | PRD 依据 |
|---|---|---|
| INV-001 | Derived View 从不作为规范事实证据 | §6.3、§8 |
| INV-002 | 未确认 proposal 不改变 Canonical | §6.1、§11 |
| INV-003 | L1 只有全成功或全失败 | §10.2、§21.1 |
| INV-004 | Current State 不覆盖 Historical State | §6.6、§9.1 |
| INV-005 | Hypothesis 不因重复或传播自动升级为 Fact | §6.4、§6.7 |
| INV-006 | 两个 Micro Core View 不得把不同 revision 同时冒充当前 | §10.1-§10.3 |
| INV-007 | 撤销不擦除审计历史 | §12.3 |
| INV-008 | 非空 trust/closeness opinion Assertion、`origin`、`role`、只读人格 sentinel 不被联系状态输入连带修改 | §13.3、§24.1 |
| INV-009 | 失败时旧 Canonical 安全可读，旧 L2 不冒充最新 | §21.1、§25.2 |
| INV-010 | 所有 fixture 和输出不含真实个人数据 | PRD 隐私说明、§24.1、§26 |

## 6. 可执行化门禁

`BQ-001`、`BQ-003`、`IQ-001`、`IQ-002`、`IQ-008`、`IQ-010` 和 `DEC-MICRO-GATE-001` 均已裁决并由纠偏版 S1/S3/S4/S5/S6/S9 固化，不再是产品语义门禁。

以下机器可读映射是 Micro required upstream Test Ref 的唯一权威集合。每个 `MM-*` 场景在 manifest 中必须包含其映射行的全部 Test Ref；未列出的 SPEC tests 均为 `reused_optional` 或 `deferred`，不得因矩阵中的长期 FR 引用被隐式提升为 Micro required。

```yaml
micro_required_contract_slices:
  MM-001: [SOM-AT-004, SOM-AT-026, SOM-AT-027, PAP-AT-029, PAP-AT-030, IMM-AT-001, IMM-AT-029, IMM-AT-030]
  MM-002: [SOM-AT-013, BTE-AT-001, BTE-AT-005, BTE-AT-017, BTE-AT-034, SHP-AT-004, SHP-AT-005, IMM-AT-005]
  MM-003: [SOM-AT-005, CS-AT-002, SHP-AT-002, IMM-AT-006]
  MM-004: [BTE-AT-001, BTE-AT-005, CS-AT-003, CS-AT-004]
  MM-005: [CS-AT-013, CS-AT-014]
  MM-006: [SOM-AT-015, BTE-AT-005, BTE-AT-027]
  MM-007: [SOM-AT-014, CS-AT-005, SHP-AT-005]
  MM-008: [CS-AT-017, CS-AT-018, CS-AT-019]
  MM-009: [CS-AT-008, CS-AT-024, CS-AT-030, CS-AT-031]
  MM-010: [BTE-AT-029, CS-AT-014, CS-AT-016, CS-AT-021, CS-AT-022]
```

当前可执行化门禁只有：

- 建立机器可读 suite manifest、上述固定 fixture 和字段级 forbidden-change oracle，使 `suite_materialized=true`。
- 实现受测模块与离线 runner；不得接入真实数据、外部网络或在线非确定模型。
- 对每个 MM 场景记录实际命令、开始/结束时间、环境、退出码、失败断言和 artifact digest。
- 同一次 `applicability=current` 的 run 中，MM-001 至 MM-010 和上述 exact upstream slices 全部 required 且 passed 后，才可设置 `suite_executed=true/suite_passed=true`；required skip/缺失只能得到 `run_result=partial`。

当前状态仍是合同场景已定义，但 suite 未物化、未执行、未通过。
