# FR 到 SPEC 需求追踪矩阵

## 1. 追踪规则

本矩阵覆盖 PRD §20 的全部 32 条功能需求，使用以下强制链路：

```text
PRD Requirement
  -> SPEC Section
  -> Acceptance Test
  -> Implementation Module
  -> Verification Result
```

当前处于 Specification Baseline Complete。S1-S9 均已 `Approved`，实现代码尚未开始，所有合同测试均为 `not_executed`。因此：

- `planned` 保留 Phase 0 的责任规划历史；九份 SPEC 的最终实际映射见 §9-§18，32 条 FR 的权威闭环见 §19。
- `TBD:<SPEC>` 是早期规划标记；若与 §19 冲突，以 §19 已定义测试为准。
- `TBD` 的 Implementation Module 表示尚未实现，不是缺陷豁免。
- Verification Result 一律为 `not_executed`；依据 PRD §6.14、§22.1，不能标记为 passed。

## 2. SPEC 代号

| 代号 | SPEC |
|---|---|
| S1 | Semantic Object Model SPEC |
| S2 | Bitemporal & Evidence SPEC |
| S3 | ChangeSet & Consistency SPEC |
| S4 | Privacy & Access Policy SPEC |
| S5 | Shiling Policy SPEC |
| S6 | Semantic Test Harness SPEC |
| S7 | Storage, Index & Portability SPEC |
| S8 | MCP Contract SPEC |
| S9 | Ingestion & Migration SPEC |

映射中的 `P` 表示规范主责，`S` 表示协作约束。S6 对所有 FR 都有测试框架责任，但只有进入当前阶段的 FR 才要求实际执行。

## 3. P0：可信变化核心

| PRD Requirement | PRD 依据 | SPEC Section（planned） | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| FR-001 接收文本与第三方规范输入包 | §20.1；§7.3；§19.4 | S9(P) 输入合同；S1/S4/S7/S8(S) | `MM-001` 仅覆盖合成文本；第三方包 `TBD:S9` | `TBD` | `not_executed` |
| FR-002 保存 Source、证据定位、哈希和 CoverageWindow | §20.1；§9.2；§21.1 | S7(P) Source 持久边界；S1/S2/S4/S9(S) | `MM-001` 覆盖 Source 定位；CoverageWindow `TBD:S2/S9` | `TBD` | `not_executed` |
| FR-003 识灵生成 Entity、Assertion、RelationshipState 候选 | §20.1；§14；§24.1 | S5(P) 候选政策；S1/S2/S3/S6(S) | `MM-002` | `TBD` | `not_executed` |
| FR-004 所有规范写入通过 ChangeSet | §20.1；§11.1 | S3(P) 唯一写路径；S1/S4/S5/S7/S8/S9(S) | `MM-003`、`MM-004`、`MM-009` | `TBD` | `not_executed` |
| FR-005 自然语言审查和高级影响预览 | §20.1；§18.3-§18.4 | S3(P) 审查/影响合同；S5/S6(S) | `MM-002`、`MM-003` | `TBD` | `not_executed` |
| FR-006 发布后更新或失效 Core View | §20.1；§10 | S3(P) L2/L3 传播；S6/S7(S) | `MM-005`、`MM-010` | `TBD` | `not_executed` |
| FR-007 ChangeSet 回执、历史和撤销 | §20.1；§11-§12 | S3(P) 回执/撤销；S6/S7/S8(S) | `MM-004`、`MM-008` | `TBD` | `not_executed` |
| FR-008 回答使用五态认知协议 | §20.1；§9.4 | S2(P) 认知状态；S1/S6/S8(S) | `BTE-AT-020` 至 `BTE-AT-030`；六态规范化见 `BQ-002` | `TBD` | `not_executed` |
| FR-009 双时态历史查询 | §20.1；§9.1 | S2(P) 双时态；S1/S6/S7/S8(S) | `BTE-AT-001` 至 `BTE-AT-010`、`BTE-AT-033`、`MM-006` | `TBD` | `not_executed` |
| FR-010 最小冲突检测与并列呈现 | §20.1；§12.1-§12.2；§26 Case E | S2(P) 冲突语义；S1/S3/S5/S6/S8(S) | `BTE-AT-030` 至 `BTE-AT-032`；发布行为 `TBD:S3` | `TBD` | `not_executed` |
| FR-011 实体合并候选和拆分回滚 | §20.1；§13.1 | S1(P) identity/merge；S3/S5/S6/S7(S) | `TBD:S1/S3`；Micro deferred | `TBD` | `not_executed` |
| FR-012 查询层强制权限和舱室 | §20.1；§17；§19.3 | S4(P) 策略；S5/S6/S7/S8(S) | `TBD:S4`；Micro 无外部 Agent | `TBD` | `not_executed` |

