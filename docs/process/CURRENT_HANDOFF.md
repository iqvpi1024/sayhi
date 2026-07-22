# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-MVP-A-CURRENT-STATE-001
slice_id: SLICE-MVP-A-CURRENT-STATE-001
current_phase: spec_applicability_reviewed
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
decision_ref: DEC-MVP-A-CURRENT-STATE-001
spec_contract: absent_pending_applicability_review
adr_ref: absent_pending_applicability_review
architecture_ref: absent_pending_applicability_review
suite_manifest: absent_pending_materialization
implementation_plan: absent_pending_planning
task_cards: absent_pending_planning
next_role: Contract_Drafter
next_single_action: draft_A2_slice_contract
scope_in:
  - fixed synthetic Commitment lifecycle and Derived due-status boundary
  - S1/S2/S3/S5/S6/S7 applicability review and B3 traceability
scope_out:
  - real personal data
  - D2/D3 production installer claims
  - changes to approved PRD or SPEC to fit implementation
  - user untracked private files
stop_condition: A2 slice contract approved; traceability is the next gate
```

## 当前事实

- `v0.1.3-synthetic-preview` 是已发布的 GitHub prerelease，不得移动、重传或复用该 tag。
- Release 包含源码 ZIP、self-contained Windows portable ZIP 与两份 SHA-256 文件；远端 digest 已与本地构建核对一致。
- portable 包只初始化合成 SQLite 数据，启动 smoke 返回 `Current revision: rev_010`。
- `.workbuddy/`、`Review-report/`、根目录 `test*.py/test_output.txt` 与 `tests/results/` 不读取、不修改、不提交。
- 真实验证详情见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`；A1/C1 历史失败结果保留，当前绑定结果分别为 35/35 和 7/7。
- 独立公开发布终审已完成，P0=0、P1=0；记录见 `docs/reviews/PUBLIC_PREVIEW_V0.1.3_INDEPENDENT_AUDIT.md`。
- B2-TASK-001 已完成，定向 3/3 storage tests passed；B2 official suite 仍未执行。
- B2-TASK-002 已完成，定向 5/5 ChangeSet tests 与 configured-adapter semantic regression 103 passed；B2 official suite 的 8 个 contract case 仍 `not_executed`，因为 adapter 属于 pending B2-TASK-004。
- B2-TASK-003 已完成，定向 4/4 summary tests 与 configured-adapter semantic regression 107 passed；下一轮只允许执行 B2-TASK-004。
- B2-TASK-004/005 已完成：official runner 8/8 passed，current result 已绑定。下一步只允许创建并复核 B2 recovery point。
- B2 recovery point `b2-episode-summary-rp-20260719` 已推送并指向审计提交；B2 切片完成，下一步必须回到 Product Decision。
- `DEC-MVP-B-COMMITMENT-001` 已选择 B3；本轮只允许进行 applicability review，禁止 B3 业务代码。
- B3 applicability review 已完成，结论为 `pass_with_slice_contract_required`；下一轮只允许起草切片合同，禁止 fixture/oracle/ADR/业务代码。
- B3 slice contract 已批准；下一轮只允许建立 traceability，禁止 ADR、suite 物化和业务代码。
- B3 traceability 已建立；下一轮只允许 ADR/Architecture View，禁止 suite 物化和业务代码。
- B3 ADR/Architecture View 已接受；下一轮只允许 suite 物化，禁止业务代码。
- B3 suite 已物化：preflight validator exit 0，contract module 8 skipped（无 adapter）；下一轮只允许 Implementation Plan，禁止业务代码。
- B3 Implementation Plan 与任务卡已建立；下一轮只允许 B3-TASK-001，禁止 TASK-002 及以后。
- B3-TASK-001 已完成：定向 5/5 passed，regression 120 OK；下一轮只允许 B3-TASK-002。
- B3-TASK-002 已完成：定向 8/8 passed，regression 128 OK；下一轮只允许 B3-TASK-003。
- B3-TASK-003 已完成：定向 4/4 passed，regression 132 OK；下一轮只允许 B3-TASK-004。
- B3-TASK-004 已完成：contract 8/8 passed（adapter）；下一轮只允许 B3-TASK-005 official runner 与绑定。
- B3-TASK-005 已完成：official 8/8 passed/current 已绑定；regression 132 OK；下一轮只允许 B3-TASK-006 Gate Review 与 recovery point。
- B3-TASK-006 已完成：Gate Review P0=0/P1=0；切片 verified；recovery tag `b3-commitment-rp-20260722` 已推送。
- `DEC-MVP-A-CURRENT-STATE-001` 已选择 A2；applicability review 结论 `pass_with_slice_contract_required`；下一轮只允许起草 slice contract，禁止 fixture/oracle/ADR/业务代码。
