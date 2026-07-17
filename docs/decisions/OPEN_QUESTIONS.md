# 开放问题

## 1. 使用规则

本文是产品裁决队列，不是事实补丁。未标记 `decided` 的问题不得由 SPEC、ADR、代码或测试夹带裁决。

状态：`open`、`decided`、`deferred`、`superseded`。

优先级：

- `blocking`：不裁决就不能完成第一份 Semantic Object Model SPEC。
- `important`：不阻止第一份 SPEC 起草，但对应正式 SPEC 必须处理。
- `deferred`：不影响 Micro-MVP，不在当前门禁内裁决。

### 1.1 当前 Micro Gate 决定

`DEC-MICRO-GATE-001` 已于 2026-07-14 由产品负责人决定并单独记录在 `MICRO_GATE_DECISION_2026-07-14.md`：PRD v0.4 canonical LF hash 获批准；只授权 Micro Gate 纠偏；personality oracle 使用只读 synthetic Hypothesis sentinel；P1 关闭性复审前业务实现门禁保持 closed。

该决定关闭 `MMF-001` 和 `MMF-005` 中必须由产品负责人裁决的部分，不改变本文件原有 BQ/IQ/DQ 状态，也不裁决多模型审计列出的 deferred 产品问题。

### 1.2 当前 PRD v0.5 基线决定

`DEC-PRD-V05-001` 于 2026-07-15 批准 `PRDv05.md` 为当前产品基线，并将 v0.4 的已确认裁决整合回 PRD。当前 blocking=0、important=0；`DQ-001..013` 保持 deferred。S1-S9 在完成 v0.5 兼容复核前不得被当作 current-compatible，也不得开始业务实现。

### 1.3 当前 MVP-A Answer Safety 决定

`DEC-MVP-A-AS-001` 于 2026-07-17 选择 `SLICE-MVP-A-ANSWER-SAFETY-001` 作为下一切片，只授权进入 S1/S2/S3/S6/S7 applicability review。当前切片 blocking=0；`DQ-012` 不重开，因为本切片不写 Canonical `value=unknown`，只在覆盖充分但无法判断时派生 `answer_status=unknown`。业务实现、ADR、suite 和 Implementation Plan 均不存在。

## 2. Blocking

### BQ-001：`RelationshipState` 的规范对象归属是什么？

- 状态：`decided`
- PRD 依据：§8 只列 `Relationship` 和 `State`；§20 FR-003、§24.1、§26 Case A 使用 `RelationshipState`。
- 必须裁决：它是通用 `State` 的子类型、`Relationship` 内的时态片段，还是第 13 个核心对象。
- 影响：标识、字段所有权、有效区间、修订、ChangeSet proposal 和视图依赖均无法稳定定义。
- 建议方向：优先在现有 12 对象内建模，避免无门禁扩充对象数量；该建议不是裁决。
- 决策人：产品负责人。
- 决定：`RelationshipState` 是 `State` 的语义子类型/配置，使用 `subject_ref` 指向 `Relationship`；它不是第 13 个核心对象。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：维持 12 对象稳定内核，同时让联系状态拥有独立标识、时间区间、证据和修订语义。
- 影响的 PRD/SPEC/测试：PRD §8、§20 FR-003、§24.1、§26 Case A；Semantic Object Model SPEC；`MM-002`、`MM-004`、`MM-006`。
- 是否需要新 PRD 基线：`no`；PRD 原文不改，差异由本决策和 SPEC 显式解释。

### BQ-002：内容类型、证据/审查状态与回答状态如何正交？

- 状态：`decided`
- PRD 依据：§8.1 把 `inferred`、`analysis`、`predicted`、`fictional`、`disputed`、`unknown` 并列为 Assertion 类型；§9.3 又有 `review_status`；§9.4 定义“五态”并追加 `unknown`。
- 必须裁决：
  - `disputed` 和 `unknown` 是否仍是 `Assertion.type`。
  - `unknown` 是第六种回答状态、补充原因码，还是无 Assertion 时的查询结果。
  - `verified` 是 Assertion 审查状态、查询结果，还是二者映射。
