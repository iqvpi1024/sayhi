# MVP-A 实体合并候选与拆分回滚切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-A-ENTITY-MERGE-001` |
| Date | 2026-07-24 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-A-CURRENT-STATE-001`（已发布 recovery point `a2-current-state-rp-20260722`） |
| Current Slice | `SLICE-MVP-A-ENTITY-MERGE-001`（A3） |

## 1. 决定内容

选择 MVP-A 的 A3 作为下一条窄切片：只证明两个固定合成 Person Entity 的 merge proposal、用户确认、引用重定向（Relationship/State/Assertion 指向合并后实体）与 split compensation（拆分回滚恢复原始引用），全程经既有 ChangeSet 原子边界。

顺序理由：按路线图 MVP-A 顺序 A1→A2→A3；A1、A2 均已 verified；A3 是 A4（权限查询层）之前的最后一个核心语义行为，且不依赖 B4。

## 2. 产品依据

- PRD §20 FR-011：提供实体合并候选和拆分回滚。
- PRD §13（识灵流水线）：合并建议 → 合并发布 → 可拆分回滚；人物实体默认不自动合并。
- PRD §10.2：`proposals` 包含合并、拆分提案，一切规范写入经 ChangeSet。
- PRD §14：Critical 级含人物误合并，需立即提示。
- PRD §26 验收场景 5：人物合并与拆分。
- PRD §12：Historical State 不被覆盖；撤销与审计保留完整历史。

## 3. 切片范围

- 单一固定合成 profile：两个 Person Entity、各自 Relationship/RelationshipState/Assertion 与既有 Source。
- Merge proposal 作为 ChangeSet 提出；用户确认后原子发布：目标实体保留，来源实体标记 `merged_into` 并保留全部历史，所有 Canonical 引用重定向。
- Split compensation：用户发起拆分 ChangeSet，恢复两个实体的原始引用与活跃状态；合并/拆分历史在审计中完整可见。
- Core View（人物卡、关系时间线、current_state）在合并发布后显式 stale 或重建一致。

## 4. 非目标

- 自动人物合并、模糊身份匹配/消歧算法、合并候选自动评分（候选生成属识灵能力，本切片只用固定合成 proposal 输入）。
- 真实联系人导入、连接器、权限/舱室 runtime（A4）、UI/应用壳（A5）。
- 非 Person 实体的合并、批量合并、跨 profile 合并。

## 5. 不变量

- 合并与拆分都是规范写入，必须经 ChangeSet 原子发布；无部分应用状态。
- 被合并实体的历史（Source、Assertion、区间）永不删除或覆盖。
- 拆分后引用恢复到合并前指向；合并前历史保持可审计。
- trust、closeness、人格判断不因合并/拆分被自动修改。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6 的 A3 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 A3 业务代码。
