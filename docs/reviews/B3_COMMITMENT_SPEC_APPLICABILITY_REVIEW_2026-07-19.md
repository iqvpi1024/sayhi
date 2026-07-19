# B3 Commitment SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `B3-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-19 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-B-COMMITMENT-001` |
| 切片 | `SLICE-MVP-B-COMMITMENT-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | B3 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Commitment 是 Canonical；Obligation 映射；关系变化不自动取消 | 最小字段、生命周期与取消原因 |
| S2 Bitemporal & Evidence v0.5 | `partial` | valid/recorded/source time 与直接 Source locator | due time、固定 clock 和 overdue 的 Derived 时间语义 |
| S3 ChangeSet & Consistency v0.4 | `partial` | proposal/approval/publish/revert、补偿 revision、L2/L3 stale | Commitment 状态变更 impact 与 reminder/due-status 失效边界 |
| S5 Shiling Policy v0.4 | `partial` | Commitment 只能先成 candidate；关系变化不得自动改变它 | fixed candidate 及无自动处理/无模型路径 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | B3 exact scenario 集、failure injection、current result 绑定 |
| S7 Storage, Index & Portability v0.3 | `partial` | Canonical/Derived 分层、删除/重建、revision 语义 | Commitment 与 Derived due-status 最小持久表示 |

S4、S8、S9 不进入 B3：本切片不建设权限/MCP runtime、真实导入、迁移、连接器或外部提醒通道。

## 发现与处理

1. S1 与 S5 只定义 Commitment 的边界，未定义可执行 status 枚举、取消原因或 due-status。
2. S3 可约束 Canonical 原子发布和补偿，但没有 Commitment 对 reminder/due-status 的明确影响合同。
3. PRD 的“提醒”不等于通知系统；`DEC-MVP-B-COMMITMENT-001` 已将本切片收缩为固定 clock 下的 Derived due-status。

处理：新增 B3 slice contract，闭合上述字段、状态机、不变量、失败与可执行验收。该合同不得修改基础 SPEC 或引入自动提醒、日历、网络、模型、真实数据。

## 下游影响

在 B3 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 B3 Commitment slice contract，并将每个字段、状态转换、Derived boundary 与验收场景绑定后再进入 Traceability。
