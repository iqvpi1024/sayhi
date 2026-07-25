# B5 Multilingual 原文与翻译对照 SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `B5-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-25 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-B-MULTILINGUAL-001` |
| 切片 | `SLICE-MVP-B-MULTILINGUAL-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | B5 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Source Vault 与 Canonical/Derived 分层；对象边界 | 翻译对照记录的对象边界：它不是 Canonical 对象、不是 Source 原文，是关联 source_ref 的派生对照记录 |
| S2 Bitemporal & Evidence v0.5 | `partial` | revision、recorded 时间语义；历史保留；Evidence Ref 解析 | 翻译修订的 revision 语义（翻译历史保留、原文不变）；Evidence Ref 永远解析到原文的强制合同 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | B5 exact scenario 集与 current result 绑定 |
| S7 Storage, Index & Portability v0.3 | `partial` | Source Vault append receipt + content hash；独立可读 | 翻译对照记录的存储形状与"不进入 Evidence Ref 解析链"的存储层保证 |

S3、S4、S5、S8、S9 不进入 B5：本切片不建设 ChangeSet 业务写入（翻译修订走本切片自己的窄追加路径）、权限 runtime、候选生成、MCP、真实导入/迁移或连接器。

## 发现与处理

1. S1/S2 没有"翻译对照"对象模型；PRD §21.5 只给出原则（分离、不得覆盖）。`DEC-MVP-B-MULTILINGUAL-001` 已将翻译收缩为独立派生对照记录，不进入 Canonical 与 Evidence 解析链。
2. S7 定义了 Source Vault 的 append receipt 与 content hash，但没有"同一 Source 多语言对照"的存储合同与缺失翻译行为。
3. 基础 SPEC 没有"以翻译覆盖原文"的拒绝行为与验收方式。

处理：新增 B5 slice contract，闭合上述字段、状态、不变量、失败与可执行验收。该合同不得修改基础 SPEC 或引入真实翻译引擎、全语言覆盖、真实数据。

## 下游影响

在 B5 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 B5 Multilingual slice contract，并将原文/翻译字段、对照读取形状、覆盖拒绝行为、缺失翻译降级与历史保留绑定后再进入 Traceability。
