# Bitemporal & Evidence SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-BTE-001` |
| 版本 | `0.4` |
| 状态 | `Approved` |
| 产品基线 | `PRDv05.md`，PRD v0.5 |
| 上游基线 | `SPEC-SOM-001` v0.5，`Approved` |
| 当前阶段 | Phase 2：Bitemporal & Evidence |
| 下一依赖 | ChangeSet & Consistency SPEC |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 产品裁决 | `IQ-003`、`IQ-004`、`IQ-007`、`IQ-009`、`IQ-010` 均于 2026-07-13 决定，见 `OPEN_QUESTIONS.md` |
| v0.5 兼容复审 | 2026-07-15；固定 `value=unknown` 在 DQ-012 未重开前的保守查询行为 |

本文定义语义合同，不选择数据库时间类型、查询引擎、证据评分模型、编程语言、序列化框架或模型供应商。

规范词：`MUST` 表示强制；`MUST NOT` 表示禁止；`SHOULD` 表示默认要求，偏离必须有理由；`MAY` 表示可选且不得成为其他强制项的隐式前提。

本文为已批准版本。§10.1（IQ-010）、§11.1（IQ-004）、§6.9（IQ-003/IQ-007）的推荐合同已由产品负责人确认并采纳；未决问题见 §20（已减至实现参数，不阻止 S3 起草）。

## 1. 目标

本 SPEC 的目标是：

1. 让系统分别回答“现实中何时成立”和“识海在何时知道”，不得混用有效时间与记录时间。
2. 让 Current State 与 Historical State 同时可查询，事后补录和纠正不得覆盖历史。
3. 定义精确、模糊、未知、开放边界和时区缺失的可移植表达。
4. 定义 CoverageWindow，使“没有记录”“没有覆盖”和“无法判断”严格分离。
5. 锁定 PRD §9.3 的七个证据维度，不用单一分数替代原始证据。
6. 定义事实型回答六态及其与内容类型、审查状态、冲突和 View freshness 的边界。
7. 为 Micro-MVP 的 RelationshipState 历史查询提供确定的时间与证据 oracle。

依据：PRD §6、§9、§12、§13、§18.5、§19、§20 FR-002/003/008/009/010、§22、§24、§26 Cases A/B/E/F/G；`SPEC-SOM-001` §3、§6、§9-§13。

## 2. 非目标

本 SPEC 不负责：

- 选择数据库、索引、物理时间类型、事件溯源框架或查询语言。
- 定义 ChangeSet 的事务、revision 编号、并发、传播、撤销执行和重试机制。
- 定义证据权重、统一 `evidence_score`、模型阈值或领域真值算法。
- 自动解析自然语言时间、判断季节所属月份或替用户消除时间歧义。
- 定义舱室策略求值、字段裁剪、sealed、删除时限或对外分享。
- 定义识灵的自动确认权限、Review Budget、候选排序或 Prompt。
- 实现财务、健康、决策、连接器、多设备同步或历史数据迁移。

## 3. 术语

| 术语 | 规范定义 |
|---|---|
| Valid Time | 某 Assertion、Relationship 或 State 在所描述现实中成立的时间或区间 |
| Recorded Time | 当前识海修订首次规范记录该语义的系统时间；不是现实发生时间 |
| Source Time | Source 自身声称产生的时间，即 `source_created_at`；可能缺失、不可信或与系统时钟不一致 |
| Ingested Time | Source 进入当前 Source Vault 的系统时间，即 `ingested_at` |
| Bitemporal Query | 同时指定现实时间条件与知识快照条件的查询 |
| Knowledge Snapshot | 按 `recorded_as_of` 截止时刻重建当时系统可知语义的查询视角；不是第 13 个核心对象 |
| Temporal Boundary | 有类型的时间端点，明确区分 known、unknown 与 unbounded |
| Temporal Precision | 时间表达的粒度：instant、day、month、season、year 或 range |
| Temporal Certainty | 时间值是 exact、approximate 还是 inferred；用户确认粗粒度表达不会把它变成 exact |
| CoverageWindow | 某 Source system 在某领域/对象范围内的覆盖声明、连续性、缺口和导出完整性记录 |
| Evidence Ref | 直接指向 Source locator 的证据引用，继承 S1 定义 |
| Evidence Dimensions | `proximity`、`integrity`、`corroboration`、`perspective`、`inference_distance`、`review_status`、`freshness` 七个正交维度 |
| Evidence Family | 共享同一上游材料或复制/转换谱系的一组 Evidence Ref；用于防止重复计证，不是核心对象 |
| Evidence Assessment | 对原始证据维度的结构化记录或按查询时刻计算的派生评估；不是新的 Canonical Object |
| Answer Status | 事实型回答的六态：verified、unconfirmed、disputed、not_covered、stale、unknown |
| Current Query | 查询目标指向请求时刻或开放有效区间当前端 |
| Historical Query | 查询目标明确指向过去的 valid time；旧证据不因年龄本身自动 stale |

## 4. 适用范围

### 4.1 对象范围

本 SPEC 对以下 S1 对象增加时间与证据合同：

| 对象 | 本 SPEC 责任 |
|---|---|
| Source | `source_created_at`、`ingested_at`、时区、语言、完整性和 CoverageWindow 关联 |
| Assertion | valid time、recorded time、Evidence Ref、七维证据与回答解释 |
| Relationship | 稳定关系 identity 的有效时间；不得代替 RelationshipState |
| State | 有效区间、记录时间、历史查询、冲突与 current 计算 |
| Hypothesis | 只定义 evidence_for/evidence_against 的时间和证据边界，不定义完整生命周期 |
| ChangeSet | 只要求 proposal/published 结果携带时间与证据语义；事务合同后置 S3 |

CoverageWindow、Evidence Family、Evidence Assessment 和 Knowledge Snapshot 都是嵌入记录、查询合同或派生结构，不增加核心对象数量。

### 4.2 Micro-MVP 切片

Micro-MVP 只验证：

```text
synthetic Source clocks
  -> proposed RelationshipState valid_from
  -> user-confirmed temporal expression
  -> new recorded_at at publication
  -> current and historical valid-time queries
  -> Source evidence trace
```

