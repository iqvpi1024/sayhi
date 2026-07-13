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

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试和示例只允许合成数据。`PRDv04-opus审查报告.md` 与 `docs/reviews/SPEC_SUITE_COMPLETION_REVIEW.md` 是历史材料，不能覆盖当前状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-14 |
| 当前阶段 | Audited Specification Baseline |
| 阶段状态 | `approved_contracts_suites_not_materialized` |
| PRD | `PRDv04.md` v0.4，`Draft for Review`，未修改 |
| PRD SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | 9/9 `Approved`：S1/S2 v0.3；S3-S9 v0.2 |
| 产品问题 | `BQ-001..005`、`IQ-001..018` decided；新增 blocking=0、important=0 |
| Deferred | `DQ-001..010` 保持 deferred |
| 追踪 | 32/32 FR 已登记；9 `micro_required_slice`、8 `specified_not_implemented`、15 `boundary_only_deferred` |
| 测试目录 | 257 个 SPEC Test ID + 10 个 MM = 267；123 条 invariant |
| 测试状态 | 全部 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 实现代码 | 无业务实现；仅有只读静态校验脚本 |
| 依赖/数据库/最终技术栈 | 无、未选择 |
| Git | 审计基线提交 `b497c2c` 与标签 `spec-suite-v0.2-audited` 已推送；最新状态以远程 `main` 为准 |

## 3. 当前结论

2026-07-13 的九份 SPEC 首次基线文件齐全，但跨规范审计发现字段、状态轴、撤销、删除、MCP 响应、测试状态和 FR 追踪存在实质漂移。2026-07-14 已完成独立修订：

1. Semantic Object Model v0.3
2. Bitemporal & Evidence v0.3
3. ChangeSet & Consistency v0.2
4. Privacy & Access Policy v0.2
5. Shiling Policy v0.2
6. Semantic Test Harness v0.2
7. Storage, Index & Portability v0.2
8. MCP Contract v0.2
9. Ingestion & Migration v0.2

批准只表示语义合同完成独立审计。没有机器 suite、业务实现、数据库或运行结果，任何 suite 都不得称为通过。

## 4. 本轮完成内容

- 完整重审 PRD、S1-S9、Micro、开放问题、追踪矩阵、历史评审和项目状态。
- 统一 ChangeSet confirmation/proposal 字段，明确 Source Vault 与 Canonical `data_revision` 边界。
- 分离 Canonical Evidence Ref 与 Derived EvidenceAssessment。
- 补齐 L1 outcome/revision/receipt 恢复边界、介入变更撤销和不可逆操作。
- 分离 seal/retention/retrieval、risk/review priority、execution/answer/freshness、Intake/Parse Attempt 等正交状态。
- 补齐 hard delete 后证据失效、Pack 路径逃逸、惰性导入和 migration verification failure。
- 修正 Micro fixture 的字段、半开区间、UTF-8 byte locator/hash 及 trust/closeness 语义。
- 将追踪矩阵合并为单一权威表，移除“32/32 已闭环”的过度结论。
- 新增零依赖静态校验器和独立审计报告。

详细依据：`docs/reviews/INDEPENDENT_BASELINE_AUDIT_2026-07-14.md`。

## 5. 权威产物

| 文件 | 当前职责 |
|---|---|
| `PRDv04.md` | 唯一产品需求基线，只读 |
| `docs/reviews/INDEPENDENT_BASELINE_AUDIT_2026-07-14.md` | 当前独立审计结论 |
| `docs/decisions/OPEN_QUESTIONS.md` | 产品裁决与 deferred 队列 |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | 32 条 FR 的唯一权威追踪表 |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | 10 个 Micro 合同场景与固定合成 fixture |
| `docs/testing/LATEST_STATIC_VALIDATION.md` | 最近一次静态验证结果及限制 |
| `docs/specs/README.md` | 九份 SPEC 顺序、边界与阶段门禁 |
| `docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` | Approved v0.3 |
| `docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md` | Approved v0.3 |
| `docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md` | Approved v0.2 |
| `docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md` | Approved v0.2 |
| `docs/specs/05_SHILING_POLICY_SPEC.md` | Approved v0.2 |
| `docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md` | Approved v0.2 |
| `docs/specs/07_STORAGE_INDEX_PORTABILITY_SPEC.md` | Approved v0.2 |
| `docs/specs/08_MCP_CONTRACT_SPEC.md` | Approved v0.2 |
| `docs/specs/09_INGESTION_MIGRATION_SPEC.md` | Approved v0.2 |
| `tools/validate_spec_baseline.ps1` | 只读静态合同校验，不是业务测试 |

## 6. 最近验证结果

实际执行：

