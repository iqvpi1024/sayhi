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

当前处于 Phase 0，没有正式 SPEC 和实现代码。因此：

- `planned` 表示计划由对应 SPEC 负责，不表示 SPEC 已写完。
- `TBD:<SPEC>` 表示验收测试必须由该 SPEC 定义，Phase 0 不伪造测试内容。
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
| FR-008 回答使用五态认知协议 | §20.1；§9.4 | S2(P) 认知状态；S1/S6/S8(S) | `TBD:S2`；受 `BQ-002` 阻塞 | `TBD` | `not_executed` |
| FR-009 双时态历史查询 | §20.1；§9.1 | S2(P) 双时态；S1/S6/S7/S8(S) | `MM-006` | `TBD` | `not_executed` |
| FR-010 最小冲突检测与并列呈现 | §20.1；§12.1-§12.2；§26 Case E | S2(P) 冲突语义；S1/S3/S5/S6/S8(S) | `TBD:S2/S3` | `TBD` | `not_executed` |
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
| S1 Semantic Object Model | FR-011、FR-104、FR-201、FR-202、FR-204 | FR-001-010、FR-103、FR-108、FR-205、FR-303 | `not_started`；受 `BQ-001..005` 阻塞 |
| S2 Bitemporal & Evidence | FR-008、FR-009、FR-010、FR-205 | FR-002/003/101/103/106/108/201/202/203/204 | `not_started` |
| S3 ChangeSet & Consistency | FR-004、FR-005、FR-006、FR-007、FR-105、FR-106、FR-107 | FR-003/010/011/104/201/202/206/301/305 | `not_started` |
| S4 Privacy & Access Policy | FR-012、FR-304、FR-305 | 所有涉及 Source、Derived View、外发、删除和 Agent 的 FR | `not_started` |
| S5 Shiling Policy | FR-003、FR-101、FR-102、FR-103、FR-203、FR-206 | FR-005/010/011/104/107/201/202/204/304/306 | `not_started` |
| S6 Semantic Test Harness | 无业务主责；主责证明全部 FR | FR-001 至 FR-306 | `not_started`；仅 Micro 场景已定义 |
| S7 Storage, Index & Portability | FR-002、FR-301、FR-303 | 所有持久、revision、重建、导出和 SLO 相关 FR | `not_started` |
| S8 MCP Contract | FR-306 | FR-001/007/008/009/010/104/106/303/304/305 | `not_started` |
| S9 Ingestion & Migration | FR-001、FR-108、FR-302 | FR-002/003/303 | `not_started` |

## 8. Micro-MVP 覆盖边界

当前 Micro 验收只形成以下部分覆盖：

- FR-001：仅合成纯文本，不含第三方包。
- FR-002：仅 Source 与证据定位，不含一般 CoverageWindow。
- FR-003：仅预置实体上的一个 `contact_state` 候选，不含通用抽取。
- FR-004 至 FR-007：覆盖确认、原子发布、两项 Core View、回执和整包撤销。
- FR-009：只覆盖 Relationship State 的当前/历史查询。

FR-008、FR-010、FR-011、FR-012 以及全部 P1-P3 均不是 Micro 通过门槛。把它们标为 deferred 不等于删除 PRD 要求。