## 4. P1：静默整理与前瞻记忆

| PRD Requirement | PRD 依据 | SPEC Section（planned） | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| FR-101 候选聚合、去重和价值排序 | §20.2；§15.2 | S5(P) 候选政策；S1/S2/S6/S7(S) | `TBD:S5`；MVP-B | `TBD` | `not_executed` |
| FR-102 Review Budget 和分级通知 | §20.2；§15.3-§15.4 | S5(P) 预算/通知；S4/S6(S) | `TBD:S5`；MVP-B | `TBD` | `not_executed` |
| FR-103 Episode 聚类与分层摘要 | §20.2；§16.2 | S5(P) 整理政策；S1/S2/S4/S6/S7(S) | `TBD:S1/S5`；MVP-B | `TBD` | `not_executed` |
| FR-104 Commitment 提取、状态和提醒 | §20.2；§8；§26 Case C | S1(P) Commitment 语义；S3/S5/S6/S7/S8(S) | `TBD:S1/S3/S5`；MVP-B | `TBD` | `not_executed` |
| FR-105 增量对账、失败队列和 stale 检测 | §20.2；§10.5；§25.2 | S3(P) 对账语义；S5/S6/S7(S) | `TBD:S3/S6`；Micro 只覆盖 `MM-010` | `TBD` | `not_executed` |
| FR-106 Semantic Diff | §20.2；§12.3；§18.6 | S3(P) revision diff；S2/S6/S7/S8(S) | `TBD:S3`；MVP-B | `TBD` | `not_executed` |
| FR-107 低风险机械变更事后可撤销 | §20.2；§11.4 | S3(P) 确认政策；S4/S5/S6(S) | `TBD:S3/S5`；Micro 不自动发布个人语义 | `TBD` | `not_executed` |
| FR-108 多语言原文与翻译对照 | §20.2；§21.5 | S9(P) 输入语言；S1/S2/S4/S6/S7(S) | `TBD:S9`；MVP-B | `TBD` | `not_executed` |

## 5. P2：成长与决策

| PRD Requirement | PRD 依据 | SPEC Section（planned） | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| FR-201 Hypothesis 支持证据、反例、范围和生命周期 | §20.3；§6.7；§26 Case G | S1(P) Hypothesis 对象；S2/S3/S5/S6/S7(S) | `TBD:S1/S2/S5`；MVP-C | `TBD` | `not_executed` |
| FR-202 Decision、Outcome、Calibration 闭环 | §20.3；§8；§18.7 | S1(P) 对象边界；S2/S3/S5/S6/S7/S8(S) | `TBD:S1`；MVP-C | `TBD` | `not_executed` |
| FR-203 周/月/年度复盘 | §20.3；§23 | S5(P) 生成政策；S2/S4/S6/S7(S) | `TBD:S5`；MVP-C | `TBD` | `not_executed` |
| FR-204 基准、乐观、悲观情景推演 | §20.3 | S1(P) predicted/fictional 边界；S2/S4/S5/S6(S) | `TBD:S1/S5`；MVP-C | `TBD` | `not_executed` |
| FR-205 跨阶段行为和结果比较 | §20.3；§18.6 | S2(P) 时态比较；S1/S5/S6/S7(S) | `TBD:S2`；MVP-C | `TBD` | `not_executed` |
| FR-206 可执行性约束和行动跟进 | §20.3；§18.7 | S5(P) 行动政策；S1/S3/S4/S6(S) | `TBD:S5`；MVP-C | `TBD` | `not_executed` |

## 6. P3：生态与长期能力

