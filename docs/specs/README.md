# SPEC 计划、边界与完成标准

## 1. 作用

本文件定义九份正式 SPEC 的职责边界、依赖关系、编写顺序和完成门禁，不包含任何正式 SPEC 正文，也不选择数据库、编程语言、框架或部署方式。

产品依据：PRD §6 语义宪法、§8-§19 语义与系统边界、§20 功能需求、§21 非功能要求、§22 测试要求、§24 路线图、§27 后续文档与开工门禁。

## 2. 当前权威顺序

经 `IQ-016` 产品裁决，本项目采用以下权威工作顺序：

1. Semantic Object Model SPEC
2. Bitemporal & Evidence SPEC
3. ChangeSet & Consistency SPEC
4. Privacy & Access Policy SPEC
5. Shiling Policy SPEC
6. Semantic Test Harness SPEC
7. Storage, Index & Portability SPEC
8. MCP Contract SPEC
9. Ingestion & Migration SPEC

PRD v0.5 §27.2 已整合 `IQ-016` 并采用本文件顺序。历史只读 `PRDv04.md` 的 §27.2 顺序不同，该差异继续由决策记录解释，不得据此回退当前顺序。

## 3. 共同写作规则

每份 SPEC 必须至少包含以下规范章节：

1. 目标
2. 非目标
3. 术语
4. 适用范围
5. 对象与边界
6. 字段语义
7. 状态机
8. 允许与禁止的状态转换
9. 系统不变量
10. 时间语义
11. 证据语义
12. 权限要求
13. 冲突行为
14. 失败与降级
15. 撤销与审计
16. 兼容与迁移
17. 正例
18. 反例
19. 可执行验收测试
20. 未决问题
21. 完成定义

某章节若对该 SPEC 不适用，仍需保留并写明“不适用”的理由和上游/下游归属，不能省略后把语义留给实现猜测。

规范措辞使用：

- `MUST`：违反即不符合 SPEC。
- `MUST NOT`：禁止行为。
- `SHOULD`：默认要求，偏离必须记录理由。
- `MAY`：可选能力，不得成为其他 MUST 的隐式前提。

产品与解释文本使用中文；Schema 字段、枚举、状态和测试 ID 使用英文。

## 4. 共同完成标准

每份 SPEC 只有同时满足以下条件才可标记完成：

- 所有适用 PRD FR/NFR 已进入需求追踪矩阵，并指向具体 SPEC 章节。
- 所有术语只有一个规范定义；别名和弃用名有显式映射。
- 对象、字段、状态机、允许/禁止转换、前置条件和后置条件可被测试观察。
- 正常路径、冲突、权限拒绝、失败、降级、撤销和迁移行为均有结果语义。
- 每条系统不变量至少对应一个正例和一个反例或失败测试。
- 测试明确区分 `suite_defined`、`suite_materialized`、`suite_executed`、`suite_passed`；Markdown 合同目录不能单独成为可运行 suite。
- 未决产品问题已裁决，或该能力被明确移出当前版本；不得在正文中暗设默认值。
- 与已确认上游 SPEC 不冲突；若冲突，先走变更门禁，不直接覆盖。
- 不包含数据库、框架或供应商的最终选择；需要技术取舍时创建 ADR 候选，但不得在本阶段提前选择。
- 产品负责人完成逐份审查和确认；已批准 SPEC 的语义修订必须升版、记录依据并重新做跨 SPEC 静态审计。

## 5. 依赖关系

```text
Semantic Object Model
  -> Bitemporal & Evidence
    -> ChangeSet & Consistency
      -> Privacy & Access Policy
        -> Shiling Policy
          -> Semantic Test Harness
            -> Storage, Index & Portability
              -> MCP Contract
                -> Ingestion & Migration
```

这是规范依赖，不是运行时组件图。后续 SPEC 可以引用已确认上游合同，不能反向改写上游语义。

## 6. 各 SPEC 边界

### 6.1 Semantic Object Model SPEC

