# Semantic Object Model SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-SOM-001` |
| 版本 | `0.4` |
| 状态 | `Approved` |
| 产品基线 | `PRDv04.md`，PRD v0.4 |
| 产品裁决 | `BQ-001` 至 `BQ-005`，2026-07-13 已决定 |
| 当前阶段 | Phase 1：Semantic Object Model |
| 下一依赖 | Bitemporal & Evidence SPEC |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 纠偏复审 | 2026-07-14；闭合 Source policy 初始化与只读 protected sentinel，不新增产品能力 |

本文定义语义合同，不选择数据库、编程语言、序列化框架、图引擎、事件溯源框架或模型供应商。

规范词：`MUST` 表示强制；`MUST NOT` 表示禁止；`SHOULD` 表示默认要求，偏离必须有理由；`MAY` 表示可选且不得成为其他强制项的隐式前提。

## 1. 目标

本 SPEC 的目标是建立一个小型、稳定、可纠正的规范语义内核，使系统能够：

1. 明确区分 Source、事实陈述、观点、推断、分析、预测、虚构和 Hypothesis。
2. 明确区分规范对象与 Derived View，阻止派生结果反向成为事实证据。
3. 封闭 PRD v0.4 的 12 个核心对象，并处理 PRD 中出现的别名词。
4. 为 Micro-MVP 的 `Source`、`Entity`、`Assertion`、`Relationship`、`State`/`RelationshipState`、`ChangeSet` 给出可测试的字段与边界。
5. 保证联系状态变化不覆盖历史，不自动修改 `origin`、`role`、`trust`、`closeness` 或人格判断。
6. 为后续双时态、ChangeSet、一致性、权限、存储和测试 SPEC 提供稳定上游合同。

依据：PRD §6-§9、§11-§13、§16、§20、§22、§24、§26。

## 2. 非目标

本 SPEC 不负责：

- 定义时间区间的开闭、模糊时间、时区换算和 CoverageWindow 算法。
- 定义 ChangeSet 的事务机制、并发控制、幂等、传播队列和 Core View 刷新实现。
- 决定 `verified` 的证据门槛、证据评分或来源独立性算法。
- 定义舱室策略求值、字段裁剪、密钥、加密或删除时限。
- 选择数据库、图结构、事件日志框架、JSON Schema 工具或 ID 生成算法。
- 实现通用 NLP、实体自动合并、Commitment、Decision、Outcome、Hypothesis 工作流。
- 扩展到多租户、多 Agent、A2A、连接器、多设备同步或历史数据迁移。

## 3. 术语

| 术语 | 规范定义 |
|---|---|
| Source | 原始材料及其来源、完整性和定位信息；它是 Source Vault 中的规范来源记录，但不是对世界的事实结论，也不属于 `data_revision` 管理的 Canonical Context |
| Canonical Context | 用户可迁移、可修订且由 `data_revision` 管理的规范语义对象集合；不包含 Source 原始载荷、Projection、Embedding、缓存和生成摘要 |
| Canonical Object | 12 个核心对象之一，或其中明确声明的语义子类型 |
| Derived View | 由 Canonical Context 计算出的 Projection、摘要、统计、索引、缓存或排序 |
| Assertion | 带主体、谓词、值、视角、证据和审查状态的陈述 |
| Fact | 查询层对 Assertion/State 和证据的受控解释，不是独立第 13 个对象 |
| Hypothesis | 可被反例削弱或推翻的模式、因果、人格或未来解释，与 Assertion 隔离 |
| State | 某主体在有效时间内的可变化值；历史 State 不因当前值变化而被覆盖 |
| RelationshipState | `State` 的语义配置，`subject_ref` 指向 `Relationship`；不是独立核心对象 |
| Review Status | 某条 Assertion/State 的审查处置状态，不等同于内容类型或查询回答状态 |
| Answer Status | 事实型回答的六态结果：`verified`、`unconfirmed`、`disputed`、`not_covered`、`stale`、`unknown`；这是对 PRD §9.4 “五态 + 必要时 unknown”的规范化，`unknown` 在本 SPEC 中是正式第六态 |
| Evidence Ref | 指向 Source 及其稳定 locator 的引用；Derived View 不能成为直接证据 |
| narrative_context | 结构化枚举无法表达的原话、背景或用户说明的可追溯容器 |
| supersede | 以新修订替代当前解释，同时保留旧记录、证据和审计历史 |
| Source Append | 原始 Source 的快速、可审计追加；不等同于 Canonical Context 的语义写入 |
| ChangeSet | 修改 Canonical Context 的唯一受控变更入口 |

## 4. 适用范围

### 4.1 规范深度

| 深度 | 对象 | 本 SPEC 责任 |
|---|---|---|
| 完整 | Source、Entity、Assertion、Relationship、State、ChangeSet | 定义字段、边界、最小状态和可执行验收 |
| 最小边界 | Episode、Hypothesis、Goal、Commitment、Decision、Outcome | 定义用途、必须隔离的语义和与别名的映射；不授权实现完整流程 |
| 非规范 | Projection、Embedding、搜索缓存、统计、摘要、推荐排序、Snapshot | 定义不得成为事实源且必须可重建 |

### 4.2 Micro-MVP 对象闭包

Micro-MVP 的规范对象闭包 MUST 仅包括：

```text
Source
Entity(person)
Relationship
Assertion（只在需要表达陈述/观点时）
State(state_kind=relationship.contact)
ChangeSet
```

人物卡和关系时间线是 Derived View，不属于规范对象闭包。

本闭包描述 Micro 的创建与修改能力。固定初始 fixture MAY 预置一个只读、全合成的 `Hypothesis` sentinel，只用于证明联系状态发布和撤销不会修改人格判断。实现只需把该对象当作受保护的 Canonical payload 比较 digest；MUST NOT 因此实现 Hypothesis 生成、编辑、检索、状态转换或推理工作流。

