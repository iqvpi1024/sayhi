# Implementation Plan：SLICE-MICRO-RELATIONSHIP-001

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MICRO-REL-001` |
| Status | `Approved` |
| Slice | `SLICE-MICRO-RELATIONSHIP-001` |
| Baseline Commit | `11e402864d84e03645ff468606949fcae3a68e75` |
| Accepted ADR | `ADR-0001` |
| Architecture | `ARCH-MICRO-REL-001` |
| Suite Manifest | `tests/micro_suite_manifest.json`；SHA-256 `54d70b993dbd5ce117605f6b07c305d2b97eba67df6a782c0e75f3afc28a5390` |
| Scope Owner | Noetide Technical Lead |

计划批准只表示任务边界可施工。所有任务当前为 pending，业务 suite 尚未执行。

## 1. 目标与非目标

目标是实现唯一一条离线合成链路：

```text
synthetic text Source -> contact ChangeSet -> user approval
-> atomic rev_011 -> two Core Views -> history/protected semantics
-> compensation rev_012 -> both Core Views consistent
```

同时实现 stale base、L1 第二 proposal 失败和单 L2 Projection 失败三个 required 故障路径。

非目标：通用 NLP/LLM、权限 runtime、MCP、连接器、真实迁移、同步、财务、健康、决策、提醒、Commitment、多租户、多 Agent、A2A、数字遗产、向量库、图数据库、长期 Context Pack 或生产 UI。

## 2. 输入合同

| PRD Requirement | SPEC Section | Acceptance Test | ADR |
|---|---|---|---|
| FR-001 | S1 §6.2；S4 §6.6；S9 §4-§7、§14 | `MM-001` 及其 manifest required refs | ADR-0001 |
| FR-002 | S1 §6.2、§7.1；S2 §6.4-§6.7；S4 §6.6；S9 §6 | `MM-001/002` 及其 manifest required refs | ADR-0001 |
| FR-003 | S1 §5-§6；S5 §4-§7 | `MM-002/007` 及其 manifest required refs | ADR-0001 |
| FR-004 | S3 §5-§9、§14 | `MM-003/004/009` 及其 manifest required refs | ADR-0001 |
| FR-005 | S3 §6.4-§6.7；S5 §6 | `MM-002/003` 及其 manifest required refs | ADR-0001 |
| FR-006 | S3 §6.4-§6.5、§8-§14 | `MM-005/007/010` 及其 manifest required refs | ADR-0001 |
| FR-007 | S3 §6.2、§6.5、§7.3、§14-§15 | `MM-004/008` 及其 manifest required refs | ADR-0001 |
| FR-009 | S1 §6.6；S2 §5-§10 | `MM-004/006` 及其 manifest required refs | ADR-0001 |
| FR-105 | S3 §8-§14；S6 §6-§14 | `MM-010` 及其 manifest required refs | ADR-0001 |

唯一 required 集由 manifest 绑定为 10 个 `MM-*` + 39 个去重 upstream refs，共 49 个 required result IDs。任何新增 required ID 必须先走 Trace/Change Control。

## 3. 模块边界

| 目标模块 | 责任 | 输入 / 输出 | 禁止责任 |
|---|---|---|---|
| `src/noetide_micro/store.py` + `schema.sql` | SQLite 连接配置、Schema、显式 transaction、seed、Canonical snapshot | fixture/SQL -> typed rows/snapshot | 不在 trigger 中生成业务语义；不提供通用 ORM |
| `src/noetide_micro/intake.py` | 校验 synthetic Intake、policy 初始化、Source + receipt 原子保存 | IntakeRequest/profile -> AppendReceipt/Source | 不解析事实；不写 Canonical |
| `src/noetide_micro/candidate.py` | 固定 fixture 的 contact Candidate/preview | Source locator -> proposed ChangeSet | 不做通用 NLP；不触达 forbidden paths |
| `src/noetide_micro/changesets.py` | approve、attempt、preflight、publish、idempotency、receipt、revert | ChangeSet/actor/key -> terminal receipt/revision | 不读 View 作为证据；不原地重试终态 |
| `src/noetide_micro/queries.py` | valid-time current/historical contact 查询和 Canonical fallback | time/revision -> State + Source evidence | 不用 ChangeSet/Projection 作为事实 Evidence Ref |
| `src/noetide_micro/views.py` | 两个 Projection、freshness、故障注入、reconcile、read barrier | committed revision -> View/read result | 不回写 Canonical；不返回旧 payload 冒充 current |
| `src/noetide_micro/testing_adapter.py` | 实现 materialized runner 的 test-only port、固定 Clock、仓库内临时 data root | fixture/data_root -> MicroSystem | 不成为产品 API；不访问网络/工作区外数据 |

`src/noetide_micro/__init__.py` 只声明包版本。除上表外不创建框架层、repository 工厂、插件系统、服务总线或通用领域平台。

## 4. 施工任务

| Task ID | 修改范围 | SPEC/Test 依据 | 完成条件 | 状态 |
|---|---|---|---|---|
| `TASK-001` | package、`schema.sql`、`store.py` | S1 §5-§9；S3 §6.3/§9；ADR-0001 | 仅逻辑分层表；foreign_keys on、DELETE journal、FULL sync；fixture seed 得到 rev_010；无业务 trigger | `pending` |
| `TASK-002` | `testing_adapter.py` 基础 factory 与固定 Clock | S6 §6.2/§10；HTH-AT-006/007；manifest | 只在调用者提供的仓库内 data_root 建库；无网络；适配器满足 Protocol 的结构检查 | `pending` |
| `TASK-003` | `intake.py` + adapter intake/source | S1 §6.2/§7.1；S4 §6.6；S9 §6-§7；`MM-001` | 58-byte Source/receipt/policy 精确；写失败 rejected；Canonical rev_010 不变 | `pending` |
| `TASK-004` | `candidate.py` + preview/approval facade | S1 §6.6；S3 §6.1-§6.2；S5 §6.4；`MM-002/003` | 只产生 end+add；single confirmation；impact 仅两个 View；未确认零 Canonical/View 变化 | `pending` |
| `TASK-005` | `changesets.py` publish/preflight/idempotency/failure | S3 §6-§14；`MM-004/009` | 成功只增 rev_011；proposal 2 failure 全回滚；stale base conflicted；同 key 重放同 receipt | `pending` |
| `TASK-006` | `queries.py` + Canonical protected snapshot | S1 §6.6；S2 §6/§10-§11；`MM-006/007` | 半开区间查询正确；两 Source evidence 不互换；三个 protected digest/revision/成员不变 | `pending` |
| `TASK-007` | `views.py` project/read/reconcile | S3 §6.4/§14；`MM-005/010` | 两 View 对齐 rev_011；单 View 失败仅 fallback 或无旧 payload；reconcile 不改 Canonical | `pending` |
| `TASK-008` | `changesets.py` compensation + audit；Views 收敛 | S3 §7.3/§15；`MM-008` | 新 rev_012 恢复等价 active；rev_011/原 ChangeSet 保留；两 View/保护字段一致 | `pending` |
| `TASK-009` | 全模块 hardening、runner 真实执行、result artifact | S6 §6-§15；49 required IDs | 同一次 current run 全部 required 执行；真实结果不可覆盖；任何 skip 只能 partial | `pending` |
| `TASK-010` | Matrix/Verification/Gate/Recovery Point | Process、Change Control、S6 §6.4 | 回填实际模块与 run；P0/P1=0 才 Review pass；commit/tag/push 后可恢复 | `pending` |

## 5. 实施顺序与检查点

顺序固定为 TASK-001 -> 002 -> 003 -> 004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010。可以在同一 task 内小步提交，但不得跨过未满足依赖并伪称完成。

每个任务至少运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

开发中的定向业务测试可运行对应 `unittest` 方法；这些临时运行不能拼接成 suite passed。只有 TASK-009 使用统一 runner 创建正式结果。

立即停止并回到 Change Control 的条件：

- fixture/oracle 无法由 Approved SPEC 唯一推导。
- 需要新增状态、字段语义、第三个 Core View 或自动修改 protected semantics。
- 需要第三方包、外部服务、在线模型或仓库外数据。
- SQLite 不能满足 required failure oracle，需要改变 ADR。
- 测试只可通过修改 expected 来迎合实现。

## 6. 数据、隐私与恢复

- Fixture 只使用合成数据：`yes`
- 外部网络：`disabled`
- 数据变更：只创建 `tmp/micro-runs/` 下的可删除合成临时数据库，以及明确的新 Verification Result。
- 回滚方式：任务内代码用 Git commit 回退；数据由固定 fixture 重建；不得用 destructive reset 覆盖用户工作。
- PRD 保护：每次验证重算 v0.4/v0.5 hash；禁止修改 `PRDv04.md` 和 `PRDv05.md`。
- 外部未跟踪目录：`.workbuddy/`、`Review-report/` 不读取、不修改、不提交。

## 7. 验证计划

正式唯一入口：

```powershell
python -m tests.runner.run_micro_suite --adapter noetide_micro.testing_adapter --output docs/testing/results/<new-run-id>.json
```

运行前必须确认：

- manifest digest 与当前记录一致，applicability=current。
- adapter 路径和 commit 已固定。
- `tmp/micro-runs/` 为空或由 runner 创建独立 run root。
- 输出路径不存在，防止覆盖历史结果。

通过标准：

- 49 个 required result IDs 在同一次 run 中均为 `passed`。
- `run_result=passed`、exit code 0、privacy_scan passed。
- Product、SPEC + materialization preflight 同时 exit code 0。
- 不以截图、日志或静态校验替代业务断言。

执行前当前状态保持 `not_executed`。

## 8. 风险与未决项

| 风险 | 控制 |
|---|---|
| 测试接口形状被误当产品 API | 仅 `testing_adapter.py` 实现 test-only Protocol；产品 API 后置 |
| SQLite 技术细节渗入 SPEC | 只在 ADR/实现模块出现；任何用户行为变化回 SPEC |
| 先做抽象后做闭环 | 模块封闭且不建插件/总线/通用 repository |
| 失败注入污染生产路径 | failure controls 只由 testing adapter 暴露 |
| 运行结果含本机路径/个人数据 | runner 隐私扫描命中即 run failed |
| task 完成被误写为业务通过 | task status 与 Verification Result 分离 |

当前无产品 blocking/important 问题。若出现会改变用户可见行为的新问题，写入 `OPEN_QUESTIONS.md` 并停止对应 task。

## 9. 完成定义

- [ ] 所有计划任务完成。
- [ ] 追踪矩阵的 Implementation Module 已更新。
- [ ] required suite 在同一次 current run 中实际执行。
- [ ] Verification Result 已保存，未执行项没有被描述为通过。
- [ ] Gate Review 完成且 P0=0、P1=0。
- [ ] Git Recovery Point 已创建、推送并验证。

这些勾选项属于未来开发完成条件；计划批准时必须保持未勾选。
