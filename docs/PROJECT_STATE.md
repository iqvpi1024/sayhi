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

当前技术入口：`ADR-0001_MICRO_RUNTIME_AND_PERSISTENCE.md`、`MICRO_RELATIONSHIP_ARCHITECTURE.md`、`tests/micro_suite_manifest.json`、`MICRO_RELATIONSHIP_IMPLEMENTATION_PLAN.md`、`MICRO_DEVELOPMENT_READINESS_GATE_2026-07-16.md`。

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试、示例和 fixture 只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-17 |
| 当前切片 | `SLICE-MICRO-RELATIONSHIP-001` |
| 当前切片交付阶段 | `verification_and_gate` |
| 开发门禁 | `open`；TASK-001..009 已完成，TASK-010 正在完成 Gate 与 Recovery Point |
| 当前 PRD | `PRDv05.md` v0.5，`Approved Product Baseline` |
| PRD v0.5 canonical LF SHA-256 | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 历史 PRD | `PRDv04.md` v0.4，`superseded_read_only`，hash `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | S1 v0.6；S2 v0.5；S3-S5 v0.4；S6 v0.5；S7-S8 v0.3；S9 v0.4，全部 `Approved/current` |
| 产品问题 | blocking=0、important=0；`DQ-001..013` deferred |
| Finding | P0=0、P1=0、P2=0；P3=1 accepted debt（`MMF-017`） |
| 追踪 | 32/32 FR current；Coverage Level 9 micro / 8 specified / 15 boundary |
| Micro required | `MM-001..010`；39 个去重 upstream refs；49 个 required result IDs |
| Suite | `defined=true`、`materialized=true`、`executed=true`、`passed=true`；结果绑定 `micro-task009-lf-20260717.json` |
| Business Verification | `passed`；同一次 current run 的 49/49 required result IDs passed |
| Business Implementation | TASK-001..009 已完成：最小 SQLite persistence、Source Append、ChangeSet publish、双时态查询、L2 Views、补偿撤销与完整离线 runner 验证；TASK-010 进行中 |
| ADR / Architecture | `ADR-0001 Accepted` / `ARCH-MICRO-REL-001` |
| Implementation Plan | `PLAN-MICRO-REL-001 Approved`；TASK-001..009 completed，TASK-010 in progress |
| 当前切片技术基线 | Python 3.12 stdlib + 单进程 SQLite；非长期最终技术栈 |
| 依赖 / 数据库实例 | 未安装依赖；未创建数据库实例 |
| Git | 分支 `codex/micro-development-readiness`；受测实现提交 `195a8fb2dfe3716c1f97a19edd8d7ec5c34d80de`；Micro Recovery Point 待发布 |

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

## 4. 开发前静态验证记录（历史）

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
- 业务 suite 未执行；所有业务行为仍待实现和真实 run 证明。
- TASK-003 起必须实现实际业务路径，不得将 TASK-002 的明确 `NotImplementedError` bootstrap 当作完成实现。
- TASK-003 的累计定向测试、产品基线与 SPEC 校验均 exit code 0；完整 suite 仍未执行。
- TASK-004/005 定向测试及正式 `MM-002`、`MM-009` 合约测试均 exit code 0；`MM-004` 的时间查询部分留待 TASK-006。
- TASK-006/007/008 定向测试和正式 `MM-004`、`MM-005`、`MM-006`、`MM-007`、`MM-008`、`MM-010` 合约测试均 exit code 0；完整 runner 仍未执行。
- 权限 runtime、MCP、连接器、真实迁移、同步、财务、健康、决策、多 Agent、A2A、数字遗产继续禁止。

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
| Bootstrap 端口被误当业务实现 | TASK-002 仅证明 factory/Clock/Protocol；完整 suite 保持未执行 |

## 8. 下一步唯一建议动作

**完成 `PLAN-MICRO-REL-001` 的 TASK-010：复核运行记录并创建 Gate Review、Recovery Record、annotated tag 和远端可解析的恢复点。**

## 9. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 / Initial Specs | PRD v0.4 审查、产品裁决、S1-S9 与 Micro 合同 |
| 2026-07-14 | Corrective Gate | P1 关闭到 0；业务测试未执行 |
| 2026-07-15 | PRD v0.5 / SPEC Compatibility | v0.5 Approved；九份 SPEC current-compatible |
| 2026-07-16 | Development Readiness | SPEC 勘误、ADR、Architecture、suite materialization、Plan 和开发前 Gate 完成 |
