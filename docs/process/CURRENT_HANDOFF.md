# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-A-HARDENING-001
slice_id: SLICE-MVP-A-HARDENING-001
current_phase: plan_approved
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
  - a4-access-policy-rp-20260724
  - a5-app-shell-rp-20260725
decision_ref: DEC-MVP-A-HARDENING-001
spec_contract: SPEC-A6-HARDENING-001 v0.1 Approved (A6-CONTRACT-REVIEW-001)
adr_ref: ADR-0010 (+ ARCH-A6-HARDENING-001)
suite_manifest: tests/a6_suite_manifest.json (materialized, not_executed)
implementation_plan: PLAN-MVP-A-A6-IMPL-001 (A6-TASK-001..006)
next_role: Implementer
next_single_action: A6-TASK-001 per docs/planning/MVP_A_A6_TASK_CARDS.md (start.py D0 entry + error recovery shell surfaces)
scope_in:
  - A6-TASK-001 only (start.py, narrow store corruption-detection, narrow tests)
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - multi-user, family authorization, digital legacy, sealed emergency recovery (DQ-003/004/009 deferred)
  - external Agent runtime, MCP runtime, policy editor UI
stop_condition: A6-TASK-001 verified (targeted tests + regression + record); then A6-TASK-002
```

## 当前事实

- A3 切片 verified，recovery tag `a3-entity-merge-rp-20260724` 已推送；official suite 8/8 passed/current 已绑定。
- `DEC-MVP-A-ACCESS-POLICY-001`（2026-07-24）选择 A4 作为 active slice，只授权 S1/S3/S4/S6 applicability review。
- A4 范围：固定合成单用户本地调用者；身份+目的+舱室+字段+时间综合判决；allowed（过滤后字段集）/denied（原因码）；多策略最严格交集、allow 交集 deny 并集、无法求交默认拒绝；复用 A1 六态降级。
- A4 非目标：多用户、家庭授权、数字遗产、sealed 紧急恢复、外部 Agent/MCP runtime、策略编辑器 UI、真实数据。
- A4 applicability review `A4-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`（2026-07-24）。
- `SPEC-A4-ACCESS-POLICY-001` 已批准（`A4-CONTRACT-REVIEW-001`，2026-07-24）。
- A4-TASK-001 已完成并验证：store 只读策略标注/digest 辅助，定向 6/6 passed，regression 175 OK（8 A4 contract skipped）。
- A4-TASK-002 已完成并验证：access_policy.py 判决器与 oracle 全场景一致，定向 8/8 passed，regression 183 OK（8 A4 contract skipped）。
- A4-TASK-003 已完成并验证：a4_testing_adapter.py contract 8/8 passed；全量 regression 191 OK 无 skip。
- A4-TASK-004 已完成并验证：official runner a4-20260724.json 8/8 passed/current，manifest 已绑定，11 validators PASSED。
- A5-TASK-001 已完成并验证：app_shell.py 呈现层纯函数与零绕过静态扫描辅助，定向 6/6 passed，configured-adapter regression 205 OK（8 A5 contract skipped），PRAGMA 检查通过；official suite 仍 `not_executed`。
- A5-TASK-002 已完成并验证：cli.py guide/receipts/history 接线与 a5_testing_adapter.py 完整 protocol 实现，定向 6/6 passed，contract 8/8 passed（adapter），全量 regression 211 OK 无 skip；official suite 仍 `not_executed`。
- A5-TASK-003 已完成并验证：contract 集成验证 8/8 passed（a45a8bd），regression 211 OK 无 skip 无退化；official suite 仍 `not_executed`。
- A5-TASK-004 已完成并验证：official runner a5-20260725.json 同一次 run 8/8 passed/current，manifest 已绑定 current result，12 个 suite validator 全 PASSED，全量 regression 211 OK 无 skip。
- A5-TASK-005 已完成：Gate Review P0=0/P1=0，A5 切片 verified，矩阵 §4.11 同步，recovery tag `a5-app-shell-rp-20260725` 已创建并推送。
- `DEC-MVP-A-HARDENING-001`（2026-07-25）选择 A6 切片并裁决 12 测试解释；A6-SPEC-APPLICABILITY-001 结论 `pass_with_slice_contract_required`。
- `SPEC-A6-HARDENING-001` v0.1 已 Approved（`A6-CONTRACT-REVIEW-001`，2026-07-25）：21 场景在同一 Reference Profile `a6_mvp_a_reference_v1` 顺序执行；FR-003 生成侧为显式已知限制（合同 §1.1）；Traceability 矩阵 §4.12 已建立。
- 全量 configured-adapter regression 基线：211 OK 无 skip；12 个 suite validator。
- 最终目标仍为 D2/D3 一键部署（`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`）；当前交付级别仅 D1 合成预览。
