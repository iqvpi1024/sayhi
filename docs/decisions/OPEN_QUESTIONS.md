# 开放问题

## 1. 使用规则

本文是产品裁决队列，不是事实补丁。未标记 `decided` 的问题不得由 SPEC、ADR、代码或测试夹带裁决。

状态：`open`、`decided`、`deferred`、`superseded`。

优先级：

- `blocking`：不裁决就不能完成第一份 Semantic Object Model SPEC。
- `important`：不阻止第一份 SPEC 起草，但对应正式 SPEC 必须处理。
- `deferred`：不影响 Micro-MVP，不在当前门禁内裁决。

## 2. Blocking

### BQ-001：`RelationshipState` 的规范对象归属是什么？

- 状态：`open`
- PRD 依据：§8 只列 `Relationship` 和 `State`；§20 FR-003、§24.1、§26 Case A 使用 `RelationshipState`。
- 必须裁决：它是通用 `State` 的子类型、`Relationship` 内的时态片段，还是第 13 个核心对象。
- 影响：标识、字段所有权、有效区间、修订、ChangeSet proposal 和视图依赖均无法稳定定义。
- 建议方向：优先在现有 12 对象内建模，避免无门禁扩充对象数量；该建议不是裁决。
- 决策人：产品负责人。

### BQ-002：内容类型、证据/审查状态与回答状态如何正交？

- 状态：`open`
- PRD 依据：§8.1 把 `inferred`、`analysis`、`predicted`、`fictional`、`disputed`、`unknown` 并列为 Assertion 类型；§9.3 又有 `review_status`；§9.4 定义“五态”并追加 `unknown`。
- 必须裁决：
  - `disputed` 和 `unknown` 是否仍是 `Assertion.type`。
  - `unknown` 是第六种回答状态、补充原因码，还是无 Assertion 时的查询结果。
  - `verified` 是 Assertion 审查状态、查询结果，还是二者映射。
- 影响：Source/事实/观点/推断/预测/虚构分离无法形成可执行不变量。
- 决策人：产品负责人。

### BQ-003：Source 写入是否必须通过 ChangeSet？

- 状态：`open`
- PRD 依据：§8 将 Source 标为规范数据；§11.1 要求任何规范写入只能经过 ChangeSet；§18.2 要求快速记录先保存原始记录、语义整理后台进行。
- 必须裁决：原始 Source 是否采用独立的 append receipt，再由 ChangeSet 只修改 Canonical Context；或 Source 自身也必须用一个机械 ChangeSet 写入。
- 影响：Micro 输入的原子边界、失败行为、`actor`、`base_revision` 和撤销语义。
- 决策人：产品负责人。

### BQ-004：12 对象之外的术语如何映射？

- 状态：`open`
- PRD 依据：§8 声明 12 类核心对象；§13.3 和 §22.2 使用 `Obligation`；§13.4 使用 `viewpoint`；§20 FR-202 使用 `Calibration`；§22.2 使用 `Snapshot`。
- 必须裁决：上述词是现有对象的别名/子类型、派生对象、测试概念，还是未来扩展对象。
- 影响：第一份 SPEC 无法给出封闭对象表和“不得绕开边界”的验收。
- 建议方向：Micro-MVP 中不新增对象；别名必须显式映射，不能靠实现猜测。
- 决策人：产品负责人。

### BQ-005：第一份 Semantic Object Model SPEC 的深度边界是什么？

- 状态：`open`
- PRD 依据：§8 要求 12 个核心对象；§24.1 只使用 Source、Entity、Assertion、Relationship/State、ChangeSet；§27.3 又把“12 个核心对象获得确认”列为实现门禁。
- 必须裁决：第一份 SPEC 是完整定义 12 对象，还是对 12 对象只定义共同语义边界、对 Micro 使用的对象给出完整字段和状态契约，其余对象明确保留到后续阶段。
- 影响：SPEC 工作量可能直接突破“窄而硬”原则。
- 建议方向：采用分层深度，完整锁定共同不变量，只详细定义 Micro 子集；该建议需产品确认。
- 决策人：产品负责人。

## 3. Important

### IQ-001：Micro-MVP 的 Core View 封闭集合是什么？

- 状态：`open`
- PRD 依据：§10.3 列 6 个；§24.2 列 3 个；§24.1 和本轮链路只要求人物卡与关系时间线。
- 处理 SPEC：ChangeSet & Consistency、Semantic Test Harness。
- 当前限制：验收文件只把人物卡和关系时间线作为 Micro 必需视图，不据此修改 PRD 白名单。

### IQ-002：L2 “同一会话”与“5 秒内”如何共同成立？

- 状态：`open`
- PRD 依据：§10.2、§21.2、§26 Case A。
- 处理 SPEC：ChangeSet & Consistency。
- 需要明确：发布响应是否构成读取屏障；超时期间返回 `updating`、直接读 Canonical，还是允许带标识旧视图。

### IQ-003：用户确认和“强直接证据”分别如何产生 `verified`？