Case B、E、F 用于 S2 合同验收，不扩展 Micro 实现范围到工作、项目或连接器领域；其 fixture 只使用通用合成 State/Assertion。

## 5. 对象与边界

### 5.1 四类时间不可替换

| 时间 | 所回答问题 | 写入者 | 可否由其他时间推断 |
|---|---|---|---|
| `valid_time` | 现实中何时成立 | 用户确认的 ChangeSet 或明确外部验证规则 | MUST NOT 从 recorded/source/ingested 静默复制 |
| `recorded_at` | 当前识海何时规范记录 | 系统发布时钟 | MUST NOT 由用户回填或伪装成 valid time |
| `source_created_at` | 来源声称何时产生 | Source 元数据/导入器 | 缺失或异常必须显式 |
| `ingested_at` | 来源何时进入当前系统 | Source Append 系统时钟 | MUST NOT 被 source time 覆盖 |

四类时间 MAY 相同，但相同必须来自真实输入或系统事件，不能为简化 Schema 而强制相同。

### 5.2 规范记录与查询时计算

- Canonical 记录 MUST 保存原始时间表达、确认后的结构化 `valid_time`、`recorded_at` 和 Evidence Ref。
- `freshness`、corroboration 汇总、Answer Status 和 `evidence_score` 是相对于查询时刻、权限和 policy 的评估，MUST 携带评估时刻与依赖 revision。
- Derived assessment MUST NOT 回写成为新的事实证据。
- 同一 Canonical 记录在不同 `recorded_as_of` 或权限下 MAY 产生不同 Answer Status，但历史规范记录不得被改写。

### 5.3 状态演化、纠正与冲突

- 非重叠的 State 值变化是时间演化，不是冲突。
- 同一 subject、互斥 state/predicate、重叠 valid time、值不兼容时形成冲突候选。
- 纠正表示“旧记录在当时就不准确”，时间演化表示“值后来发生变化”；两者 MUST NOT 仅按最新 `recorded_at` 猜测。
- 纠正使用 `supersedes` 和新 recorded revision；演化关闭旧有效区间并新增 State。具体 ChangeSet 操作由 S3 定义。

## 6. 字段语义

### 6.1 TemporalBoundary

```yaml
boundary_kind: known | unknown | unbounded
value: ISO-8601-compatible value | null
precision: instant | day | month | season | year | range | unknown
certainty: exact | approximate | inferred | unknown
timezone: IANA zone | numeric offset | unknown | not_applicable
lexical_locator: optional Source locator pointing to original text
earliest: optional normalized lower candidate
latest_exclusive: optional normalized upper candidate (per IQ-010 决定：[start,end) 半开区间)
resolution_status: unresolved | proposed | confirmed | rejected | superseded
```

约束：

- `boundary_kind=known` 时 `value` 或一组 `earliest/latest_exclusive` MUST 存在。
- `boundary_kind=unknown` 表示边界应该存在但当前不知道；MUST NOT 等同于无限延伸。
- `boundary_kind=unbounded` 表示语义上没有该侧边界，例如当前仍有效；MUST NOT 用于掩盖缺失数据。
- `precision` 描述原信息粒度，不得因格式化而虚假提高。
- `lexical_locator` SHOULD 保留指向原文的 Source locator；是否内联原话由 S7 决定；MUST NOT 把内联正文副本当作独立 Evidence Ref。
- `certainty=inferred` MUST 带推断 provenance，不能因用户查看而改成 exact。

### 6.2 ValidTime

```yaml
valid_time:
  kind: instant | interval | unknown
  start: TemporalBoundary | null
  end: TemporalBoundary | null
  bounds: "[)"
```

IQ-010 已决定：State 区间统一采用半开区间 `[start,end)`；`end` 时刻属于下一状态而不属于旧状态。瞬时事件使用 `kind=instant`，不得用 start=end 的空区间伪装。

当月、季、年等粗粒度边界只能形成一个可能范围。例如“2029 年 4 月离开”表示离开边界落在该月范围内，而不是自动选择 4 月 1 日或 4 月 30 日。处于不确定带内的点查询 MUST 返回时间不确定结果，不得伪造精确值。

### 6.3 RecordedTime 与查询切面

| 字段 | 必需 | 语义 |
|---|---|---|
| `recorded_at` | MUST | 当前规范修订写入的系统时间；不可由调用者回填 |
| `object_revision` | MUST | 直接沿用 SOM §6.1 字段；引用对象最近一次语义变化对应的全局 `data_revision`；与 `base_revision`/`published_revision` 的关系由 S3 定义 |
| `recorded_by` | MUST | actor reference |
| `recorded_as_of` | 查询时 MAY | 只读取不晚于该时刻已记录且当时未被后续知识覆盖的知识切面 |
| `evaluated_at` | 回答 MUST | Answer Status 与 freshness 的计算时刻 |

同一对象被纠正时，新修订 MUST 有新的 `recorded_at`；旧修订继续可供审计和 `recorded_as_of` 查询。BTE 不新增 `recorded_revision` 字段，避免与 S1 的公共 Envelope 产生别名。

### 6.4 Source 时间字段

| 字段 | 必需 | 语义 |
|---|---|---|
| `source_created_at` | SHOULD | Source 自身产生时间；缺失为显式 unknown |
| `source_timezone` | SHOULD | IANA zone、offset 或 unknown |
| `ingested_at` | MUST | 当前 Source Vault 接收完成时间 |
| `time_metadata_status` | MUST | `trusted`、`unverified`、`conflicting`、`unknown` |

`source_created_at > ingested_at`、时区缺失或来源时钟漂移 MUST 触发可见异常，不得静默改写时间或据此拒绝保留 Source。

### 6.5 CoverageWindow

```yaml
coverage_window_id: stable identifier
source_system: source system reference
scope_ref: domain, account, entity set, or declared scope
coverage_start: TemporalBoundary
coverage_end: TemporalBoundary
continuity: continuous | gapped | unknown
gaps: [valid-time intervals]
export_completeness: complete | partial | unknown
timezone: IANA zone | offset | unknown
language: BCP-47-like tag | unknown
declared_at: recorded timestamp
evidence_refs: [Source locator]
declaration_receipt_ref: Source Append/export receipt | null
```

