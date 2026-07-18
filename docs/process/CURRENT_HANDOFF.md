# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-B-EPISODE-SUMMARY-001
slice_id: SLICE-MVP-B-EPISODE-SUMMARY-001
current_phase: suite_materialized
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
ci_runs:
  - 29654926812
  - 29654930604
decision_ref: DEC-MVP-B-EPISODE-SUMMARY-001
spec_contract: SPEC-B2-EPISODE-SUMMARY-001
adr_ref: ADR-0004
architecture_ref: ARCH-B2-EPISODE-SUMMARY-001
suite_manifest: tests/b2_suite_manifest.json
next_role: Implementation Planner
next_single_action: create_b2_implementation_plan_and_task_cards
scope_in:
  - fixed synthetic Episode, Derived summary, freshness and traceability boundary
  - S1/S2/S3/S5/S6/S7 applicability review and B2 traceability
scope_out:
  - real personal data
  - D2/D3 production installer claims
  - changes to approved PRD or SPEC to fit implementation
  - user untracked private files
stop_condition: B2 Implementation Plan and Task Cards are approved and each task maps to contract/suite/ADR
```

## 当前事实

- `v0.1.3-synthetic-preview` 是已发布的 GitHub prerelease，不得移动、重传或复用该 tag。
- Release 包含源码 ZIP、self-contained Windows portable ZIP 与两份 SHA-256 文件；远端 digest 已与本地构建核对一致。
- portable 包只初始化合成 SQLite 数据，启动 smoke 返回 `Current revision: rev_010`。
- `.workbuddy/`、`Review-report/`、根目录 `test*.py/test_output.txt` 与 `tests/results/` 不读取、不修改、不提交。
- 真实验证详情见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`；A1/C1 历史失败结果保留，当前绑定结果分别为 35/35 和 7/7。
- 独立公开发布终审已完成，P0=0、P1=0；记录见 `docs/reviews/PUBLIC_PREVIEW_V0.1.3_INDEPENDENT_AUDIT.md`。
- B2 已完成 product decision、SPEC applicability、slice contract、traceability、ADR/architecture 与 suite materialization；不得在 Implementation Plan 完成前编写 Episode/Summary 业务代码。