- 状态：`open`
- PRD 依据：§6.1、§6.7、§9.3-§9.4、§11.4、§19.3。
- 处理 SPEC：Bitemporal & Evidence、Shiling Policy。
- 需要明确：用户确认的是“记录了该陈述”“该陈述为用户观点”还是“客观事实成立”。

### IQ-004：证据来源何时算相互独立？

- 状态：`open`
- PRD 依据：§9.3。
- 处理 SPEC：Bitemporal & Evidence。
- 需要明确：同一原始内容的转发、截图、摘要和多次模型提取不得被重复计数。

### IQ-005：失败时“旧安全版本”的可读边界是什么？

- 状态：`open`
- PRD 依据：§14.3、§21.1、§25.2。
- 处理 SPEC：ChangeSet & Consistency、Storage, Index & Portability。
- 需要明确：Canonical、L2 和 L3 分别可返回什么，以及必须附带何种 freshness 信息。

### IQ-006：`narrative_context` 保存内容还是 Source 引用？

- 状态：`open`
- PRD 依据：§6.12、§13.2、§16.2。
- 处理 SPEC：Semantic Object Model、Storage, Index & Portability。
- 需要明确：避免复制敏感原文与满足独立可读之间的边界。

### IQ-007：回答 `stale` 与 View `freshness_status=stale` 是否同一状态？

- 状态：`open`
- PRD 依据：§9.4、§10.2、§20 FR-105。
- 处理 SPEC：Bitemporal & Evidence、ChangeSet & Consistency。

### IQ-008：撤销是否发布补偿 revision？

- 状态：`open`
- PRD 依据：§11.3、§12.3、§24.1、§26 Case A。
- 处理 SPEC：ChangeSet & Consistency。
- 当前验收只要求：当前语义与撤销前基线等价、修订历史不被擦除、所有 Micro Core View 对齐同一新 revision。

### IQ-009：模糊有效时间如何表达和确认？

- 状态：`open`
- PRD 依据：§9.1、§26 Case A。
- 处理 SPEC：Bitemporal & Evidence。
- 当前限制：Micro fixture 使用明确时间，不实现“去年秋天”的解析。

### IQ-010：相邻 Relationship State 区间的端点规则是什么？

- 状态：`open`
- PRD 依据：§9.1、§12.2、§13.2-§13.3。
- 处理 SPEC：Bitemporal & Evidence。
- 需要明确：区间开闭、同一时刻切换、未知端点和重叠冲突。

### IQ-011：硬删除的范围、时限、证明和失败状态是什么？

- 状态：`open`
- PRD 依据：§6.13、§12.4、§21.4。
- 处理 SPEC：Privacy & Access Policy、Storage, Index & Portability、ChangeSet & Consistency。
- 需要覆盖：Source、Canonical、Ledger 正文、索引、缓存、备份、导出副本。

### IQ-012：私有完整导出与对外分享导出是否采用不同策略？

- 状态：`open`
- PRD 依据：§17.5、§19.2、§21.4。
- 处理 SPEC：Privacy & Access Policy、Storage, Index & Portability、MCP Contract。

### IQ-013：多舱室策略冲突如何合并？

- 状态：`open`
- PRD 依据：§17.2-§17.4。
- 处理 SPEC：Privacy & Access Policy。
- 需要明确：默认拒绝、策略交集、字段裁剪，以及 Derived View 的权限继承。

### IQ-014：MVP SLO 的测量环境和计时边界是什么？

- 状态：`open`
- PRD 依据：§21.2。
- 处理 SPEC：Semantic Test Harness；具体环境由后续 ADR 记录。

### IQ-015：未知扩展字段往返的语义保真边界是什么？

- 状态：`open`
- PRD 依据：§21.4。
- 处理 SPEC：Storage, Index & Portability、Ingestion & Migration。
- 需要明确：字段名、类型、顺序、原始字节和不可识别枚举分别保证什么。

### IQ-016：九份 SPEC 的权威顺序采用哪一版？

- 状态：`open`
- PRD 依据：§27.2。
- 冲突：本轮任务明确要求顺序为 Semantic、Bitemporal、ChangeSet、Privacy、Shiling、Harness、Storage、MCP、Ingestion；PRD §27.2 把 Shiling 置于 Privacy 前，并把 MCP、Storage、Harness 排为第 6-8。
- 当前处理：`docs/specs/README.md` 按本轮明确顺序建档；不静默修改 PRD。
- 决策人：产品负责人。

### IQ-017：删除、封存、归档和降权是否都必须形成 ChangeSet？

- 状态：`open`
- PRD 依据：§11.2、§12.4、§19.2。
- 处理 SPEC：ChangeSet & Consistency、Privacy & Access Policy。

### IQ-018：`base_revision` 是全局 revision 还是对象级 revision？

- 状态：`open`
- PRD 依据：§2.2 #39、§10.2、§11.2、§19.2。
- 处理 SPEC：ChangeSet & Consistency；实现机制另立 ADR。

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
