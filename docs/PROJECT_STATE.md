# 项目状态

## 1. 恢复入口

任何新任务必须按顺序读取：

1. `PRDv04.md`
2. `docs/PROJECT_STATE.md`
3. `docs/decisions/OPEN_QUESTIONS.md`
4. `docs/process/README.md`
5. 当前切片适用的 Approved SPEC
6. `docs/traceability/REQUIREMENTS_MATRIX.md`
7. 当前 suite 合同、manifest 和最近 Verification Result；当前 manifest/result 均不存在，只读 `docs/testing/MICRO_MVP_ACCEPTANCE.md` 与 `docs/testing/LATEST_STATIC_VALIDATION.md`
8. 当前适用 ADR、Architecture View、Implementation Plan 和 Gate Review；当前 ADR/View/Plan 均不存在

产品门禁先读 `docs/decisions/MICRO_GATE_DECISION_2026-07-14.md`；纠偏依据与结论分别读 `docs/reviews/MULTI_MODEL_FINAL_AUDIT.md` 和 `docs/reviews/MICRO_GATE_CORRECTIVE_REVIEW_2026-07-14.md`。历史报告不能覆盖当前状态。

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试、示例和 fixture 只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-15 |
| 当前阶段 | 长期交付流程建档完成；Micro 最小架构门禁待启动 |
| 当前切片 | `SLICE-MICRO-RELATIONSHIP-001` |
| 当前切片交付阶段 | `traceable` |
| PRD | `PRDv04.md` v0.4；文件仍显示 `Draft for Review`，原文未修改；产品基线批准见 `DEC-MICRO-GATE-001` |
| PRD canonical LF SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | 9/9 `Approved`：S1 v0.4；S2 v0.3；S3-S6 v0.3；S7-S8 v0.2；S9 v0.3 |
| 原审计 | P0=0、P1=7、P2=9、P3=1；结论 `no` |
| 关闭性复审 | P0=0、P1=0、P2=7、P3=1；结论 `yes_with_conditions` |
| 产品问题 | 原 BQ/IQ 保持 decided；本轮新增 blocking=0、important=0；DQ-001..010 保持 deferred |
| 追踪 | 32/32 FR 登记；9 `micro_required_slice`、8 `specified_not_implemented`、15 `boundary_only_deferred` |
| 测试目录 | 269 个 SPEC Test ID + 10 个 MM；128 条 invariant；39 个去重 Micro required upstream Test Ref |
| 测试状态 | 全部 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 实现代码 | 无业务实现；只有只读静态合同校验脚本 |
| 依赖/数据库/最终技术栈 | 无、未选择 |
| 交付流程 | PRD -> Decisions -> SPEC -> Traceability -> ADR -> Executable Tests -> Implementation Plan -> Development -> Verification -> Review -> Recovery Point |
| 当前下游产物 | ADR=`absent`；Architecture View=`absent`；Implementation Plan=`absent`；Business Verification=`not_executed` |
| Git | 当前分支 `codex/project-delivery-workflow`；基于已验证 tag `micro-gate-corrective-v0.1-validated` |

## 3. 本轮完成内容