- CoverageWindow 是”系统对可见材料范围的声明”，不是事件不存在的证据。
- `declaration_receipt_ref` 只证明声明/导入动作及其完整性结果，不能进入 Assertion/State 的 `evidence_refs`，也不能单独证明任何个人事实。
- CoverageWindow 附属于其宿主 Source 对象，不是独立核心对象，也不直接接受独立 ChangeSet proposal。原始覆盖声明可随 Source Append receipt 保存；只有参与 Canonical 查询/`not_covered` 判定的规范化 CoverageWindow 及其纠正，才通过引用宿主 Source 的 ChangeSet 发布。`coverage_window_id` 是稳定引用标识，其持久化机制由 S7 定义。
- 多个窗口 MAY 重叠；查询必须保留各自来源和完整性，不能未经规则合并成”完整覆盖”。
- `continuity=unknown` 或 `export_completeness!=complete` 时，缺少搜索结果 MUST NOT 支持否定事实。
- 查询跨越 gap 或窗口外区间时 MUST 返回缺口范围。

### 6.6 CanonicalEvidenceRef 与 EvidenceAssessment

```yaml
evidence_ref:
  source_id: stable Source ID
  locator: stable source locator
  stance: supports | contradicts | contextual
  claim_ref: Canonical claim or proposal reference
```

`stance` 只表示该证据如何被当前 claim 使用，不等于证据真实、独立或足以 Verify。

Canonical `evidence_ref` MUST 只保存稳定 Source locator、stance 和 claim 绑定。查询时会随权限、policy、时间或谱系规则改变的 `evidence_family_id` 与 `dimensions` MUST NOT 嵌入 Canonical Evidence Ref。

```yaml
evidence_assessment:
  assessment_id: stable derived result ID
  evidence_refs: [CanonicalEvidenceRef]
  evidence_family_refs: [derived provenance family reference]
  dimensions: EvidenceDimensions
  assessment_policy_ref: versioned policy
  evaluated_at: timestamp
  data_revision: canonical revision used
```

EvidenceAssessment 是可删除、可重算的 Derived 结果，不是第 13 个核心对象，也没有独立事实写入口。Evidence Family ID 由 Source provenance 关系和版本化规则推导；持久化与查询索引机制后置 S7/ADR。该拆分防止一次旧 assessment 随 Canonical 记录永久化，并阻止其反向成为事实证据。

### 6.7 EvidenceDimensions

| 维度 | 最小字段语义 | 禁止简化 |
|---|---|---|
| `proximity` | `direct_observation`、`first_person_report`、`third_party_report`、`deterministic_system_record`、`inference`、`unknown` | 不得把“用户相关”一律当直接观察 |
| `integrity` | `source_form`、`hash_status`、`metadata_status`、转换谱系 | 不得把截图、摘要与原件视为相同完整性 |
| `corroboration` | evidence family 集合、独立性状态和可见独立 family 数 | 不得按 Evidence Ref 数量直接计数 |
| `perspective` | `perspective_ref` 与 `perspective_kind` | 不得抹去陈述主体或把观点变客观事实 |
| `inference_distance` | `steps=0..n|unknown` 与推断链引用 | 不得用模型重复次数缩短距离 |
| `review_status` | 继承 S1 四态及其 actor/time | confirmed 不自动改 assertion_kind |
| `freshness` | `evidence_effective_at`、`evaluated_at`、`policy_ref`、`freshness_status` | 不得只保存动态分数而丢原始时间 |

完整性和 proximity 是不同维度：原件可以是第三方陈述，截图也可以记录第一人称陈述；系统不得把它们压成单一等级。

### 6.8 AnswerEnvelope

事实型回答 MUST 至少返回：

```yaml
answer_status: verified | unconfirmed | disputed | not_covered | stale | unknown
answer_value: value | null | withheld
valid_time: requested and resolved valid-time scope
recorded_as_of: requested knowledge snapshot | current
evaluated_at: timestamp
evidence_refs: authorized direct Source refs or empty
coverage: relevant windows and gaps
reason_codes: stable semantic reasons
data_revision: canonical revision
assessment_policy_ref: verification/freshness policy identifier
```

无权限是访问结果，不是第七种 Answer Status。权限拒绝的返回和最小披露由 S4 定义；系统不得借 `reason_codes` 泄露隐藏证据。

### 6.9 六态判定边界

| answer_status | 必要语义 |
|---|---|
| `verified` | 命中明确 verification rule，且适用证据中无未解决冲突；必须声明验证的 claim scope |
| `unconfirmed` | 有可见 candidate/proposal 或未完成审查的 Assertion/State，但尚未满足验证规则 |
| `disputed` | 同一可比较 claim 在重叠 valid time 有不兼容证据/记录，系统不能安全选一方 |
| `not_covered` | 查询时间或领域没有足够 CoverageWindow 支持该问题，尤其不能支持“事件未发生”的否定结论 |
| `stale` | 对当前性有要求，但唯一可用证据已不满足声明的 freshness policy |
| `unknown` | 覆盖足够且没有待审 candidate/明确冲突，但仍不能安全判断 |

正向事实可被直接证据证明时，覆盖缺口不抹去该证据；但回答 MUST 披露缺口。否定事实需要覆盖能够支持“未发生”的推理，否则优先 `not_covered`。

IQ-003 已决定：用户确认必须声明 `verification_scope`，其封闭枚举为 `record_accuracy | statement_occurrence | viewpoint | world_claim`；实现 MUST 拒绝枚举外的 scope 值。确认观点只可 Verify “该主体持有此观点”，确认 reported Assertion 只可 Verify “该陈述被记录/报告”，不得自动 Verify 其 world claim。个人语义 world claim 只有用户明确确认该 claim，或命中已批准的强直接证据规则，才能 `verified`；外部 Agent 无权设置该结果。

IQ-007 已决定：`answer_status=stale` 与 Derived View 的 `freshness_status` 是两个轴。fresh View 仍可能只包含 stale evidence；stale View 不能把旧答案标成当前 verified。View freshness 的传播合同由 S3 定义。