Assertion 是可选项，因为 PRD §24.1 的 Micro-MVP 要求联系状态变化不能连带修改信任和人格判断，而 PRD §13.2-§13.4 又要求主观判断与关系状态分离。只有输入或变更需要保留陈述、观点或视角时才创建 Assertion；单纯发布 `relationship.contact` State 不得为凑齐对象而创建 Assertion。

## 5. 对象与边界

### 5.1 12 个核心对象

| object_type | 规范用途 | 边界 |
|---|---|---|
| `source` | 保存原始材料、哈希、来源和 locator | 输入不是知识；Source 内容不能直接充当已验证事实 |
| `entity` | 表示人物、组织、地点、账号、项目、物品的稳定 identity | 实体身份与实体当前状态分离 |
| `episode` | 表示有时间边界的一段经历或事件集合 | Episode 不是稳定事实摘要；完整合同后置 |
| `assertion` | 表示可审查、有视角的陈述 | 内容类型、审查状态、回答状态必须正交 |
| `relationship` | 表示两个或多个 Entity 间稳定的关系 identity | 不直接承载会变化的 contact/trust/closeness 当前值 |
| `state` | 表示主体在有效区间内的可变化值 | Current 不覆盖 Historical |
| `hypothesis` | 表示可反驳解释 | 不得自动升级为 Assertion/Fact |
| `goal` | 表示目标和衡量标准 | 不等同于预测或 Commitment |
| `commitment` | 表示承诺、责任、待办和截止日期 | `Obligation` 映射到此对象 |
| `decision` | 表示问题、选项、约束、假设、预测和选择 | 不等同于最终 Outcome |
| `outcome` | 表示行动结果、副作用、复盘和校准 | `Calibration` 是其语义部分 |
| `changeset` | 表示对 Canonical Context 的受控变更 | 所有语义写入只能经此发布 |

领域扩展 MUST 归入上述边界。新增第 13 个核心对象需要新的产品决策，不能由实现、迁移器或模型自行创建。

### 5.2 别名与非核心词映射

| PRD 用词 | 规范映射 | 约束 |
|---|---|---|
| `RelationshipState` | `State`，且 `subject_ref.type=relationship` | 不是新对象 |
| `contact_state` | `State(state_kind=relationship.contact)` | 不作为 Relationship identity 的可覆盖字段 |
| `Obligation` | `Commitment` 的语义配置 | 不建立独立表意类型 |
| `viewpoint` | `Assertion(assertion_kind=opinion)`，必须有 `perspective_ref` | 不等同于客观事实 |
| `sentiment` | `Assertion(assertion_kind=opinion)`，必须有表达该感受主体的 `perspective_ref`；证据不足的解释进入 `Hypothesis` | 不建立独立字段或独立对象 |
| `Calibration` | `Outcome` 的校准字段/子结构 | 不建立独立对象 |
| `Snapshot` | Derived `Projection` | 过期只影响 freshness，不成为事实证据 |
| `Verified Context` | 查询层对规范对象、证据和策略的结果集合 | 不是持久核心对象 |

### 5.3 规范与派生边界

- Canonical Object MUST 可脱离当前软件导出并保持语义可读。
- Derived View MUST 声明其 Canonical 依赖和生成 revision。
- Derived View MUST NOT 出现在 `evidence_refs` 中。
- Embedding、缓存、摘要、统计和排序 MUST 可删除并从 Canonical/Source 重建。
- 模型输出首先是 proposal、Assertion candidate 或 Hypothesis candidate；MUST NOT 因写入 Projection 而成为事实。

## 6. 字段语义

### 6.1 共同 Envelope

除下述 Source/ChangeSet 例外外，Canonical Context Object MUST 具备：

| 字段 | 类型语义 | 约束 |
|---|---|---|
| `object_id` | stable identifier | 创建后不可复用；ID 算法后置 ADR |
| `object_type` | closed enum | 只能是 12 个核心类型 |
| `schema_version` | version identifier | 必须可决定字段解释规则 |
| `object_revision` | revision reference | 粒度由 ChangeSet SPEC 最终定义；不得静默倒退 |
| `owner_ref` | Entity/owner reference | 单用户不等于可省略 owner 语义 |
| `created_at` | recorded timestamp | 不是现实有效时间 |
| `created_by` | actor reference | 必须区分用户、识灵、导入器或外部 Agent |
| `sensitivity` | policy label | 预留 `normal/private/restricted/sealed`；求值由 Privacy SPEC 定义 |
| `compartments` | set of policy domains | 可多值；策略合并后置 |
| `extensions` | namespaced object | 未知扩展字段往返时不得被静默丢弃 |

本表中的 `object_id` 是抽象 ID 槽位；对象专属名称（例如 `entity_id`、`relationship_id`、`state_id`）是该槽位在相应类型中的序列化名称，MUST NOT 同时保存两个可能不同的 ID。`created_at` 是对象首次创建时间，`recorded_at` 是某次规范修订的记录时间；二者不得作为别名互换。

Source 是 12 类语义对象之一，但初次 Source Append 位于 Source Vault，使用 §6.2 专属字段和 append receipt，不增加 `data_revision`。ChangeSet 是 Revision Ledger 中的变更记录，使用 §6.7 专属字段。Source 的规范化语义元数据被纠正、封存或删除，以及任何由 Source 产生的 Canonical Context 写入，仍必须经 ChangeSet。对象专属字段 MUST NOT 被塞入 `extensions` 以绕过本 SPEC。

### 6.2 Source

