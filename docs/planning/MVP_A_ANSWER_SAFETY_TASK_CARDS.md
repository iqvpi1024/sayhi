# MVP-A Answer Safety 逐任务施工卡

## 0. 文档状态

| 字段 | 值 |
|---|---|
| Card Set ID | `CARDS-MVP-A-AS-001` |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Parent Plan | `PLAN-MVP-A-AS-IMPL-001` |
| Status | `Approved Companion` |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Acceptance | `ACCEPT-MVP-A-AS-001` |
| ADR / Architecture | `ADR-0002` / `ARCH-MVP-A-AS-001` |
| Business Code Authorized | `true`，但只限 `CURRENT_HANDOFF.next_single_action` 指向的单一 Task |

本文件把未来 `AS-TASK-001..009` 拆成低上下文模型可以逐项执行的施工合同。它不替代 Approved SPEC、materialized suite 或字段级 oracle，也不单独授权业务编码。

只有同时满足以下条件，本卡集才能在 Planning Gate 中改为 `Approved Companion`：

1. `suite_materialized=true`、`suite_executed=false`、`suite_passed=false`。
2. A1 manifest、fixture、oracle、scenario plan、adapter protocol、semantic tests、runner 和 validator 均存在且 hash 匹配。
3. `PLAN-MVP-A-AS-IMPL-001` 已从 Draft 升为 Approved。
4. `docs/process/CURRENT_HANDOFF.md` 的 `next_single_action` 指向待执行的唯一 `AS-TASK-*`。
5. Suite Materialization Gate 和 Development Readiness Gate 均为 P0=0、P1=0。

若本文件与 PRD、Decision、Approved SPEC、Acceptance、Accepted ADR 或 materialized oracle 冲突，以上游合同为准并立即停线；不得选择对实现更方便的一方。

## 1. 全局执行合同

### 1.1 每个 Task 的固定开始动作

Implementer 在每个 Task 开始前 MUST：

1. 完整读取 `AGENTS.md`，并按其恢复顺序读取当前权威文件。
2. 核验 `CURRENT_HANDOFF.current_phase=implementation_planned|implementing`。
3. 核验 Implementation Plan 和本卡集均为 Approved，且 `next_single_action` 恰好等于本 Task ID。
4. 核验 A1 manifest 的 artifact hash、35 个 required result ID 和 `suite_materialized=true`。
5. 运行 `git status --short --branch`，确认相关改动可归属；忽略但不提交 `.workbuddy/`、`Review-report/`。
6. 记录开始 HEAD、Python/SQLite/OS 版本和本 Task 适用的测试入口。
7. 只在仓库内使用批准的合成 fixture；不得读取工作区外个人资料或访问网络。

任一条件不满足时，Task 状态保持 `blocked`，只允许记录门禁问题，不得写业务代码。

### 1.2 所有 Task 共同禁止

- 修改 `PRDv04.md`、`PRDv05.md`、Product Decision、Approved SPEC 或 Acceptance expected。
- 修改旧 Micro fixture、oracle、历史 result 或已发布 tag 来迎合 A1。
- 从实现 actual 生成、补全或更新 oracle。
- 引入第三方依赖、ORM、Web API、CLI、UI、插件系统、服务总线、在线模型或外部服务。
- 实现权限 runtime、MCP、通用问答/RAG、通用规则引擎、冲突裁决、Canonical `value=unknown`、ChangeSet 写入或第三个 View。
- 读取真实个人数据，或新增真实姓名、地址、组织、电话、邮箱、凭据、债务、健康或亲密关系资料。
- 把定向测试通过写成 A1 35/35 或 Micro 49/49 已通过。
- 覆盖 failed/errored/partial result，移动已发布 tag，或把静态检查描述为业务验证。
- 使用 `Set-Content` 等方式绕过 `apply_patch`；`apply_patch` helper 失败时立即停线。

### 1.3 允许更新的公共记录

每个 Task 完成后只允许按真实结果更新：

- `docs/PROJECT_STATE.md`
- `docs/process/CURRENT_HANDOFF.md`
- `docs/planning/MVP_A_ANSWER_SAFETY_IMPLEMENTATION_PLAN.md`
- 当前 Task 的定向验证记录

