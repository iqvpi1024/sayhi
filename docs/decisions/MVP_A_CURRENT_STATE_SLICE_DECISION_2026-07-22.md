# MVP-A current_state Core View 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-A-CURRENT-STATE-001` |
| Date | 2026-07-22 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-B-COMMITMENT-001`（已发布 recovery point `b3-commitment-rp-20260722`） |
| Current Slice | `SLICE-MVP-A-CURRENT-STATE-001` |

## 1. 决定内容

选择 MVP-A 的 A2 作为下一条窄切片：把 PRD §24.2 的 `current_state` 从 Micro 两个 Core View 的受控读取结果提升为第三个 MVP-A Core View，仅在一个固定合成 Canonical snapshot 上验证其读取、发布后更新/失效与 stale 检测。

顺序调整理由：路线图允许切片顺序按风险调整；`B4-RECONCILIATION-DIFF` 依赖 A2 与 B3，B3 已 verified，先完成 A2 可解锁 MVP-B 后续切片。

## 2. 产品依据

- PRD §24.2：MVP-A 必须有三个 Core View：人物卡、关系时间线、当前状态；前两者已由 Micro 链路验证。
- PRD §20 FR-006：发布后更新或失效 Core View。
- PRD §20 FR-008：事实型回答使用六态认知协议（A1 已验证，本切片复用不重复实现）。
- PRD §20 FR-105 的 MVP-A 切片：Core View 的 stale 检测；增量对账与失败队列完整化属于 B4。
- PRD §9-§12：Current State 不覆盖 Historical State；Derived View 不反向成为事实证据；Core View 确认后保持一致或显式标记 stale。

## 3. 切片范围

- 单一固定合成 profile 的 Canonical snapshot：Entity、Relationship、RelationshipState、Assertion 与既有 Source。
- `current_state` Core View 只读投影：当前有效的对象集合、各自 `object_revision`、视图 `data_revision/view_revision` 与 `freshness_status`。
- Canonical 变更（经既有 ChangeSet 边界）后视图显式 stale；重建后与从 Canonical 直接计算的结果等价。
- 投影删除后仅可从 Canonical 与 Source 等价重建；`current_state` 内容不得作为 Evidence Ref、Assertion input 或 ChangeSet trigger。

## 4. 非目标

- 通用查询语言、自由文本检索、UI/应用壳、权限/舱室 runtime（属 A4）、实体合并（属 A3）。
- Commitment/提醒扩展、L3 画像、六态回答重实现、B4 的增量对账/失败队列/Semantic Diff。
- 多设备、同步、连接器、真实个人数据。

## 5. 不变量

- `current_state` 是 Derived；删除后可从 Canonical 等价重建，不得反向写入 Canonical。
- Historical State 永不被 Current 覆盖；视图只呈现当前有效区间。
- 视图 revision 与 Canonical `data_revision` 不对齐时必须 stale/unavailable，不得伪装 current。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6/S7 的 A2 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 A2 业务代码。
