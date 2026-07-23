# A5 自然语言审查与最小可用应用壳 SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `A5-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-24 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-APP-SHELL-001` |
| 切片 | `SLICE-MVP-A-APP-SHELL-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | A5 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `pass` | 现有对象类型与 Policy Subject 字段；A5 不引入新对象类型 | 无 |
| S3 ChangeSet & Consistency v0.4 | `partial` | ChangeSet 状态机、原子发布、撤销补偿、审计回执 | 显式合同：应用壳每个写操作必经 ChangeSet，壳不存在绕过审查的写入路径；撤销后全部 Core View 恢复一致 |
| S5 Shiling Policy v0.4 | `partial` | Candidate Envelope 字段语义、Review Priority；候选生成语义不改 | 自然语言审查呈现合同：候选与影响预览的自然语言形状、证据引用呈现、不暴露 ChangeSet JSON 的普通用户路径；呈现为 Derived，不改变底层语义 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | A5 旅程场景集、每步预期结果、current result 绑定 |
| S7 Storage, Index & Portability v0.4 | `partial` | 数据目录由用户拥有；SQLite schema 与导出格式不变 | 壳的本地数据目录约定与单一入口可达性；壳不引入新存储格式 |

S2、S4、S8、S9 不进入 A5：本切片不引入新双时态语义、新权限判决、MCP、真实导入或迁移。

## 发现与处理

1. S5 定义了 Candidate Envelope 的语义字段，但没有定义面向普通用户的自然语言呈现形状——摘要文本、证据引用、影响预览的具体呈现合同需要切片合同闭合，且必须声明呈现为 Derived、不反向成为语义证据。
2. S3 的 ChangeSet 语义完整，但"壳层无绕过写入"需要显式不变量，防止实现为求便捷在壳层直接写 Canonical 或 Projection。
3. 现有 CLI（`DEC-PHASE8-UI-DEPLOY-001` 已决定 CLI 形态、无 Web/桌面 UI）已覆盖部分命令，但缺少引导式旅程、回执、历史与影响预览命令；A5 的壳形态 ADR 必须与 DEC-PHASE8-UI-DEPLOY-001 保持一致（stdlib CLI，无新依赖）。
4. 旅程步骤的确切顺序与每步可观察结果（revision 前进、视图 freshness、回执 ID）需要可执行验收定义。

处理：新增 A5 slice contract，闭合固定合成旅程、壳命令到核心能力的映射、自然语言呈现形状、零绕过不变量、撤销一致性与可执行验收。该合同不得修改基础 SPEC，不得引入 Web/桌面 UI、云账户、多租户、在线依赖或真实数据。

## 下游影响

在 A5 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 A5 app shell slice contract，并将旅程步骤、壳命令映射、自然语言呈现形状、零绕过与验收场景绑定后再进入 Traceability。