Requirements Matrix 只在 Implementation Module 或正式 Verification Result 发生可证实变化时更新。历史 result、旧 Gate 和旧 Recovery Record 不原地改写。

### 1.4 Task 结果记录最小字段

```yaml
task_id: AS-TASK-nnn
started_from_commit: full SHA
files_changed: [repository-relative paths]
commands:
  - command: exact command
    environment: Python/SQLite/OS + relevant env
    exit_code: integer
    result: passed | failed | errored | not_executed
business_suite_state:
  suite_executed: false
  suite_passed: false
product_or_spec_ambiguity: none | stable issue ID
privacy_or_scope_issue: none | stable finding ID
next_single_action: one action
```

定向测试结果只能证明本 Task 的局部行为。`suite_executed` 和 `suite_passed` 在 `AS-TASK-008` 产生统一 current result 前保持 `false`。

### 1.5 每个 Task 的固定结束动作

1. 复核实际 diff 只包含本卡允许路径和必要状态记录。
2. 运行本卡定向检查、受影响 Micro 回归、Product/SPEC/A1 artifact validators 和 `git diff --check`。
3. 记录所有失败尝试、真实 exit code 和未执行项。
4. 更新当前 Task 为 `completed`、`blocked` 或保持 `in_progress`；不得用“基本完成”。
5. 仅在完成条件全部满足时，把 `next_single_action` 指向下一 Task。
6. 完成一个 Task 后停止；不得在同一实施轮顺手开始下一 Task。

## 2. 总映射

| Task | 主要职责 | Acceptance Scenario | Exact Upstream Test Ref | 主要实现文件 |
|---|---|---|---|---|
| `AS-TASK-001` | A1 additive schema/store/seed | `AS-010` 基础 | `HTH-AT-006/007/008/009/013` | `schema.sql`、`store.py` |
| `AS-TASK-002` | AnswerEnvelope 与直接 Evidence 选择 | `AS-001/002/008/009` | `SOM-AT-008/009/018`、`BTE-AT-020/021/034`、`SIP-AT-006` | `answers.py` |
| `AS-TASK-003` | Coverage 评估 | `AS-005/007` | `BTE-AT-012/013/025` | `answers.py` |
| `AS-TASK-004` | 显式 Freshness 评估 | `AS-006` | `BTE-AT-026/027` | `answers.py` |
| `AS-TASK-005` | 最小冲突检测 | `AS-004` | `SOM-AT-021`、`BTE-AT-030` | `answers.py` |
| `AS-TASK-006` | Unconfirmed、adapter、确定性只读闭合 | `AS-003/010` | `BTE-AT-024`、`HTH-AT-006/007/008/009/013` | `answers.py`、`answer_testing_adapter.py` |
| `AS-TASK-007` | 结果失败与运行边界硬化 | `AS-011` | `HTH-AT-002/019/020/023` | `answer_testing_adapter.py`；suite 文件默认只读 |
| `AS-TASK-008` | A1 统一验证与 Micro 回归 | 全部 | 35 个 A1 required IDs + 49 个 Micro required IDs | 新 result 与状态记录 |
| `AS-TASK-009` | Trace、审计门禁和 Recovery Point | Process | 不新增业务 Test ID | Matrix、Gate、Recovery、Git refs |

场景在多个 Task 出现时表示“前置能力”与“最终闭合”分工，不允许跨 Task 拼接为 suite passed。Scenario-to-upstream 的唯一集合仍以 `ACCEPT-MVP-A-AS-001` §7 和 A1 manifest 为准。

## 3. `AS-TASK-001`：A1 additive store/schema seed

### 3.1 入口门禁

- 全局入口条件全部满足。
- `next_single_action=AS-TASK-001`。
- A1 fixture/oracle 已通过 materialization validator，且数据库 case identity 互相隔离。
- 既有 Micro 49/49 result 只作为历史证据；本 Task 必须运行受影响的 Micro store/adapter 定向回归。

### 3.2 权威输入

- ADR-0002 §2、§4-§7。
- Architecture §1-§5 的 `SemanticStore`、case isolation 和全层 digest。
- Acceptance §3、§5 `AS-010`、§6 `AS-INV-008/009`、§7 的 HTH refs。
- S1 §5.3、§6.2；S2 §6.5-§6.7；S6 §6、§9。
- materialized A1 fixture、oracle、adapter protocol；不得从未来 evaluator 推断 seed 形状。