目标：定义规范对象、派生对象、标识、引用、共同元数据和对象间不可跨越的语义边界，证明 Source、事实、观点、推断、预测和虚构不会被混为一类。依据为 PRD §6-§8、§13、§16。

输入依赖：PRD v0.5 基线；`BQ-001` 至 `BQ-005` 已裁决并整合。当前 Approved 正文：`docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` v0.5。

范围内：

- 12 个核心对象的封闭清单、别名规则和规范/派生分类。
- Micro-MVP 对象的完整语义：`Source`、`Entity`、`Assertion`、`Relationship`、`State`/`RelationshipState`、`ChangeSet`。
- `narrative_context`、Source 引用、对象 identity、revision 引用的语义位置。
- 内容类型、认知/审查状态、生命周期状态的正交轴。
- 对象引用完整性、Derived View 不得成为证据、Hypothesis 不得自动升级为 Fact 等不变量。

范围外：

- 双时态区间算法和证据评分。
- ChangeSet 发布事务、视图传播和撤销执行。
- 权限策略求值、识灵候选排序、物理存储 Schema。
- 对非 Micro 对象提前实现完整业务流程。

本 SPEC 的完成标准：对象表封闭；所有 PRD 未映射名词有处置；Micro 对象可以构造有效与无效 fixture；跨层证据循环、类型升格和历史覆盖均能写成可执行断言。

### 6.2 Bitemporal & Evidence SPEC

目标：定义有效时间、记录时间、来源时间、摄取时间、CoverageWindow、证据引用和认知状态的语义。依据为 PRD §6、§9、§12、§13、§18.5、§26 Cases A/B/E/F/G。

输入依赖：已确认 Semantic Object Model SPEC v0.5。当前 Approved 正文：`docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md` v0.4。

范围内：

- `valid_time.start`、`valid_time.end`、`recorded_at`、`source_created_at`、`ingested_at`。
- 精确、模糊、未知时间和区间端点规则。
- 证据的 proximity、integrity、corroboration、perspective、inference_distance、review_status、freshness。
- 事实型回答状态、`unknown`、`not_covered`、`stale` 与冲突的正交关系。
- Current 与 Historical 查询、事后补录和状态区间不覆盖历史的不变量。

范围外：

- 证据评分模型或模型供应商选择。
- 查询引擎、索引结构和物理时间类型。
- 用户界面文案的最终设计。

本 SPEC 的完成标准：所有时间点/区间边界可穷尽测试；同一事实可分别回答 valid time 与 recorded time；无覆盖、未知、冲突、过期和已验证互不混淆；Micro 关系历史 oracle 明确。

### 6.3 ChangeSet & Consistency SPEC

目标：定义所有规范语义变更的唯一受控路径、原子发布、冲突、影响传播、回执、撤销和一致性等级。依据为 PRD §6.9、§10-§12、§20 FR-004/005/006/007/010、§21、§25.2、§26。

输入依赖：已确认 S1 v0.5 与 S2 v0.4。当前 Approved 正文：`docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md` v0.4。

范围内：

- ChangeSet 字段、proposal 操作、状态机、转换前置条件和失败终态。
- `base_revision` 并发检查、幂等、原子性和 `published_revision`。
- L1/L2/L3 定义、Micro Core View 白名单、显式依赖和影响回执。
- 冲突检测后的变更行为、整包撤销、补偿修订和审计。
- 发布失败、传播失败、重建等待、stale/更新中和安全旧版本行为。

范围外：

- 数据库事务实现和消息机制选择。
- LLM 临时推断核心依赖。
- 单 proposal 撤销若未进入 Micro 门禁。

本 SPEC 的完成标准：Micro-MVP 的确认、发布、视图更新、历史保留、禁止变化、撤销和两个失败场景均有确定 oracle；任何失败都不能产生半完成 L1 状态或把旧 L2 冒充最新。

### 6.4 Privacy & Access Policy SPEC

