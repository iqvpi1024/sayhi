# 项目状态

## 1. 恢复入口

任何新任务必须按顺序读取：

1. `docs/product/CURRENT_PRODUCT_BASELINE.md`
2. 读取其中 `current_prd_path` 指向的完整 PRD
3. `docs/PROJECT_STATE.md`
4. `docs/decisions/OPEN_QUESTIONS.md`
5. `docs/process/README.md`
6. 当前切片适用的 Approved SPEC
7. `docs/traceability/REQUIREMENTS_MATRIX.md`
8. 当前 suite/verification 记录
9. 当前 ADR、Implementation Plan 和 Gate Review

当前规划入口：`MASTER_DELIVERY_ROADMAP.md`、`MVP_A_ANSWER_SAFETY_SLICE_DECISION_2026-07-17.md`、`MODEL_HANDOFF_PROTOCOL.md`。上一已完成切片的恢复证据继续由 `MICRO_MVP_V0.1_RECOVERY_POINT.md` 保存。

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试、示例和 fixture 只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-17 |
| 当前切片 | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| 当前切片交付阶段 | `architecture_decided` |
| 开发门禁 | `closed`；当前只允许执行 `PLAN-MVP-A-AS-SUITE-001` 的 `AS-PRE-001..005` |
| 当前 PRD | `PRDv05.md` v0.5，`Approved Product Baseline` |
| PRD v0.5 canonical LF SHA-256 | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 历史 PRD | `PRDv04.md` v0.4，`superseded_read_only`，hash `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | 仓库基线全部 `Approved`；A1 的 S1/S2/S3/S6/S7 applicability 已复核通过并保持 current |
| 产品问题 | A1 blocking=0；`DQ-012` 不重开，其他 `DQ-*` 按阶段 deferred |
| Finding | P0=0、P1=0、P2=0；P3=1 accepted debt（`MMF-017`） |
| 追踪 | 现有 32/32 FR 基线有效；A1 映射覆盖 FR-002/008/010，exact required set 为 11 个场景 + 24 个唯一 upstream refs = 35 IDs |
| 上一 Micro 结果 | `MM-001..010` + 39 upstream refs，49/49 passed；保持 current historical evidence |
| A1 Suite | `defined=true`、`materialized=false`、`executed=false`、`passed=false` |
| A1 Business Verification | `not_executed` |
| A1 Business Implementation | `absent` |
| A1 ADR / Architecture | `ADR-0002 Accepted`；`ARCH-MVP-A-AS-001 Accepted Design Baseline` |
| A1 Implementation Plan | `Draft - blocked by suite_materialized=false`；不可执行 `AS-TASK-*` |
| A1 技术基线 | Python 3.12 stdlib + 单进程 SQLite 的加法式查询切片；只限 A1，不是长期技术栈承诺 |
| 依赖 / 数据库实例 | 未安装依赖；未创建数据库实例 |
| Git | 分支 `codex/mvp-a-answer-safety-planning` 已推送；tag `mvp-a-answer-safety-planning-v0.1-approved` 已推送并指向 `bf333a30b5f4df7b06c63dd6dd9dbb4569f31dca`。上一 Micro tag 保持不变 |

## 3. 本阶段完成内容

1. 恢复读取 S1-S9 后关闭三类开发前残留：S1 状态摘要、S2 上游/测试四态、S6 验收表列结构。
2. 仅升版实际变更的 S1/S2/S6，复审确认 S3-S5/S7-S9 保持 current-compatible。
3. Accepted `ADR-0001`：当前 Micro 使用 Python 标准库、单进程 SQLite 事务和 JSON 测试工件，不选择长期平台。
4. 建立 `ARCH-MICRO-REL-001`，固定 Source/Canonical/Ledger/Projection、写读失败和信任边界。
5. 物化 exact Micro suite：manifest、完整合成 fixture、结构化 oracle、10 场景计划、adapter protocol、test module 和离线 runner。
6. 建立并批准 `PLAN-MICRO-REL-001`，7 个目标模块、TASK-001..010 全部 pending。
7. 开发前 Gate Review 结论 yes；没有业务源码、依赖、数据库实例或业务结果。
8. Python/JSON/Markdown/PowerShell 的 Git EOL 策略固定为 LF，manifest raw-byte digest 可在恢复后复算。
9. TASK-001 已建立 `src/noetide_micro` 最小 SQLite persistence foundation：Source/Canonical/Ledger/Projection 逻辑分层表、显式事务、`foreign_keys=ON`、`journal_mode=DELETE`、`synchronous=FULL` 与 `rev_010` 合成 seed；没有业务 trigger。
10. TASK-002 已建立 test-only adapter factory 与 fixture 固定 Clock。factory 仅接受仓库内临时 data root 和合成 fixture，并满足 runner Protocol 的结构检查；尚未实现 Intake、Candidate、ChangeSet、Query 或 View 业务行为。
11. TASK-003 已实现固定合成 Source Append：校验明确 request、UTF-8 byte length/hash、Source policy 初始化和 receipt；成功不改变 Canonical `rev_010`，失败返回 rejected 且不落 Source。
12. TASK-004 已实现一个未确认的 allowlisted `end + add` contact ChangeSet、preview 和单次确认；proposal 不写 Canonical 或 Projection。
13. TASK-005 已实现 publish attempt、base revision preflight、idempotency binding/receipt 与 SQLite L1 原子发布；第二 proposal 失败全回滚，stale base 进入 conflicted，retry 创建新 ChangeSet。
14. TASK-006 已实现 Canonical relationship contact 半开区间查询、两 Source evidence 隔离和 protected snapshot。
15. TASK-007 已实现 `person_card`、`relationship_timeline` 投影、Publish Barrier 读取和单 View 失败的 Canonical fallback/reconcile。
16. TASK-008 已实现整包补偿撤销、新 `rev_012`、审计 event 和两个 View 的撤销后收敛。
17. TASK-009 已在 `195a8fb2dfe3716c1f97a19edd8d7ec5c34d80de` 上通过正式离线 runner；`docs/testing/results/micro-task009-lf-20260717.json` 记录 49 个 required result IDs 全部 `passed`，exit code `0`，仅使用合成数据且隐私扫描通过。
18. TASK-010 已完成：实现后 Gate Review P0=0、P1=0；annotated tag `micro-mvp-v0.1-validated` 和分支已推送，远端引用已核验。
19. 建立 `ROADMAP-NOETIDE-001`，按 MVP-A、MVP-B、MVP-C、Year 2 和长期阶段拆分交付切片与依赖。
20. 建立 `MODEL_HANDOFF_PROTOCOL.md`，固定 Planner、Implementer、Auditor、Debugger 和 Releaser 的顺序与交接证据。
21. 建立 `ONE_CLICK_DELIVERY_PLAN.md`，把开发启动、评审包、普通用户安装包和 GitHub Release 分为 D0-D3 门禁。
22. `DEC-MVP-A-AS-001` 选择 A1 Answer Safety 为下一切片；只授权 SPEC applicability review，不授权代码、ADR、suite 或 Implementation Plan。
23. `GATE-MVP-A-AS-PRODUCT-001` 通过，P0=0、P1=0；产品、SPEC 和既有 Micro artifact 静态校验均 exit code `0`。
24. 路线图与 A1 Product Decision 已建立 Git Recovery Point；分支和 annotated tag 已推送并核验。
25. `REVIEW-MVP-A-AS-SPEC-001` 完成 S1/S2/S3/S6/S7 applicability review：全部适用合同保持 current，无需修改正式 SPEC。
26. 建立 `ACCEPT-MVP-A-AS-001`：固定 AS-001..011、24 个唯一 upstream refs 和 35 个 required result IDs；当前只达到 `suite_defined=true`。
27. Requirements Matrix §4.1 已建立 A1 active-slice 追踪，覆盖 FR-002/008/010，Implementation Module 仍为 `TBD`，Verification 为 `not_executed/current`。
28. Accepted `ADR-0002`：A1 延续 Python 3.12 stdlib + 单进程 SQLite，只新增固定合成 Coverage/Answer evaluator，不建设通用问答、服务或规则平台。
29. 建立 `ARCH-MVP-A-AS-001`，固定 Evidence/Coverage/Conflict/Answer 只读数据流、case 隔离和查询前后全层 digest 不变证明。
30. 批准 `PLAN-MVP-A-AS-SUITE-001` 仅用于物化 suite；`AS-PRE-001..005` 未开始，禁止创建 A1 业务实现。
31. 建立 `PLAN-MVP-A-AS-IMPL-001` Draft；在 suite materialized 和开发前 Gate 通过前，`AS-TASK-001..009` 全部 blocked。
32. `GATE-MVP-A-AS-PRE-SUITE-001` 通过，P0=0、P1=0、P2=0、P3=1；只授权 suite 物化，不授权业务开发。

## 4. 当前 A1 规划验证

2026-07-17 在分支 `codex/mvp-a-answer-safety-planning`、起始 HEAD `c4ec6b45970e00b1dd92a82aa9a1bca2a5342370` 的规划工作树上实际执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
python .\tools\validate_micro_suite.py
git diff --check
```

