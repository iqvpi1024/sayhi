# 审查与门禁说明

## 1. 职责

本目录保存两类材料：

1. 历史审计/评审快照，用于保留当时证据和 Finding。
2. 当前切片 Gate Review，用于判断是否可以进入下一阶段。

审查报告可以否决门禁，但不能修改 PRD、SPEC、测试结果或历史事实。旧报告的结论不得覆盖 `docs/PROJECT_STATE.md` 中已由后续证据更新的当前状态。

## 2. Finding 优先级

| 等级 | 含义 | 门禁处理 |
|---|---|---|
| P0 | 数据破坏、隐私泄漏或核心不变量失守 | 立即停止 |
| P1 | 当前切片无法安全进入下一阶段 | 关闭前不得通过 |
| P2 | 重要但不阻塞当前门禁 | 明确 owner、阶段和关闭条件 |
| P3 | 改进项 | 可后置但必须保留 |

严重度不因实现困难而降低；后置也不等于关闭。

## 3. Gate Review 输入

- 当前 PRD/Decision/SPEC/Matrix/ADR/Plan 基线。
- 实际 suite manifest、fixture、runner 和 Verification Result（适用时）。
- 变更 diff、隐私检查、PRD hash 和 Git 状态。
- 旧 Finding 的关闭证据与剩余风险。

模板见 `GATE_REVIEW_TEMPLATE.md`。

## 4. 通过规则

只有 P0=0、P1=0，且当前阶段的硬门禁有真实证据时才可写通过。`yes_with_conditions` 的 condition 不能隐藏新的 P1，也不能把未执行测试当作通过条件已满足。

## 5. 当前状态

上一完成切片的最新 Gate 为 `MICRO_MVP_IMPLEMENTATION_GATE_2026-07-17.md`：P0=0、P1=0，Recovery Point 已发布。

当前 A1 已通过 Product Gate、SPEC Applicability Review 和 `MVP_A_ANSWER_SAFETY_PRE_SUITE_GATE_2026-07-17.md`。最新门禁 P0=0、P1=0，只允许执行 `AS-PRE-001..005` 物化 suite；Development Gate 尚未通过。