1. 保存多模型 Finding 台账和最终审计报告，不改写审计快照。
2. 建立 hash/commit 绑定的 `DEC-MICRO-GATE-001`，明确纠偏授权、实现门禁和 personality sentinel 裁决。
3. S1/S4/S9 闭合 Source policy/subject 初始化：授权声明 + profile 唯一映射；缺失为 private/personal/provisional/unknown。
4. S3 闭合 Publish Attempt、preflight `conflicted|failed` 终态、receipt、幂等重放和 `retry_of`。
5. Micro 为旧 active State 增加独立 historical Source evidence；trust/closeness opinion 改为非空；加入只读 synthetic Hypothesis sentinel。
6. S6 分离 individual test、run、suite artifact、applicability 和 verification result；Micro §6 锁定 exact required refs。
7. 校验器改为 canonical LF hash、§19 结构化 invariant mapping、12 项正向 enum、真实隐私启发式扫描和 exact Micro mapping。
8. 添加 `.gitattributes`，并在 LF/CRLF 隔离副本中复现相同静态结果。
9. 生成关闭性复审，P1 从 7 降为 0；未开始业务代码或技术选型。
10. 建立 `docs/process/` 交付流程与变更控制，定义切片阶段、门禁、停止条件和恢复顺序。
11. 建立 Architecture、ADR、Planning、Testing、Review、Release/Recovery Point 的目录职责和中性模板。
12. 建立 `tests/fixtures`、`tests/semantic`、`tests/integration` 目录边界；只创建说明，未物化 manifest、fixture、oracle、runner 或业务测试。
13. 建立根级 `AGENTS.md`，使新 Codex 任务自动获得恢复顺序、隐私边界和阶段门禁。
14. 将 20 个流程基础文件、`delivery_phase_values`、新目录别名检查和隐私扫描纳入静态校验器。
15. 修正 SPEC 索引中过期的门禁描述，明确下一步是最小 ADR，不是直接编码。
16. 完成 `GATE-PROCESS-FOUNDATION-001` 复审，P0=0、P1=0；只批准建立流程 Git Recovery Point。
17. 建立 `project-delivery-workflow-v0.1-validated` Recovery Record，业务验证仍为 `not_executed`。

## 4. 验证结果

实际执行：

```powershell
& .\tools\validate_spec_baseline.ps1
```

结果：exit code 0，`PASSED (static contract checks only; no business test was executed)`。

| 检查 | 结果 |
|---|---|
| PRD canonical LF hash | passed；raw CRLF checkout 差异不再误判语义变化 |
| EOL portability | passed；LF 与 CRLF 隔离副本 exit code 均为 0，去 Root 输出一致 |
| SPEC/Test/Invariant | passed；9 份 SPEC、269 tests、128 invariants |
| Micro | passed；10 个 MM、两个 58-byte Source、39 个 exact upstream refs |
| 追踪 | passed；32 FR、9/8/15 Coverage Level、全部矩阵 Test Ref 可解析 |
| Workflow | passed；20 个流程基础文件存在 |
| Enum | passed；13 个机器可读封闭枚举与正向集合一致 |
| 隐私启发式 | passed；36 份权威合同/流程/测试文件未命中 phone-like、email-like、本机 user-directory path |
| Markdown | passed；46 份 Markdown fence parity 正常 |
| 业务合同执行 | `not_executed` |

静态 passed 不证明原子性、权限、撤销、删除、性能或任何业务行为。准确命令、环境与 artifact digest 见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

## 5. 权威产物

| 文件 | 当前职责 |
|---|---|
| `PRDv04.md` | 唯一产品需求基线，只读 |
| `AGENTS.md` | 新任务自动恢复入口与全仓协作红线 |
| `docs/decisions/MICRO_GATE_DECISION_2026-07-14.md` | 当前产品门禁批准与范围 |
| `docs/decisions/OPEN_QUESTIONS.md` | BQ/IQ 裁决与 deferred 队列 |
| `docs/reviews/MULTI_MODEL_FINDINGS_LEDGER.md` | 纠偏前 Finding 快照 |
| `docs/reviews/MULTI_MODEL_FINAL_AUDIT.md` | 纠偏前 `no` 结论 |
| `docs/reviews/MICRO_GATE_CORRECTIVE_REVIEW_2026-07-14.md` | 纠偏关闭台账与 `yes_with_conditions` 结论 |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | 32 条 FR 的权威追踪表 |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | 10 个 Micro 场景、固定合成 fixture 和 exact required refs |
| `docs/testing/LATEST_STATIC_VALIDATION.md` | 最近静态验证、环境、exit code 和 digest |
| `docs/specs/README.md` | 九份 SPEC 顺序、版本、边界和阶段门禁 |
| `docs/process/README.md` | 长期切片交付阶段、门禁、恢复顺序和 Stop-the-line 规则 |
| `docs/process/CHANGE_CONTROL.md` | 变更分层、下游失效和冲突处理 |
| `docs/architecture/README.md` | Architecture View 职责与创建条件 |
| `docs/adrs/README.md` | ADR 生命周期、边界和模板入口 |
| `docs/planning/README.md` | Implementation Plan/TODO 门禁和职责 |
| `docs/testing/README.md` | suite 物化、执行与结果语义 |
| `docs/reviews/README.md` | Finding 等级和 Gate Review 规则 |
| `docs/reviews/PROJECT_DELIVERY_WORKFLOW_REVIEW_2026-07-15.md` | 本轮流程建档门禁复审 |
| `docs/releases/README.md` | Git Recovery Point 与产品 Release 的边界 |
| `docs/releases/PROJECT_DELIVERY_WORKFLOW_V0.1_RECOVERY_POINT.md` | 本轮流程 Git 恢复记录 |
| `tests/README.md` | 可执行测试目录边界；当前仅骨架 |
| `tools/validate_spec_baseline.ps1` | 只读静态合同校验，不是业务测试 |

