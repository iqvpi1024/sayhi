# C2 Hypothesis Lifecycle 切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `C2-CONTRACT-REVIEW-001` |
| 日期 | 2026-07-26 |
| 合同 | `SPEC-C2-HYPOTHESIS-001` v0.1 |
| 结论 | `approved_for_traceability` |

## 复核项

| 检查 | 结果 |
|---|---|
| 目标/非目标与 DEC-MVP-C-HYPOTHESIS-001 一致 | pass |
| 字段语义完整（Hypothesis、EvidenceRef、HypothesisView） | pass |
| 状态机与禁止转换（retired 非删除；无自动迁移；restore 必须用户确认） | pass |
| 不变量可证（C2-INV-001..007 均有正反场景） | pass |
| 时间/证据语义（不回填、Evidence Ref 必须指向真实 Source、Derived 非证据） | pass |
| 失败与降级（未确认操作/非法迁移/非法引用/upgrade_to_fact 全部显式 rejected 且无写入） | pass |
| 验收场景可执行（C2-001..010 Given/When/Then） | pass |
| 未修改基础 SPEC、未引入自动生成/自动迁移/评分算法/真实数据 | pass |

## 发现

无 blocking 发现。已记录限制：本切片不实现识灵自动提出 Hypothesis（自动生成属非目标）；display_tone 收缩为由 status 决定的纯函数，不建设完整呈现层改版；外部验证规则引擎后置。

## 下一步

建立矩阵 §4.16（PRD §20.2 FR-201、§26 Case G -> SPEC-C2-HYPOTHESIS-001 -> C2-001..010），随后进入 ADR 与 suite 物化。