```yaml
canonical_unknown_answer_status_values: [unknown]
```

`DQ-012` 仍为 deferred。它重开并形成新 Product Decision 前，Canonical `State.value=unknown` 只表示“规范状态值被记录为未知”，不得被解释为已验证的具体 world value。查询实际状态时 MUST 返回 `answer_status=unknown`、`answer_value=null`；获授权响应 MAY 给出非泄露 `canonical_value_unknown` reason。系统 MUST NOT 返回 `verified + value=unknown`，也不得把该记录当作 `not_covered`、`unconfirmed` 或支持任一具体值的反证。该保守规则不裁决未来 UI 是否允许表达“已验证地不知道”。

## 7. 状态机

### 7.1 时间解释状态

```text
unresolved -> proposed
proposed -> confirmed | rejected | superseded
confirmed -> superseded
rejected -> proposed (必须是新的解释候选)
```

- `proposed` 只能存在于 proposal/ChangeSet 审查上下文，不能冒充 Canonical confirmed time。
- `confirmed` MAY 保持 `precision=month|season|year` 或 `certainty=approximate`；确认不等于精确化。
- `superseded` 保留旧解释和 actor/time，不物理覆盖。

### 7.2 Review Status

沿用 S1：

```text
unreviewed -> confirmed | denied | in_dispute
confirmed -> in_dispute | denied
in_dispute -> confirmed | denied
```

Review Status 的变化不自动改变 valid time、assertion_kind、Evidence Ref 或 Answer Status。

### 7.3 Answer Status 不是持久生命周期

Answer Status MUST 按 query valid time、recorded_as_of、授权证据、CoverageWindow、freshness policy 和当前 revision 重新计算。系统 MUST NOT 把一次 `verified` 结果持久化后永久沿用。

同一 claim MAY 因新证据从 verified 变成 disputed，或因 current freshness 要求从 verified 变成 stale；这是派生评估变化，不是对历史记录的静默改写。

## 8. 允许与禁止的状态转换

### 8.1 允许

- 用户确认“去年秋天”对应的粗粒度季节范围，同时保留原词与 approximate/season 精度。
- 事后补录创建 valid time 在过去、recorded_at 在当前的新修订。
- 新 State 关闭旧 State 的开放有效区间并保留旧记录。
- 新证据使 confirmed 记录进入 in_dispute，并使当前查询返回 disputed。
- 纠正通过新修订 supersede 旧时间解释，历史 `recorded_as_of` 仍能看到旧知识切面。

### 8.2 禁止

- 用 `recorded_at`、`source_created_at` 或 `ingested_at` 自动填充缺失 `valid_time`。
- 把 unknown 边界序列化为 unbounded，或把 unbounded 当成 unknown。
- 把 month/season/year 格式化成一个精确瞬间而丢失粒度。
- 因新记录的 `recorded_at` 更晚而自动覆盖有效时间重叠的旧记录。
- 把无搜索结果当成事件未发生，尤其在 CoverageWindow 外或 gap 内。
- 把同一 Source 的摘要、截图、转发、OCR 和模型重复当成独立 corroboration。
- 用 `evidence_score` 单独设置 verified。
- 用 Derived View、旧 AnswerEnvelope 或模型摘要作为直接 Evidence Ref。
- 因用户确认而把 opinion/reported/inferred 改写为 observed。
- 因历史证据年代久远而把历史查询自动标 stale。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `BTE-INV-001` | valid、recorded、source-created、ingested 四类时间语义不可互换 |
| `BTE-INV-002` | Current State 不覆盖 Historical State；事后补录不伪装成当时已知 |
| `BTE-INV-003` | known、unknown、unbounded 与粗粒度时间严格区分 |
| `BTE-INV-004` | 所有事实型回答恰有一个六态主状态，并保留 reason/coverage/evidence |
| `BTE-INV-005` | not_covered、unknown、unconfirmed、disputed、stale、verified 不得互相代替 |
| `BTE-INV-006` | 七个原始证据维度正交保留，单一分数不能替代或决定真值 |
| `BTE-INV-007` | 共享上游谱系的 Evidence Ref 最多计为一个独立 evidence family |
| `BTE-INV-008` | 用户确认的 verification scope 不得被扩大到未确认的 world claim |
| `BTE-INV-009` | Perspective 差异本身不是客观事实冲突；同 perspective/claim 的不兼容值才进入冲突判断 |
| `BTE-INV-010` | Evidence 必须回到 Source locator，Derived View 不反向作证 |
| `BTE-INV-011` | Answer freshness 与 View freshness 分轴表达，任何旧值不得冒充当前 verified |
| `BTE-INV-012` | 时间解析和证据评估失败必须降级为诚实状态，不得猜测 |
| `BTE-INV-013` | 纠正、裁决与撤销保留 recorded-time 审计历史和反证 |
| `BTE-INV-014` | 仅使用调用者有权访问的证据计算回答，且不得通过状态或错误泄露隐藏内容 |
| `BTE-INV-015` | 所有 fixture 和示例只使用合成数据 |
| `BTE-INV-016` | DQ-012 未重开前，Canonical `value=unknown` 的实际状态查询只能保守返回 Answer `unknown`，不得伪装为 verified 具体值或其他认知状态 |

## 10. 时间语义

### 10.1 半开区间候选规则

IQ-010 已决定：State 区间采用 `[valid_from, valid_to)`。在 `transition_at` 前一瞬旧 State 有效，从 `transition_at` 起新 State 有效。同一 subject/state_kind 的相邻区间可首尾相接，不视为重叠冲突。

开放当前状态使用 `end.boundary_kind=unbounded`。未知结束时间使用 `end.boundary_kind=unknown`，此时系统不得断言状态当前仍有效。

### 10.2 粗粒度和模糊时间

IQ-009 已决定：自然语言时间先保留 Source locator 和 `lexical_locator`，解析器只能产生 `resolution_status=proposed` 的候选范围。用户可以确认粗粒度范围，也可以保持 unknown；系统不得要求用户虚构精确日期。

查询落在模糊边界的不确定带内时：