### 3.3 允许文件

- `src/noetide_micro/schema.sql`
- `src/noetide_micro/store.py`
- `src/noetide_micro/__init__.py`，仅在需要导出新稳定类型时
- 可选窄测试：`tests/semantic/test_answer_task_001_store.py`
- §1.3 的公共记录

其他业务文件禁止修改。

### 3.4 必须行为

1. 只做加法式 A1 逻辑存储，既有 Micro 表、约束和 seed 行为保持兼容。
2. 固定保存 A1 Source、Canonical Assertion、CoverageWindow、candidate/derived test input 所需的最小结构；物理表名由实现决定，但逻辑层不得混用。
3. `foreign_keys=ON`、`journal_mode=DELETE`、`synchronous=FULL` 继续生效。
4. schema 初始化可重复；同一 fixture seed 幂等，不重复写行。
5. 相同 fixture identity + 不同 payload 必须拒绝，不覆盖数据库。
6. 任一 seed 字段、引用、hash/locator 或 synthetic 声明非法时整包失败，不留下部分 seed。
7. 提供只读 snapshot/digest/count 能力，覆盖 Source、Canonical、Ledger、Projection；digest 规则确定且不读墙钟。
8. A1 seed 不创建 ChangeSet、Canonical revision 增量、Ledger 业务事件或新 Projection。

### 3.5 明确禁止

- trigger、stored procedure 或 seed 过程判定 Answer Status。
- 修改 Micro `rev_010` fixture 或把 A1 case 注入旧 Micro 数据库。
- 在此 Task 创建 `answers.py` 业务判断、AnswerEnvelope 或 conflict/freshness 逻辑。
- 把 Derived input 写入 `canonical_evidence_refs`。

### 3.6 Task 验证

- Python compile/import。
- A1 schema 初始化、PRAGMA、外键、重复 seed、冲突 seed、失败原子性和 11 case isolation 的窄测试。
- Micro `test_task_001_store`、`test_task_002_adapter`；若共享 store 影响其他 Micro 测试，扩大到相应定向集合。
- Product/SPEC/A1 artifact validators 和 `git diff --check`。
- 完整 A1 runner：`not_executed`。

### 3.7 完成与交接

全部验证符合预期、无产品歧义、Micro 定向回归通过后，Task=`completed`，下一动作=`AS-TASK-002`。任一 schema 需求不能由 fixture/ADR 唯一确定时停线回 Planning Gate。

## 4. `AS-TASK-002`：AnswerEnvelope 与 EvidenceSelector

### 4.1 入口门禁

- `AS-TASK-001=completed`，`next_single_action=AS-TASK-002`。
- store 只读接口与 protocol 可满足独立 case 查询，不需要补产品字段。

### 4.2 权威输入

- Acceptance §4、`AS-001/002/008/009`、`AS-INV-001/002/004/007/008`。
- S1 §6.4、§11；S2 §6.6-§6.9、§11.2；S7 §11。
- `SOM-AT-008/009/018`、`BTE-AT-020/021/034`、`SIP-AT-006`。
- Architecture 的 `EvidenceSelector`、`AnswerEvaluator` 禁止责任。

### 4.3 允许文件

- 新建 `src/noetide_micro/answers.py`
- `src/noetide_micro/__init__.py`，仅导出本 Task 的稳定值类型/异常
- 可选窄测试：`tests/semantic/test_answer_task_002_evidence.py`
- §1.3 的公共记录

默认不允许修改 schema/store/adapter 或 materialized suite。

### 4.4 必须行为

1. `AnswerEnvelope` 字段至少与 Acceptance §4 完全一致；主状态使用封闭六态。
2. 非 `verified` 回答的 `verification_scope=null`。
3. EvidenceSelector 只接受授权的直接 Source locator；locator 缺失/非法不得补造。
4. confirmed opinion 只能在 `viewpoint` scope 验证“主体持有观点”。
5. confirmed reported Assertion 只能在 `statement_occurrence` scope 验证陈述发生；world claim 不自动 verified。
6. Projection、旧 AnswerEnvelope、摘要和 receipt 被排除，并产生稳定非泄露 reason。
7. fictional Assertion 不进入现实 world claim evidence，且 Canonical kind 不变。
8. evaluator 为纯读取；不得调用 store 的 mutation 方法。