- 影响：Source/事实/观点/推断/预测/虚构分离无法形成可执行不变量。
- 决策人：产品负责人。
- 决定：使用三个正交轴。`assertion_kind` 只包含 `observed`、`reported`、`quoted`、`opinion`、`inferred`、`analysis`、`predicted`、`fictional`；`disputed` 与 `unknown` 不再是 Assertion 内容类型。`review_status` 单独描述审查结果。事实型回答使用六态 `answer_status`：`verified`、`unconfirmed`、`disputed`、`not_covered`、`stale`、`unknown`。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：内容来源、审查行为和查询结论不能互相覆盖；承认六态比保留错误的“五态”名称更诚实。
- 影响的 PRD/SPEC/测试：PRD §6、§8.1、§9.3-§9.4、FR-008；Semantic Object Model SPEC 与 Bitemporal & Evidence SPEC。
- 是否需要新 PRD 基线：`no`；PRD 的“五态”措辞保留为已知差异，后续 SPEC 使用 `answer_status` 六态。

### BQ-003：Source 写入是否必须通过 ChangeSet？

- 状态：`decided`
- PRD 依据：§8 将 Source 标为规范数据；§11.1 要求任何规范写入只能经过 ChangeSet；§18.2 要求快速记录先保存原始记录、语义整理后台进行。
- 必须裁决：原始 Source 是否采用独立的 append receipt，再由 ChangeSet 只修改 Canonical Context；或 Source 自身也必须用一个机械 ChangeSet 写入。
- 影响：Micro 输入的原子边界、失败行为、`actor`、`base_revision` 和撤销语义。
- 决策人：产品负责人。
- 决定：原始 Source 使用独立、可审计的 append receipt 快速保存，不要求先创建 ChangeSet；由 Source 产生或修改 Canonical Context 的一切语义写入必须经过 ChangeSet。Source 的纠正、封存和删除仍必须走受控操作，具体合同由后续 SPEC 定义。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：同时满足快速记录、Source 不静默丢失和规范语义唯一写路径。
- 影响的 PRD/SPEC/测试：PRD §8、§11.1、§18.2、FR-001/002/004；Semantic Object Model SPEC；`MM-001`、`MM-003`。
- 是否需要新 PRD 基线：`no`；SPEC 明确“规范语义写入”的边界。

### BQ-004：12 对象之外的术语如何映射？

- 状态：`decided`
- PRD 依据：§8 声明 12 类核心对象；§13.3 和 §22.2 使用 `Obligation`；§13.4 使用 `viewpoint`；§20 FR-202 使用 `Calibration`；§22.2 使用 `Snapshot`。
- 必须裁决：上述词是现有对象的别名/子类型、派生对象、测试概念，还是未来扩展对象。
- 影响：第一份 SPEC 无法给出封闭对象表和“不得绕开边界”的验收。
- 建议方向：Micro-MVP 中不新增对象；别名必须显式映射，不能靠实现猜测。
- 决策人：产品负责人。
- 决定：`Obligation` 是 `Commitment` 的语义配置；`viewpoint` 是带 `perspective` 的 `opinion` Assertion；`Calibration` 是 `Outcome` 的校准语义；`Snapshot` 是非规范 `Projection`。四者均不新增核心对象。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：封闭 12 对象词表，避免案例用词暗中扩张本体。
- 影响的 PRD/SPEC/测试：PRD §8、§13.3-§13.4、§20 FR-202、§22.2；Semantic Object Model SPEC。
- 是否需要新 PRD 基线：`no`。

### BQ-005：第一份 Semantic Object Model SPEC 的深度边界是什么？

