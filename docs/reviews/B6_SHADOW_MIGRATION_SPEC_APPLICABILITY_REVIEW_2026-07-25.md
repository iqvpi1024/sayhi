# B6 Shadow Migration SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `B6-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-25 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-B-SHADOW-MIGRATION-001` |
| 切片 | `SLICE-MVP-B-SHADOW-MIGRATION-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | B6 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Canonical/Derived 分层；实体与引用模型 | 影子副本的对象边界：不是 Canonical、不是证据；消歧候选不是事实 |
| S2 Bitemporal & Evidence v0.5 | `partial` | revision/快照历史语义；历史保留 | 迁移后 bitemporal 历史完整性的验收方式（revision、快照、翻译历史逐条对应） |
| S3 ChangeSet & Consistency v0.4 | `partial` | ChangeSet 唯一写入入口；补偿与撤销保留 | 迁移程序不绕过 ChangeSet 的证明方式；已确认合并的传播计数合同 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | B6 exact scenario 集、故障注入、确定性计数 oracle |
| S7 Storage, Index & Portability v0.3 | `partial` | 投影重建（B4 深度对账可复用）；独立可读 | 影子迁移的副本写入边界、失败无部分写入、迁移后对账分区 |

S4、S5、S8、S9 不进入 B6：不建设权限 runtime、候选生成策略（消歧候选仅固定合成规则）、MCP、真实导入/迁移或连接器。

## 发现与处理

1. 基础 SPEC 没有"影子迁移"对象与状态机；`DEC-MVP-B-SHADOW-MIGRATION-001` 已将影子收缩为非 Canonical 可丢弃副本，迁移失败不得污染原始库。
2. S3 没有"迁移程序写入边界"的可执行证明；B3/A3 的合并传播是单实体尺度，B6 需要成规模确定性计数。
3. 基础 SPEC 没有"压测"合同；本切片将压测收缩为确定性计数断言（条数/批次数），明确排除 wall-clock SLO。

处理：新增 B6 slice contract，闭合上述字段、状态、不变量、失败与可执行验收。不得修改基础 SPEC 或引入真实迁移、真实数据、性能 SLO。

## 下游影响

在 B6 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 B6 Shadow Migration slice contract，并将影子状态机、迁移变换、失败无部分写入、消歧/传播计数与历史保留绑定后再进入 Traceability。
