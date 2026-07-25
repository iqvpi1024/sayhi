# B6 Shadow Migration 切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `B6-CONTRACT-REVIEW-001` |
| 日期 | 2026-07-25 |
| 合同 | `SPEC-B6-SHADOW-MIGRATION-001` v0.1 |
| 结论 | `approved_for_traceability` |

## 复核项

| 检查 | 结果 |
|---|---|
| 目标/非目标与 DEC-MVP-B-SHADOW-MIGRATION-001 一致 | pass |
| 字段语义完整（ShadowCopy、DisambiguationCandidate、MergePropagation） | pass |
| 状态机与禁止转换（failed 影子只能 discarded；候选无自动转换） | pass |
| 不变量可证（B6-INV-001..007 均有正反场景） | pass |
| 时间/证据语义（不回填、影子非证据、复用 B4 对账语义） | pass |
| 失败与降级（故障注入显式 failed、零部分写入、mismatch 不静默修复） | pass |
| 验收场景可执行（B6-001..010 Given/When/Then） | pass |
| 未修改基础 SPEC、未引入真实迁移/性能 SLO/真实数据 | pass |

## 发现

无 blocking 发现。已记录限制：压测收缩为确定性计数断言（明确排除 wall-clock SLO）；真实 schema 演进合同与增量实时同步属非目标。

## 下一步

建立矩阵 §4.15（PRD §24.3 -> SPEC-B6-SHADOW-MIGRATION-001 -> B6-001..010），随后进入 ADR 与 suite 物化。