- 状态：`decided`
- PRD 依据：§8 要求 12 个核心对象；§24.1 只使用 Source、Entity、Assertion、Relationship/State、ChangeSet；§27.3 又把“12 个核心对象获得确认”列为实现门禁。
- 必须裁决：第一份 SPEC 是完整定义 12 对象，还是对 12 对象只定义共同语义边界、对 Micro 使用的对象给出完整字段和状态契约，其余对象明确保留到后续阶段。
- 影响：SPEC 工作量可能直接突破“窄而硬”原则。
- 建议方向：采用分层深度，完整锁定共同不变量，只详细定义 Micro 子集；该建议需产品确认。
- 决策人：产品负责人。
- 决定：对 12 个核心对象定义封闭清单、共同边界和最小语义；只对 Micro-MVP 使用的 `Source`、`Entity`、`Assertion`、`Relationship`、`State`/`RelationshipState`、`ChangeSet` 给出完整字段与状态合同。其余对象不得据此提前实现。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：先锁住不可后补的语义地基，同时保持第一条链路窄而硬。
- 影响的 PRD/SPEC/测试：PRD §8、§24.1、§27.3；Semantic Object Model SPEC；SOM 验收测试。
- 是否需要新 PRD 基线：`no`。

## 3. Important

### IQ-001：Micro-MVP 的 Core View 封闭集合是什么？

- 状态：`decided`
- PRD 依据：§10.3 列 6 个；§24.2 列 3 个；§24.1 和本轮链路只要求人物卡与关系时间线。
- 处理 SPEC：ChangeSet & Consistency、Semantic Test Harness。
- 当前限制：验收文件只把人物卡和关系时间线作为 Micro 必需视图，不据此修改 PRD 白名单。
- 决定：Micro Core View 封闭集合仅为 `person_card` 与 `relationship_timeline`；PRD §10.3 其他 View 保持后续 MVP 白名单，不进入 Micro 门禁。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权按保守方案完成全部 SPEC）。
- 影响：S3、S6、`MM-005`/`MM-008`/`MM-010`；无需新 PRD 基线。

### IQ-002：L2 “同一会话”与“5 秒内”如何共同成立？

- 状态：`decided`
- PRD 依据：§10.2、§21.2、§26 Case A。
- 处理 SPEC：ChangeSet & Consistency。
- 需要明确：发布响应是否构成读取屏障；超时期间返回 `updating`、直接读 Canonical，还是允许带标识旧视图。
- 决定：发布响应构成同会话 Publish Barrier。L1 成功后 L2 只能返回新 revision、直接 Canonical fallback，或无旧 payload 的 `updating/unavailable`；5 秒是测量 SLO，不是返回旧值许可。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S3、S6、S8、`MM-005`/`MM-010`；无需新 PRD 基线。

### IQ-003：用户确认和”强直接证据”分别如何产生 `verified`？

- 状态：`decided`
- PRD 依据：§6.1、§6.7、§9.3-§9.4、§11.4、§19.3。
- 处理 SPEC：Bitemporal & Evidence、Shiling Policy。
- 需要明确：用户确认的是”记录了该陈述””该陈述为用户观点”还是”客观事实成立”。
- 决定：使用 `verification_scope` 封闭枚举：`record_accuracy | statement_occurrence | viewpoint | world_claim`。确认记录/陈述/观点不得自动扩大为对 world claim 的验证。强直接证据规则必须按 claim/source kind 显式批准并版本化；外部 Agent 无权设置个人语义事实为 `verified`；实现 MUST 拒绝枚举外 scope 值。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：防止模型或 Agent 因用户确认一层语义而自动扩大验证范围；枚举封闭后各层 claim 边界可测试。
- 影响的 PRD/SPEC/测试：PRD §6.1、§9.4；SPEC-BTE-001 §6.9、§11.2；BTE-AT-020 至 022。
- 是否需要新 PRD 基线：no。

### IQ-004：证据来源何时算相互独立？

- 状态：`decided`
- PRD 依据：§9.3。
- 处理 SPEC：Bitemporal & Evidence。
- 决定：Evidence independence 按共同上游 provenance 判定。同一 Source 的 excerpt/OCR/截图/摘要/模型提取只计一个 evidence family；依赖关系 unknown 时不得默认 independent。Evidence Family 没有独立写入口，由系统从 provenance 推算；持久化机制后置 S7/ADR。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：防止同一内容经多次转换后被重复计数为独立证据，造成虚假高置信度。
- 影响的 PRD/SPEC/测试：PRD §9.3；SPEC-BTE-001 §6.6、§11.1；BTE-AT-017、018。
- 是否需要新 PRD 基线：no。