| PRD Requirement | PRD 依据 | SPEC Section（planned） | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| FR-301 加密多设备同步 | §20.4；§24.5 | S7(P) 数据/修订合同；S3/S4/S6(S) | `TBD:S7`；Year 2 | `TBD` | `not_executed` |
| FR-302 有限高价值连接器 | §20.4；§24.5 | S9(P) 适配合同；S4/S6/S7/S8(S) | `TBD:S9`；Year 2 | `TBD` | `not_executed` |
| FR-303 Context Pack 导出与导入 | §20.4；§21.4 | S7(P) 包格式语义；S1/S4/S6/S8/S9(S) | `TBD:S7/S9`；MVP-C/后续 | `TBD` | `not_executed` |
| FR-304 专业 Agent 权限模板 | §20.4；§19.3 | S4(P) 权限模板；S5/S6/S8(S) | `TBD:S4/S8`；Year 2 | `TBD` | `not_executed` |
| FR-305 家庭授权和数字遗产完整工作流 | §20.4；§17.5；§24.5-§24.6 | S4(P) 授权原则；S3/S6/S7/S8(S) | `TBD:S4`；Year 2+，受法律/伦理门禁 | `TBD` | `not_executed` |
| FR-306 A2A 或其他 Agent 互操作适配 | §20.4；§24.6 | S8(P) 能力接口；S4/S5/S6(S) | `TBD:S8`；Year 3-5 | `TBD` | `not_executed` |

## 7. 九份 SPEC 覆盖汇总

| SPEC | 主责 FR | 关键协作 FR | 当前状态 |
|---|---|---|---|
| S1 Semantic Object Model | FR-011、FR-104、FR-201、FR-202、FR-204 | FR-001-010、FR-103、FR-108、FR-205、FR-303 | `approved`；v0.2；`BQ-001..005` 已决定；测试未执行 |
| S2 Bitemporal & Evidence | FR-008、FR-009、FR-010、FR-205 | FR-002/003/101/103/106/108/201/202/203/204 | `approved`；v0.2；IQ-003/004/007/009/010 已决定；测试未执行 |
| S3 ChangeSet & Consistency | FR-004、FR-005、FR-006、FR-007、FR-105、FR-106、FR-107 | FR-003/010/011/104/201/202/206/301/305 | `approved`；v0.1；测试未执行 |
| S4 Privacy & Access Policy | FR-012、FR-304、FR-305 | 所有涉及 Source、Derived View、外发、删除和 Agent 的 FR | `approved`；v0.1；测试未执行 |
| S5 Shiling Policy | FR-003、FR-101、FR-102、FR-103、FR-203、FR-206 | FR-005/010/011/104/107/201/202/204/304/306 | `approved`；v0.1；测试未执行 |
| S6 Semantic Test Harness | 无业务主责；主责证明全部 FR | FR-001 至 FR-306 | `approved`；v0.1；测试未执行 |
| S7 Storage, Index & Portability | FR-002、FR-301、FR-303 | 所有持久、revision、重建、导出和 SLO 相关 FR | `approved`；v0.1；测试未执行 |
| S8 MCP Contract | FR-306 | FR-001/007/008/009/010/104/106/303/304/305 | `approved`；v0.1；测试未执行 |
| S9 Ingestion & Migration | FR-001、FR-108、FR-302 | FR-002/003/303 | `approved`；v0.1；测试未执行 |

## 8. Micro-MVP 覆盖边界

当前 Micro 验收只形成以下部分覆盖：

- FR-001：仅合成纯文本，不含第三方包。
- FR-002：仅 Source 与证据定位，不含一般 CoverageWindow。
- FR-003：仅预置实体上的一个 `contact_state` 候选，不含通用抽取。
- FR-004 至 FR-007：覆盖确认、原子发布、两项 Core View、回执和整包撤销。
- FR-009：只覆盖 Relationship State 的当前/历史查询。

FR-008、FR-010、FR-011、FR-012 以及全部 P1-P3 均不是 Micro 通过门槛。把它们标为 deferred 不等于删除 PRD 要求。
## 9. S1 实际追踪（Approved）

S1 正文：`docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` v0.2。以下映射已经定义，但测试仍未执行，Implementation Module 仍为 `TBD`。