目标：定义主体、舱室、敏感度、动作、目的、时间、字段裁剪、封存、删除和导出的授权策略。依据为 PRD §6.10、§6.13、§12.4、§17、§19、§21.4、§25、§26 Case D。

输入依赖：当前 Approved S1-S3。当前 Approved 正文：`docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md` v0.4。

范围内：

- `owner`、`subject`、`recorder`、`viewer/caller` 的语义。
- compartment、sensitivity、purpose、action、time-bound grant 和字段级裁剪。
- 多域策略合并、Derived View 权限继承和旁路推断禁止。
- `archive`、`seal`、`soft_delete`、`hard_delete` 的授权、回执、撤销和审计语义。
- 私有备份导出、对外分享导出和第三方默认脱敏的区别。

范围外：

- 多租户身份系统、家庭协作、数字遗产完整流程。
- 操作系统密钥库或加密算法选择。
- Micro-MVP 外部 Agent 接入。

本 SPEC 的完成标准：默认拒绝和最小披露可测试；无权限时所有直接与派生路径一致少回答；删除不作虚假承诺；sealed 不被检索、摘要、候选或外发旁路使用。

### 6.5 Shiling Policy SPEC

目标：定义识灵可以观察、提出、排序、自动处理和声明什么，以及绝对禁止什么。依据为 PRD §6、§11.4、§14-§15、§19.3、§20 FR-003/101/102/107、§22.4、§25。

输入依赖：当前 Approved S1-S4。当前 Approved 正文：`docs/specs/05_SHILING_POLICY_SPEC.md` v0.4。

范围内：

- 七类职责作为一个协调内核的政策边界，不拆成多 Agent 系统。
- 候选生成、风险级别、确认政策、低风险机械操作和 Review Budget。
- 不确定、无覆盖、冲突、传播失败和权限拒绝时的诚实行为。
- Prompt injection 数据/指令边界。
- Micro 中只生成一个联系状态 proposal，且明确禁止修改 trust、closeness 和人格 Hypothesis。

范围外：

- 模型、Prompt、Reranker 或编排框架选择。
- 通用人格诊断、因果推断、决策引擎。
- 多 Agent 辩论或 A2A。

本 SPEC 的完成标准：每种自动权限有正反测试；未确认候选不能进入规范事实；权限不足和证据不足均有确定降级；Micro proposal 的允许字段集合封闭。

### 6.6 Semantic Test Harness SPEC

目标：定义用初始规范状态、Source、ChangeSet、预期状态、影响视图和禁止变化证明语义合同的方法。依据为 PRD §6.14、§22、§23.3、§24、§26。

输入依赖：当前 Approved S1-S5，作为测试 oracle。当前 Approved 正文：`docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md` v0.4。

范围内：

- fixture 包结构、确定性时钟、合成数据规则和版本标识。
- `suite_defined`、`suite_materialized`、`suite_executed`、`suite_passed` 状态机。
- 正常、反例、冲突、权限、失败、撤销、重放和迁移测试合同。
- PRD Requirement -> SPEC Section -> Acceptance Test -> Implementation Module -> Verification Result 的机器可检查追踪，并标记 `coverage_level`。
- Micro-MVP 场景作为第一套必须可执行的合同测试。

范围外：

- 把未运行场景报告为通过。
- 用文档审查代替代码测试。
- 全部 12 类长期场景在 Micro 阶段实现。

本 SPEC 的完成标准：测试包可以在无真实数据、无网络、固定时钟下复现；结果报告不能混淆定义、执行和通过；禁止变化有字段级 oracle。

### 6.7 Storage, Index & Portability SPEC

目标：定义 Source Vault、Canonical Context、Revision Ledger、Derived Index 和 Context Pack 的持久性、重建与独立可读合同。依据为 PRD §1、§7、§8、§16、§21、§25。

输入依赖：当前 Approved S1-S6，尤其是测试状态与删除合同。当前 Approved 正文：`docs/specs/07_STORAGE_INDEX_PORTABILITY_SPEC.md` v0.3。

