# 项目状态

## 1. 恢复入口

任何新任务必须按顺序读取：

1. `PRDv04.md`
2. `docs/PROJECT_STATE.md`
3. `docs/decisions/OPEN_QUESTIONS.md`
4. 当前工作对应的 Approved SPEC
5. `docs/traceability/REQUIREMENTS_MATRIX.md`
6. `docs/testing/MICRO_MVP_ACCEPTANCE.md`
7. `docs/testing/LATEST_STATIC_VALIDATION.md`
8. 最近适用的业务 Verification Result（当前不存在）

产品门禁先读 `docs/decisions/MICRO_GATE_DECISION_2026-07-14.md`；纠偏依据与结论分别读 `docs/reviews/MULTI_MODEL_FINAL_AUDIT.md` 和 `docs/reviews/MICRO_GATE_CORRECTIVE_REVIEW_2026-07-14.md`。历史报告不能覆盖当前状态。

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试、示例和 fixture 只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-14 |
| 当前阶段 | Micro Gate Corrective Revision 完成并通过关闭性复审 |
| 阶段状态 | `corrective_review_passed_ready_for_micro_planning` |
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
| Git | 审计报告提交 `0c7e2d2` 已推送到 `codex/multi-model-audit`；纠偏分支为 `codex/micro-gate-corrective-revision` |

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
| Enum | passed；12 个机器可读封闭枚举与正向集合一致 |
| 隐私启发式 | passed；权威合同/测试语料未命中 phone-like、email-like、本机 user-directory path |
| 业务合同执行 | `not_executed` |

静态 passed 不证明原子性、权限、撤销、删除、性能或任何业务行为。准确命令、环境与 artifact digest 见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

## 5. 权威产物

| 文件 | 当前职责 |
|---|---|
| `PRDv04.md` | 唯一产品需求基线，只读 |
| `docs/decisions/MICRO_GATE_DECISION_2026-07-14.md` | 当前产品门禁批准与范围 |
| `docs/decisions/OPEN_QUESTIONS.md` | BQ/IQ 裁决与 deferred 队列 |
| `docs/reviews/MULTI_MODEL_FINDINGS_LEDGER.md` | 纠偏前 Finding 快照 |
| `docs/reviews/MULTI_MODEL_FINAL_AUDIT.md` | 纠偏前 `no` 结论 |
| `docs/reviews/MICRO_GATE_CORRECTIVE_REVIEW_2026-07-14.md` | 纠偏关闭台账与 `yes_with_conditions` 结论 |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | 32 条 FR 的权威追踪表 |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | 10 个 Micro 场景、固定合成 fixture 和 exact required refs |
| `docs/testing/LATEST_STATIC_VALIDATION.md` | 最近静态验证、环境、exit code 和 digest |
| `docs/specs/README.md` | 九份 SPEC 顺序、版本、边界和阶段门禁 |
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

## 8. 下一步唯一建议动作

**在新的明确任务中编制 Micro-MVP 最小实现计划与必要 ADR，然后只物化并实现 `MICRO_MVP_ACCEPTANCE.md` §6 的 exact required 合成链路。**

本轮到此停止。尚未开始业务代码、技术选型、依赖安装或数据库工作。

## 9. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | PRD 审查、追踪、SPEC 计划、Micro 验收、Git 基线 |
| 2026-07-13 | Initial Spec Suite | S1-S9 首次 Approved；测试未执行 |
| 2026-07-14 | Independent Audit | 审计基线 `spec-suite-v0.2-audited`；业务测试未执行 |
| 2026-07-14 | Multi-model Synthesis | P1=7，结论 `no`；报告提交 `0c7e2d2` 已推送 |
| 2026-07-14 | Micro Gate Corrective Revision | 关闭 P1 与直接耦合 P2；九份 SPEC 保持独立版本 |
| 2026-07-14 | Corrective Review | P1=0，结论 `yes_with_conditions`；业务测试仍未执行 |
