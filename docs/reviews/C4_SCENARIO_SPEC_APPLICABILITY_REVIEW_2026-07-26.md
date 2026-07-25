# C4 Scenario & Action SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `C4-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-26 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-C-SCENARIO-001` |
| 切片 | `SLICE-MVP-C-SCENARIO-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | C4 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | `predicted` 是合法 assertion_kind 且与事实型分离；scenario 以 assertion 持久化的 C1 先例；commitment 是核心对象 | 情景三元组 + 可执行性约束字段合同；feasibility 确定性纯函数定义；`not_professional_advice` 呈现合同；S1 未定义情景生命周期与行动跟进 |
| S2 Bitemporal & Evidence v0.5 | `partial` | revision 历史保留；Derived 不作证据；固定 synthetic clock | FollowUp 状态变化产生新 revision 且历史保留的验收；`missed` 作为 Derived 视图（clock + due + status）不写入 Canonical 的证明 |
| S3 ChangeSet & Consistency v0.4 | `partial` | 用户确认语义；规范写入入口 | 创建情景/选择/创建跟进/完成跟进四入口必须用户确认的证明；自动迁移计数恒 0；upgrade-to-observed 拒绝合同 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | C4 exact scenario 集、确定性 feasibility oracle、未确认操作拒绝注入、missed 视图 oracle |

S4、S5、S7、S8、S9 不进入 C4：不建设权限 runtime、候选生成策略、存储/导出扩展、MCP 或导入迁移。

## 发现与处理

1. S1 给了 `predicted` 的合法性与边界，但没有情景三元组、可执行性约束或行动跟进的对象级合同；PRD §20.3 FR-204/206 要求这两类能力，路线图要求"情景不是预测事实；不替代专业意见"。
2. C1 已验证单情景创建/比较（`assertion_kind=predicted` 持久化）；C4 复用该持久化模式但不重建 C1 闭环，扩展为完整生命周期（创建→选择→跟进→missed 视图）。
3. S2/S3 没有"跟进动作"的现成合同；C4 把跟进收缩为 Canonical commitment 对象 + payload 内嵌 revision_history（C2 先例），`missed` 收缩为 Derived 纯函数视图（B4 due-status 先例的确定性计算）。
4. 可执行性评估必须是确定性纯函数（防"评分算法"蔓延）；专业建议禁令落为呈现层恒真标记与无建议文案字段。

处理：新增 C4 slice contract，闭合字段、状态机、不变量、失败与可执行验收。不得修改基础 SPEC，不得引入自动生成、评分算法、建议文案、自动跟进或真实数据。

## 下游影响

在 C4 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 C4 Scenario & Action slice contract，绑定情景字段、feasibility 纯函数、选择与跟进入口、missed Derived 视图、专业建议禁令、用户确认门禁与 fail-closed 边界后进入 Traceability。
