# B4 Reconciliation 与 Semantic Diff SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `B4-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-25 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-B-RECONCILIATION-001` |
| 切片 | `SLICE-MVP-B-RECONCILIATION-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | B4 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Canonical/Derived 分层；Core View 白名单（person_card、relationship_timeline、current_state） | 对账报告与 Semantic Diff 的对象边界：它们不是 Canonical 对象，是只读派生产物 |
| S2 Bitemporal & Evidence v0.5 | `partial` | revision、valid/recorded 时间语义；历史保留 | 两个 revision 间 diff 的时间语义（diff 是查询时派生，不回填 recorded_at） |
| S3 ChangeSet & Consistency v0.4 | `partial` | 写后校验、L1/L2 revision 一致性、补偿 revision、stale 语义 | 增量对账四类发现（失败队列、stale 视图、孤儿引用、未消费 ChangeSet）的检测合同与"隔离+报告、不静默修复"行为 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | B4 exact scenario 集、failure injection、current result 绑定 |
| S7 Storage, Index & Portability v0.3 | `partial` | 投影重建、revision 语义、Canonical 独立可读 | 深度对账的投影分区重建比较合同；Semantic Diff 不持久化 |

S4、S5、S8、S9 不进入 B4：本切片不建设权限 runtime、候选生成、MCP、真实导入/迁移或连接器。

## 发现与处理

1. S3 定义了写后校验与 stale 语义，但没有"增量对账"的可执行发现类型枚举、报告形状或"先隔离不静默修复"的强制行为合同。
2. S7 定义了投影可重建，但没有"重建后与现有投影比较"的深度对账验收方式与分区边界。
3. S1/S2 没有 Semantic Diff 的对象模型；PRD §18.6 只定义用户可比较的内容范围。`DEC-MVP-B-RECONCILIATION-001` 已将 diff 收缩为查询时派生的只读呈现，不进入 Canonical。

处理：新增 B4 slice contract，闭合上述字段、状态、不变量、失败与可执行验收。该合同不得修改基础 SPEC 或引入自动修复、调度器、多设备同步、真实数据。

## 下游影响

在 B4 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 B4 Reconciliation slice contract，并将每个发现类型、报告字段、diff 呈现形状、失败与降级行为绑定后再进入 Traceability。