| 字段 | 必需 | 语义 |
|---|---|---|
| `source_id` | MUST | Source stable ID |
| `source_kind` | MUST | `synthetic_text`、file、chat、audio 等来源种类；Micro 只用 `synthetic_text` |
| `content_ref` | MUST | 指向原始内容的人类可迁移引用，不规定物理路径 |
| `content_hash` | MUST | 完整性校验值；算法由 Storage SPEC/ADR 定义 |
| `source_system` | MUST | 来源系统或 `synthetic_fixture` |
| `source_created_at` | SHOULD | 来源自身产生时间；缺失必须显式 unknown |
| `ingested_at` | MUST | 进入 Source Vault 的时间 |
| `language` | MUST | 原文语言；翻译不能覆盖原文 |
| `source_timezone` | SHOULD | 原始时区或显式 unknown |
| `locator_scheme` | MUST | 定义 Source 片段如何稳定定位；Micro 固定为 `text_utf8_byte_range_v1` |
| `coverage_window_ref` | MAY | 覆盖窗口引用；详细语义后置 S2/S9 |
| `append_receipt_id` | MUST | Source Append 的审计回执 |
| `policy_profile_ref` | MUST | append 时使用的版本化 Source policy 初始化配置；不得来自 Source 正文 |
| `owner_ref` | MUST | 来自已授权 intake context 的 owner |
| `subject_refs` | MUST | 调用者显式声明且已验证的主体集合；未声明时为空集合，不得从正文同步猜测 |
| `recorder_ref` | MUST | 显式 recorder；仅 direct owner intake 可由 profile 确定性回落为 `owner_ref` |
| `sensitivity` | MUST | 不低于 profile floor；hint 只能升高，不能降低 |
| `compartments` | MUST | 已声明集合，或 profile 的保守默认集合 |
| `third_party_present` | MUST | `true|false|unknown`；缺少完整主体声明时必须为 unknown |
| `retention_policy_ref` | MUST | 来自已授权 profile 的版本化 policy，不由正文或模型选择 |
| `retention_state` | MUST | 初次成功 append 固定为 `active` |
| `policy_resolution_status` | MUST | `declared|provisional|confirmed`；见 S4/S9 |

Source Append MUST 在不等待语义处理的情况下返回 receipt。Source Append 成功 MUST NOT 自动产生或修改 Assertion、Relationship、State 或其他 Canonical Context 对象。

Source policy 初始化 MUST 是 `IntakeRequest` 中获授权的显式声明与 `policy_profile_ref` 的确定性函数，不得读取正文后再猜字段。显式 `subject_refs`、第三方声明和 compartment 声明完整且通过引用校验时可写 `policy_resolution_status=declared`；缺失时必须使用 profile 的保守默认：`sensitivity>=private`、`compartments=[personal]`、`subject_refs=[]`、`third_party_present=unknown`、`policy_resolution_status=provisional`。provisional Source 对非 owner/非 intake purpose 必须 fail closed。后续解析只能提出受控的 Source policy metadata 修订，不能静默扩大访问、降低 sensitivity 或把 Candidate 当已确认主体。

上述初始化合同只闭合 Source append schema，不要求 Micro 实现通用权限运行时。S4 定义字段与 fail-closed 语义，S9 定义输入来源和 receipt 映射。

`text_utf8_byte_range_v1` 使用原始 UTF-8 字节序列上的零基、尾端不含区间 `[start_byte,end_byte_exclusive)`，并绑定 `content_hash`。实现不得用字符、UTF-16 code unit 或渲染后文本偏移冒充该 scheme。

### 6.3 Entity

| 字段 | 必需 | 语义 |
|---|---|---|
| `entity_id` | MUST | stable identity |
| `entity_kind` | MUST | person、organization、place、account、project、item；Micro 只用 person |
| `canonical_label` | SHOULD | 用户可读标签，不作为唯一 identity |
| `aliases` | MAY | 带来源的别名集合 |
| `source_identities` | MAY | 原来源中的账号/标识引用 |
| `identity_status` | MUST | `provisional`、`active`、`merged`、`retired`；描述记录处置，不描述人的人生状态 |
| `merged_into` | 条件 MUST | `identity_status=merged` 时指向目标 Entity |

名称相同 MUST NOT 自动合并人物。模型相似度只能形成 merge proposal。

### 6.4 Assertion

| 字段 | 必需 | 语义 |
|---|---|---|
| `assertion_id` | MUST | stable ID |
| `subject_ref` | MUST | 被陈述的 Canonical Object/Entity |
| `predicate` | MUST | 受控谓词标识，不是自然语言整句 |
| `value` | MUST | 结构化值或有类型的文本值 |
| `assertion_kind` | MUST | 内容来源/性质的八态枚举 |
| `perspective_ref` | 条件 MUST | `reported`、`opinion`、`analysis` 等带主体视角时必需 |
| `evidence_refs` | MUST | 可为空但必须显式；有证据时只能指向 Source locator |
| `evidence_status` | MUST | `present|missing`；refs 非空时必须 present，refs 为空时必须 missing |
| `review_status` | MUST | `unreviewed`、`confirmed`、`denied`、`in_dispute` |
| `valid_time` | SHOULD | 现实有效时间占位；详细结构由 S2 定义 |
| `recorded_at` | MUST | 系统记录时间 |
| `narrative_context` | MAY | 见 §6.8 |
| `supersedes` | MAY | 被本修订替代的对象引用 |

`assertion_kind` 的合法值：

```text
observed | reported | quoted | opinion |
inferred | analysis | predicted | fictional
```

`disputed` 和 `unknown` MUST NOT 作为 `assertion_kind`。用户确认 MUST NOT 把 `opinion`、`inferred`、`analysis`、`predicted` 或 `fictional` 改写为 `observed`。