### 4.5 明确禁止

- 定义通用 world-claim 强证据规则、默认 scope 或 evidence score 阈值。
- 通过 Assertion 数量、模型 confidence 或 review 时间提高真值。
- 将 EvidenceAssessment/AnswerEnvelope 持久化为 Canonical 或事实 evidence。
- 在本 Task 实现 Coverage、freshness 或 conflict precedence。

### 4.6 Task 验证

- 定向执行 `AS-001/002/008/009`；核对 exact status/value/scope/evidence/reason。
- 对查询前后 Source/Canonical/Ledger/Projection digest 做不变比较。
- 重复同一 query 的结构化语义结果一致。
- 运行 Task 001 store tests 和受影响 Micro 定向测试。
- validators、compile/import、`git diff --check`。

### 4.7 完成与交接

四个场景定向通过且无越权规则后，下一动作=`AS-TASK-003`。若 world claim 要求未由 fixture 唯一声明，停线，不创建默认验证规则。

## 5. `AS-TASK-003`：CoverageEvaluator

### 5.1 入口门禁

- `AS-TASK-002=completed`，`next_single_action=AS-TASK-003`。

### 5.2 权威输入

- Acceptance `AS-005/007`、`AS-INV-003`。
- S2 §6.5、§6.9、§10.3、§14；`BTE-AT-012/013/025`。
- Architecture 的 `CoverageEvaluator` 边界。

### 5.3 允许文件

- `src/noetide_micro/answers.py`
- 可选窄测试：`tests/semantic/test_answer_task_003_coverage.py`
- §1.3 的公共记录

### 5.4 必须行为

1. query valid scope 在 CoverageWindow 外时返回 `not_covered` 并列起点/gap。
2. `continuity=unknown` 且零结果的否定查询返回 `not_covered`，不得返回 verified negative 或 unknown。
3. 覆盖充分、无 candidate/conflict/verification/freshness failure 时返回 `unknown`。
4. Coverage declaration/receipt 只支持覆盖判断，不进入事实 `evidence_refs`。
5. 返回实际 window、gap、continuity 与 completeness，不合并成虚假完整覆盖。

### 5.5 明确禁止

- 将搜索零结果解释为“事件未发生”。
- 自动合并多个窗口或发明 coverage precedence。
- 写 Canonical unknown State。
- 在此 Task 加 freshness 或 conflict 逻辑。

### 5.6 Task 验证

- 定向执行 `AS-005/007` 的全部 query variant。
- 断言 `not_covered != unknown`，coverage/reason 字段级匹配 oracle。
- 查询前后全层 digest 不变；重复查询确定。
- 回归 `AS-001/002/008/009` 和受影响 Micro tests。

### 5.7 完成与交接

覆盖与 unknown 边界闭合后，下一动作=`AS-TASK-004`。出现“正向证据 + coverage gap”等未在 A1 固定 case 中的复合条件时停线，不扩展 precedence。

## 6. `AS-TASK-004`：显式 FreshnessEvaluator

### 6.1 入口门禁

- `AS-TASK-003=completed`，`next_single_action=AS-TASK-004`。

### 6.2 权威输入

- Acceptance `AS-006`、`AS-INV-006`。
- S2 §6.7、§6.9、§11.3；`BTE-AT-026/027`。
- fixture 中显式、版本化 policy；该 policy 不是产品默认。

### 6.3 允许文件

- `src/noetide_micro/answers.py`
- 可选窄测试：`tests/semantic/test_answer_task_004_freshness.py`
- §1.3 的公共记录

### 6.4 必须行为

1. 只读 fixture Clock，不读业务墙钟。
2. 只在 query 明确要求当前性且 fixture policy 适用、证据超期时返回 `stale`。
3. `stale` 返回 `assessment_policy_ref`、`evaluated_at` 和证据有效时间。
4. 同一证据用于匹配 historical valid time 时，不得仅因当前年龄 stale。
5. Answer freshness 不读取或改变 Projection freshness。

### 6.5 明确禁止

