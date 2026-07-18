# 端到端连续执行模式决定

## 文档信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-E2E-EXEC-001` |
| Date | 2026-07-18 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Decision Type | Delivery process only |
| Status | `decided` |
| Decision Maker | 产品负责人 |

## 决定

本次 Release Candidate 纠偏开发采用连续执行模式：

```yaml
execution_mode: continuous_end_to_end
manual_task_approval_required: false
manual_gate_wait_required: false
quality_checkpoints_required: true
product_semantics_may_be_invented: false
public_release_before_independent_audit: false
```

开发代理不再每完成一个 Task 就暂停等待产品负责人确认。代理按批准的总施工计划连续完成修复、补全、测试、打包和本地发布候选验证。

## 不取消的约束

- PRD、Approved SPEC、fixture/oracle 不能为了迎合实现而修改。
- 未执行测试不能记为 passed，失败结果不能被隐藏或覆盖。
- Source、Canonical、Ledger、Projection、ChangeSet、历史、证据和隐私不变量继续有效。
- 只使用合成 fixture；不得读取 `.workbuddy/`、`Review-report/` 或工作区外个人资料。
- 新产品歧义不得由代码暗中裁决。能采用现有最保守合同继续的，采用保守行为并记录；无法继续的，仅冻结受影响能力并完成其他独立工作。
- GitHub 默认分支合并、正式 tag、GitHub Release 和公开发布必须等待独立代码审计通过。

## 连续执行中的自动检查点

原流程中的 Gate 不再要求人工停顿，但保留为机器可验证的质量检查点：

1. 合同一致性检查。
2. suite/fixture/oracle 完整性检查。
3. 实现和定向测试检查。
4. 完整回归与不可变结果检查。
5. 隐私、可移植性和干净环境安装检查。
6. Release Candidate 审计包检查。

任一检查点失败时，开发代理直接进入修复循环，直到通过或形成真实 blocker，不向用户报告虚假完成。

## 完成边界

连续执行只到 `audit_ready_release_candidate`。在交接前，实施代理必须连续完成开发、测试、内部审计、Debug、全量回归和内部复审；内部审计与复审不能替代独立审计。Codex 只在该候选形成后进行最终独立审计。合并到 GitHub 默认分支、正式版本 tag 和 GitHub Release 均不由实施代理自行完成。
