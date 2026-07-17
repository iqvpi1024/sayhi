# 当前模型交接包

## 1. 权威状态

本文件是下一执行模型的当前入口，不替代 `AGENTS.md`、PRD、SPEC、ADR、Acceptance 或 Plan。每次阶段变化后必须更新本文件；聊天中的“继续”不能替代这里的 `next_single_action`。

```yaml
handoff_id: HANDOFF-MVP-A-AS-001
slice_id: SLICE-MVP-A-ANSWER-SAFETY-001
current_phase: architecture_decided
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
suite_manifest: absent
suite_materialization_plan: docs/testing/MVP_A_ANSWER_SAFETY_SUITE_MATERIALIZATION_PLAN.md
implementation_plan: docs/planning/MVP_A_ANSWER_SAFETY_IMPLEMENTATION_PLAN_DRAFT.md
implementation_plan_status: draft_blocked
verification_result: not_executed
gate_review: docs/reviews/MVP_A_ANSWER_SAFETY_PRE_SUITE_GATE_2026-07-17.md
git_branch: codex/mvp-a-answer-safety-planning
git_commit: 5f81f1f6634b07f8890d26f4f84df9322f622e72
git_recovery_tag: mvp-a-answer-safety-handoff-v0.1-approved
scope_in:
  - AS-PRE-001 fixture
  - AS-PRE-001 oracle
  - task-scoped static validation and status records
scope_out:
  - A1 business implementation
  - AS-PRE-002..005
  - AS-TASK-001..009
  - PRD, Product Decision, Approved SPEC and Acceptance semantic changes
  - old Micro fixture, oracle, result and tag changes
  - UI, API, permission runtime, MCP, deployment and public release
open_blockers: []
next_role: SuiteMaterializer
next_single_action: AS-PRE-001
```

## 2. 当前允许范围

`AS-PRE-001` 只允许：

- 创建 `tests/fixtures/answer_safety_v1/fixture.json`。
- 创建 `tests/fixtures/answer_safety_v1/oracles.json`。
- 使用 11 个互相隔离的合成 case、固定 Clock、CoverageWindow、显式 freshness policy 和字段级 forbidden-write oracle。
- 运行只证明 fixture/oracle 结构、hash、locator、确定性和合成数据边界的检查。
- 更新 `PROJECT_STATE.md`、本交接包和对应静态验证记录。

`AS-PRE-001` 明确禁止：

- 创建或修改 `src/noetide_micro/answers.py`、业务 Schema、业务 adapter 或任何 A1 evaluator。
- 创建 scenario runner、manifest 或 validator；这些分别属于 `AS-PRE-002..004`。
- 执行完整 A1 business suite 或设置 `suite_materialized=true`。
- 修改 PRD、Product Decision、Approved SPEC、Acceptance expected、旧 Micro fixture/oracle/result/tag。
- 读取工作区外个人资料、访问网络或引入第三方依赖。

## 3. 完成与停止

完成 `AS-PRE-001` 必须留下：

1. fixture/oracle 的字段来源可回到 `ACCEPT-MVP-A-AS-001` 和适用 SPEC。
2. 11 个 case 相互隔离，hash/UTF-8 locator/digest 可重算。
3. 合成数据和路径边界检查有实际命令、环境、exit code 和真实结果。
4. A1 状态仍为 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。
5. `next_single_action` 更新为 `AS-PRE-002`，然后立即停止。

出现以下任一项必须停止并记录 Finding/Open Question：

- expected 需要自行定义六态 precedence、默认 freshness 阈值或 world-claim verification rule。
- fixture/oracle 只能通过读取实现 actual 生成。
- 需要权限 runtime、MCP、LLM、外部服务或真实数据。
- 需要改变旧 Micro expected 或任何 Approved 语义合同。
- `apply_patch` 出现 filesystem sandbox helper 错误。

## 4. 后续固定接力

```text
AS-PRE-001 fixture/oracle
-> AS-PRE-002 scenarios/protocol
-> AS-PRE-003 semantic tests/runner
-> AS-PRE-004 manifest/validator
-> AS-PRE-005 independent Suite Materialization Gate
-> Planner approves Implementation Plan
-> Implementer executes AS-TASK-001..007 one task at a time
-> Verifier executes AS-TASK-008 unified A1 + Micro regression
-> Auditor performs independent read-only audit
-> Debugger fixes confirmed findings and creates new results
-> Auditor rechecks P0/P1 closure
-> Releaser executes AS-TASK-009 Recovery Point
```

可复制提示词见 `docs/process/AI_EXECUTION_PROMPTS.md`。当前只能使用其中的“Suite Materializer / 单一 PRE Task”提示词。