- 定义任何产品默认 freshness 时长。
- 把 View fresh 提升为 Answer verified，或把 View stale 直接映射为 Answer stale。
- 使用系统当前时间、文件 mtime 或 runner wall time作为业务时间。

### 6.6 Task 验证

- 定向执行 AS-006 current/historical query，字段级比较。
- 注入不同机器墙钟不影响语义结果。
- 回归已完成 A1 场景、全层 digest 和受影响 Micro tests。

### 6.7 完成与交接

AS-006 两种时间查询闭合后，下一动作=`AS-TASK-005`。fixture policy 缺失或不唯一时必须初始化失败，不能回落默认值。

## 7. `AS-TASK-005`：ConflictDetector

### 7.1 入口门禁

- `AS-TASK-004=completed`，`next_single_action=AS-TASK-005`。

### 7.2 权威输入

- Acceptance `AS-004`、`AS-INV-005`。
- S1 §13；S2 §5.3、§13；`SOM-AT-021`、`BTE-AT-030`。
- Architecture 的 `ConflictDetector` 禁止自动选胜者。

### 7.3 允许文件

- `src/noetide_micro/answers.py`
- 可选窄测试：`tests/semantic/test_answer_task_005_conflict.py`
- §1.3 的公共记录

### 7.4 必须行为

1. 只比较同 subject、predicate/互斥 state kind、重叠 valid time、同 perspective/claim scope 的不兼容值。
2. 未裁决冲突返回 `disputed`、`answer_value=null`。
3. 并列返回两方授权直接 evidence、valid time 和 perspective。
4. 输入顺序变化不得改变状态或选择某一方。
5. 查询只读，不创建 `in_dispute` 修订、ChangeSet 或冲突裁决。

### 7.5 明确禁止

- 按 `recorded_at`、证据数量、文案长度、模型 confidence 或排序位置选胜者。
- 将不同 perspective 的观点自动视为客观冲突。
- 引入通用冲突规则 DSL 或实现冲突裁决 UI。

### 7.6 Task 验证

- 定向执行 AS-004，交换两方输入顺序并比较结构化结果。
- evidence refs 集合、valid time、perspective 与 oracle 一致。
- 回归 AS-001..009 已完成场景、全层 digest 和 Micro tests。

### 7.7 完成与交接

AS-004 闭合后，下一动作=`AS-TASK-006`。若 fixture 出现多个主状态条件同时成立且合同未定义优先级，停线回 SPEC/Acceptance。

## 8. `AS-TASK-006`：Unconfirmed、adapter 与确定性只读

### 8.1 入口门禁

- `AS-TASK-005=completed`，`next_single_action=AS-TASK-006`。
- `answers.py` 已覆盖 verified/disputed/not_covered/stale/unknown 的固定 case。

### 8.2 权威输入

- Acceptance `AS-003/010`、全部 `AS-INV-*` 中只读/确定性项。
- S2 §6.9、`BTE-AT-024`。
- S6 §6-§14、`HTH-AT-006/007/008/009/013`。
- materialized adapter protocol，方法签名不得自行改变。

### 8.3 允许文件

- `src/noetide_micro/answers.py`
- 新建 `src/noetide_micro/answer_testing_adapter.py`
- `src/noetide_micro/__init__.py`，仅必要导出
- 可选窄测试：`tests/semantic/test_answer_task_006_adapter.py`
- §1.3 的公共记录

schema 和 suite artifact 默认只读。

### 8.4 必须行为

1. 覆盖充分且只有可见未审 Candidate 时返回 `unconfirmed`。
2. Candidate 只可出现在允许的 reason/candidate 引用，不进入 Canonical `evidence_refs`。
3. adapter 逐项实现 materialized Protocol，使用独立 per-case data root 和 fixture Clock。
4. adapter 只接受 `synthetic=true`、工作区内临时路径和 manifest 绑定 fixture。
5. 同一 case/query/policy/Clock 重放两次，除明确排除运行元数据外语义结果相同。
6. 每次查询前后 `data_revision`、Source count/digest、Canonical digest、Ledger count/digest、Projection count/digest 均相同。
7. A1 case 之间使用独立数据库 identity，关闭/失败不污染其他 case。
8. adapter 是 test-only，不建立产品 API。

### 8.5 明确禁止

