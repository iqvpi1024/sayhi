# B4 Reconciliation 与 Semantic Diff 切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `B4-CONTRACT-REVIEW-001` |
| Contract | `SPEC-B4-RECONCILIATION-001` v0.1 |
| 日期 | 2026-07-25 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| 产品决定 | `DEC-MVP-B-RECONCILIATION-001` |
| 结论 | `approved_for_traceability` |

## 结论依据

- 10 个场景（`B4-001..010`）与 FR-105/FR-106 的映射逐条对照 `DEC-MVP-B-RECONCILIATION-001` §1，无增删改；场景只重述 PRD §10.5/§12/§18.6/§20 已批准的行为，未补写新产品规则。
- "隔离 + 报告、不静默修复"缺口闭合：`B4-INV-001` 显式声明 `auto_repair_attempted=false` 恒成立，发现处置唯一终态 `quarantined_reported`（§2/§3），这正是 S3 写后校验语义所缺的对账强制行为合同。
- 深度对账边界正确分层：§2/§5 固定按投影分区（person_card / relationship_timeline / current_state）逐一重建比较，不要求整图重算（`B4-INV-003`），与 PRD §22（948 行）一致；mismatch 只报告期望/实际 digest，原投影不被改写（§6）。
- Semantic Diff 边界正确：§2.2 固定为查询时派生、不持久化，`B4-INV-002` 要求 diff 查询前后 Canonical digest 不变，与 S1/S2 的 Derived 不作证据一致；diff 覆盖 PRD §18.6 的当前状态、关系角色与联系状态、Hypothesis 变化（`B4-008/009`）。
- 保护层不变量完整：`B4-INV-005`（trust/closeness/人格不被自动修改）、`B4-INV-006`（撤销历史不擦除）、`B4-INV-004`（未确认 candidate 不成事实）、`B4-INV-007`（profile 外 fail closed）。
- 非目标与 DEC §4 一致：多设备同步、自动修复、调度器、重大升级对账、真实数据均被排除。
- 失败行为明确：对账自身失败返回显式 unavailable 报告壳，不得返回空报告冒充"无发现"（§6）；diff 目标 revision 不存在显式拒绝。

## 发现

无 B4 blocking 产品歧义。两点范围说明已写入合同：增量对账四类发现固定为 failure_queue / stale_view / orphan_reference / unconsumed_changeset（§2.1，对应 PRD §10.5 日常增量对账）；Semantic Diff 的 `change_type` 限 create / modify / no_change 三类（§2.2），删除差异不在本切片（删除/封存语义由 S7 与后续切片覆盖）。

## 下一步

建立 FR-105/FR-106 的 B4 Traceability（矩阵新增切片小节），随后进入 B4 的 ADR 步骤（对账检测实现位置 + 投影重建比较策略），之后才物化 executable suite。合同 Approved 前不得物化 fixture/oracle/runner 或编写业务代码。
