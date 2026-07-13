# Micro-MVP Given/When/Then 验收场景

## 1. 测试状态

| 字段 | 值 |
|---|---|
| `suite_id` | `micro_mvp_relationship_state_v0` |
| `suite_defined` | `true` |
| `suite_executed` | `false` |
| `suite_passed` | `false` |
| 数据类型 | 全合成 fixture |
| 外部网络 | 禁止 |
| 真实个人数据 | 禁止 |

依据 PRD §6.14 和 §22.1，本文只定义验收场景。尚无实现和测试运行器，因此不得描述为通过。

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
source_id: src_micro_001
source_type: synthetic_text
language: zh-CN
text: "从2031年9月1日起，我不再与 person_beta 联系。"
locator:
  start: 0
  end: 35
```

`locator.end` 的最终计数单位由 Ingestion & Migration SPEC 定义；Micro 测试只要求 proposal 能回指同一 Source 片段，不能用 Derived View 作为证据。依据 PRD §6.2-§6.3、§7.2、§19.4。

### 3.3 初始 Canonical State

```yaml
data_revision: rev_010
entities:
  - entity_id: person_alpha
    entity_type: person
  - entity_id: person_beta
    entity_type: person
relationship:
  relationship_id: rel_alpha_beta
  participants: [person_alpha, person_beta]
  origin: project_peer
relationship_role_state:
  object_type: state
  state_id: state_role_001
  state_kind: relationship.role
  subject_ref: rel_alpha_beta
  value: peer
  valid_from: 2030-01-01T00:00:00+08:00
  valid_to: null
relationship_state:
  object_type: state
  state_id: state_contact_001
  state_kind: relationship.contact
  subject_ref: rel_alpha_beta
  value: active
  valid_from: 2030-01-01T00:00:00+08:00
  valid_to: null
protected_semantics:
  trust: unknown
  closeness: unknown
  personality_hypotheses: []
core_views:
  person_card:
    view_revision: rev_010
    contact_state: active
  relationship_timeline:
    view_revision: rev_010
    current_contact_state: active
```

`RelationshipState` 已根据 `BQ-001` 裁决为 `State(state_kind=relationship.contact)`；物理 Schema 仍由后续实现 ADR 决定。

### 3.4 允许与禁止变化

允许 proposal 触达的语义：

```text
state[relationship.contact].value
relationship_state.valid_interval
recorded_at
trigger_sources
impact_set.person_card
impact_set.relationship_timeline
```

禁止被该输入自动或连带修改的语义：

```text
relationship.origin
state[relationship.role].value
state[relationship.trust].value
state[relationship.closeness].value
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
- `impact_set` 至少且仅针对 Micro 必需视图列出人物卡和关系时间线；是否允许额外视图受 `IQ-001` 裁决。
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
- 精确读取屏障和 5 秒 SLO 的关系受 `IQ-002` 裁决；安全断言不受该问题影响。

依据：PRD §6.9、§10.1-§10.3、§21.2、§24.1、§26 Case A。

### MM-006：Historical State 不被 Current State 覆盖

关联需求：FR-009。

Given：当前 revision 为 `rev_011`。

When：分别查询 `transition_at` 之前和之后的 Relationship 状态。

Then：

- `transition_at` 之前的查询返回 `active`。
- `transition_at` 及之后的当前查询返回 `no_contact`。
- 两次查询都能回到对应状态的 revision 与 Source/ChangeSet 证据链。
- 历史 `origin=project_peer` 和 `role=peer` 始终保留。
- 不允许用 `no_contact` 覆盖或删除旧 `active` 记录。

依据：PRD §6.6、§9.1、§12.2、§13.2-§13.3、§24.1。

### MM-007：禁止变化字段保持字节级或语义级不变

关联需求：FR-003、FR-004、FR-006。

Given：保存 `rev_010` 中禁止变化路径的 canonical serialization 或等价稳定 digest。

When：完成 MM-004 和 MM-005。

Then：

- `origin`、`role`、`trust`、`closeness`、`personality_hypotheses` 与发布前语义相等。
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
- 产生一个可区分于 `rev_010` 和 `rev_011` 的撤销后 revision；最终编号方案由 ChangeSet SPEC 定义。
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
- 发布结果是明确 conflict/failure，不产生部分 RelationshipState。
- 原 ChangeSet 保持可审计，并可按后续 SPEC 规定重新基于新 revision 提案。
- 人物卡和关系时间线继续对应发布前的当前 revision。

依据：PRD §11.2、§12.1、§21.1、§25.2。具体错误码和 retry 状态由 ChangeSet SPEC 定义。

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
| INV-008 | `trust`、`closeness`、`origin`、`role`、人格判断不被联系状态输入连带修改 | §13.3、§24.1 |
| INV-009 | 失败时旧 Canonical 安全可读，旧 L2 不冒充最新 | §21.1、§25.2 |
| INV-010 | 所有 fixture 和输出不含真实个人数据 | PRD 隐私说明、§24.1、§26 |

## 6. 可执行化门禁

在把本文转成实际测试前必须完成：

`BQ-001` 与 `BQ-003` 已于 2026-07-13 裁决，并由 Semantic Object Model SPEC 固化。剩余可执行化门禁：

- `IQ-001`：确认 Micro Core View 最终封闭集合。
- `IQ-002`：确认 L2 读取屏障与 SLO。
- `IQ-008`：确认撤销 revision 语义。
- `IQ-010`：确认区间端点规则。

测试实现完成后，验证结果必须记录实际命令、开始/结束时间、环境、退出码、失败用例和产物路径；只更新 `suite_passed=true` 是不充分的。