- Candidate 自动确认、写 Canonical 或升级为 Fact。
- adapter 接受任意路径、真实 fixture、环境当前时钟或网络资源。
- 为通过 Protocol 增加未在 Architecture/Acceptance 中出现的业务方法。
- 修改 `testing_adapter.py` 破坏旧 Micro adapter。

### 8.6 Task 验证

- 定向执行 `AS-003/010`，并回归 `AS-001..009` 全部场景。
- Protocol runtime check、11 case isolation、重复查询、digest/count 不变。
- 网络 socket 被 runner 阻断时仍可完整运行；路径逃逸和非 synthetic fixture 拒绝。
- 运行受影响 Micro adapter/完整定向测试、validators 和 diff check。

### 8.7 完成与交接

AS-001..010 定向场景都可执行且只读证明完整后，下一动作=`AS-TASK-007`。定向通过仍不设置 suite executed/passed。

## 9. `AS-TASK-007`：结果失败与运行边界硬化

### 9.1 入口门禁

- `AS-TASK-006=completed`，`next_single_action=AS-TASK-007`。
- materialized runner 已定义不可覆盖输出和 result failure injection；本 Task 不得静默改 suite。

### 9.2 权威输入

- Acceptance `AS-011`、`AS-INV-009/010`。
- S6 §6.3、§7、§9、§14、§15；`HTH-AT-002/019/020/023`。
- ADR-0002 §5 的 result write failure。

### 9.3 允许文件

- `src/noetide_micro/answer_testing_adapter.py`
- 可选窄测试：`tests/semantic/test_answer_task_007_hardening.py`
- §1.3 的公共记录

Materialized manifest、fixture、oracle、semantic test 和 runner 默认只读。若 AS-011 失败源于 suite 工件缺陷，必须停止、把 suite 标为 superseded 并回 `AS-PRE-*`，不得在业务 Task 中偷改测试。

### 9.4 必须行为

1. adapter 对工作区外路径、非 synthetic fixture、manifest/fixture identity 不匹配 fail closed。
2. 测试运行不访问网络；任何访问尝试使 run failed/errored。
3. result writer 注入失败时不存在 current passed artifact，不覆盖旧 result，不把 suite 标 passed。
4. required missing/skip 为 partial；assertion mismatch 为 failed；runner/environment error 为 errored。
5. 失败日志和 structured result 执行隐私扫描；命中后不发布 pass。
6. 输出只写仓库允许的 result 目录，目标已存在时拒绝。

### 9.5 明确禁止

- 捕获写入错误后仍返回 exit code 0。
- 删除临时失败证据来制造 clean pass。
- 在 result 中写凭据、本机用户路径或 fixture 原文以外的环境隐私。
- 以定向 AS-011 self-check 更新 manifest 的 suite passed flag。

### 9.6 Task 验证

- 执行 AS-011 的 result write failure self-check，并确认输出不存在/旧文件不变、exit code 非 0。
- 执行 output exists、path escape、network attempt、privacy pattern、required missing 的窄失败测试。
- 正常定向 A1 场景仍可执行；Micro 回归不受影响。
- 完整 A1 runner仍为 `not_executed`，留待 AS-TASK-008。

### 9.7 完成与交接

失败路径均诚实且未改 suite expected 后，下一动作=`AS-TASK-008`。

## 10. `AS-TASK-008`：统一 Verification

### 10.1 入口门禁

- `AS-TASK-001..007=completed`，`next_single_action=AS-TASK-008`。
- 实现 diff 冻结，工作树无无法归属的相关改动。
- manifest/fixture/oracle/runner hash 当前，Implementation Adapter 路径已填入计划但不改 expected。

### 10.2 权威输入

- A1 manifest 的 11 scenario + 24 unique upstream refs = 35 required IDs。
- Micro manifest 的 10 scenario + 39 upstream refs = 49 required IDs。
- S6 的同一次 run、结果枚举、不可覆盖和 applicability 合同。

### 10.3 允许文件

- 新 A1 result：`docs/testing/results/<unique-a1-run>.json`
- 新 Micro regression result：`docs/testing/results/<unique-micro-run>.json`
- A1/Micro manifest 的 latest-result metadata，仅在对应 run 完整有效后
- `docs/testing/LATEST_STATIC_VALIDATION.md` 或当前验证记录
- Matrix、Plan、PROJECT_STATE、CURRENT_HANDOFF 的真实结果字段