### IQ-005：失败时“旧安全版本”的可读边界是什么？

- 状态：`decided`
- PRD 依据：§14.3、§21.1、§25.2。
- 处理 SPEC：ChangeSet & Consistency、Storage, Index & Portability。
- 需要明确：Canonical、L2 和 L3 分别可返回什么，以及必须附带何种 freshness 信息。
- 决定：发布前/L1 失败继续读取旧 Canonical；L1 成功后旧 L2 不得作为 current，只能新 Canonical fallback 或 unavailable；L3 可返回旧 payload 但必须 stale。所有获授权响应返回实际 revision；拒绝响应按最小披露可返回 `withheld`，不能借全局 revision 泄露活动。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S3、S7、S8；无需新 PRD 基线。

### IQ-006：`narrative_context` 保存内容还是 Source 引用？

- 状态：`decided`
- PRD 依据：§6.12、§13.2、§16.2。
- 处理 SPEC：Semantic Object Model、Storage, Index & Portability。
- 需要明确：避免复制敏感原文与满足独立可读之间的边界。
- 决定：Canonical 默认保存 Source locator 与可选最小用户自写 note，不复制原始敏感正文；owner 私有导出可按 policy 内联相应 Source，分享导出继续裁剪。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S1、S4、S7、S9；无需新 PRD 基线。

### IQ-007：回答 `stale` 与 View `freshness_status=stale` 是否同一状态？

- 状态：`decided`
- PRD 依据：§9.4、§10.2、§20 FR-105。
- 处理 SPEC：Bitemporal & Evidence、ChangeSet & Consistency。
- 决定：两者分轴。Answer `stale` 说明证据不满足查询的当前性要求；View freshness 说明 Projection 是否对齐 Canonical revision。fresh View 仍可能包含 stale evidence；stale View 不得把旧 answer 冒充当前 verified。传播行为由 S3 定义。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：两个轴混用会导致 View 刷新就自动提升事实置信度，破坏证据独立原则。
- 影响的 PRD/SPEC/测试：PRD §9.4、§10.2；SPEC-BTE-001 §6.9；BTE-AT-028、029。
- 是否需要新 PRD 基线：no。

### IQ-008：撤销是否发布补偿 revision？

- 状态：`decided`
- PRD 依据：§11.3、§12.3、§24.1、§26 Case A。
- 处理 SPEC：ChangeSet & Consistency。
- 当前验收只要求：当前语义与撤销前基线等价、修订历史不被擦除、所有 Micro Core View 对齐同一新 revision。
- 决定：撤销整个已发布 ChangeSet 必须产生新的 Compensation Revision；当前语义恢复等价，但原发布、确认和中间 revision 全部保留。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S3、S6、`MM-008`；无需新 PRD 基线。

### IQ-009：模糊有效时间如何表达和确认？

- 状态：`decided`
- PRD 依据：§9.1、§26 Case A。
- 处理 SPEC：Bitemporal & Evidence。
- 当前限制：Micro fixture 使用明确时间，不实现”去年秋天”的解析。
- 决定：保留 `lexical_locator`（指向原文的 Source locator）、候选范围、`precision` 和 `certainty`；用户可确认粗粒度/近似范围，不必虚构精确日期；解析结果在确认前仅为 `resolution_status=proposed`；候选经用户确认后才进入 Canonical。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：防止系统把”去年秋天”自动映射为任意精确日期，保留原始模糊语义并可追溯到原文。
- 影响的 PRD/SPEC/测试：PRD §9.1、§26 Case A；SPEC-BTE-001 §6.1、§10.2；BTE-AT-007、008、009。
- 是否需要新 PRD 基线：no。

### IQ-010：相邻 Relationship State 区间的端点规则是什么？