最终均 exit code `0`。A1 exact mapping 另经机器解析为 11 个场景、24 个唯一 upstream refs、35 个 required IDs，exit code `0`。这些结果只证明产品/SPEC/Trace/既有 Micro 工件和规划范围静态有效；A1 `suite_materialized=false`、业务测试 `not_executed`。

第一次 SPEC validator 因 A1 子表 FR 单元格被旧正则误计为第二套主表而 exit code `1`；将三个 active-slice FR 单元格改为 Markdown code identifiers 后复跑通过，未改变任何业务合同。完整环境、digest 和未证明项见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

### 4.1 开发前静态验证记录（历史）

最终实际执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
python .\tools\validate_micro_suite.py
powershell -ExecutionPolicy Bypass -File .\tools\validate_pre_development_gate.ps1
git diff --check
```

最终均 exit code 0。

| 检查 | 结果 |
|---|---|
| PRD hash / index | v0.4 immutable 与 v0.5 Approved passed |
| SPEC structure | 275 Test ID；133 Invariant；20 closed enum passed |
| Traceability | 32 FR；174 唯一 Test Ref；9/8/15 Coverage passed |
| Micro contract | 10 场景、39 upstream refs、两个 58-byte Source passed（静态合同） |
| Suite materialization | manifest、8 artifact digest、3 protected seed、stdlib AST、隐私预检 passed |
| Development Gate | ADR/Plan/13 前置产物、0 产品阻塞、无业务源码/依赖/result、PRD diff=0 |
| Diff hygiene | `git diff --check` passed |
| Business tests | 当时为 `not_executed`；已由 TASK-009 的正式 result 取代 |

TASK-001/TASK-002 的初始定向验证曾实际运行：

```powershell
$env:PYTHONPATH='src'; python -m unittest -v tests.semantic.test_task_001_store tests.semantic.test_task_002_adapter
```

exit code `0`，共 7 项测试通过。当时完整 `tests.runner.run_micro_suite` 尚未运行；该历史状态已由 TASK-009 的正式 current result 取代。

2026-07-17 恢复核验再次实际运行同一 TASK-001/TASK-002 命令，exit code `0`，7/7 通过；并运行 `$env:PYTHONPATH='src'; python -m compileall -q src\\noetide_micro tests\\semantic`，exit code `0`。该次核验只证明 TASK-001/002 的窄范围基础能力，不构成完整 Micro suite 结果。

详细环境、工具 hash、输出 digest 和诊断失败见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

## 5. 当前权威产物

| 文件 | 当前职责 |
|---|---|
| `docs/product/CURRENT_PRODUCT_BASELINE.md` | 当前/历史 PRD 唯一指针和 hash |
| `PRDv05.md` | 当前 Approved 产品需求基线 |
| `docs/planning/MASTER_DELIVERY_ROADMAP.md` | 全项目切片路线、依赖和发布目标 |
| `docs/process/MODEL_HANDOFF_PROTOCOL.md` | 不同模型顺序接力和证据交接协议 |
| `docs/releases/ONE_CLICK_DELIVERY_PLAN.md` | D0-D3 一键部署与 GitHub Release 门禁 |
| `docs/decisions/MVP_A_ANSWER_SAFETY_SLICE_DECISION_2026-07-17.md` | 当前 A1 Product Decision |
| `docs/reviews/MVP_A_ANSWER_SAFETY_PRODUCT_GATE_2026-07-17.md` | A1 Product Gate Review |
| `docs/releases/MVP_A_ANSWER_SAFETY_PLANNING_V0.1_RECOVERY_POINT.md` | 当前规划恢复说明 |
| `docs/reviews/MVP_A_ANSWER_SAFETY_SPEC_APPLICABILITY_2026-07-17.md` | A1 适用 SPEC 复核与范围边界 |
| `docs/testing/MVP_A_ANSWER_SAFETY_ACCEPTANCE.md` | A1 人类可读 exact 合同与 35-ID required 集合 |
| `docs/adrs/ADR-0002_ANSWER_SAFETY_RUNTIME_AND_STORAGE.md` | A1 运行时与持久化增量技术决定 |
| `docs/architecture/MVP_A_ANSWER_SAFETY_ARCHITECTURE.md` | A1 只读组件、数据与失败边界 |
| `docs/testing/MVP_A_ANSWER_SAFETY_SUITE_MATERIALIZATION_PLAN.md` | A1 suite-only 物化计划 |
| `docs/planning/MVP_A_ANSWER_SAFETY_IMPLEMENTATION_PLAN_DRAFT.md` | A1 被 suite 门禁阻塞的未来施工草案 |
| `docs/reviews/MVP_A_ANSWER_SAFETY_PRE_SUITE_GATE_2026-07-17.md` | A1 architecture_decided -> suite_materialization 门禁 |
| `docs/specs/01..09` | 当前 Approved 语义合同 |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | 32 FR 的当前追踪 |
| `docs/adrs/ADR-0001_MICRO_RUNTIME_AND_PERSISTENCE.md` | 当前切片运行时/事务技术决定 |
| `docs/architecture/MICRO_RELATIONSHIP_ARCHITECTURE.md` | 当前切片组件、数据和失败边界 |
| `tests/micro_suite_manifest.json` | exact required suite 唯一机器入口 |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | 人类可读 Micro 合同 |
| `docs/planning/MICRO_RELATIONSHIP_IMPLEMENTATION_PLAN.md` | 唯一施工计划与 TODO |
| `docs/reviews/MICRO_DEVELOPMENT_READINESS_GATE_2026-07-16.md` | 当前开发前 Gate |
| `docs/reviews/MICRO_MVP_IMPLEMENTATION_GATE_2026-07-17.md` | 实现后 Gate Review |
| `docs/testing/LATEST_STATIC_VALIDATION.md` | 最近实际静态/物化/Gate 验证 |
| `docs/testing/results/micro-task009-lf-20260717.json` | 当前 Micro 业务 Verification Result |
| `docs/releases/MICRO_DEVELOPMENT_READY_V0.1_RECOVERY_POINT.md` | Git 恢复与重验步骤 |
| `docs/releases/MICRO_MVP_V0.1_RECOVERY_POINT.md` | Micro 实现恢复点发布与重验步骤 |

## 6. 未决问题与后置项

- 当前 PRD/Micro blocking=0、important=0。
- `DQ-001..013` 均 deferred，按记录阶段重开；S2/S5/S8 的保守规则不等于永久产品决定。
- `MMF-017` 保持 P3：长期 275 个合同测试按切片逐套物化。
- 本 Micro suite 已执行，但它只证明固定单进程、离线、合成链路；不能外推为完整产品业务验证。
- 后续切片必须重新完成产品裁决、SPEC、Traceability、ADR、可执行 suite 和 Implementation Plan，不得复用 Micro 的 passed 结果。
- 权限 runtime、MCP、连接器、真实迁移、同步、财务、健康、决策、多 Agent、A2A、数字遗产继续禁止。
- A1 exact 合同、ADR、Architecture 和 suite 物化计划已存在；机器 manifest/fixture/oracle/runner 仍不存在，Implementation Plan 仍为 blocked Draft。
- A1 当前没有业务实现或业务结果；35 个 required result IDs 全部 `not_executed`，不得复用上一 Micro 的 49/49 pass。

## 7. 范围锁与风险

| 风险 | 当前控制 |
|---|---|
| 把物化 passed 当业务 passed | suite 状态与不可变业务 result 分开记录，并由 manifest hash 绑定 |
| 测试接口变成产品 API | `testing_adapter.py` 明确 test-only |
| SQLite 变成长期平台承诺 | ADR 限定当前 Micro，可由新 ADR 替换 |
| raw-byte digest 被 EOL 破坏 | `.gitattributes` 固定 `*.py/*.json/*.md/*.ps1` 为 LF |
| 运行数据落到仓库外 | runner/test 根固定 `tmp/micro-runs/` 且 Git ignore |
| 真实个人数据进入项目 | synthetic fixture、网络禁用和隐私扫描 |
| 开工扩大范围 | Plan 固定 10 tasks；每个停止条件回 Change Control |
| Bootstrap 端口被误当业务实现 | TASK-002 仍为 test-only factory；业务通过只限已记录的固定 Micro 合同 |
| 路线图被误当实施授权 | 每个 future slice 必须重新经过 Decision、SPEC、Trace、ADR、suite 和 Plan |
| 其他模型丢失上下文 | 强制按 `AGENTS.md` 和 `MODEL_HANDOFF_PROTOCOL.md` 恢复，聊天不是权威状态 |
| 六态复合条件诱发实现自定 precedence | 11 个 case 独立物化；出现未由 S2 唯一决定的组合即停止并回 SPEC |
| Draft Plan 被误当开工授权 | 明确 `suite_materialized=false`，只有 `AS-PRE-001..005` 可执行 |

## 8. 下一步唯一建议动作

**执行 `PLAN-MVP-A-AS-SUITE-001` 的 `AS-PRE-001`：只创建 A1 固定合成 fixture/oracle；不得编写业务代码。**

## 9. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 / Initial Specs | PRD v0.4 审查、产品裁决、S1-S9 与 Micro 合同 |
| 2026-07-14 | Corrective Gate | P1 关闭到 0；业务测试未执行 |
| 2026-07-15 | PRD v0.5 / SPEC Compatibility | v0.5 Approved；九份 SPEC current-compatible |
| 2026-07-16 | Development Readiness | SPEC 勘误、ADR、Architecture、suite materialization、Plan 和开发前 Gate 完成 |
| 2026-07-17 | MVP-A Answer Safety Architecture | SPEC applicability、A1 exact contract、Trace、ADR-0002、Architecture、suite-only Plan 和 Pre-Suite Gate 完成；业务开发门禁仍 closed |