上述八态是对 PRD §8.1 “Assertion 类型”的规范精化：PRD 表中混列的 `disputed` 被移到 `review_status`/`answer_status`，`unknown` 被移到 `answer_status` 或有类型的 State value；二者不再描述 Assertion 的内容来源或性质。依据：`BQ-002` 与 `SOM-INV-004`。

### 6.5 Relationship

| 字段 | 必需 | 语义 |
|---|---|---|
| `relationship_id` | MUST | stable relationship identity |
| `participant_refs` | MUST | 至少两个互不相同的 Entity 引用 |
| `origin` | SHOULD | 历史来源语义；未知必须显式，不从联系状态猜测 |
| `evidence_refs` | MUST | 支持关系 identity/origin 的 Source 引用 |
| `evidence_status` | MUST | `present|missing`，必须与 refs 是否为空一致 |
| `narrative_context` | MAY | 无法被枚举压平的关系背景 |
| `identity_status` | MUST | `active`、`merged`、`retired`；不等同于联系状态 |

`contact_state`、时变 `role`、`trust`、`closeness`、`sentiment` MUST NOT 作为 Relationship identity 的可覆盖当前字段。`contact_state` 与 `role` 由 State 表达；`trust`、`closeness` 和 `sentiment` 属于带主体视角的 `opinion` Assertion，证据不足的解释只能进入 Hypothesis。

### 6.6 State 与 RelationshipState

| 字段 | 必需 | 语义 |
|---|---|---|
| `state_id` | MUST | stable State record ID |
| `state_kind` | MUST | 受控状态种类 |
| `subject_ref` | MUST | State 所描述的 Canonical Object |
| `value` | MUST | 与 `state_kind` 匹配的有类型值 |
| `valid_time` | MUST | 状态有效区间占位；端点规则由 S2 定义 |
| `recorded_at` | MUST | 系统得知/发布时间 |
| `evidence_refs` | MUST | Source locator 引用集合 |
| `evidence_status` | MUST | `present|missing`，必须与 refs 是否为空一致 |
| `review_status` | MUST | 与 Assertion 相同的审查状态集合 |
| `supersedes` | MAY | 纠正而非时间演化时引用被替代记录 |
| `narrative_context` | MAY | 状态原话与背景引用 |

Micro-MVP 的 RelationshipState 配置固定为：

```yaml
object_type: state
state_kind: relationship.contact
subject_ref:
  object_type: relationship
value: active | low_frequency | no_contact | blocked | unknown
```

其中 `value=unknown` 表示规范状态值明确为未知；它与查询层 `answer_status=unknown` 是不同轴。

对“从某时起不再联系”的确认发布 MUST 新建 `no_contact` State，并结束旧 `active` State 的有效区间；MUST NOT 原地覆盖旧 State。精确端点规则由 S2 定义。

### 6.7 ChangeSet

| 字段 | 必需 | 语义 |
|---|---|---|
| `changeset_id` | MUST | stable ID |
| `base_revision` | MUST | proposal 基于的 Canonical revision |
| `actor` | MUST | 发起 ChangeSet 的 actor；确认者必须记录在独立 review/approval event 中，不得覆盖发起者 |
| `trigger_sources` | MUST | 触发 proposal 的 Source locator |
| `proposals` | MUST | 一个或多个有类型的语义操作 |
| `impact_set` | MUST | 受影响 Canonical 对象和 Derived View |
| `risk_level` | MUST | `low`、`medium`、`high`、`critical` |
| `confirmation_policy` | MUST | `automatic`、`posthoc_revertible`、`single_confirmation`、`double_confirmation` |
| `status` | MUST | 见 §7.4 |
| `published_revision` | 条件 MUST | 发布成功后存在 |
| `receipt` | 条件 MUST | 发布尝试后存在 |
| `rollback_reference` | 条件 MUST | 可撤销发布成功后存在 |

每个 proposal 至少包含以下与 S3 一致的字段：

```text
proposal_id
operation
target_ref
before_digest
after_value
valid_time
evidence_refs
protected_paths
```

`target_ref` MUST 同时表达目标 `object_type`、stable ID（或新对象 ID）和可选 field path；`before_digest=absent` 表示新增。`evidence_refs` 只能指向 Source locator。下游 SPEC 不得以 `before`、`on_success` 或 `source_evidence_refs` 创建第二套同义字段。

Micro 联系状态 proposal 的 `protected_paths` MUST 至少包含：

```text
relationship.origin
state[relationship.role].value
assertion[relationship.trust].value
assertion[relationship.closeness].value
hypothesis[relationship.personality]
entity identity
unrelated canonical objects
```

ChangeSet 的完整事务、并发、幂等和 rollback 合同由 S3 定义。

### 6.8 narrative_context

`narrative_context` 是逻辑容器，不在本 SPEC 决定物理复制策略。它 MAY 包含：

| 字段 | 语义 |
|---|---|
| `source_refs` | 指向原话/背景所在 Source locator；引用原话时 MUST 存在 |
| `canonical_note` | 用户或明确 actor 编写的规范说明，必须记录作者和时间 |
| `language` | 文本语言 |

`canonical_note` MUST NOT 因存在于 Canonical Context 就自动成为其描述事实的证据。是否在导出包复制 excerpt 由 Storage SPEC 决定。

### 6.9 非 Micro 对象最小合同

| 对象 | 最小必需语义 | 禁止提前推断 |
|---|---|---|
| Episode | participants、source/evidence refs、time boundary | 不从一次 Episode 生成永久人格标签 |
| Hypothesis | statement、scope、evidence_for、evidence_against、status | 不自动升级为 Assertion/Fact |
| Goal | desired_state、measure、owner、status | 不把预测当成目标 |
| Commitment | obligation/commitment statement、responsible party、due semantics、status | 关系变化不自动取消 |
| Decision | question、options、constraints、assumptions、choice | 不把推荐当作用户选择 |
| Outcome | decision/action refs、observed result、side effects、calibration | 不用期望结果覆盖真实结果 |