- 状态：`decided`
- PRD 依据：§9.1、§12.2、§13.2-§13.3。
- 处理 SPEC：Bitemporal & Evidence。
- 决定：State 使用半开区间 `[start,end)`；`transition_at` 前一瞬旧 State 有效，从 `transition_at` 起新 State 有效；相邻区间首尾相接不构成冲突。`unknown` 端点与 `unbounded` 端点严格分离：unknown 表示边界存在但不知道，unbounded 表示语义上无该侧边界。instant 事件单独建模，不得用 start=end 空区间伪装。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：半开区间保证同一时刻切换时不存在重叠或空隙，简化历史查询和冲突判定。
- 影响的 PRD/SPEC/测试：PRD §9.1、§13.2；SPEC-BTE-001 §6.1、§6.2、§10.1；BTE-AT-005、006、009、032。
- 是否需要新 PRD 基线：no。

### IQ-011：硬删除的范围、时限、证明和失败状态是什么？

- 状态：`decided`
- PRD 依据：§6.13、§12.4、§21.4。
- 处理 SPEC：Privacy & Access Policy、Storage, Index & Portability、ChangeSet & Consistency。
- 需要覆盖：Source、Canonical、Ledger 正文、索引、缓存、备份、导出副本。
- 决定：按 `live_source`、`canonical_payload`、`ledger_payload`、`derived_index`、`cache`、`backup`、`export_copy`、`minimal_audit_proof` 分层回执。系统控制内完成才算 deleted；备份可 `pending_expiry`，外部副本 `out_of_control`，失败为 partial failure；无 retention policy 不承诺时限；审计不留正文。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S3、S4、S7；无需新 PRD 基线。

### IQ-012：私有完整导出与对外分享导出是否采用不同策略？

- 状态：`decided`
- PRD 依据：§17.5、§19.2、§21.4。
- 处理 SPEC：Privacy & Access Policy、Storage, Index & Portability、MCP Contract。
- 决定：两者是不同动作。owner 私有导出按明确范围提供可移植完整包；外部分享默认最小披露、第三方脱敏和字段裁剪，不能复用全量导出权限。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S4、S7、S8；无需新 PRD 基线。

### IQ-013：多舱室策略冲突如何合并？

- 状态：`decided`
- PRD 依据：§17.2-§17.4。
- 处理 SPEC：Privacy & Access Policy。
- 需要明确：默认拒绝、策略交集、字段裁剪，以及 Derived View 的权限继承。
- 决定：所有适用策略取最严格交集；字段 allow 取交集、deny 取并集，无法求交默认 deny。Derived View 继承依赖 compartments 合集和最高 sensitivity。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S4、S5、S8；无需新 PRD 基线。

### IQ-014：MVP SLO 的测量环境和计时边界是什么？

- 状态：`decided`
- PRD 依据：§21.2。
- 处理 SPEC：Semantic Test Harness；具体环境由后续 ADR 记录。
- 决定：SLO 使用版本化 Reference Profile；计时从本地核心接受请求开始，到满足合同的响应可供调用者读取结束，后台工作另记。具体硬件、OS 和 runner 由 ADR 记录，结果不得跨 profile 外推。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S3、S6、S7；无需新 PRD 基线。

### IQ-015：未知扩展字段往返的语义保真边界是什么？

- 状态：`decided`
- PRD 依据：§21.4。
- 处理 SPEC：Storage, Index & Portability、Ingestion & Migration。
- 需要明确：字段名、类型、顺序、原始字节和不可识别枚举分别保证什么。
- 决定：结构化未知字段保留命名空间、字段名、类型、嵌套和值语义，不保证 JSON 键顺序、空白或原始字节；需要字节保真的未知格式作为 opaque Source blob + media type/hash 保存；未知 required enum fail closed。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S7、S9；无需新 PRD 基线。

### IQ-016：九份 SPEC 的权威顺序采用哪一版？

- 状态：`decided`
- PRD 依据：§27.2。
- 冲突：本轮任务明确要求顺序为 Semantic、Bitemporal、ChangeSet、Privacy、Shiling、Harness、Storage、MCP、Ingestion；PRD §27.2 把 Shiling 置于 Privacy 前，并把 MCP、Storage、Harness 排为第 6-8。
- 当前处理：`docs/specs/README.md` 按本轮明确顺序建档；不静默修改 PRD。
- 决策人：产品负责人。
- 决定：采用 `docs/specs/README.md` 的当前九份顺序，即 Privacy 先于 Shiling、Semantic Test Harness 先于 Storage、MCP 位于 Storage 之后、Ingestion & Migration 最后。
- 决定日期：2026-07-13。
- 决策人：产品负责人（用户明确确认推荐方案）。
- 理由：先锁定权限再定义识灵权限边界，先定义测试合同再选择持久化合同，并让 MCP 建立在稳定存储与权限语义之上。
- 影响的 PRD/SPEC/测试：PRD §27.2；`docs/specs/README.md`；`docs/PROJECT_STATE.md`。
- 是否需要新 PRD 基线：`no`；保留 PRD §27.2 原文并记录本决策。

