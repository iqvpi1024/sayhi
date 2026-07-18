# MVP-B Shiling 切片产品决定

## 文档信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-B-SHILING-001` |
| Date | 2026-07-18 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` (completed) |
| Current Slice | `SLICE-MVP-B-SHILING-001` |

## 1. 决定内容

选择 MVP-B Shiling 为下一切片，具体范围限定为 B1 Candidate Review 的窄子集：

- FR-101：候选聚合与去重
- FR-102：Review Budget 和分级通知机制
- FR-107：低风险机械变更的事后可撤销策略

## 2. 目标

让识灵能够：
1. 聚合多个来源的候选（不重复提问同一语义变更）
2. 按价值评分排序候选
3. 控制用户审查频率（Review Budget）
4. 对低风险变更采用事后可撤销策略

## 3. 非目标（明确后置）

- 通用 Episode 聚类与分层摘要（B2）
- Commitment 提取与提醒（B3）
- 增量对账与 Semantic Diff（B4）
- 多语言对照（B5）
- 影子迁移（B6）
- 实体合并拆分（A3）
- 权限 runtime（A4）
- 决策引擎（C1）
- 连接器、同步、多设备

## 4. 必须重开的 Deferred 问题

- `DQ-002`：识灵默认自动处理范围（进入 B1 前必须裁决）
- `DQ-011`：Review Budget 具体数值和策略（进入 B1 前必须裁决）

## 5. 依赖

- Micro-MVP 核心完成（49/49 passed）
- MVP-A Answer Safety 完成（35/35 passed）
- Phase 4 CLI 完成（CLI-001..006）

## 6. 授权边界

本决定只授权：
1. SPEC applicability review（S1/S2/S3/S6/S7 适用性复核）
2. Traceability 更新
3. 不开始业务代码、ADR、suite 物化或 Implementation Plan

## 7. 完成定义

- B1 的 exact contract 定义完成
- 候选聚合、Review Budget、事后可撤销的验收场景物化
- SPEC applicability review 通过
- 不提前实现 B2-B6 或 A3-A6 能力

---

> 本决定由产品负责人授权，技术代理不得自行扩大范围。