- 有明确 candidate 但未确认，返回 `unconfirmed`。
- 已确认其粗粒度表达但该时间点仍无法判定，返回 `unknown` 并显示可能范围。
- 不得选择范围中点、第一天或最后一天作为隐藏默认值。

### 10.3 Bitemporal Query

查询 MUST 分别接受：

```yaml
valid_at: valid-time point or interval
recorded_as_of: recorded-time cutoff | current
```

- 只给 `valid_at` 时，使用当前知识切面回答该现实时间。
- 只给 `recorded_as_of` 时，查询当时已知的 current/指定默认 valid scope，并显式返回解析后的 valid scope。
- 两者都给时，返回“截至 recorded_as_of，系统如何理解 valid_at”。
- 两者都缺失时，才是 current valid time + current knowledge，响应仍必须写明两个解析值。

### 10.4 事后补录

事后补录 MUST 满足：

- `valid_time` 保留现实时间，`recorded_at` 使用当前发布时刻。
- 不能向过去伪造 recorded history。
- 当前视图 MAY 因该新知识改变，但历史 `recorded_as_of` 查询仍显示系统当时不知道该记录。
- 旧 valid-time 查询根据新知识可得到更准确结果；响应必须说明当前知识 revision。

### 10.5 时区与语言

- 精确瞬间比较前必须有可解释时区或 offset。
- 仅有 local time 且时区 unknown 时，记录原值并返回比较不确定，不得假定设备当前时区。
- Source language 与时间词原文必须保留；翻译不得覆盖原始时间表达。
- 夏令时歧义、非法本地时间和来源时钟异常必须可见；具体库与算法后置 ADR。

## 11. 证据语义

### 11.1 证据谱系与独立性

IQ-004 已决定：Evidence independence 按上游 provenance 判定，而不是文件数或 URL 数。以下情况 MUST 归入同一 evidence family：

- 同一 Source 的 excerpt、OCR、摘要、Embedding 或模型提取。
- 同一原材料的截图、转发、复制和格式转换，能够识别共同上游时。
- 多个模型对同一 locator 的重复判断。

来源依赖关系 unknown 时，corroboration independence MUST 标为 unknown，不得默认 independent。真正独立来源需要不同上游产生链，且无已知互相复制关系；领域阈值不在本 SPEC 定义。

Evidence Family 没有独立写入口；`evidence_family_id` 由系统从 Source provenance 关系推算，不作为独立核心对象持久化；具体 ID 推算和索引机制后置 S7/ADR。

### 11.2 Review 与 Verify

- `review_status=confirmed` 说明用户确认了指定 scope 的记录，不自动说明所有 world claim 成立。
- `review_status=denied` 保留原 Source 与否认 actor/time，不能删除 Source 以制造一致。
- `review_status=in_dispute` 必须保留支持与反对 Evidence Ref。
- 强直接证据规则必须命名、版本化、限定 claim/predicate/source kind，并由后续 Shiling Policy 批准；不存在通用“高分即 verified”。
- 外部 Agent、模型或重复推断 MUST NOT 直接设置个人语义事实为 verified。

### 11.3 Freshness

- Freshness 是“证据是否足以代表查询要求的时间”，不是记录质量总分。
- Historical Query 以目标 valid time 评估相关性，不能仅按 `evaluated_at - source_created_at` 判 stale。
- Current Query 必须引用明确 freshness policy；没有适用 policy 时不得猜测 fresh，可返回 unknown 或领域不适用原因。
- policy 变化只重新计算 assessment，不改写 Source、valid time 或 review history。

### 11.4 Evidence Score

`evidence_score` MAY 作为 Derived assessment，但必须：

- 携带算法/policy 版本、输入 Evidence Ref、七维原始值和 `evaluated_at`。
- 可删除并重算。
- 不成为 Evidence Ref。
- 不单独触发 verified、自动确认、覆盖冲突或删除反证。

## 12. 权限要求

本 SPEC 只定义时间/证据回答必须服从权限，不定义完整策略：

- Answer Status 和 Evidence Assessment MUST 基于调用者在当前目的下获准读取的证据。
- 无权读取的 Source locator、时间范围、第三方视角和舱室内容 MUST NOT 出现在响应、计数、reason code 或 coverage 细节中。
- 若隐藏证据会使可见答案不安全，系统 MUST fail closed，返回不泄露原因的拒绝/降级；具体状态由 S4 定义。
- 时间范围授权 MUST 同时裁剪 valid-time 查询、recorded-time 查询和 Evidence Ref，不能只裁剪 View。
- Derived assessment 的敏感度不低于全部输入证据的策略交集。

## 13. 冲突行为

### 13.1 冲突检测条件

冲突候选至少同时满足：

1. subject 相同或已明确同一 identity。
2. predicate/state_kind 相同或被规范声明互斥。
3. valid-time 可能范围重叠。
4. value 在同一 perspective/claim scope 下不兼容。
5. 双方至少各有可定位 Source 或可审计记录；缺证据 candidate 仍可并列，但必须显示 missing evidence。

不同主体观点、不同 perspective 的 sentiment、非重叠状态演化和纯 Coverage gap MUST NOT 自动标为事实冲突。

### 13.2 冲突回答

- 未解决冲突的查询返回 `disputed`，并列可见证据、时间范围和 perspective。
- 系统不得按最新 recorded_at、来源数量、模型置信度或文案完整度自动选胜者。
- 用户裁决创建新的审查/规范修订，但保留冲突历史和反证。
- 模糊时间仅“可能重叠”时，响应必须标明 temporal overlap uncertainty；不得伪装成确定冲突或确定不冲突。

## 14. 失败与降级