本表只锁定边界，不表示这些对象进入 Micro-MVP 实现。

## 7. 状态机

### 7.1 Source Append Receipt

```text
received -> stored | rejected
stored -> immutable
```

解析失败不把已成功 `stored` 的 Source 改成 rejected；解析状态属于后续摄取处理状态。

### 7.2 Entity Identity Status

```text
provisional -> active | merged | retired
active -> merged | retired
merged -> active  (仅经已确认 split/revert ChangeSet)
retired -> active (仅经用户纠正 ChangeSet)
```

这是记录处置状态，不是人物生命周期。

### 7.3 Assertion/State Review Status

```text
unreviewed -> confirmed | denied | in_dispute
confirmed -> in_dispute | denied
in_dispute -> confirmed | denied
```

任何转换 MUST 保留触发证据、actor 和历史状态。`confirmed` 不自动意味着查询 `answer_status=verified`；映射由 S2/S5 定义。

### 7.4 ChangeSet Status

```yaml
changeset_status_values: [proposed, reviewing, approved, rejected, publishing, published, conflicted, failed, reverted]
```

```text
proposed -> reviewing
reviewing -> approved | rejected
approved -> publishing | conflicted | failed
publishing -> published | failed
published -> reverted
```

本 SPEC 只固定状态名称和方向。`conflicted` 与 `failed` 均为终态；前者表示发布前复检发现 revision/target conflict，后者表示非冲突性复检或发布失败。重试必须创建新 ChangeSet 并引用原项；preflight attempt、receipt、并发冲突、补偿 revision 和原子发布条件由 S3 定义，当前实现不得自行添加 `conflicted|failed -> publishing` 转换。

### 7.5 无线性状态机的对象

Relationship identity、普通 Entity 的现实语义、State 值本身不强制套用单一线性业务状态机。它们的变化通过新修订、有效区间和 ChangeSet 表达。

## 8. 允许与禁止的状态转换

### 8.1 允许

- Source receipt 从 `received` 到 `stored` 或 `rejected`。
- Source policy metadata 经受控修订从 `provisional -> declared|confirmed` 或 `declared -> confirmed`；不改变原 append receipt。
- 未审查 Assertion 经用户审查进入 `confirmed`、`denied` 或 `in_dispute`。
- 新证据使已确认 Assertion 进入 `in_dispute`，反证不得被删除。
- Relationship contact 经已批准 ChangeSet 从旧 State 演化为新 State，同时保留旧有效区间。
- 已合并 Entity 经可审计 split/revert ChangeSet 恢复为 active identity。

### 8.2 禁止

- `proposed` ChangeSet 直接跳到 `published`。
- 模型或外部 Agent 直接把 `review_status` 改为 `confirmed`。
- 用户确认导致 `assertion_kind` 改写为 `observed`。
- `Hypothesis` 直接变成 `Assertion`；如用户确认相关陈述，必须创建新 Assertion 并保留来源关系。
- Current State 通过原地覆盖删除 Historical State。
- Derived View、摘要、Embedding 或 Snapshot 被写入 `evidence_refs`。
- Source Append 隐式修改 Canonical Context。
- parser/model 把 provisional Source 直接标为 declared/confirmed，或通过 metadata 修订降低 sensitivity/移除适用 compartment。
- 未知 `object_type` 被默认为最相近的核心对象。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `SOM-INV-001` | 核心对象集合固定为 12 类；RelationshipState 仍是 State |
| `SOM-INV-002` | Source、Canonical Context、Derived View 三层不可混用 |
| `SOM-INV-003` | Derived View 永远不能成为直接事实证据 |
| `SOM-INV-004` | `assertion_kind`、`review_status`、`answer_status` 三轴正交 |
| `SOM-INV-005` | Hypothesis 不得自动升级为 Assertion/Fact |
| `SOM-INV-006` | Current State 不覆盖 Historical State |
| `SOM-INV-007` | Source Append 不要求 ChangeSet，但任何 Canonical 语义写入必须经 ChangeSet |
| `SOM-INV-008` | 对象引用必须指向存在且类型兼容的对象，否则整个语义写入失败 |
| `SOM-INV-009` | 联系状态变化不得连带修改 origin、role、trust、closeness 或人格判断 |
| `SOM-INV-010` | 用户确认改变审查结果，不改变陈述的来源性质 |
| `SOM-INV-011` | 未知扩展字段必须语义往返保留，不能静默丢弃 |
| `SOM-INV-012` | 所有自动操作必须能归因到 actor、时间、版本和结果 |
| `SOM-INV-013` | 任何冲突处置都保留支持与反对证据 |
| `SOM-INV-014` | 合成测试数据与真实个人数据严格隔离 |
| `SOM-INV-015` | Canonical evidence 的 present/missing 状态与 Source refs 是否存在一致；receipt/Derived 不得填补该状态 |
| `SOM-INV-016` | Source policy 字段只能由获授权 Intake 声明与版本化 profile 确定性初始化；缺失时使用 provisional 保守默认，不解析正文猜测 |

## 10. 时间语义

- Assertion、Relationship、State MUST 预留 valid time 与 recorded time 的独立表达。
- Source MUST 区分 `source_created_at` 与 `ingested_at`。
- `created_at`/`recorded_at` MUST NOT 被当作现实有效时间。
- 时间缺失或模糊 MUST 显式表达，MUST NOT 填充模型猜测值。
- State 演化 MUST 产生可查询的历史记录。
- 区间开闭、模糊精度、时区和重叠冲突由 Bitemporal & Evidence SPEC 定义。

## 11. 证据语义