## 6. 未决问题与后置项

- 当前 Micro 规范门禁 blocking=0、important=0。
- `MMF-009..015` 保持 P2，分别在 MCP、ingestion/migration、privacy mutate、MVP-B/query semantics 阶段处理；不得带入首轮 Micro。
- `MMF-017` 保持 P3：合同目录仍需按阶段物化，不能把 Markdown 数量当可运行测试数量。
- DQ-001..010 状态不变；本轮没有替产品负责人裁决 deferred 问题。

## 7. 范围锁与风险

在 Micro required suite 真实物化并通过前，禁止：财务、健康、决策、成长、多设备、连接器、真实迁移、多租户、多 Agent、A2A、数字遗产、通用图数据库平台和真实个人数据。

| 风险 | 当前控制 |
|---|---|
| 把静态 passed 当业务 passed | suite 四态与 `not_executed` 明示 |
| personality sentinel 导致范围扩张 | 只读 digest oracle；禁止 Hypothesis workflow |
| 权限字段导致建设权限 runtime | Source 初始化合同明确不授权 runtime |
| 长期 FR 扩大 runner | Micro §6 exact mapping 是唯一 required 集合 |
| P2 被遗忘 | 关闭性复审与本文件保留 `MMF-009..015` 队列 |
| 换行再次导致假失败 | `.gitattributes` + validator canonical LF + 双 EOL 复验 |
| 模板被误当成完成产物 | 各 README 明示当前 `absent/not_executed`；validator 只检查流程骨架存在 |
| TODO 绕过 ADR/测试门禁 | 流程要求 ADR Accepted、suite materialized 后才批准 Implementation Plan |
| 流程文档与实际状态漂移 | 每次结束更新本文件并运行静态校验；上游变化按 Change Control 失效下游 |

## 8. 下一步唯一建议动作

**只为 `SLICE-MICRO-RELATIONSHIP-001` 编制必要的最小 ADR；ADR Accepted 后才物化 `MICRO_MVP_ACCEPTANCE.md` §6 的 exact required suite。**

尚未开始业务代码、suite 物化、依赖安装、数据库选择或最终技术栈选择。

## 9. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | PRD 审查、追踪、SPEC 计划、Micro 验收、Git 基线 |
| 2026-07-13 | Initial Spec Suite | S1-S9 首次 Approved；测试未执行 |
| 2026-07-14 | Independent Audit | 审计基线 `spec-suite-v0.2-audited`；业务测试未执行 |
| 2026-07-14 | Multi-model Synthesis | P1=7，结论 `no`；报告提交 `0c7e2d2` 已推送 |
| 2026-07-14 | Micro Gate Corrective Revision | 关闭 P1 与直接耦合 P2；九份 SPEC 保持独立版本 |
| 2026-07-14 | Corrective Review | P1=0，结论 `yes_with_conditions`；业务测试仍未执行 |
| 2026-07-15 | Delivery Workflow Foundation | 建立长期切片交付流程、变更控制、ADR/测试/计划/验证/审查/恢复点模板与静态门禁；业务测试仍未执行 |
