# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-A-ACCESS-POLICY-001
slice_id: SLICE-MVP-A-ACCESS-POLICY-001
current_phase: implementation_in_progress
product_baseline:
  path: PRDv05.md
  version: 0.5
  canonical_lf_sha256: 34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7
release:
  tag: v0.1.3-synthetic-preview
  commit: c340eac939cdbc094d6ec8da7f4e710d879cf1c1
  url: https://github.com/iqvpi1024/sayhi/releases/tag/v0.1.3-synthetic-preview
  prerelease: true
  delivery_level: D1_synthetic_preview
latest_recovery_points:
  - b2-episode-summary-rp-20260719
  - b3-commitment-rp-20260722
  - a2-current-state-rp-20260722
  - a3-entity-merge-rp-20260724
decision_ref: DEC-MVP-A-ACCESS-POLICY-001
spec_contract: SPEC-A4-ACCESS-POLICY-001 (approved)
adr_ref: ADR-0008
suite_manifest: tests/a4_suite_manifest.json (materialized, not_executed)
implementation_plan: PLAN-MVP-A-A4-IMPL-001 (docs/planning/MVP_A_A4_IMPLEMENTATION_PLAN.md)
next_role: Implementer
next_single_action: execute_A4_TASK_002 (access_policy.py pure-function policy evaluator per task card)
scope_in:
  - A4-TASK-002 only: access_policy.py, test_a4_task_002_access_policy.py
scope_out:
  - real personal data
  - A4-TASK-003+ files, adapter, official runner, fixture/oracle changes
  - multi-user, family authorization, digital legacy, sealed emergency recovery (DQ-003/004/009 deferred)
  - external Agent runtime, MCP runtime, policy editor UI
stop_condition: A4-TASK-002 targeted evaluator tests passed and recorded
```

## 当前事实

- A3 切片 verified，recovery tag `a3-entity-merge-rp-20260724` 已推送；official suite 8/8 passed/current 已绑定。
- `DEC-MVP-A-ACCESS-POLICY-001`（2026-07-24）选择 A4 作为 active slice，只授权 S1/S3/S4/S6 applicability review。
- A4 范围：固定合成单用户本地调用者；身份+目的+舱室+字段+时间综合判决；allowed（过滤后字段集）/denied（原因码）；多策略最严格交集、allow 交集 deny 并集、无法求交默认拒绝；复用 A1 六态降级。
- A4 非目标：多用户、家庭授权、数字遗产、sealed 紧急恢复、外部 Agent/MCP runtime、策略编辑器 UI、真实数据。
- A4 applicability review `A4-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`（2026-07-24）。
- `SPEC-A4-ACCESS-POLICY-001` 已批准（`A4-CONTRACT-REVIEW-001`，2026-07-24）。
- A4-TASK-001 已完成并验证：store 只读策略标注/digest 辅助，定向 6/6 passed，regression 175 OK（8 A4 contract skipped）。
- 全量 configured-adapter regression 基线：169 OK 无 skip；10 个 suite validator 全 PASSED。
- 最终目标仍为 D2/D3 一键部署（`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`）；当前交付级别仅 D1 合成预览。