| PRD Requirement | S1 实际章节 | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-001 文本输入的 Source 边界 | §5.1、§6.2、§14 | `SOM-AT-004`、`SOM-AT-020`、`MM-001` | `TBD` | `not_executed` |
| FR-002 Source、定位和哈希语义 | §6.2、§11、§14 | `SOM-AT-004`、`SOM-AT-019`、`SOM-AT-020` | `TBD` | `not_executed` |
| FR-003 Entity/Assertion/RelationshipState 候选边界 | §5.2、§6.3-§6.7、§8-§9 | `SOM-AT-002`、`SOM-AT-013`、`SOM-AT-014` | `TBD` | `not_executed` |
| FR-004 Canonical 语义写入必须经过 ChangeSet | §6.7、§8、`SOM-INV-007` | `SOM-AT-005`、`SOM-AT-006` | `TBD` | `not_executed` |
| FR-008 认知三轴与六态回答边界 | §3、§6.4、§7.3、§13 | `SOM-AT-007`、`SOM-AT-008`、`SOM-AT-018`、`SOM-AT-021` | `TBD` | `not_executed` |
| FR-009 Historical State 对象边界 | §6.6、§8、§10 | `SOM-AT-015`、`SOM-AT-024`、`MM-006` | `TBD` | `not_executed` |
| FR-010 冲突对象并列语义 | §7.3、§13 | `SOM-AT-021` | `TBD` | `not_executed` |
| FR-011 Entity merge/split identity 边界 | §6.3、§7.2、§8、§15 | `SOM-AT-017` | `TBD` | `not_executed` |
| FR-103 Episode 对象边界 | §5.1、§6.9 | `TBD:S5`；S1 只定义边界 | `TBD` | `not_executed` |
| FR-104 Commitment/Obligation 对象边界 | §5.2、§6.9 | `SOM-AT-003`；生命周期 `TBD:S3/S5` | `TBD` | `not_executed` |
| FR-108 Source 语言与原文边界 | §6.2、§6.8、§16 | `SOM-AT-019`；完整对照 `TBD:S9` | `TBD` | `not_executed` |
| FR-201 Hypothesis 隔离边界 | §5.1、§6.9、`SOM-INV-005` | `SOM-AT-010` | `TBD` | `not_executed` |
| FR-202 Decision/Outcome/Calibration 边界 | §5.2、§6.9 | `SOM-AT-003`；闭环 `TBD:S2/S5` | `TBD` | `not_executed` |
| FR-204 predicted/fictional 边界 | §6.4、§8、§11 | `SOM-AT-018` | `TBD` | `not_executed` |
| FR-205 跨阶段对象可比较前提 | §6.1、§10、§16 | `SOM-AT-015`；比较规则 `TBD:S2` | `TBD` | `not_executed` |
| FR-303 Context Pack 对象可移植前提 | §6.1、§16 | `SOM-AT-016`；完整包 `TBD:S7/S9` | `TBD` | `not_executed` |
## 10. S2 实际追踪（Approved）

S2 正文：`docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md` v0.2。以下测试均为合同定义，尚无 Implementation Module，全部未执行。

| PRD Requirement | S2 实际章节 | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-002 Source 时间、证据定位与 CoverageWindow | §5.1-§5.2、§6.4-§6.7、§10-§11 | `BTE-AT-001`、`BTE-AT-011` 至 `BTE-AT-019` | `TBD` | `not_executed` |
| FR-003 候选的时间与证据边界 | §4.2、§6.1-§6.7、§7.1、§10.2 | `BTE-AT-007` 至 `BTE-AT-009`、`BTE-AT-016` 至 `BTE-AT-018` | `TBD` | `not_executed` |
| FR-008 六态事实回答 | §6.8-§6.9、§7.2-§7.3、§11.2-§11.3 | `BTE-AT-020` 至 `BTE-AT-030` | `TBD` | `not_executed` |
| FR-009 双时态历史查询 | §5.1-§5.3、§6.1-§6.4、§10 | `BTE-AT-001` 至 `BTE-AT-010`、`BTE-AT-033` | `TBD` | `not_executed` |
| FR-010 冲突检测与并列呈现 | §5.3、§6.9、§13 | `BTE-AT-030` 至 `BTE-AT-032` | `TBD` | `not_executed` |
| FR-101 证据去重前提 | §6.6-§6.7、§11.1 | `BTE-AT-017`、`BTE-AT-018` | `TBD` | `not_executed` |
| FR-106 recorded-time Semantic Diff 前提 | §6.3、§10.3-§10.4、§15 | `BTE-AT-004`、`BTE-AT-033`；完整 diff `TBD:S3` | `TBD` | `not_executed` |
| FR-108 原文、时区和语言边界 | §6.1、§6.4、§10.2、§10.5 | `BTE-AT-007`、`BTE-AT-010`、`BTE-AT-011` | `TBD` | `not_executed` |
| FR-201 Hypothesis 正反证据边界 | §4.1、§6.6-§6.7、§11 | `BTE-AT-016` 至 `BTE-AT-018`；生命周期 `TBD:S5` | `TBD` | `not_executed` |
| FR-205 跨阶段有效/记录时间比较 | §10.3-§10.4、§15-§16 | `BTE-AT-003`、`BTE-AT-004`、`BTE-AT-033` | `TBD` | `not_executed` |
## 11. S3 实际追踪（Approved）

