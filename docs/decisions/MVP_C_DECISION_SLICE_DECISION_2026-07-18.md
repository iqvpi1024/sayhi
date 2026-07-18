# MVP-C 决策与成长切片产品决定

## 文档信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-DECISION-001` |
| Date | 2026-07-18 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-B-SHILING-001` (completed) |
| Current Slice | `SLICE-MVP-C-DECISION-001` |

## 1. 决定内容

选择 MVP-C 决策与成长为下一切片，具体范围限定为 C1 Decision-Outcome 的窄子集：

- FR-202：Decision、Outcome 和 Calibration 闭环
- FR-204：基准、乐观、悲观情景推演（只限 predicted/fictional，不写入 observed）
- FR-206：可执行性约束和行动跟进

## 2. 目标

让用户能够：
1. 记录一个 Decision（问题、选项、约束、假设、选择）
2. 记录 Decision 的 Outcome（结果、副作用）
3. 进行 Calibration（预测 vs 实际结果对比）
4. 创建情景推演（保持 predicted/fictional，不自动写入 observed）

## 3. 非目标（明确后置）

- Hypothesis 完整生命周期（C2，需要 FR-201）
- 周/月/年度复盘（C3，需要 FR-203/205）
- Context Pack 备份（C5，需要 FR-303）
- MVP 公开发布（C6）
- 健康/法律/财务专业建议
- 自动因果推断
- 多设备同步、连接器、A2A

## 4. 必须重开的 Deferred 问题

- `DQ-006`：Decision 与专业建议边界（进入 C1 前必须裁决）

## 5. 依赖

- Micro-MVP 核心完成（49/49 passed）
- MVP-A Answer Safety 完成（35/35 passed）
- Phase 4 CLI 完成
- Phase 5 B1 Candidate Review 完成（8/8 passed）

## 6. 授权边界

本决定只授权：
1. SPEC applicability review
2. Traceability 更新
3. 不开始业务代码、ADR、suite 物化或 Implementation Plan

## 7. 完成定义

- C1 的 exact contract 定义完成
- Decision/Outcome/Calibration 验收场景物化
- SPEC applicability review 通过
- 不提前实现 C2-C6 或 B2-B6 能力

---

> 本决定由产品负责人授权，技术代理不得自行扩大范围。
