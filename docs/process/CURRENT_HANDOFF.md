# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-A-ENTITY-MERGE-001
slice_id: SLICE-MVP-A-ENTITY-MERGE-001
current_phase: implementation_planned
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
decision_ref: DEC-MVP-A-ENTITY-MERGE-001
spec_contract: SPEC-A3-ENTITY-MERGE-001 (approved)
adr_ref: ADR-0007
suite_manifest: tests/a3_suite_manifest.json (materialized, not_executed)
implementation_plan: PLAN-MVP-A-A3-IMPL-001 (docs/planning/MVP_A_A3_IMPLEMENTATION_PLAN.md)
next_role: Implementer
next_single_action: execute_A3_TASK_001 (store merge_records helpers per task card)
scope_in:
  - A3-TASK-001 only: schema.sql, store.py, test_a3_task_001_store.py
scope_out:
  - real personal data
  - A3-TASK-002+ files, adapter, official runner, fixture/oracle changes
  - automatic person merge, fuzzy identity matching, connectors, permissions runtime
stop_condition: A3-TASK-001 targeted store tests passed and recorded
```

## 当前事实

- A2 切片 verified，recovery tag `a2-current-state-rp-20260722` 已推送；official suite 8/8 passed/current 已绑定。
- `DEC-MVP-A-ENTITY-MERGE-001`（2026-07-24）选择 A3 作为 active slice，只授权 S1/S2/S3/S6 applicability review。
- A3 applicability review `A3-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`（2026-07-24）。
- A3 范围：固定合成两个 Person Entity 的 merge proposal → 用户确认 → ChangeSet 原子发布（引用重定向 + `merged_into` 标记）→ split compensation；历史永不删除；trust/closeness/人格判断不自动修改。
- A3 非目标：自动合并、模糊身份匹配、真实联系人导入、权限 runtime、UI、非 Person 合并。
- `SPEC-A3-ENTITY-MERGE-001` 已批准（`A3-CONTRACT-REVIEW-001`，approved_for_traceability，2026-07-24）。
- 全量 configured-adapter regression 基线：151 OK 无 skip；9 个 suite validator 全 PASSED。
- 最终目标仍为 D2/D3 一键部署（`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`）；当前仅 D1 合成预览。