S3 正文：`docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md` v0.1。以下测试均为合同定义，尚无 Implementation Module，全部未执行。

| PRD Requirement | S3 实际章节 | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-004 所有规范写入通过 ChangeSet | §5-§6、§7.2、§9 | `CS-AT-001` 至 `CS-AT-005`、`MM-003`、`MM-004` | `TBD` | `not_executed` |
| FR-005 自然语言审查和高级影响预览 | §6.4、§6.6 | `CS-AT-006`、`MM-002`、`MM-003` | `TBD` | `not_executed` |
| FR-006 发布后更新或失效 Core View | §8、§10 | `CS-AT-010` 至 `CS-AT-013`、`MM-005`、`MM-010` | `TBD` | `not_executed` |
| FR-007 ChangeSet 回执、历史和撤销 | §6.5、§7.3、§15 | `CS-AT-014` 至 `CS-AT-016`、`MM-004`、`MM-008` | `TBD` | `not_executed` |
| FR-105 增量对账、失败队列和 stale 检测 | §8.3、§10.5、§14 | `CS-AT-017` 至 `CS-AT-019`、`MM-010` | `TBD` | `not_executed` |
| FR-106 Semantic Diff | §6.3、§15 | `CS-AT-020`；完整 UI `TBD:S6` | `TBD` | `not_executed` |
| FR-107 低风险机械变更事后可撤销 | §6.7、§7.2 | `CS-AT-007`；识灵政策 `TBD:S5` | `TBD` | `not_executed` |

## 12. S4 实际追踪（Approved）

正文：`docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md` v0.1。

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-012 查询层权限/舱室 | §5-§14 | `PAP-AT-001` 至 `PAP-AT-010` | `TBD` | `not_executed` |
| FR-304 专业 Agent 权限模板边界 | §6、§12、§16 | `PAP-AT-001`、`PAP-AT-008`、`MCP-AT-001` 至 `MCP-AT-003` | `TBD` | `not_executed` |
| FR-305 家庭/数字遗产原则边界 | §2、§12-§16、§20 | `PAP-AT-011`、`PAP-AT-012`；完整工作流 deferred | `TBD` | `not_executed` |

## 13. S5 实际追踪（Approved）

正文：`docs/specs/05_SHILING_POLICY_SPEC.md` v0.1。

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-003 语义候选 | §5-§7 | `SHP-AT-001`、`SHP-AT-002`、`SHP-AT-004` | `TBD` | `not_executed` |
| FR-101 候选聚合/去重/排序 | §6.1-§6.3、§7 | `SHP-AT-003`、`SHP-AT-011` 至 `SHP-AT-014` | `TBD` | `not_executed` |
| FR-102 Review Budget | §6.2-§6.3 | `SHP-AT-011` 至 `SHP-AT-013` | `TBD` | `not_executed` |
| FR-103 Episode/摘要政策边界 | §5、§7、§11 | `SHP-AT-001`、`SHP-AT-014`；完整聚类实现 deferred | `TBD` | `not_executed` |
| FR-203 周/月/年度复盘政策边界 | §2、§6.3、§11 | `SHP-AT-011`、`SHP-AT-021`；完整复盘实现 deferred | `TBD` | `not_executed` |
| FR-206 行动跟进政策边界 | §5、§12、§14 | `SHP-AT-008`、`SHP-AT-016`、`SHP-AT-022` | `TBD` | `not_executed` |

