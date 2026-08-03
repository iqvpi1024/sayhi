# Y2-S4 Slice Contract 复核

| 字段 | 值 |
|---|---|
| Review ID | `Y2S4-CONTRACT-REVIEW-001` |
| Date | 2026-08-03 |
| Contract | `SPEC-Y2S4-CLOUD-MODEL-001` v0.1 |
| 结论 | `approved_for_traceability` |

## 1. 复核范围

核对 slice contract 与 `DEC-Y2-S4-001`、applicability review（`Y2S4-SPEC-APPLICABILITY-001`）、PRDv06 §14.5.3/§17.4/§22.4/§24.5/§25.1 与上游 S1/S2/S3/S4/S5/S6/S7/S8/S9 的一致性。

## 2. 结论

`approved_for_traceability`，理由：

1. applicability 的四个缺口（默认关闭与按舱室授权、红线绝对 deny、外发预览、云端调用审计与离线测试合同）已分别由合同 §2/§3/§5/§6/§7 闭合。
2. 合同采用批内授权原子：任一 Source 未获授权或属红线舱室即整批拒绝且零后端调用；`Y2S4-001/003/004/005/006/007` 提供反向证明，`Y2S4-002` 提供正向证明。
3. 候选复用 Y2-S2 的 propose-only 与整批输出校验；云端模块只写 Ledger `cloud_audit`，不写 Canonical，未扩张到 MCP、账户、真实凭据或真实数据。
4. 10 场景覆盖 6 条不变量；`Y2S4-010` 覆盖确定性、loopback stub、stdlib 与 profile fail closed。
5. 合同把 PRD §17.4 的“授权页面如实显示数据范围”实现为不包含原始正文的 `outbound_preview.data_scope`，可机器断言且不降低保护。

## 3. 条件

- fixture 必须显式声明 `synthetic=true`、`external_data_used=false`。
- 测试网络仅限本机回环；runner 继续全局阻断外部网络；`CloudHttpBackend` 的 loopback override 只能由测试显式传入。
- 审计 Ledger 只记录元数据与拒绝原因，不得写入 Source 正文或真实凭据。
