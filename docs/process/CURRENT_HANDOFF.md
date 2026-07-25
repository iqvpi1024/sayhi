# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-B-RECONCILIATION-001
slice_id: SLICE-MVP-B-RECONCILIATION-001
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
  - a4-access-policy-rp-20260724
  - a5-app-shell-rp-20260725
  - a6-hardening-rp-20260725
  - b4-reconciliation-rp-20260725
decision_ref: DEC-MVP-B-RECONCILIATION-001
spec_contract: SPEC-B4-RECONCILIATION-001 v0.1 Approved (B4-CONTRACT-REVIEW-001)
adr_ref: ADR-0011 (+ ARCH-B4-RECONCILIATION-001)
suite_manifest: tests/b4_suite_manifest.json (materialized, executed, passed, bound to b4-20260725.json)
implementation_plan: PLAN-MVP-B-B4-IMPL-001 (B4-TASK-001..006)
next_role: Product/Architecture
next_single_action: choose next slice per docs/planning/MASTER_DELIVERY_ROADMAP.md (B4/B5/B6, C2-C6, D2/D3); start with a Decision gate
scope_in:
  - next slice decision only (no business code before Decision gate)
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - multi-user, family authorization, digital legacy, sealed emergency recovery (DQ-003/004/009 deferred)
  - external Agent runtime, MCP runtime, policy editor UI
stop_condition: next slice decided; A6 hardening slice is verified (gate review passed, recovery tag pushed)
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
- A6-TASK-001 已完成（e6a77cc）：start.py D0 入口与错误恢复壳面，定向 6/6 passed。
- A6-TASK-002 已完成（3fc39db）：alpha_explainability.py + cli 接线，定向 8/8 passed，regression 259 OK（21 skipped）。
- A6-TASK-003 已完成（08173d8）：a6_journey.py 编排辅助，定向 13/13 passed，regression 259 OK（21 skipped）。
- A6-TASK-004 已完成（77066da）：a6_testing_adapter.py，contract 21/21 passed，regression 264 OK 0 skip。
- A6-TASK-005 已完成（00d146a）：official runner 21/21 passed/current，manifest 已绑定，13 个 suite validator 全 PASSED。
- A6-TASK-006 已完成：Gate Review P0=0/P1=0，A6 切片 verified，矩阵 §4.12 同步，recovery tag `a6-hardening-rp-20260725` 已推送。
- `DEC-MVP-B-RECONCILIATION-001`（2026-07-25）选择 B4 切片；`SPEC-B4-RECONCILIATION-001` v0.1 Approved（`B4-CONTRACT-REVIEW-001`）；`ADR-0011`/`ARCH-B4-RECONCILIATION-001` 已接受；suite 物化 10 场景。
- B4-TASK-001 已完成（5b7be53）：reconciliation.py 增量对账四类发现 + store B4 additive 只读助手，定向 7/7 passed。
- B4-TASK-002 已完成（53a4e86）：深度对账三分区重建比较 + unavailable 壳，定向 11/11 passed。
- B4-TASK-003 已完成（341eb61）：semantic_diff.py 查询时派生 diff（derived-only），定向 7/7 passed。
- B4-TASK-004 已完成（59aa8a9）：b4_testing_adapter.py，contract 10/10 passed。
- B4-TASK-005 已完成（56d1c51）：official runner `b4-20260725.json` 同一次 run 10/10 passed/current，manifest 已绑定，14 个 suite validator 全 PASSED，全量 regression 292 OK 0 skip。
- B4-TASK-006 已完成：Gate Review `B4_RECONCILIATION_GATE_REVIEW_2026-07-25.md` P0=0/P1=0，B4 切片 verified，矩阵 §4.13 同步，recovery tag `b4-reconciliation-rp-20260725`。
- 全量 configured-adapter regression 基线：292 OK 0 skip；14 个 suite validator。
- 最终目标仍为 D2/D3 一键部署（`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`）；当前交付级别仅 D1 合成预览。