## 14. S6 实际追踪（Approved）

正文：`docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md` v0.1。S6 对全部 32 条 FR 负责证明格式与结果真实性；`HTH-AT-001` 至 `HTH-AT-020` 验证三态、fixture、oracle、追踪、SLO 和隐私。业务实现不存在，因此全部为 `not_executed`。

## 15. S7 实际追踪（Approved）

正文：`docs/specs/07_STORAGE_INDEX_PORTABILITY_SPEC.md` v0.1。

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-002 Source/定位/hash/覆盖持久边界 | §5-§6、§11 | `SIP-AT-001`、`SIP-AT-003`、`SIP-AT-010` | `TBD` | `not_executed` |
| FR-301 多设备数据/修订边界 | §2、§10、§16、§20 | `SIP-AT-012`、`SIP-AT-021`；同步实现 deferred | `TBD` | `not_executed` |
| FR-303 Context Pack | §6.1-§6.4、§16 | `SIP-AT-001` 至 `SIP-AT-004`、`SIP-AT-007` 至 `SIP-AT-009` | `TBD` | `not_executed` |

## 16. S8 实际追踪（Approved）

正文：`docs/specs/08_MCP_CONTRACT_SPEC.md` v0.1。

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-306 Agent 互操作边界 | §4-§9、§12、§20 | `MCP-AT-001` 至 `MCP-AT-023`；A2A 实现 deferred | `TBD` | `not_executed` |
| FR-007/008/009/010 MCP 响应协作 | §6-§14 | `MCP-AT-004` 至 `MCP-AT-012`、`MCP-AT-017` | `TBD` | `not_executed` |
| FR-304/305 权限/破坏性动作协作 | §6.3、§12 | `MCP-AT-013`、`MCP-AT-014`、`MCP-AT-021` | `TBD` | `not_executed` |

## 17. S9 实际追踪（Approved）

正文：`docs/specs/09_INGESTION_MIGRATION_SPEC.md` v0.1。

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-001 文本/输入包 | §4-§7、§14 | `IMM-AT-001` 至 `IMM-AT-006` | `TBD` | `not_executed` |
| FR-002 Source 输入协作 | §6.1-§6.2、§10-§11 | `IMM-AT-001`、`IMM-AT-007` 至 `IMM-AT-010` | `TBD` | `not_executed` |
| FR-108 原文/翻译 | §6.3、§10-§11 | `IMM-AT-011`、`IMM-AT-013` | `TBD` | `not_executed` |
| FR-302 连接器适配边界 | §2、§6、§14、§20 | `IMM-AT-002`、`IMM-AT-013`；连接器实现 deferred | `TBD` | `not_executed` |
| FR-303 Pack 导入/迁移 | §6.5、§7.2、§13-§16 | `IMM-AT-015` 至 `IMM-AT-021` | `TBD` | `not_executed` |

## 18. 验证结果语义

- 九份 SPEC 均已完成并批准，表示语义合同完成。
- Implementation Module 全部为 `TBD`，因为本轮没有业务代码。
- 所有 Acceptance Test 只完成定义，Verification Result 全部为 `not_executed`。
- 任何后续实现必须回填真实模块、命令、环境、时间、exit code 和 artifact，才能把单项改为 passed/failed。