### IQ-017：删除、封存、归档和降权是否都必须形成 ChangeSet？

- 状态：`decided`
- PRD 依据：§11.2、§12.4、§19.2。
- 处理 SPEC：ChangeSet & Consistency、Privacy & Access Policy。
- 决定：archive、seal、soft/hard delete 等 Canonical 状态或权限语义必须经 ChangeSet；纯 Derived 清缓存/重建不经；降权若只改变派生 retrieval activation 不经，若持久为 Canonical policy 则经。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S3、S4、S7；无需新 PRD 基线。

### IQ-018：`base_revision` 是全局 revision 还是对象级 revision？

- 状态：`decided`
- PRD 依据：§2.2 #39、§10.2、§11.2、§19.2。
- 处理 SPEC：ChangeSet & Consistency；实现机制另立 ADR。
- 决定：`base_revision` 使用全局 Canonical `data_revision`；`object_revision` 记录对象最后一次语义变化对应的全局 revision。成功 ChangeSet 产生一个新全局 revision，未变化对象 revision 不变。
- 决定日期：2026-07-13；决策人：产品负责人（整体授权）。
- 影响：S1、S2、S3、S7、S8；无需新 PRD 基线。

## 4. Deferred

| ID | 问题 | PRD 依据 | 何时重开 |
|---|---|---|---|
| DQ-001 | Noetide 商标、域名和应用商店可用性 | §27.1 | 品牌和发布准备阶段 |
| DQ-002 | 默认 Review Budget 是否按用户模式变化 | §15.4、§27.1 | MVP-B / Shiling 产品校准 |
| DQ-003 | Sealed 内容紧急访问和恢复策略 | §27.1 | 非 Micro 的 Privacy 设计评审 |
| DQ-004 | 第三方数据分享、继承和纠纷规则 | §17.5、§27.1 | 法律/伦理验证阶段；Micro 不实现分享和继承 |
| DQ-005 | 个人工具与商业产品的开源边界 | §27.1 | 商业化决策阶段 |
| DQ-006 | 哪些 Decision 类型需要专业风险提示 | §27.1、§25.3 | MVP-C 决策室设计阶段 |
| DQ-007 | 多设备同步冲突与密钥恢复 | §20 FR-301、§24.5 | Year 2 规划门禁 |
| DQ-008 | 连接器优先级与适配范围 | §20 FR-302、§24.5 | Year 2 规划门禁 |
| DQ-009 | 家庭授权、托管人和数字遗产工作流 | §20 FR-305、§24.5-§24.6 | 法律/伦理验证完成后 |
| DQ-010 | A2A 或其他 Agent 协议选择 | §20 FR-306、§24.6 | 生态阶段，不影响 MCP 最小合同 |
| DQ-011 | 用户预授权自动处理的最大范围 | §11.4、§27.1 | MVP-B / FR-107 前；Micro 不扩大自动权限 |
| DQ-012 | Canonical `value=unknown` 与 Answer Status 的组合 | §9.4、§27.1 | 引入 unknown State 查询前 |
| DQ-013 | MCP 不可逆动作是否存在非 verified 例外 | §19.3、§27.1 | MCP runtime 前；未裁决时采用最保守拒绝 |

## 5. 决策记录模板

问题裁决后，在原问题下追加：

```text
- 状态: decided
- 决定:
- 决定日期:
- 决策人:
- 理由:
- 影响的 PRD/SPEC/测试:
- 是否需要新 PRD 基线: yes | no
```

不得删除原问题或用实现结果代替产品决定。
