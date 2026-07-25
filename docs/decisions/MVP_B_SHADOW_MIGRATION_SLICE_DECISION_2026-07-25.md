# MVP-B Shadow Migration 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-B-SHADOW-MIGRATION-001` |
| Date | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-B-MULTILINGUAL-001`（已 verified，recovery tag `b5-multilingual-rp-20260725`） |
| Current Slice | `SLICE-MVP-B-SHADOW-MIGRATION-001` |

## 1. 决定内容

选择 MVP-B 的 B6 Shadow Migration 作为下一条窄切片（PRD §24.3 "匿名化/合成复杂数据影子迁移，压测消歧与传播"），在一个固定合成复杂 profile 上验证两类能力：

1. 影子迁移：把固定合成复杂 profile（Source、Canonical、revision 历史、投影、翻译对照、ChangeSet 草稿）经一次模拟 v1->v2 迁移写入影子副本，用深度对账证明影子与期望一致、原始库零改动；迁移中途失败时原始库不受任何部分写入。
2. 压测消歧与传播：在成规模的合成相似实体集上，消歧候选生成是确定性的、未经确认绝不自动合并；一次已确认合并的引用传播计数确定且历史全部保留；大批量输入按确定性批次处理，结果计数可复现。

## 2. 产品依据

- PRD §24.3（1100 行）：匿名化/合成复杂数据影子迁移，压测消歧与传播。
- PRD §6（84 行）：系统停止维护后原始材料仍可独立读取与迁移。
- PRD §10.5（444 行）：重大升级对账——迁移版本变更后执行完整回归。
- PRD §13.2（452 行）：迁移程序不能绕过 ChangeSet 直接修改 Canonical。
- PRD §15（239 行）：可迁移性是产品能力。

## 3. 切片范围

- 单一固定合成 profile `b6_shadow_migration_v1`：合成复杂数据（多实体相似名、多 revision 历史、翻译对照、投影），全部显式合成。
- 影子迁移只写影子副本；原始库只读；迁移后深度对账（复用 B4 能力）给出逐分区 match/mismatch。
- 迁移失败注入：显式 failed 状态 + 原始库零部分写入 + 影子可丢弃。
- 消歧压测：N 个合成相似实体的候选对计数确定；未确认候选不因压力成为事实；已确认合并的传播计数确定。
- 所有计数断言为确定性计数（条数/批次数），不做 wall-clock 性能 SLO。

## 4. 非目标

- 真实历史数据迁移、真实连接器、真实个人数据。
- wall-clock 性能 SLO、并发迁移、增量实时同步。
- 多设备、自动消歧合并、LLM 消歧。
- 真实 schema 演进合同（本切片为模拟 v1->v2 变换）。

## 5. 不变量

- 原始库在任何影子迁移（成功或失败）后逐字节语义不变。
- 迁移程序不绕过 ChangeSet 修改 Canonical；影子副本不是 Canonical 证据。
- 未确认的消歧候选不因压力或迁移自动升级为事实或自动合并。
- 迁移与传播保留全部 bitemporal 历史（revision、快照、翻译历史、撤销记录）。
- 压测结果计数确定性可复现；固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6/S7 的 B6 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 B6 业务代码。