## 19. 全部 32 条 FR 权威闭环

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| FR-001 | S9 §4-§7 | `IMM-AT-001` 至 `IMM-AT-006` | `TBD` | `not_executed` |
| FR-002 | S2 §6.4-§6.7；S7 §5-§6；S9 §6 | `BTE-AT-011` 至 `BTE-AT-019`、`SIP-AT-001`、`IMM-AT-001` | `TBD` | `not_executed` |
| FR-003 | S1 §5-§6；S5 §5-§7 | `SOM-AT-002`、`SHP-AT-001`、`SHP-AT-004` | `TBD` | `not_executed` |
| FR-004 | S3 §5-§9 | `CS-AT-001` 至 `CS-AT-005` | `TBD` | `not_executed` |
| FR-005 | S3 §6.4-§6.6 | `CS-AT-006`、`MM-002`、`MM-003` | `TBD` | `not_executed` |
| FR-006 | S3 §8、§14 | `CS-AT-013` 至 `CS-AT-015`、`MM-005`、`MM-010` | `TBD` | `not_executed` |
| FR-007 | S3 §6.5、§7.3、§15 | `CS-AT-016` 至 `CS-AT-019`、`MM-008` | `TBD` | `not_executed` |
| FR-008 | S2 §6.8-§7.3 | `BTE-AT-020` 至 `BTE-AT-030` | `TBD` | `not_executed` |
| FR-009 | S2 §5-§10 | `BTE-AT-001` 至 `BTE-AT-010`、`BTE-AT-033` | `TBD` | `not_executed` |
| FR-010 | S2 §13；S3 §13 | `BTE-AT-030` 至 `BTE-AT-032`、`CS-AT-008` | `TBD` | `not_executed` |
| FR-011 | S1 §6.3、§7.2、§15 | `SOM-AT-017` | `TBD` | `not_executed` |
| FR-012 | S4 §5-§14 | `PAP-AT-001` 至 `PAP-AT-010` | `TBD` | `not_executed` |
| FR-101 | S5 §6-§7 | `SHP-AT-003`、`SHP-AT-011` 至 `SHP-AT-014` | `TBD` | `not_executed` |
| FR-102 | S5 §6.2-§6.3 | `SHP-AT-011` 至 `SHP-AT-013` | `TBD` | `not_executed` |
| FR-103 | S1 §5.1；S5 §5、§6.5、§11 | `SHP-AT-025` | `TBD` | `not_executed` |
| FR-104 | S1 §5.2、§6.9；S5 §6.5 | `SOM-AT-003`、`SHP-AT-026` | `TBD` | `not_executed` |
| FR-105 | S3 §14；S6 §6 | `CS-AT-021`、`CS-AT-022`、`MM-010` | `TBD` | `not_executed` |
| FR-106 | S3 §6.3、§15 | `CS-AT-020` | `TBD` | `not_executed` |
| FR-107 | S3 §6.7；S5 §6.2 | `CS-AT-007`、`SHP-AT-009`、`SHP-AT-010` | `TBD` | `not_executed` |
| FR-108 | S7 §10；S9 §6.3、§10-§11 | `SIP-AT-011`、`IMM-AT-011`、`IMM-AT-013` | `TBD` | `not_executed` |
| FR-201 | S1 §5、§9；S2 §11；S5 §6.5 | `SOM-AT-010`、`BTE-AT-016` 至 `BTE-AT-018`、`SHP-AT-030` | `TBD` | `not_executed` |
| FR-202 | S1 §5.2、§6.9；S5 §6.5 | `SOM-AT-003`、`SHP-AT-031` | `TBD` | `not_executed` |
| FR-203 | S5 §6.3、§6.5、§11 | `SHP-AT-027` | `TBD` | `not_executed` |
| FR-204 | S1 §6.4、§11；S5 §6.5 | `SOM-AT-018`、`SHP-AT-028` | `TBD` | `not_executed` |
| FR-205 | S2 §10.3-§10.4 | `BTE-AT-003`、`BTE-AT-004`、`BTE-AT-033` | `TBD` | `not_executed` |
| FR-206 | S5 §5、§6.5、§12、§14 | `SHP-AT-029` | `TBD` | `not_executed` |
| FR-301 | S7 §5、§10、§16、§20 | `SIP-AT-012`、`SIP-AT-021` | `TBD` | `not_executed` |
| FR-302 | S9 §6、§14、§20 | `IMM-AT-002`、`IMM-AT-013` | `TBD` | `not_executed` |
| FR-303 | S7 §6、§16；S9 §6.5、§7.2 | `SIP-AT-001` 至 `SIP-AT-009`、`IMM-AT-015` 至 `IMM-AT-021` | `TBD` | `not_executed` |
| FR-304 | S4 §6、§12；S8 §12 | `PAP-AT-001`、`PAP-AT-008`、`MCP-AT-001` 至 `MCP-AT-003` | `TBD` | `not_executed` |
| FR-305 | S4 §2、§12-§16 | `PAP-AT-011`、`PAP-AT-012` | `TBD` | `not_executed` |
| FR-306 | S8 §4-§9、§20 | `MCP-AT-001` 至 `MCP-AT-023` | `TBD` | `not_executed` |
