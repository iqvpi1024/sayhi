# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-A-ENTITY-MERGE-001
slice_id: SLICE-MVP-A-ENTITY-MERGE-001
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
  - b2-episode-summary-rp-20260719
  - b3-commitment-rp-20260722
  - a2-current-state-rp-20260722
  - a3-entity-merge-rp-20260724
decision_ref: DEC-MVP-A-ENTITY-MERGE-001
spec_contract: SPEC-A3-ENTITY-MERGE-001 (approved)
adr_ref: ADR-0007
architecture_ref: ARCH-A3-ENTITY-MERGE-001
suite_manifest: tests/a3_suite_manifest.json (executed, passed, bound)
implementation_plan: PLAN-MVP-A-A3-IMPL-001 (all 5 tasks completed)
gate_review: docs/reviews/A3_ENTITY_MERGE_GATE_REVIEW_2026-07-24.md (P0=0, P1=0)
next_role: Product_Decider
next_single_action: return_to_product_decision_for_next_slice (candidates per docs/planning/MASTER_DELIVERY_ROADMAP.md: A4 access policy, B4 reconciliation - A2+B3 deps now satisfied)
scope_in:
  - reading roadmap and open questions to propose the next slice decision
scope_out:
  - real personal data
  - D2/D3 production installer claims
  - any business code before a new Product Decision exists
  - moving or reusing any existing tag
stop_condition: new Product Decision recorded; no implementation may start before it
```

## 当前事实

- A3 切片 verified：official runner `a3-20260724.json` 8/8 passed/current 已绑定；Gate Review P0=0/P1=0；recovery tag `a3-entity-merge-rp-20260724` 已推送。
- 全量 configured-adapter regression 基线：169 OK 无 skip；10 个 suite validator 全 PASSED。
- 施工前 Change Control 已记录：A3-006/008 fixture 采用 `pre_published` 播种；`split_records` 独立成表保持 `merge_records` 严格只增不改。
- B4-RECONCILIATION-DIFF 的 A2+B3 依赖均已 verified；A4 需要 S4 applicability review 与相关 Privacy Product Decision。
- 最终目标仍为 D2/D3 一键部署（`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`）；当前交付级别仅 D1 合成预览。