- Assertion/Relationship/State 的 `evidence_refs` MUST 直接指向 Source locator；非空时 `evidence_status=present`，空集合时 `evidence_status=missing`。receipt、View 或 Derived assessment 不能让 missing 变 present。
- 同一 Source 的多次摘要、复制或模型重复 MUST NOT 被当作多个独立证据。
- `assertion_kind=inferred|analysis|predicted` MUST 保留推断来源和距离，不因用户查看或重复而增强真值。
- `assertion_kind=fictional` MUST 永远与真实世界 Assertion 隔离。
- 用户确认只能说明用户完成了审查；它是否足以产生 `answer_status=verified` 由 S2/S5 依据视角和证据定义。
- PRD §9.3 的原始证据维度固定为：`proximity`、`integrity`、`corroboration`、`perspective`、`inference_distance`、`review_status`、`freshness`。本 SPEC 只锁定名称与正交边界，字段结构和计算规则由 S2 定义。
- Evidence score MAY 后续计算，但 MUST NOT 替代上述七个原始证据维度，也不得单独决定事实真伪。

## 12. 权限要求

本 SPEC 只定义对象必须携带的权限标签，不定义策略求值：

- Canonical Object MUST 有 `owner_ref`。
- 涉及第三方的记录 MUST 可表达 `subject_ref` 与 `recorder_ref`。
- `sensitivity` 和 `compartments` MUST 位于规范对象或可继承的规范父对象上。
- Derived View MUST 继承其全部依赖对象的限制，不得降低敏感度。
- 无权限调用者 MUST NOT 通过错误信息、摘要或关系推断获得受限字段。
- 具体交集、临时授权、字段裁剪、sealed、删除和外发由 Privacy & Access Policy SPEC 定义。

## 13. 冲突行为

- 同一 subject/predicate/有效时间存在不兼容值时，系统 MUST 保留并列记录，MUST NOT 静默挑选一个。
- 冲突是记录/查询状态，不是 Assertion 内容类型。
- 参与冲突的 Assertion/State MAY 标记 `review_status=in_dispute`。
- 查询层 MUST 产生 `answer_status=disputed`，具体计算由 S2 定义。
- 用户裁决 MAY 新增确认修订，但 MUST NOT 删除反证或冲突历史。
- Entity identity 冲突 MUST 阻止自动合并并生成 proposal。

## 14. 失败与降级

| 失败 | MUST 行为 |
|---|---|
| Source 保存失败 | 返回 rejected receipt，不生成语义候选，不声称已保存 |
| Source 已保存但解析失败 | 保留 Source，记录解析失败，不生成猜测 |
| Source policy 声明缺失 | 仍可按保守 profile 保存；标 `provisional`、第三方状态 unknown，并对非 owner/非 intake purpose fail closed |
| Source policy 声明非法或试图降低 profile floor | 拒绝该声明；不得降级 sensitivity 或扩大访问，Source append 按 S9 返回明确结果 |
| 未知 object_type | 拒绝 Canonical 写入并返回 `unsupported_object_type` |
| 字段类型不匹配 | 拒绝整个 proposal，不做部分写入 |
| dangling reference | 拒绝整个 Canonical 发布 |
| Derived View 被用作 evidence | 拒绝并返回 `derived_evidence_forbidden` |
| assertion_kind 使用 disputed/unknown | 拒绝并提示使用 review/answer status |
| RelationshipState subject 不是 Relationship | 拒绝并返回 `invalid_state_subject` |
| protected path 被 proposal 修改 | 拒绝整个 Micro ChangeSet |
| 模型不可用 | 仍允许 Source Append、浏览、手动 proposal 和导出 |

错误码是语义标识，不规定传输协议格式。

## 15. 撤销与审计

- Canonical Object 的纠正 MUST 通过新修订表达，不静默重写既有审计历史。
- 撤销已发布 ChangeSet MUST 保留原 ChangeSet、发布 revision 和撤销 actor。
- 撤销后当前语义 MAY 与旧 revision 等价，但 MUST 使用新的审计可见 revision；最终规则由 S3 定义。
- Source 原始内容默认尽量不可变；其纠正、封存和删除必须记录受控操作结果。
- 硬删除允许清除正文，审计只能保留不含正文的最小删除证明；具体范围由 Privacy/Storage SPEC 定义。
- Entity merge/split MUST 可审计并保持原 Source identity。

## 16. 兼容与迁移

- 每个对象 MUST 携带 `schema_version`。
- 导入未知核心 `object_type` MUST fail closed；不得猜测映射。
- 已命名的 `extensions` 未被当前版本理解时 MUST 语义保留并原样再导出；字节级与顺序保证由 Storage SPEC 定义。
- 别名映射 MUST 在导入边界规范化，不得在 Canonical Context 同时制造重复核心对象。
- Schema 升级 MUST 通过受控迁移和 ChangeSet，不直接重写 Source 或用户确认历史。
- 模型、Prompt、Embedding 或索引升级 MUST NOT 改变 `assertion_kind`、Source 或确认历史。

## 17. 正例

### 17.1 Source Append 不修改语义

```yaml
source:
  source_id: src_micro_001
  source_kind: synthetic_text
  source_system: synthetic_fixture
  language: zh-CN
  content_ref: fixtures/src_micro_001.txt
  content_hash: hash_placeholder
  policy_profile_ref: owner_intake_private_v1
  owner_ref: person_alpha
  subject_refs: [person_alpha, person_beta]
  recorder_ref: person_alpha
  sensitivity: private
  compartments: [personal]
  third_party_present: true
  retention_policy_ref: user_controlled_v1
  retention_state: active
  policy_resolution_status: declared
append_receipt:
  status: stored
canonical_mutations: []
```

### 17.2 RelationshipState 是 State