| 失败 | MUST 行为 |
|---|---|
| valid time 缺失 | 显式 unknown；不得复制 recorded_at |
| 自然语言时间解析失败 | 保留原文和 Source locator，`resolution_status=unresolved`，不猜测 |
| 时间格式非法 | 拒绝该语义 proposal；Source 继续保留 |
| 时区缺失/冲突 | 保留 local value 和异常状态；跨区比较降级为 unknown |
| Source hash mismatch | integrity 标记 mismatch；不得用其单独 Verify，Source 处置后置 S7/S9 |
| CoverageWindow 缺失或不完整 | 否定性查询返回 not_covered，不把零结果当“未发生” |
| Evidence lineage 无法确定 | independence=unknown，不能增加 independent corroboration count |
| Evidence assessment 失败 | 不返回 verified；保留原始维度并返回 unknown/unconfirmed 或明确 unavailable |
| 冲突评估失败 | 不自动选值；返回 disputed/unknown 与可见失败原因 |
| freshness policy 缺失 | 不声称 fresh；返回 unknown/not_applicable 语义 |
| Derived View stale | 不将旧 payload 冒充当前；由 S3 选择 Canonical fallback 或 unavailable |
| 权限不足 | 少回答且不泄露隐藏证据是否存在；详细合同后置 S4 |

## 15. 撤销与审计

- 所有时间解释的确认、拒绝、supersede MUST 记录 actor、recorded_at、revision、原表达和结果。
- 纠正 valid time MUST 创建新修订，旧 recorded-time 知识切面继续可查询。
- 撤销 ChangeSet MUST 产生新的审计可见 revision；不得删除曾经发布的时间/证据判断。
- 用户裁决冲突不能删除反证；审计必须能还原裁决前后的 Answer Status 所依据证据。
- Evidence assessment MUST 记录 policy/version/evaluated_at，但可作为派生结果重建。
- 硬删除是例外：可按后续 S4/S7 合同移除正文，审计只保留不含正文的最小删除证明；本 SPEC 不承诺正文永存。

## 16. 兼容与迁移

- 所有时间、CoverageWindow 和 Evidence assessment 结构 MUST 携带 `schema_version`。
- 旧数据只有一个 `timestamp` 时，迁移器 MUST NOT 猜它同时是 valid、recorded、source-created 和 ingested；必须保留原字段并标为 unresolved mapping。
- 未知时间 precision、certainty 或证据枚举 MUST fail closed for verification，同时通过 namespaced extension 保留以便往返。
- 时区数据库或解析器升级不得静默改变已确认 valid time；需要变更时走 ChangeSet/迁移审计。
- evidence family 规则升级 MAY 重算 corroboration，但不得改写 Source 或审查历史。
- Answer Status、freshness 和 evidence score 属于可重算结果；导出时必须带 policy/version，导入不得把旧结果直接当当前事实。

## 17. 正例

### 17.1 事后补录保持双时态

```yaml
object_type: state
state_id: state_synthetic_work_002
state_kind: synthetic.assignment
valid_time:
  kind: interval
  end:
    boundary_kind: known
    precision: month
    earliest: 2029-04-01T00:00:00+08:00
    latest_exclusive: 2029-05-01T00:00:00+08:00
    certainty: approximate
recorded_at: 2030-06-10T10:00:00+08:00
```

它能表达“现实边界在 2029 年 4 月，系统到 2030 年才记录”，但不伪造具体离开日。

### 17.2 当前联系状态演化

```yaml
before:
  value: active
  valid_time:
    kind: interval
    start: {boundary_kind: known, value: 2030-01-01T00:00:00+08:00, precision: instant, certainty: exact}
    end: {boundary_kind: known, value: 2030-09-15T12:00:00+08:00, precision: instant, certainty: exact}
    bounds: "[)"
after:
  value: no_contact
  valid_time:
    kind: interval
    start: {boundary_kind: known, value: 2030-09-15T12:00:00+08:00, precision: instant, certainty: exact}
    end: {boundary_kind: unbounded, value: null, precision: unknown, certainty: unknown}
    bounds: "[)"
recorded_at: 2030-11-01T09:00:00+08:00
```

valid time 在过去而 recorded time 是当前；旧 active State 继续存在。

### 17.3 无覆盖窗口

```yaml
query_valid_at: 2025-02
coverage_window:
  coverage_start: 2025-06-01
  coverage_end: unbounded
answer_status: not_covered
answer_value: null
reason_codes: [outside_coverage_window]
```

### 17.4 观点的有限验证范围

```yaml
assertion_kind: opinion
perspective_ref: entity_person_alpha
review_status: confirmed
verification_scope: viewpoint
answer_status: verified
```

这里只 Verify “该合成主体确认自己持有此观点”，不 Verify 观点所评价的外部世界事实。

## 18. 反例

### 18.1 把记录时间当现实时间

```yaml
valid_from: copy(recorded_at)
```

无效。valid time 未知时必须 unknown。

### 18.2 用 null 混淆 unknown 与当前有效

```yaml
valid_to: null
```

含义不充分。必须明确 `boundary_kind=unknown` 或 `unbounded`。

### 18.3 重复材料伪造独立证据

```yaml
independent_source_count: 3
inputs: [original_excerpt, screenshot_of_same_excerpt, model_summary_of_same_excerpt]
```

无效。三者属于同一 evidence family。

### 18.4 零搜索结果断言没有事件

```yaml
search_hits: 0
answer_status: verified
answer_value: no_event
coverage: unknown
```

无效。应为 not_covered，不得断言事件未发生。

### 18.5 用户确认把陈述变成客观事实

```yaml
assertion_kind: reported
review_status: confirmed
verification_scope: world_claim
automatic: true
```

无效。确认记录/陈述发生不自动 Verify world claim。

### 18.6 历史查询因证据旧而 stale

```yaml
query_valid_at: 2020-01
evidence_effective_at: 2020-01
answer_status: stale
reason: evidence_is_old
```

无效。历史相关性必须相对目标 valid time 评估。

## 19. 可执行验收测试

### 19.1 测试状态

