# DEC-PRD-V05-001：批准 PRD v0.5 整合基线

## 1. 决定

产品负责人于 2026-07-15 明确授权：保留 `PRDv04.md`，先完成 PRD v0.5 并确认无问题，再逐份优化/复核 SPEC。基于该授权和 `PRD_V05_READINESS_REVIEW.md`，作出以下决定：

1. `PRDv05.md` v0.5 成为当前 Approved Product Baseline。
2. `PRDv04.md` v0.4 状态变为 `superseded_read_only`，原文和历史 tag 保持不变。
3. v0.5 是已确认产品裁决的整合，不新增 FR、不扩大 Micro、不选择技术栈。
4. 九份现有 SPEC 不因本决定自动兼容；在逐份 Compatibility Review 完成前，业务实现门禁保持 closed。
5. `DQ-001..013` 保持 deferred，不影响 Micro，也不得由 SPEC/ADR/实现提前裁决。

## 2. 基线绑定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-PRD-V05-001` |
| Date | 2026-07-15 |
| Product Owner Authorization | 当前任务中明确“先 PRD05 没问题了再优化 SPEC” |
| Parent Recovery Point | tag `project-delivery-workflow-v0.1-validated` / commit `74e14f7` |
| Reviewed Draft canonical LF SHA-256 | `322680431123342856C86225ADB42CA554736590FABF30FD220D170E84AF6E21` |
| Approved `PRDv05.md` canonical LF SHA-256 | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| Immutable `PRDv04.md` canonical LF SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |

Approved hash 与 reviewed draft hash 的唯一语义外变化是文档状态从 `Consolidated Draft for Gate Review` 提升为 `Approved Product Baseline`。

## 3. v0.5 整合范围

- 纠正 Assertion 内容类型、审查状态与六态回答的混用。
- 固定 RelationshipState 与对象别名归属。
- 区分 Source append receipt 与 Canonical ChangeSet。
- 固定 Micro 两个 Core View、补偿撤销和必要失败场景。
- 明确删除/封存/导出、舱室合并和授权到期的产品行为。
- 明确 suite 四态、SPEC 顺序和业务开工门禁。
- 将 42 条历史审查评分留在 v0.4/审计材料，不继续占用当前 PRD 正文。

## 4. 明确未授权

- 不开始业务代码、数据库、依赖、模型或最终技术选择。
- 不物化 suite，不把静态校验描述为业务通过。
- 不实现权限 runtime、MCP runtime、迁移、连接器、同步、财务、健康、决策、多 Agent、A2A 或数字遗产。
- 不把 deferred 问题的保守默认解释为永久产品裁决。

## 5. 下游失效与恢复

- S1-S9 的正文和历史 Approved 记录保留，但 current applicability 暂为 `compatibility_review_required`。
- Matrix、Micro Acceptance 和静态校验器必须切换到 v0.5 基线。
- 兼容复核若发现行为变化，受影响 SPEC 必须升版并同步 Test/Matrix；不得只替换版本字符串。
- PRD v0.5 建立独立 commit/tag 恢复点后，才进入 SPEC 兼容阶段。

## 6. 下一步唯一建议动作

逐份执行 S1 到 S9 对 PRD v0.5 的兼容复核；先证明，再保留或升版。
