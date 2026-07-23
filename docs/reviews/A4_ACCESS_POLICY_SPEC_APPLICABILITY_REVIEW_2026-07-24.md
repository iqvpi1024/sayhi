# A4 查询层权限与舱室强制执行 SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `A4-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-24 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-ACCESS-POLICY-001` |
| 切片 | `SLICE-MVP-A-ACCESS-POLICY-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | A4 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | 对象的 `sensitivity`/`compartments`/`owner_ref` 等 Policy Subject 字段归属 | 本切片固定合成对象集合与其策略标注的具体值 |
| S3 ChangeSet & Consistency v0.4 | `partial` | 权限标签修改必须经 ChangeSet；Derived 不作证 | 显式合同：查询层判决是请求时 Derived，绝不产生 Canonical revision 或写入 |
| S4 Privacy & Access Policy v0.4 | `partial` | AccessRequest/PolicyDecision 字段语义；`allow/deny/allow_with_redaction`；多舱室最严格交集（PAP-INV-002、§12 `IQ-013` 裁决）；非泄露拒绝（PAP-INV-005）；policy engine 不可用 fail closed（§14） | 固定合成 profile 的调用者/策略/对象/查询集；字段 allow 交集 deny 并集的可执行判定；拒绝响应的侧信道边界；时间约束（Grant 有效期/请求时刻）求值规则 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | A4 exact scenario 集、泄漏探针、current result 绑定 |

S2、S5、S7、S8、S9 不进入 A4：本切片不引入新双时态语义、新的识灵候选生成、新存储格式、MCP、真实导入或迁移。

## 发现与处理

1. S4 已定义判决语义与冲突规则，但没有固定合成调用者/策略/对象/查询的可执行集合——哪些字段被裁剪、拒绝响应的确切形状需要切片合同闭合。
2. S4 的 `allow_with_redaction` 与本切片"少回答"的关系需要明确：A4 的 allowed 响应只允许返回过滤后字段集，拒绝时仅返回非泄露原因码。
3. 时间约束（Grant 有效期、请求时刻）在固定 clock 下的求值需要显式合同。
4. 判决不产生 Canonical revision 需要与 S3 显式绑定，防止实现借判决写入审计对象以外的任何 Canonical 状态。

处理：新增 A4 slice contract，闭合固定 profile、判决输入/输出形状、交集/并集规则、拒绝非泄露边界、时间求值、零写入与可执行验收。该合同不得修改基础 SPEC，不得引入多用户、Grant 管理 UI、外部 Agent runtime 或真实数据。

## 下游影响

在 A4 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 A4 access policy slice contract，并将判决形状、交集规则、非泄露边界、时间求值与验收场景绑定后再进入 Traceability。