```yaml
suite_id: bitemporal_evidence_v0_4
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

本文只定义合同测试目录。没有 fixture manifest、测试运行器或实现模块，全部 Verification Result 为 `not_executed`。

### 19.2 测试清单

| Test ID | Given | When | Then |
|---|---|---|---|
| `BTE-AT-001` | 四类时间值不同的合成记录 | 往返并查询 | valid/recorded/source-created/ingested 各自保持，不互相覆盖 |
| `BTE-AT-002` | valid time 缺失、recorded_at 存在 | 规范化 | valid time 为 unknown，不复制 recorded_at |
| `BTE-AT-003` | PRD Case B 合成事后补录 | 分别查询 valid 与 recorded time | 回答现实边界在 2029-04、系统于 2030 记录 |
| `BTE-AT-004` | Case B 记录尚未进入系统的 recorded cutoff | 以该 cutoff 查询 | 当时知识切面不包含补录记录 |
| `BTE-AT-005` | 同一 State 的 active/no_contact 相邻区间 | 查询 transition 前后 | 前为 active，从 transition 起为 no_contact，历史均保留 |
| `BTE-AT-006` | unknown end 与 unbounded end | 查询 current | unknown 不得被解释为仍有效，unbounded 可表示开放当前状态 |
| `BTE-AT-007` | “去年秋天”合成 Source | 解析但未确认 | 只产生 proposed 时间范围并保留原文 locator |
| `BTE-AT-008` | 用户确认 season 粒度 | 读取 Canonical | 仍为 season/approximate，不虚构精确日期 |
| `BTE-AT-009` | 查询点落在 confirmed 模糊边界不确定带 | 求状态 | 返回 unknown 和可能范围，不选中点 |
| `BTE-AT-010` | local time 且 timezone unknown | 跨时区比较 | 返回时间比较 unknown，不假定设备时区 |
| `BTE-AT-011` | source_created_at 晚于 ingested_at | 摄取 Source | Source 保留，time metadata 标 conflicting，不静默修正 |
| `BTE-AT-012` | Case F 窗口从 2025-06 开始、查询 2025-02 | 查询是否发生联系 | answer_status=not_covered，显示覆盖起点 |
| `BTE-AT-013` | continuous=unknown 且零搜索结果 | 查询否定事实 | 返回 not_covered，不返回 verified no_event |
| `BTE-AT-014` | 查询区间部分覆盖且含 gap | 查询整个区间 | 返回覆盖子区间与 gaps，不把整段视为完整覆盖 |
| `BTE-AT-015` | 一条直接正向 Source 位于不完整窗口 | 查询该正向事件 | 可按验证规则回答该事件，并同时披露 coverage gap |
| `BTE-AT-016` | Evidence assessment | 校验字段 | 七个维度都存在或显式 unknown，不能只有 score |
| `BTE-AT-017` | 原文、同源截图、同源模型摘要 | 计算 corroboration | independent family count=1 |
| `BTE-AT-018` | 两个来源依赖关系未知 | 计算 corroboration | independence=unknown，不默认 count=2 |
| `BTE-AT-019` | 原件第三方陈述与截图第一人称陈述 | 评估证据 | proximity 与 integrity 分轴，不压成单一等级 |
| `BTE-AT-020` | confirmed opinion | 计算回答 | viewpoint scope 可 verified；其 world claim 不自动 verified |
| `BTE-AT-021` | confirmed reported Assertion | 计算回答 | statement occurrence 与 world claim 分别评估 |
| `BTE-AT-022` | 外部 Agent 提交 verify | 执行动作 | 拒绝设置个人语义事实 verified |
| `BTE-AT-023` | 高 evidence_score 但缺原始维度 | 计算回答 | 不得返回 verified，报告 assessment invalid |
| `BTE-AT-024` | 有未审 candidate 且覆盖充分 | 查询 claim | answer_status=unconfirmed |
| `BTE-AT-025` | 覆盖充分、无 candidate、无法判断 | 查询 claim | answer_status=unknown |
| `BTE-AT-026` | Current Query 只有超出 policy 的旧证据 | 查询当前状态 | answer_status=stale，返回 policy/evaluated_at |
| `BTE-AT-027` | Historical Query 的证据与目标时间匹配 | 查询过去状态 | 不因证据年龄自动 stale |
| `BTE-AT-028` | fresh View 包含 stale evidence | 查询当前 claim | View fresh 不得把 answer 提升为 verified |
| `BTE-AT-029` | stale View 含旧 verified payload | 查询当前 claim | 不把旧 payload 冒充当前 verified |
| `BTE-AT-030` | Case E 三个不兼容项目状态且 valid time 重叠 | 查询状态 | answer_status=disputed，并列证据，不自动选值 |
| `BTE-AT-031` | 两个不同 perspective 的 sentiment | 检测冲突 | 保留为不同观点，不自动标客观冲突 |
| `BTE-AT-032` | 非重叠 active/no_contact State | 检测冲突 | 识别时间演化，不进入 disputed |
| `BTE-AT-033` | valid-time 纠正产生新 recorded revision | 查询当前与旧 cutoff | 当前见纠正，旧 cutoff 仍见当时知识 |
| `BTE-AT-034` | Derived View 作为 Evidence Ref | 校验 assessment | 返回 `derived_evidence_forbidden` |
| `BTE-AT-035` | 无权限 evidence 会影响结论 | 生成低权限回答 | fail closed 且不通过状态、计数或 reason 泄露隐藏证据 |
| `BTE-AT-036` | 全部 S2 fixture | 执行隐私静态扫描 | 仅含合成 ID/内容，不出现真实个人数据 |
| `BTE-AT-037` | Canonical Evidence Ref 带 `dimensions`、`evidence_family_id` 或 export receipt | 校验规范写入 | 拒绝派生/receipt 字段进入事实 evidence；assessment 只能进入 Derived EvidenceAssessment，receipt 只能进入 Coverage declaration/审计引用 |
| `BTE-AT-038` | Canonical RelationshipState 的 `value=unknown`，且覆盖充分、无具体值证据 | 查询实际联系状态 | `answer_status=unknown`、`answer_value=null`；不得返回 verified/not_covered/unconfirmed，也不得推断任一具体联系状态 |

### 19.3 PRD Case 覆盖

| PRD Case | S2 Test |
|---|---|
| Case A：关系状态与模糊时间 | `BTE-AT-005`、`BTE-AT-007`、`BTE-AT-008`、`BTE-AT-009` |
| Case B：事后补录 | `BTE-AT-003`、`BTE-AT-004`、`BTE-AT-033` |
| Case E：来源冲突 | `BTE-AT-030`、`BTE-AT-031`、`BTE-AT-032` |
| Case F：无覆盖窗口 | `BTE-AT-012`、`BTE-AT-013`、`BTE-AT-014` |
| Case G：Hypothesis 反例边界 | `BTE-AT-016`、`BTE-AT-017`；完整生命周期后置 S5 |

### 19.4 Micro-MVP 对应

| S2 Test | Micro Test |
|---|---|
| `BTE-AT-001`、`BTE-AT-002` | `MM-001`、`MM-004` 的时间前置条件 |
| `BTE-AT-005` | `MM-004`、`MM-006` |
| `BTE-AT-007`、`BTE-AT-008`、`BTE-AT-009` | `MM-002` 的 `transition_at` 候选 |
| `BTE-AT-017`、`BTE-AT-034` | `MM-002` 的 Source-only evidence 约束 |
| `BTE-AT-029` | `MM-010` |

### 19.5 不变量覆盖

| Invariant | Acceptance Test |
|---|---|
| `BTE-INV-001` | `BTE-AT-001`、`BTE-AT-002`、`BTE-AT-011` |
| `BTE-INV-002` | `BTE-AT-003`、`BTE-AT-004`、`BTE-AT-005`、`BTE-AT-033` |
| `BTE-INV-003` | `BTE-AT-006`、`BTE-AT-008`、`BTE-AT-009` |
| `BTE-INV-004` | `BTE-AT-020`、`BTE-AT-024`、`BTE-AT-025`、`BTE-AT-026`、`BTE-AT-030` |
| `BTE-INV-005` | `BTE-AT-012`、`BTE-AT-024`、`BTE-AT-025`、`BTE-AT-026`、`BTE-AT-030` |
| `BTE-INV-006` | `BTE-AT-016`、`BTE-AT-019`、`BTE-AT-023`、`BTE-AT-037` |
| `BTE-INV-007` | `BTE-AT-017`、`BTE-AT-018`、`BTE-AT-037` |
| `BTE-INV-008` | `BTE-AT-020`、`BTE-AT-021`、`BTE-AT-022` |
| `BTE-INV-009` | `BTE-AT-030`、`BTE-AT-031`、`BTE-AT-032` |
| `BTE-INV-010` | `BTE-AT-017`、`BTE-AT-034` |
| `BTE-INV-011` | `BTE-AT-026`、`BTE-AT-027`、`BTE-AT-028`、`BTE-AT-029` |
| `BTE-INV-012` | `BTE-AT-002`、`BTE-AT-007`、`BTE-AT-010`、`BTE-AT-023` |
| `BTE-INV-013` | `BTE-AT-030`、`BTE-AT-033` |
| `BTE-INV-014` | `BTE-AT-035` |
| `BTE-INV-015` | `BTE-AT-036` |
| `BTE-INV-016` | `BTE-AT-038` |

## 20. 未决问题

以下五个产品语义已于 2026-07-13 由产品负责人明确确认推荐方案，不再阻止本 SPEC 批准：

| 问题 | 决定 |
|---|---|
| `IQ-003` | verification_scope 封闭枚举；确认记录/观点不自动 Verify world claim；见 §6.9 |
| `IQ-004` | 按共同上游 provenance 归并 evidence family；未知依赖不计独立；见 §11.1 |
| `IQ-007` | Answer stale 与 View freshness 分轴；见 §6.9 |
| `IQ-009` | 模糊时间保留 lexical_locator、范围、精度和确定性；用户可确认粗粒度，不必虚构日期；见 §10.2 |
| `IQ-010` | State 采用半开区间 `[start,end)`；instant 单独建模；unknown 与 unbounded 严格分离；见 §6.1/§10.1 |

以下实现参数不需要在本 SPEC 选择，后续由对应 SPEC/ADR 处理：

- 各领域 freshness policy 和强直接证据规则由 S5 定义并版本化。
- `recorded_at` 的可信时钟、精度和全局/object revision 关系由 S3 与 ADR 定义。
- 物理时间格式、时区数据库、索引和序列化由 S7 与 ADR 定义。
- 权限不足时的外部错误合同与最小披露由 S4/S8 定义。
- Evidence Family 的持久化 ID 推算机制由 S7/ADR 定义。

`DQ-012` 保持 deferred；§6.9 只规定其重开前的最保守行为，不把该行为升级为永久产品裁决。

## 21. 完成定义

本 SPEC 批准须满足以下条件，已全部达成：

- 上游 `SPEC-SOM-001` v0.3 保持 Approved，且本 SPEC 不反向改变对象边界。✓
- `IQ-003`、`IQ-004`、`IQ-007`、`IQ-009`、`IQ-010` 已由产品负责人明确决定并记录（见 §20 与 `OPEN_QUESTIONS.md`）。✓
- 四类时间、unknown/unbounded、粗粒度、时区和事后补录均有唯一语义（见 §5-§10）。✓
- State 区间端点、相邻、重叠和 current/historical 查询可穷尽测试（见 §10.1、BTE-AT-005/006/009/032）。✓
- 七个证据维度、Evidence Family、Review/Verify 和 score 边界无混用（见 §6.7、§11）。✓
- 六个 Answer Status 各有正例、反例和组合降级测试（见 §17-§18、BTE-AT-020 至 030）。✓
- PRD Cases A/B/E/F/G 与 FR-002/003/008/009/010/205 已进入追踪矩阵（见 §19.3 与 REQUIREMENTS_MATRIX.md §10）。✓ FR-205 S2 责任仅限时间可比性边界（§10.3-§10.4），不扩大 Micro 或 P2 实现范围。
- 每条 `BTE-INV-*` 至少由一个 `BTE-AT-*` 覆盖（见 §19.5）。✓
- 所有示例和 fixture 均为合成数据；未选择数据库、技术栈或模型供应商。✓
- 文档结构、内部引用、枚举和测试 ID 通过静态校验。✓
- 产品负责人已明确批准本 SPEC。✓
- 测试状态继续如实区分 defined、executed、passed；未执行不得称为通过。✓

当前结论：本 SPEC v0.4 于 2026-07-15 完成 PRD v0.5 兼容复审并保持 `Approved`。Canonical Evidence Ref 与可重算 assessment 继续分离，并增加 DQ-012 未裁决期间的保守查询约束；测试仍未物化、执行或通过。
