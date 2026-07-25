# A6 MVP-A 硬化与本地 Alpha 切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `A6-CONTRACT-REVIEW-001` |
| Contract | `SPEC-A6-HARDENING-001` v0.1 |
| 日期 | 2026-07-25 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| 产品决定 | `DEC-MVP-A-HARDENING-001` |
| 结论 | `approved_for_traceability` |

## 结论依据

- 12 个集成场景（`A6-001..012`）与 FR 的映射逐条对照 `DEC-MVP-A-HARDENING-001` §2 表格，无增删改；场景只重述已 Approved 的 SPEC 行为（`A6-INV-006`），未补写新产品规则。
- 集成证明缺口闭合：§2 明确 21 个场景在同一 Reference Profile `a6_mvp_a_reference_v1` 上顺序执行、共享同一系统状态；§3 规则 2 固定执行顺序与失败即组失败；`A6-INV-001` 显式声明集成执行不削弱、不替代已 verified suite 的独立证据。这正是 A1-A5 独立 fixture 证明所缺的协同证据。
- Reference Profile 具体化边界正确分层：环境描述符的具体值按 S6 IQ-014 留待 A6 的 ADR 步骤记录（合同 §9.1 不预选），SLO 记录边界与 profile 绑定、不外推（`A6-INV-002`、`A6-021`），并显式排除 MVP-A 不适用的冷来源搜索 SLO、注明撤销可用性已由 `A6-006` 覆盖。
- 错误恢复壳层表面固定预期完整覆盖 DEC §3 列出的五项（干净启动、数据库损坏、目录不可写、发布失败回滚、视图 unavailable），且每项复用 S3/A1 已验证语义、不新增恢复语义（§6、`A6-INV-004`、`A6-INV-008`）。
- 本地 Alpha 可解释性以文档 + 可执行 smoke 闭合（`A6-018..020`），卸载默认不删用户数据、删除独立确认（`A6-INV-005`），合成/真实路径分离可验证（`A6-INV-003`）。
- FR-003 生成侧限制处理得当：§1.1 显式记录 Entity/Assertion 候选生成无已批准 executable 语义，`A6-002` 限定为"候选不成事实"不变量证明，未静默补写候选生成规则；该限制移交后续切片决策，不阻塞本切片。
- 非目标与 DEC §4 一致：MVP-B、D2/D3 发布动作、真实数据、新策略语义均被排除；Alpha 版本号与发布动作留待 A6 Gate Review 后的发布门禁单独决定。

## 发现

无 A6 blocking 产品歧义。两点范围说明已写入合同：固定 SLO 检查项限 MVP-A 已存在能力面对应的四项（§2 附注）；三个 Core View 固定为 `person_card` + `relationship_timeline` + `current_state`（§2），`A6-005` 允许"更新或显式失效"两种合法结果、禁止返回旧值冒充 fresh（与 PRD §21.2 一致）。

## 下一步

建立 FR-001..012 的 A6 Traceability（矩阵新增切片小节），随后进入 A6 的 ADR 步骤（Reference Profile 环境描述符 + 开发启动/evaluator package 决策），之后才物化 executable suite。合同 Approved 前不得物化 fixture/oracle/runner 或编写业务代码。