禁止修改 `src`、fixture、oracle、scenario、semantic tests 或 runner。发现缺陷只记录结果并转 Debug，不在 Verifier 角色修复。

### 10.4 必须行为

1. 冻结实际命令、adapter、git commit、manifest/fixture/oracle/implementation hash 和环境。
2. 一次 A1 run 产生 35 个 required result；缺失、skip 或跨 run 不能 passed。
3. 在同一实现提交上执行一次完整 Micro regression，产生 49 个 required result。
4. 两类 result 使用不同 run ID/文件，旧 result 不覆盖。
5. 记录 Python/SQLite/OS、网络状态、业务 Clock 来源、exit code、开始/结束和 privacy scan。
6. 任一 run 非 passed 时 Gate closed，next action 指向 independent audit/Debug triage，不得选择漂亮子集。

### 10.5 完成与交接

只有 A1 35/35 与 Micro 49/49 均在各自一次 current run 中 passed，Task 才为 `completed`，切片进入 `verified`，下一动作=`independent_audit`。否则保存真实结果并保持 Gate closed。

## 11. `AS-TASK-009`：Trace、Gate 与 Recovery Point

### 11.1 入口门禁

- current A1 与 Micro result 均有效。
- Independent Auditor 已提交只读报告；P0=0、P1=0。
- 若经过 Debug，原 Finding、新 result 和独立 Re-audit 关闭证据全部存在。
- `next_single_action=AS-TASK-009`。

### 11.2 允许文件与动作

- Requirements Matrix 的 A1 Implementation Module/Verification Result 回填。
- PROJECT_STATE、CURRENT_HANDOFF、Approved Plan 最终状态。
- 当前实现后 Gate Review、Recovery Record。
- 只暂存当前切片文件，创建范围单一 commit、annotated tag，推送 branch/tag，并核验远端 refs。

禁止改 PRD/SPEC/ADR/Acceptance、业务代码、suite expected、旧 result 或旧 tag。禁止创建公开 GitHub Product Release、改变仓库可见性或通知外部用户。

### 11.3 必须行为

1. Trace 链闭合到实际模块和 current result，不夸大 FR-002/008/010 的长期完成度。
2. Gate Review 检查范围、隐私、只读不变量、A1/Micro result、Git diff 和恢复步骤。
3. Recovery Record 写出 commit/tag、artifact digest、恢复与重验命令、已知限制。
4. PRD v0.5/current hash 与 v0.4 历史 hash 匹配；真实数据/凭据扫描通过。
5. annotated tag 不移动，push 后从远端解析 branch/tag/peeled commit。

### 11.4 完成定义

- `AS-TASK-001..009=completed`。
- A1 阶段=`recovery_point_published`。
- A1 35/35、Micro 49/49 current 结果可定位。
- Audit/Re-audit P0=0/P1=0。
- Recovery commit/tag/remote/record 四者一致。
- 下一动作只可指向下一个 Product Slice 的 Product Decision/Gate，不得直接实现 A2。

## 12. 统一停线条件

以下任一情况发生时，当前 Task 不得继续：

- 产品或 SPEC 对预期状态、字段、scope、Coverage、freshness 或 conflict 有两种合理解释。
- 两个主 Answer Status 条件同时成立，但 A1 fixture/Acceptance 未定义唯一 case。
- 需要产品默认 freshness policy、world-claim 强证据规则或冲突 precedence。
- materialized suite 与 Approved SPEC/Acceptance 不一致，或 expected 只能从 actual 生成。
- 需要写 Canonical/Ledger/Projection、调用 ChangeSet 或引入权限/MCP/LLM/外部服务。
- 发现真实数据、凭据、工作区外访问、网络访问或路径逃逸。
- 旧 Micro 行为回归，或只能修改旧 expected 才能通过。
- `apply_patch` filesystem sandbox helper 失败。
- 工作树出现无法归属且与当前 Task 重叠的改动。

停线后将问题写入 Finding、Gate Review 或 `OPEN_QUESTIONS.md`；不得只在聊天里说明，也不得让低模型自行选择答案。
