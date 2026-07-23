# A4 查询层权限切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `A4-CONTRACT-REVIEW-001` |
| Contract | `SPEC-A4-ACCESS-POLICY-001` v0.1 |
| 结论 | `approved_for_traceability` |

## 结论依据

- AccessRequest/Grant/PolicyDecision 字段形状与 S4 §6.2-§6.4 一致；`allow/deny/allow_with_redaction` 枚举未扩张。
- 最严格交集、allow 交集 deny 并集、无法求交默认拒绝，直接落实 PRD §17.2 与 S4 PAP-INV-002、`IQ-013` 裁决。
- 无明确允许即拒绝、非泄露 reason_code、sealed 排除，符合 S4 PAP-INV-001/004/005 与 §14 fail closed 表。
- 判决零写入与 S3 显式绑定；PolicyDecision 不作证据，符合 S4 §11 与项目 Derived 不作证边界。
- 多用户、家庭授权、数字遗产、sealed 紧急恢复、Grant 管理 UI、外部 Agent/MCP runtime、真实数据均明确为非目标；`DQ-003/004/009` 保持 deferred。

## 发现

无 A4 blocking 产品歧义。`allow_with_redaction` 的字段裁剪语义在本切片闭合为"请求字段的过滤子集"，不引入通用脱敏规则。

## 下一步

建立 FR-012 的 A4 Traceability，随后才可选择 ADR 和物化 executable suite。
