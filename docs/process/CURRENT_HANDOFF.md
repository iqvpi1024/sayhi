# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-C-HYPOTHESIS-001
slice_id: SLICE-MVP-C-HYPOTHESIS-001
current_phase: slice_verified
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
  - b4-reconciliation-rp-20260725
  - b5-multilingual-rp-20260725
  - b6-shadow-migration-rp-20260725
  - c2-hypothesis-lifecycle-rp-20260726
decision_ref: DEC-MVP-C-HYPOTHESIS-001
spec_contract: SPEC-C2-HYPOTHESIS-001 v0.1 Approved (C2-CONTRACT-REVIEW-001)
adr_ref: ADR-0014 (+ ARCH-C2-HYPOTHESIS-001)
suite_manifest: tests/c2_suite_manifest.json (materialized, executed, passed, bound to c2-20260726.json)
implementation_plan: PLAN-MVP-C-C2-IMPL-001 (C2-TASK-001..004, all completed)
next_role: Product/Architecture
next_single_action: choose next slice per docs/planning/MASTER_DELIVERY_ROADMAP.md (C3-REVIEW-CALIBRATION FR-203/205, then C4/C5/C6, D2/D3); start with a Decision gate
scope_in:
  - next slice decision only (no business code before Decision gate)
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - multi-user, family authorization, digital legacy, sealed emergency recovery (DQ-003/004/009 deferred)
  - external Agent runtime, MCP runtime, policy editor UI
  - automatic hypothesis generation/transition/scoring (C2 contract non-goals)
stop_condition: next slice decided; C2 hypothesis lifecycle slice is verified (gate review passed, recovery tag pushed)
```

## 当前事实

- C2 切片 verified，recovery tag `c2-hypothesis-lifecycle-rp-20260726` 已推送；official suite 10/10 passed/current 已绑定（`docs/testing/results/c2-20260726.json`）。
- `DEC-MVP-C-HYPOTHESIS-001`（2026-07-26）选择 C2 作为 active slice：FR-201 Hypothesis 支持证据、反例、范围与生命周期；约束 Hypothesis 不升级为 Fact。
- C2 applicability review `C2-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`（2026-07-26）；`SPEC-C2-HYPOTHESIS-001` v0.1 经 `C2-CONTRACT-REVIEW-001` 批准。
- `ADR-0014` Accepted：复用 canonical_objects(object_type=hypothesis) + canonical_evidence_refs，payload 内嵌 revision_history，迁移收据进修订账本；零 schema 变更。
- C2-TASK-001 完成：`hypotheses.py` 五入口（create/attach/transition/present/upgrade-reject）全部 confirmed-only，定向 9/9 passed（`c2-task001-20260726.json`）。
- C2-TASK-002 完成：`c2_testing_adapter.py` 完整实现 protocol，contract 10/10 passed（`c2-task002-20260726.json`）。
- C2-TASK-003 完成：official runner 同一次 run 10/10 passed/current，manifest 绑定，17 个 suite validator 全 PASSED，全量 regression 347 OK 0 skip（`c2-task003-20260726.json`）。
- C2-TASK-004 完成：Gate Review `C2_HYPOTHESIS_GATE_REVIEW_2026-07-26.md` P0=0/P1=0；矩阵 §4.16 verified=true。

## 回归基线（2026-07-26）

- 全量 configured-adapter semantic regression：347 tests OK、0 skipped（13 个 adapter 环境变量：MICRO/ANSWER/A2/A3/A4/A5/A6/B2/B3/B4/B5/B6/C2）。
- suite validators：17 个全部 PASSED。
- 已 verified 切片：Micro、A1-A6、B1-B6、C1、C2、Synthetic Ingestion、Context Pack。
- 剩余路线：C3-REVIEW-CALIBRATION → C4-SCENARIO-ACTION → C5-CONTEXT-PACK-BACKUP → C6-MVP-RELEASE → D2 → D3（发布动作需用户确认）。
