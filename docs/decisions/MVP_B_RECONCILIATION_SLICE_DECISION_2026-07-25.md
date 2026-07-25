# MVP-B Reconciliation 与 Semantic Diff 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-B-RECONCILIATION-001` |
| Date | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-A-HARDENING-001`（已 verified，recovery tag `a6-hardening-rp-20260725`） |
| Current Slice | `SLICE-MVP-B-RECONCILIATION-001` |

## 1. 决定内容

选择 MVP-B 的 B4 Reconciliation 与 Semantic Diff 作为下一条窄切片，在一个固定合成 profile 上验证三类对账能力与一个只读差异视图：

1. 写后校验与日常增量对账（FR-105）：失败队列条目、stale 视图、孤儿引用、未消费 ChangeSet 的检测与报告。
2. 周期深度对账（FR-105）：从 Canonical 重建核心投影（person_card / relationship_timeline / current_state）并与现有 L2 投影比较，输出 match / mismatch 报告。
3. Semantic Diff（FR-106）：同一对象在两个 revision 之间的语义差异只读呈现。

## 2. 产品依据

- PRD §10.5：对账分级（写后校验、日常增量对账、周期深度对账、重大升级对账）。
- PRD §12：用户可以查看两个时间点之间的 Semantic Diff；撤销保留全部历史。
- PRD §18.6：Semantic Diff 覆盖当前状态、关系角色与联系状态、用户观点或 Hypothesis 的变化。
- PRD §20 FR-105：增量对账、失败队列和 stale 检测；FR-106：Semantic Diff。
- PRD §22（948 行）：深度对账采用增量/分区处理，不要求每次整图重算。
- PRD §25.3 邻近（1165 行）：对账发现问题先隔离、生成报告；除已授权机械修复外不静默改写语义。

## 3. 切片范围

- 单一固定合成 profile（复用 rev_010 demo 基线与受控注入），对账检测四类增量发现与投影重建比较。
- 对账发现仅隔离并生成报告；任何修复性写入仍必须经 ChangeSet（本切片不实现自动修复）。
- Semantic Diff 为 Derived 只读呈现：字段级 before/after、变更类型（create/modify/no_change）、对象与 revision 引用；不持久化为事实、不作证据。
- 深度对账按投影分区逐一执行，不要求整图重算。

## 4. 非目标

- 多设备同步、跨设备冲突合并（Year 2，FR-301）。
- 自动静默修复、机械修复执行器、后台调度器、真实定时任务。
- 重大升级对账的完整回归编排（模型/Schema/索引迁移）。
- 性能 SLO、通用图 diff 算法、任意对象集合的 diff UI。
- 真实个人数据、LLM、连接器。

## 5. 不变量

- 对账发现不得静默改写 Canonical 语义；发现仅隔离 + 报告。
- Semantic Diff 是 Derived，不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。
- 未确认的 candidate 不得因对账而成为事实。
- trust、closeness、人格判断不因对账或 diff 被自动修改。
- 固定 synthetic profile 外输入 fail closed 且无写入。
- 撤销历史不因对账被擦除；补偿 revision 全部保留。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6/S7 的 B4 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 B4 业务代码。
