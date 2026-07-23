# ADR-0008：A4 查询层判决器的纯函数化与零写入机制

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Slice | `SLICE-MVP-A-ACCESS-POLICY-001` |
| Contract | `SPEC-A4-ACCESS-POLICY-001` |

## 决定

A4 判决器实现为纯函数：输入为 AccessRequest、fixture 给定的 Grant 集合与对象策略标注（sensitivity/compartments），输出为 PolicyDecision（`allow/allow_with_redaction/deny` + 字段集 + 非泄露 reason_code）。判决器只读 store 中的对象标注，不持有连接、不写任何表；PolicyDecision 不持久化。Grant 集合由 fixture 直接注入，不建 Grant 存储或生命周期。

## 不采用的方案

- 判决写入审计 Canonical 对象：会把请求时 Derived 伪装为事实并产生无用户确认 revision（合同禁止零写入以外的行为；非泄露审计只记录 reason_code 分布，属后续切片）。
- 缓存判决结果复用：Grant 过期或 scope 变化时缓存判决会猜测当前授权，违反 S4 §14。
- 引入通用 RBAC/ABAC 框架或策略引擎依赖：超出固定合成切片范围，且引入第三方依赖。
- 把判决放在 Derived View 读取路径之后：视图内容可能成为权限证据绕过判决，违反 A4-INV-007。

## 后果与验证

- 纯函数输入输出可在 suite 中逐案例断言；零写入由 revision 与 Canonical 对象前后 digest 证明。
- 时间求值只比较 `requested_at` 与 Grant 固定窗口，无系统时钟依赖，跨平台确定。
- 拒绝响应形状由合同固定，泄漏探针（A4-008）可直接断言响应只含合同字段。
- A4 suite 必须证明：fail closed 全集、最严格交集、sealed 排除、过期/不匹配 Grant 无效、零写入、视图不可绕过。