```yaml
object_type: state
state_id: state_contact_002
state_kind: relationship.contact
subject_ref:
  object_type: relationship
  object_id: rel_alpha_beta
value: no_contact
review_status: confirmed
evidence_status: present
evidence_refs:
  - source_id: src_micro_001
    locator: {scheme: text_utf8_byte_range_v1, start_byte: 0, end_byte_exclusive: 58}
```

### 17.3 观点仍是观点

```yaml
object_type: assertion
assertion_kind: opinion
perspective_ref: person_alpha
predicate: relationship.trust_assessment
value: uncertain
review_status: confirmed
evidence_refs: []
evidence_status: missing
```

确认后 `assertion_kind` 仍为 `opinion`；查询是否 verified 由后续证据合同决定。

### 17.4 联系状态变更保护无关语义

```yaml
proposals:
  - proposal_id: end_contact_active
    operation: end
    target_ref: state_contact_001.valid_time.end
    before_digest: digest_of_unbounded_end
    after_value: transition_at
    valid_time: {kind: interval, end: transition_at, bounds: "[)"}
    evidence_refs:
      - source_id: src_micro_001
        locator: {scheme: text_utf8_byte_range_v1, start_byte: 0, end_byte_exclusive: 58}
        stance: supports
        claim_ref: end_contact_active
    protected_paths: &contact_protected_paths
      - relationship.origin
      - state[relationship.role].value
      - assertion[relationship.trust].value
      - assertion[relationship.closeness].value
      - hypothesis[relationship.personality]
  - proposal_id: add_contact_no_contact
    operation: add
    target_ref: state_contact_002
    before_digest: absent
    after_value: {state_kind: relationship.contact, value: no_contact, evidence_status: present}
    valid_time: {kind: interval, start: transition_at, end: unbounded, bounds: "[)"}
    evidence_refs:
      - source_id: src_micro_001
        locator: {scheme: text_utf8_byte_range_v1, start_byte: 0, end_byte_exclusive: 58}
        stance: supports
        claim_ref: add_contact_no_contact
    protected_paths: *contact_protected_paths
```

## 18. 反例

### 18.1 把冲突当内容类型

```yaml
assertion_kind: disputed
```

无效。应使用合法 `assertion_kind`，并把冲突放入 `review_status`/`answer_status`。

### 18.2 View 反向作证

```yaml
evidence_refs:
  - projection_id: person_card_001
```

无效。人物卡是 Projection，不是 Source。

### 18.3 覆盖历史状态

```yaml
update state_contact_001:
  value: no_contact
```

无效。必须结束旧有效区间并新增 State。

### 18.4 从断联推断人格

```yaml
input: no_contact
implicit_mutation:
  hypothesis: avoids_conflict
```

无效。该输入不授权人格或因果推断。

### 18.5 Source Append 绕过 ChangeSet 修改 Canonical

```yaml
append_source:
  side_effect:
    relationship.contact: no_contact
```

无效。Source Append 与 Canonical semantic mutation 必须分离。

## 19. 可执行验收测试

### 19.1 测试状态

