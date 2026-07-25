# C2 Hypothesis Lifecycle SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `C2-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-26 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-C-HYPOTHESIS-001` |
| 切片 | `SLICE-MVP-C-HYPOTHESIS-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | C2 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Hypothesis 术语边界（与 Assertion 隔离、可反驳）；hypothesis 已是 12 核心对象之一 | Hypothesis 生命周期字段（valid_scope、evidence_for/evidence_against、status）与状态机；S1 明确把完整 Hypothesis 工作流列为非目标 |
| S2 Bitemporal & Evidence v0.5 | `partial` | Evidence Ref 语义（Source+locator+stance）；revision 历史保留；Derived 不作证据 | 反例（stance=contradicts）进入 evidence_against 的验收方式；状态迁移产生新 revision 且历史不删除的证明 |
| S3 ChangeSet & Consistency v0.4 | `partial` | ChangeSet 唯一规范写入入口；用户确认语义 | 状态迁移/证据追加必须经用户确认 ChangeSet 的证明；自动迁移计数恒 0；纠正性回退（weakened->active）与 retired 终态合同 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | C2 exact scenario 集、未确认操作拒绝注入、确定性计数 oracle |

S4、S5、S7、S8、S9 不进入 C2：不建设权限 runtime、候选生成策略、存储/导出扩展、MCP 或导入迁移。

## 发现与处理

1. S1 只给了 Hypothesis 最小边界（§4 最小边界层），明确不授权完整流程；`DEC-MVP-C-HYPOTHESIS-001` 已把生命周期收缩为"用户确认的显式状态机 + 证据追加"，不包含自动生成或自动迁移。
2. S2 定义了 Evidence Ref 与 stance，但没有 evidence_for/evidence_against 双清单的对象级合同；PRD §26 Case G 要求反例进入 evidence_against 且历史不删除。
3. S3 没有"状态迁移必须用户确认"的 Hypothesis 专项证明；PRD §5.2 第 7 条禁止自动升格，PRD §23 要求禁止自动升格与认知隔离。
4. 呈现语气（确定性文案禁令）来自 PRD §26 Case G，基础 SPEC 无此合同；切片把 `display_tone` 收缩为由 status 决定的纯函数。

处理：新增 C2 slice contract，闭合字段、状态机、不变量、失败与可执行验收。不得修改基础 SPEC，不得引入自动生成、自动迁移、评分算法或真实数据。

## 下游影响

在 C2 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 C2 Hypothesis Lifecycle slice contract，绑定状态机、证据双清单、呈现语气、用户确认门禁、历史保留与 fail-closed 边界后进入 Traceability。