```powershell
& .\tools\validate_spec_baseline.ps1
```

结果：`PASSED`，只代表静态合同检查。

| 检查 | 结果 |
|---|---|
| PRD SHA-256 | passed：基线未变 |
| SPEC 章节/版本/状态 | passed：9/9 为 §0-§21 且版本匹配 |
| SPEC Test ID | passed：257 个连续且唯一 |
| Micro 场景 | passed：`MM-001..010` 存在 |
| Micro locator/hash | passed：UTF-8 58 bytes、SHA-256 与 locator 一致 |
| Invariant | passed：123 条连续且有覆盖引用 |
| FR 追踪 | passed：32 行与 PRD 32 个唯一 FR 完全一致 |
| Coverage Level | passed：9 micro slices / 8 specified / 15 deferred boundaries |
| Matrix Test Ref | passed：103 个唯一引用展开后全部存在 |
| 已知字段/状态漂移 | passed：未检出 |
| Markdown 围栏 | passed：20 个文件成对 |
| 隐私启发式扫描 | 未发现电话/本机用户目录；仅命中已知 Git SSH endpoint |
| 业务合同执行 | `not_executed` |

静态 passed 不证明原子性、权限、撤销、删除、性能或任何业务行为。

## 7. 核心合同摘要

- Source Append 独立进入 Source Vault；由 Source 产生或修改 Canonical 语义仍只经 ChangeSet。
- Current State 不覆盖 Historical State；valid/recorded/source/ingested time 分离。
- Canonical Evidence Ref 只指向 Source；EvidenceAssessment 是可重算 Derived 结果。
- ChangeSet 发布的 L1、revision、outcome 与 receipt summary 处于同一恢复边界。
- 撤销产生基于 current revision 的补偿修订，不覆盖介入变更；hard delete 不伪装可撤销。
- seal、retention、retrieval activation 正交；删除证据后依赖答案和 View 必须失效重评。
- risk、review priority、confidence、truth 正交；识灵仍是一个协调内核。
- MCP execution、Answer、View freshness、authorization 正交；拒绝响应不泄露 revision。
- exported Pack 是不可变 snapshot；导入引用不得逃逸根目录，内容不得执行。
- Intake receipt 与 Parse Attempt 正交；parser 失败不改 Source stored 状态。

完整产品裁决见 `docs/decisions/OPEN_QUESTIONS.md`。

## 8. 范围锁

在 Micro-MVP 的真实 suite 物化并通过前，禁止：

- 财务、健康、决策和成长业务实现。
- 多设备同步、连接器、真实历史迁移。
- 多租户、多 Agent、A2A、数字遗产。
- 通用图数据库平台和全量依赖语言。
- 导入任何真实个人数据。

15 条 `boundary_only_deferred` FR 只用于防止未来旁路，不是当前建设授权。

## 9. 风险

| 风险 | 当前控制 |
|---|---|
| 把 Approved 当成已实现 | `suite_materialized/executed/passed=false` 四态明示 |
| 长期 FR 拉大 Micro | 追踪矩阵 `coverage_level` + 范围锁 |
| 跨 SPEC 再次漂移 | `tools/validate_spec_baseline.ps1` 必须随每次规范修改运行 |
| 静态 pass 被误报业务 pass | 最近验证文件明确未证明项 |
| 删除/权限作虚假承诺 | 分层 receipt、fail closed、evidence invalidation |
| 历史审查覆盖当前状态 | 两份历史报告已标记 superseded/历史基线 |

## 10. 下一步唯一建议动作

**建立 Micro-MVP 最小实现计划与必要 ADR，只物化 `MM-001..010` 的 manifest、fixture、forbidden-change oracle 和离线 runner，然后实现这一条合成 RelationshipState 链路。**

技术选择必须服务于这条链路，不得把 deferred FR 带入首轮。尚未开始业务代码或最终技术选型。

## 11. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | PRD 审查、追踪、SPEC 计划、Micro 验收、Git 基线 |
| 2026-07-13 | Initial Spec Suite | S1-S9 首次 Approved；测试未执行 |
| 2026-07-13 | GitHub Backup | 提交 `721838f` 和首次批准标签已推送；状态提交 `0b3908e` |
| 2026-07-14 | Independent Audit | S1/S2 升 v0.3，S3-S9 升 v0.2；修复 16 类跨规范/追踪问题 |
| 2026-07-14 | Static Validation | 257 SPEC tests、123 invariants、10 MM、32 FR 静态检查 passed；业务测试仍未执行 |
| 2026-07-14 | GitHub Backup | 审计基线提交 `b497c2c` 与标签 `spec-suite-v0.2-audited` 已通过 SSH-over-443 推送 |