```yaml
suite_id: semantic_object_model_v0_4
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

本文只定义合同测试目录。尚无 fixture manifest、测试运行器或实现模块，因此 `suite_materialized=false`，所有 Verification Result 均为 `not_executed`。

### 19.2 测试清单

| Test ID | Given | When | Then |
|---|---|---|---|
| `SOM-AT-001` | 12 个合法 object_type | 校验对象词表 | 全部接受；第 13 个未知类型被拒绝 |
| `SOM-AT-002` | RelationshipState fixture | 规范化对象 | 输出 `object_type=state`、`state_kind=relationship.contact` |
| `SOM-AT-003` | `Obligation/viewpoint/Calibration/Snapshot` | 规范化别名 | 分别映射 Commitment/opinion Assertion/Outcome/Projection |
| `SOM-AT-004` | 合成 Source | 执行 Source Append | 返回 stored receipt；Canonical revision 不变 |
| `SOM-AT-005` | 已存 Source 和未确认 proposal | 查询 Canonical | 不出现 proposal 的 no_contact 值 |
| `SOM-AT-006` | 绕过 ChangeSet 的 Canonical 写请求 | 执行写入 | 返回 `changeset_required`，无对象变化 |
| `SOM-AT-007` | `assertion_kind=disputed` 或 unknown | 校验 Assertion | 返回 invalid assertion kind |
| `SOM-AT-008` | confirmed opinion Assertion | 用户确认 | review_status 改变，assertion_kind 仍为 opinion |
| `SOM-AT-009` | Projection 作为 evidence_ref | 校验写入 | 返回 `derived_evidence_forbidden` |
| `SOM-AT-010` | Hypothesis 被模型重复 100 次 | 聚合候选 | 仍为 Hypothesis，不新增 Fact/observed Assertion |
| `SOM-AT-011` | State subject_ref 不存在 | 发布 proposal | 整个发布失败，无部分对象 |
| `SOM-AT-012` | RelationshipState 指向 Entity | 校验对象 | 返回 `invalid_state_subject` |
| `SOM-AT-013` | active contact + confirmed no_contact proposal | 生成变更集 | 只触达 contact State；protected_paths 完整 |
| `SOM-AT-014` | 发布联系状态变化 | 比较前后 Canonical | origin/role/trust/closeness/personality 语义相等 |
| `SOM-AT-015` | 当前 no_contact 与历史 active | 查询对象集合 | 两条 State 都存在，旧记录未覆盖 |
| `SOM-AT-016` | 未知 namespaced extensions | 导出再导入 | 扩展字段语义保持，不静默丢失 |
| `SOM-AT-017` | 两个同名 person Entity | 模型请求合并 | 只产生 merge proposal，不直接合并 |
| `SOM-AT-018` | fictional Assertion | 用户确认 | 仍为 fictional，不进入现实事实回答 |
| `SOM-AT-019` | narrative_context 引用原话 | 校验对象 | 存在 Source locator；Canonical note 有 actor/time |
| `SOM-AT-020` | Source 保存后解析失败 | 处理失败 | Source 保留，解析失败可见，不生成猜测 |
| `SOM-AT-021` | 同 subject/predicate/time 的两个不兼容 Assertion | 校验冲突集合 | 两者并列保留并进入 in_dispute，不自动选胜者 |
| `SOM-AT-022` | 缺少 actor、time、revision 或 result 的自动操作记录 | 校验审计 Envelope | 拒绝记录并返回 audit metadata missing |
| `SOM-AT-023` | 全部 SOM 与 Micro fixtures | 执行隐私静态扫描 | 仅含合成 ID/内容，不出现真实个人数据 |
| `SOM-AT-024` | 2030 年补录一条 `valid_to=2029-04` 的合成 State（PRD §26 Case B 占位） | 分别读取现实有效时间与系统记录时间 | `valid_time != recorded_at`；可分别回答“何时成立”和“何时记录”；完整区间规则由 S2 验收 |
| `SOM-AT-025` | evidence_refs 为空但 status=present，或 refs 非空但 status=missing | 校验 Canonical 对象 | 拒绝不一致；receipt/Derived ref 也不能把 evidence_status 设为 present |
| `SOM-AT-026` | 获授权 Intake 显式声明 recorder、subjects、third-party 和 compartments，并引用固定 policy profile | 初始化 Source | 每个 expected policy 字段由 request/profile 唯一产生；不读取正文推断 |
| `SOM-AT-027` | Intake 缺少 subject/compartment 声明且 hint 低于 profile floor | 初始化 Source | Source 为 private/personal/provisional，subjects 为空、third-party=unknown；非 owner/非 intake purpose fail closed，hint 不降低保护 |

### 19.3 与 Micro-MVP 的对应

| SOM Test | Micro Test |
|---|---|
| `SOM-AT-004` | `MM-001` |
| `SOM-AT-005`、`SOM-AT-013` | `MM-002`、`MM-003` |
| `SOM-AT-006` | `MM-004` 的唯一写路径前置条件 |
| `SOM-AT-014` | `MM-007` |
| `SOM-AT-015` | `MM-006` |

### 19.4 不变量覆盖

| Invariant | Acceptance Test |
|---|---|
| `SOM-INV-001` | `SOM-AT-001`、`SOM-AT-002`、`SOM-AT-003` |
| `SOM-INV-002` | `SOM-AT-004`、`SOM-AT-009` |
| `SOM-INV-003` | `SOM-AT-009` |
| `SOM-INV-004` | `SOM-AT-007`、`SOM-AT-008`、`SOM-AT-018` |
| `SOM-INV-005` | `SOM-AT-010` |
| `SOM-INV-006` | `SOM-AT-015`、`SOM-AT-024` |
| `SOM-INV-007` | `SOM-AT-004`、`SOM-AT-006` |
| `SOM-INV-008` | `SOM-AT-011`、`SOM-AT-012` |
| `SOM-INV-009` | `SOM-AT-013`、`SOM-AT-014` |
| `SOM-INV-010` | `SOM-AT-008`、`SOM-AT-018` |
| `SOM-INV-011` | `SOM-AT-016` |
| `SOM-INV-012` | `SOM-AT-022` |
| `SOM-INV-013` | `SOM-AT-021` |
| `SOM-INV-014` | `SOM-AT-023` |
| `SOM-INV-015` | `SOM-AT-009`、`SOM-AT-025` |
| `SOM-INV-016` | `SOM-AT-026`、`SOM-AT-027` |
## 20. 未决问题

以下问题不阻止本 SPEC 评审，但必须由对应后续 SPEC 处理：

| 问题 | 后续归属 |
|---|---|
| `confirmed` 何时映射为 `answer_status=verified` | Bitemporal & Evidence、Shiling Policy（`IQ-003`） |
| 有效区间端点和模糊时间 | Bitemporal & Evidence（`IQ-009`、`IQ-010`） |
| `narrative_context` excerpt 的物理复制与导出 | Storage, Index & Portability（`IQ-006`） |
| global revision 与 object revision 的组合 | ChangeSet & Consistency（`IQ-018`） |
| Entity merge/split 的并发和撤销细节 | ChangeSet & Consistency、Shiling Policy |
| 多舱室策略合并和 Derived View 权限继承 | Privacy & Access Policy（`IQ-013`） |
| Source 纠正、封存、删除的完整操作合同 | ChangeSet、Privacy、Storage |

这些问题不得由实现自行裁决。

## 21. 完成定义

本 SPEC 只有满足以下条件才可从 `Draft for Review` 变为 `Approved`：

- `BQ-001` 至 `BQ-005` 已记录为 decided。
- 12 对象清单与别名映射无遗漏。
- Micro 六对象的字段、边界、状态转换和失败行为可测试。
- 每条 `SOM-INV-*` 至少由一个正例、反例或 `SOM-AT-*` 覆盖。
- FR-003、FR-004、FR-008、FR-011、FR-104、FR-201、FR-202、FR-204 的 S1 责任已进入需求追踪。
- 所有示例和 fixture 均为合成数据。
- 未选择数据库、技术栈或模型供应商。
- 文档结构、内部引用和枚举通过静态校验。
- 产品负责人逐份审查并明确批准本 SPEC。
- 测试状态仍如实区分 defined、executed、passed；未执行不得称为通过。

当前结论：本 SPEC v0.4 于 2026-07-14 完成 Micro Gate 纠偏并保持 `Approved`。本次修订闭合 Source policy 初始化和只读 protected sentinel 边界；不表示测试已物化、执行或通过，也不授权扩大 Micro-MVP 或实现 Hypothesis 工作流。
