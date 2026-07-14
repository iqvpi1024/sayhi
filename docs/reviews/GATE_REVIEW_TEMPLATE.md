# Gate Review：<gate_id>

## 0. 元数据

| 字段 | 值 |
|---|---|
| Gate ID | `<gate_id>` |
| Slice | `<slice_id>` |
| From Phase | `<phase>` |
| Target Phase | `<phase>` |
| Date | `<YYYY-MM-DD>` |
| Reviewer | `<role>` |
| Verdict | `not_reviewed` |

## 1. 审查范围与非范围

明确本次判断覆盖什么，以及不能从本结论推导什么。

## 2. 基线

| Artifact | Version / Commit / Digest | Applicability |
|---|---|---|
| PRD | `<value>` | `current` |
| Decision / SPEC / ADR | `<value>` | `<status>` |
| Suite / Implementation | `<value or absent>` | `<status>` |
| Verification Result | `<value or not_executed>` | `<status>` |

## 3. 门禁检查

| Check | Evidence | Result |
|---|---|---|
| 范围未扩张 | `<reference>` | `<pass/fail/not_applicable>` |
| PRD 未静默修改 | `<hash/diff>` | `<result>` |
| 追踪完整 | `<reference>` | `<result>` |
| 阶段验证真实 | `<result artifact>` | `<result>` |
| 隐私边界 | `<scan/review>` | `<result>` |
| 回退可执行 | `<steps/test>` | `<result>` |

## 4. Findings

| ID | Severity | Finding | Evidence | Required Action | Status |
|---|---|---|---|---|---|
| `<id>` | `<P0-P3>` | `<statement>` | `<reference>` | `<action>` | `open` |

## 5. 结论

填写 `yes | no | yes_with_conditions`，并解释条件。P0/P1 非零时不得写 `yes`。

## 6. 未证明与剩余风险

列出未执行测试、后置 P2/P3 和任何 applicability 限制。

## 7. 下一步唯一建议动作

只写一个动作，并与 verdict 一致。
