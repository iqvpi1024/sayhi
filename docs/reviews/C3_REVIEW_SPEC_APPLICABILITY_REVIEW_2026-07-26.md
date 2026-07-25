# C3 Review & Calibration SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `C3-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-26 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-C-REVIEW-001` |
| 切片 | `SLICE-MVP-C-REVIEW-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | C3 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Derived 层证据边界（Derived 不作事实证据）；Episode/Commitment/Decision/Hypothesis 已是核心对象，指标来源对象语义明确 | ReviewReport 与 PhaseComparison 的 Derived 对象合同（字段、指标集定义、半开窗口语义、`derived_only=true`）；S1 未定义周期性复盘与跨阶段比较对象 |
| S2 Bitemporal & Evidence v0.5 | `partial` | revision 历史保留不覆盖；stale/freshness 语义（B2 已验证 summary projection 失效机制可复用）；Derived 不作证据 | 报告 fresh->stale 的判定合同（底层 Canonical digest 变化后相关窗口报告 stale）；同窗口历史报告版本保留的验收方式；重建等价性证明 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | C3 exact scenario 集、固定窗口确定性计数与 delta oracle、不合法比较 fail-closed 且无写入的断言方式 |

S3 不进入 C3：本切片无 Canonical 写入路径，报告/比较生成只写 Derived 层（B2/B5/B6 先例：Derived 写入不经 ChangeSet）；决策与决定一致，若后续发现需要 Canonical 写入必须重开 review。S4、S5、S7、S8、S9 不进入 C3：不建设权限 runtime、候选生成策略、存储/导出扩展、MCP 或导入迁移。

## 发现与处理

1. S1 定义了核心对象与 Derived 证据边界，但没有周期性复盘报告或跨阶段比较对象；PRD §20.3 FR-203/FR-205 要求这两类能力，PRD §12 L3 与 §16.2 要求其为 Derived 且底层变化后失效。
2. S2 给了 stale 语义与历史保留，B2 切片已在 projection 层验证同类机制；C3 需要把它落到"按窗口索引的报告"上，并证明同一窗口历史版本不覆盖、重建等价。
3. 阶段可比性约束（同一指标集才可比、窗口必须同类型同长度半开区间）来自 PRD §20.3 FR-205 与路线图约束，基础 SPEC 无此合同；切片把不合法比较收缩为 fail closed 且无写入。
4. 确定性计数（记录天数、Episode 数、Commitment 完成/取消/按期闭环、决策复盘完成、Hypothesis 状态分布）为纯函数；切片禁止因果、趋势、人格推断与任何 Canonical 修改。

处理：新增 C3 slice contract，闭合对象字段、指标集、窗口语义、freshness、历史保留、重建等价、可比性与 fail-closed 边界。不得修改基础 SPEC，不得引入自然语言生成、因果推断、自动 Hypothesis 状态变化或真实数据。

## 下游影响

在 C3 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 C3 Review & Calibration slice contract，绑定 Derived 对象字段、指标集定义、半开窗口、freshness/stale、历史版本保留、重建等价、阶段可比性与 fail-closed 边界后进入 Traceability。
