# 当前模型交接包

## 1. 权威状态

本文件是下一执行模型的当前入口，不替代 `AGENTS.md`、PRD、SPEC、ADR、suite、Approved Plan 或 Task Cards。聊天中的“继续”不能替代 `next_single_action`。

```yaml
handoff_id: HANDOFF-MVP-A-AS-002
slice_id: SLICE-MVP-A-ANSWER-SAFETY-001
current_phase: implementation_planned
product_baseline:
  path: PRDv05.md
  version: 0.5
  canonical_lf_sha256: 34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7
decision_refs:
  - DEC-MVP-A-AS-001
spec_refs:
  - SPEC-SOM-001@0.6
  - SPEC-BTE-001@0.5
  - SPEC-CS-001@0.4
  - SPEC-HTH-001@0.5
  - SPEC-SIP-001@0.3
traceability_ref: docs/traceability/REQUIREMENTS_MATRIX.md#41-active-slicemvp-a-answer-safety
acceptance_ref: docs/testing/MVP_A_ANSWER_SAFETY_ACCEPTANCE.md
adr_refs:
  - ADR-0002
architecture_ref: docs/architecture/MVP_A_ANSWER_SAFETY_ARCHITECTURE.md
suite_manifest: tests/answer_safety_suite_manifest.json
suite_flags:
  suite_defined: true
  suite_materialized: true
  suite_executed: false
  suite_passed: false
implementation_plan: docs/planning/MVP_A_ANSWER_SAFETY_IMPLEMENTATION_PLAN.md
implementation_plan_status: approved
task_cards: docs/planning/MVP_A_ANSWER_SAFETY_TASK_CARDS.md
task_cards_status: approved_companion
verification_result: not_executed
gate_review: docs/reviews/MVP_A_ANSWER_SAFETY_DEVELOPMENT_READINESS_GATE_2026-07-17.md
git_branch: codex/mvp-a-answer-safety-planning
git_commit: 80a920aa8f07571bb866ce223039033c56b5dd72
git_content_commit: 7e28546c3f1766afeb5c3524bc55a97ff1102e3f
git_recovery_tag: mvp-a-answer-safety-development-ready-v0.1-approved
scope_in:
  - AS-TASK-003 Coverage evaluator
  - AS-TASK-003 narrow tests
  - task-scoped verification and status records
scope_out:
  - AS-TASK-004..009
  - answers.py and answer_testing_adapter.py
  - AnswerEnvelope, EvidenceSelector, Coverage, freshness and conflict behavior
  - A1 full runner and business Verification Result
  - PRD, Product Decision, Approved SPEC, Acceptance expected and materialized oracle changes
  - old Micro fixture, oracle, historical result and tag changes
  - UI, API, permission runtime, MCP, deployment and public release
open_blockers: []
next_role: Implementer
next_single_action: AS-TASK-003
```

## 2. `AS-TASK-001` 权威入口

Implementer 必须完整读取：

1. `AGENTS.md` 和其恢复链。
2. `PLAN-MVP-A-AS-IMPL-001`。
3. `CARDS-MVP-A-AS-001` 的 §1、§2、§3 和 §12。
4. A1 manifest、fixture、oracle、adapter protocol 和 `AS-010` scenario。
5. ADR-0002、Architecture 与 `VERIFY-MVP-A-AS-SUITE-001`。

只有以上文件仍显示 Approved/current 且 manifest validator exit code `0` 时，才允许写 AS-TASK-001。

## 3. 当前允许文件

- `src/noetide_micro/schema.sql`
- `src/noetide_micro/store.py`
- `src/noetide_micro/__init__.py`，仅必要 export
- `tests/semantic/test_answer_task_001_store.py`，可选窄测试
- `docs/PROJECT_STATE.md`
- `docs/process/CURRENT_HANDOFF.md`
- Approved Plan 的 Task 状态和 AS-TASK-001 定向验证记录

任何其他业务路径需要先由 Task Card 或 Change Control 授权。

## 4. 当前禁止

- 不创建 `src/noetide_micro/answers.py` 或 `answer_testing_adapter.py`。
- 不实现六态判断、Evidence/Coverage/Freshness/Conflict evaluator。
- 不修改 manifest、fixture、oracle、scenario、protocol、semantic contract test 或 runner 来迎合实现。
- 不执行完整 A1 runner，不设置 `suite_executed=true` 或 `suite_passed=true`。
- 不修改旧 Micro expected/result/tag，不引入第三方依赖、网络、真实数据或工作区外读取。
- 不开始 AS-TASK-002。

## 5. `AS-TASK-001` 完成证据

必须同时留下：

1. A1 逻辑存储为加法式，不破坏现有 Micro schema/seed。
2. 11 case 可独立、幂等 seed；相同 identity 不同 payload 拒绝；失败不部分写入。
3. PRAGMA、外键、hash/locator、Source/Canonical/Ledger/Projection count/digest 能力有窄测试。
4. 受影响 Micro store/adapter 定向测试、Product/SPEC/Micro/A1 validators 和 diff check 的真实命令、环境、exit code、结果。
5. 完整 A1 suite 仍为 `not_executed`。
6. 完成后 `next_single_action=AS-TASK-002`，然后立即停止。

## 6. 停线条件

出现 Task Cards §12 任一条件必须停止并记录。特别是：需要定义物理 schema 之外的产品语义、需要修改 oracle、需要创建 AnswerEnvelope、需要工作区外路径或 `apply_patch` helper 失败时，不得绕过。

## 7. 后续固定接力

```text
AS-TASK-001..007 one task per handoff
-> AS-TASK-008 independent unified A1 + Micro verification
-> independent read-only audit
-> Debug + new Verification Result when findings exist
-> independent re-audit closes P0/P1
-> AS-TASK-009 engineering Recovery Point
-> next slice Product Decision
```

可复制提示词见 `docs/process/AI_EXECUTION_PROMPTS.md`。当前只允许使用 Implementer 提示词并替换 `<TASK_ID> = AS-TASK-001`。