范围内：

- 规范数据与派生数据的持久边界、校验清单、版本和重建要求。
- 原始材料、Markdown、JSON 和可选 JSON-LD 的可移植结果语义。
- 未知扩展字段往返、Schema 版本、导入前验证和失败回执。
- 删除在 live data、索引、缓存、备份和最小审计证明中的表现。
- 容量与 SLO 的可测工作负载定义。

范围外：

- 最终数据库、向量库、图数据库、事件溯源框架和云供应商选择。
- 多设备同步实现。
- 把 Markdown 当事务协调器或 Derived Index 当事实源。

本 SPEC 的完成标准：Canonical 和 Source 可在当前应用停止后按文档读取；Derived Index 可从规范包重建；往返不丢未知字段；删除/导出回执可验证且不夸大结果。

### 6.8 MCP Contract SPEC

目标：定义外部调用者读取、提出和执行受控动作时的最小能力接口、权限结果、revision、新鲜度和错误合同。依据为 PRD §7.3、§10.2、§19、§20 FR-304/306。

输入依赖：当前 Approved S1-S7。当前 Approved 正文：`docs/specs/08_MCP_CONTRACT_SPEC.md` v0.3。

范围内：

- Resources 和 Tools 的规范请求/响应边界。
- read、propose、append、controlled mutate、destructive 动作的授权和回执。
- `data_revision`、`view_revision`、`freshness_status`、evidence/missing_evidence。
- stale 数据不能驱动不可逆行动，调用者只获得最小上下文。

范围外：

- MCP 作为大文件传输总线或内部事件总线。
- A2A、多 Agent 编排、专业 Agent 市场。
- 协议 SDK 或运行时选择。

本 SPEC 的完成标准：每个工具有成功、拒绝、冲突、stale、幂等和失败响应；不能绕过 ChangeSet；权限裁剪后不得通过摘要或错误信息泄露受限内容。

### 6.9 Ingestion & Migration SPEC

目标：定义外部材料进入 Source 层、解析产物进入候选层，以及旧版本规范包迁移的合同。依据为 PRD §7.2-§7.3、§19.4、§20 FR-001/002/108/302/303、§22.4、§25.2。

输入依赖：当前 Approved S1-S8。当前 Approved 正文：`docs/specs/09_INGESTION_MIGRATION_SPEC.md` v0.4。

范围内：

- Source 引用、来源系统、原始时间、时区、语言、哈希、解析器版本和覆盖窗口输入合同。
- 原始输入、解析产物、语义候选、用户确认事实的隔离。
- 重复导入、部分失败、解析失败、未知字段、版本升级和回滚。
- 迁移只能提出/执行受控 ChangeSet，不静默重写 Verified Context。
- Micro 只定义合成纯文本入口，不实现连接器和历史迁移。

范围外：

- 全连接器、OCR/ASR/视频处理能力建设。
- 真实历史个人数据迁移。
- MCP 承担大文件传输。

本 SPEC 的完成标准：原始材料不会因解析失败丢失；重复输入可识别且不重复计证；解析结果不能自动伪装为事实；迁移可回滚并通过语义回归集。

## 7. 阶段门禁

当前状态：PRD v0.5 Compatibility Review 已完成正文修订。S1 v0.5；S2-S6 v0.4；S7-S8 v0.3；S9 v0.4，均为当前 `Approved`。兼容台账见 `docs/reviews/PRD_V05_SPEC_COMPATIBILITY_REVIEW.md`。实现代码仍为零，所有合同 suite 均未物化、未执行、未通过；`DQ-011..013` 继续 deferred，并采用各 SPEC 明示的最保守临时行为。

兼容静态验证与追踪复核通过后，当前切片恢复到 `traceable`。下一步唯一建议动作才是只为 `SLICE-MICRO-RELATIONSHIP-001` 编制必要的最小 ADR；不得借 ADR 选择长期数据库、扩展 Micro 范围或提前编码。
