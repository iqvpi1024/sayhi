# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-C-RELEASE-001
slice_id: SLICE-MVP-C-RELEASE-001
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
  - c3-review-calibration-rp-20260726
  - c4-scenario-action-rp-20260726
  - c5-context-pack-backup-rp-20260726
  - c6-mvp-release-gate-rp-20260726
decision_ref: DEC-MVP-C-RELEASE-001
spec_contract: SPEC-C6-RELEASE-001 v0.1 Approved (C6-CONTRACT-REVIEW-001)
adr_ref: ADR-0018 (+ C6_RELEASE_GATE_ARCHITECTURE)
suite_manifest: tests/c6_suite_manifest.json (materialized, executed, passed, bound to c6-20260726.json)
implementation_plan: PLAN-MVP-C-C6-IMPL-001 (C6-TASK-001..002, all completed)
next_role: Delivery/Release
next_single_action: execute D2 one-click installer per docs/releases/ONE_CLICK_DELIVERY_PLAN.md (build v0.2.0-beta portable ZIP with tools/build_release.py, verify unzip -> launch -> synthetic init -> status/guide usable, record real verification, tag d2-installer-rp-20260726, push; do NOT publish a GitHub Release)
scope_in:
  - D2 one-click installer build and verification only
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - GitHub Release publication (D3 requires explicit user confirmation)
  - multi-user, family authorization, digital legacy, sealed emergency recovery (DQ-003/004/009 deferred)
  - production cryptography claims (stdlib_deterministic_v1 is explicitly non-production; AEAD/KDF is a D2/D3 decision)
stop_condition: D2 installer built and verified with real results; D3 GitHub Release requires user confirmation before any publish action
```

## 当前事实

- C6 切片 verified，recovery tag `c6-mvp-release-gate-rp-20260726` 已推送；release audit 8/8 passed 已绑定（`docs/testing/results/c6-20260726.json`）。
- `DEC-MVP-C-RELEASE-001`（2026-07-26）选择 C6 作为 active slice：MVP 发布门禁（首年全量回归、安全审计、公开 Beta 门禁）。
- C6 applicability review `C6-SPEC-APPLICABILITY-001` 结论 pass_with_slice_contract_required；`SPEC-C6-RELEASE-001` v0.1 经 `C6-CONTRACT-REVIEW-001` 批准。
- `ADR-0018` Accepted：确定性 release audit runner（8 项审计：validator 子进程、全量回归零 skip、隐私扫描、AST 依赖/网络隔离审计、manifest 绑定审计、恢复演练、Beta 门禁核验）。
- C6-TASK-001 完成：`tests/runner/run_c6_release_audit.py`；run1 失败留痕（`c6-audit-run1-failed-20260726.json`）：validator 自哈希滞后 + b1/c1 旧 fixture 无 `external_data_used` 字段，口径修正为「未声明外部数据即通过」，manifest hash 已同步。
- C6-TASK-002 完成：audit 真实执行 8/8 passed 绑定 `c6-20260726.json`；Beta 门禁 `BETA_GATE_REVIEW_2026-07-26.md` 结论 **beta_ready=true**；Gate Review `C6_RELEASE_GATE_REVIEW_2026-07-26.md` P0=0/P1=0；矩阵 §4.20 verified=true。
- suite validators：21 个全部 PASSED（含 C6）。

## 回归基线（2026-07-26）

- 全量 configured-adapter semantic regression：392 tests OK、0 skipped（16 个 adapter 环境变量：MICRO/ANSWER/A2/A3/A4/A5/A6/B2/B3/B4/B5/B6/C2/C3/C4/C5）。
- suite validators：21 个全部 PASSED。
- 已 verified 切片：Micro、A1-A6、B1-B6、C1、C2、C3、C4、C5、C6、Synthetic Ingestion、Context Pack。
- MVP C 系列全部收口，beta_ready=true。剩余路线：D2 一键安装 → D3 GitHub Release（发布动作需用户确认）。
