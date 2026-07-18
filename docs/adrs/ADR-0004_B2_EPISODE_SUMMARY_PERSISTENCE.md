# ADR-0004：B2 Episode 与摘要的分层持久化

## 0. 元数据

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0004` |
| Status | `Accepted` |
| Date | `2026-07-19` |
| Slice | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| Decision Owner | System Architect |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

如何在既有 Python 3.12 + SQLite runtime 中持久化 B2 的 Canonical Episode，并让可失效、可重建的 day/phase summary 与它严格分层。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | PRD §6、§8、§10、§16、§20 FR-103；`DEC-MVP-B-EPISODE-SUMMARY-001` |
| SPEC | `SPEC-B2-EPISODE-SUMMARY-001` §4-§19；S1 v0.6、S2 v0.5、S3 v0.4、S5 v0.4、S6 v0.5、S7 v0.3 |
| Acceptance Test | `B2-001` 至 `B2-008` |
| Traceability | Requirements Matrix §4.6 |

## 3. 约束与非目标

- Runtime 保持 Python 3.12 标准库、SQLite、`foreign_keys=ON`、`journal_mode=DELETE`、`synchronous=FULL`。
- Episode 是 Canonical，写入必须经 ChangeSet；summary 是 Derived，永远不得成为 evidence 或 Canonical 写入输入。
- Derived refresh 只能从 Episode/Source/Canonical dependency 读取；不使用 trigger、LLM、网络、ORM、向量库或通用图数据库。
- 本 ADR 只决定 B2 的最小表与服务边界，不决定权限 runtime、真实导入、长期索引、跨设备同步或 UI。

## 4. 候选方案

### Option A：明确 Canonical 与 Derived SQLite 表

- 做法：新增 `episodes` Canonical 表和 `summary_projections` Derived 表；由 Python service 明确执行 ChangeSet 发布、stale 标记与确定性 rebuild。
- 优点：字段、外键、revision 与删除 Derived 后的重建可单独验证；不会把摘要混入事实层。
- 代价与风险：需要最小 schema migration 和更多定向测试。
- 可逆性：Derived 表可全部删除重建；Episode schema 变更遵循 SQLite migration 与 Context Pack 兼容合同。

### Option B：把 Episode 与 summary 都序列化进通用 Canonical JSON

- 做法：复用现有对象 payload，不新增明确 Derived 层。
- 优点：短期改动少。
- 代价与风险：摘要可能被误读为 Canonical/evidence；无法独立重建或验证 freshness。
- 可逆性：差，字段边界依赖实现约定。

### Option C：只输出 Markdown 文件摘要

- 做法：不持久化 summary，只在导出时生成文件。
- 优点：实现最少。
- 代价与风险：不能证明 stale/rebuild/receipt 合同，无法满足 B2-003 至 B2-007。
- 可逆性：不阻塞，但无法完成本切片。

## 5. 决定

采用 Option A。`SemanticStore` 增加最小 Episode Canonical 表与 summary Derived 表；`EpisodeService` 只构造/校验固定 synthetic candidate 并调用现有 ChangeSet 边界；`SummaryProjector` 只读取允许 dependency，生成确定性文本、dependency digest、revision 与 freshness；`SummaryReader` 只返回 fresh、显式 stale 或 unavailable 的结果。

SQLite trigger MUST NOT 承担聚类、证据、freshness 或业务裁决。所有业务语义由显式 Python service 与可执行 oracle 证明。

## 6. 后果

### 正向后果

- Canonical Episode 与 Derived summary 的存储、证据和删除/重建边界可机器验证。
- summary 的 stale/rebuild 可在事务外执行，不破坏 Canonical L1 原子性。
- future Context Pack 可以明确导出 Episode，按 policy 排除或重建 summary。

### 负向后果与债务

- B2 需要 schema migration、fixture profile 与定向 failure injection。
- 只支持固定 `day|phase` summary，不提供通用聚类或文本生成。
- summary rebuild 的调度暂由显式服务调用，不引入队列或后台框架。

## 7. 验证与回退

- 验证方式：`B2-001..008`、Micro/A1/B1/C1 回归、schema/foreign-key、Derived delete/rebuild 与 privacy scan。
- 失败信号：summary 成为 evidence、旧 revision 被标 fresh、rebuild 修改 Canonical、非合成输入写入。
- 回退步骤：删除 `summary_projections` 的 Derived 行并回到 Canonical/Episode 读取；已发布 Episode 使用补偿 ChangeSet，不回拨 revision。
- 数据兼容：migration 必须是显式版本化，未知 required enum fail closed；不得修改历史 Source、Ledger 或已发布 revision。

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | 创建 `B2_EPISODE_SUMMARY_ARCHITECTURE.md` |
| Suite Materialization | fixture、oracle、manifest、runner、validator 与 failure cases `B2-001..008` |
| Implementation Plan | 先 schema/store，再 Episode service，再 projector/reader，最后 suite/verification |
| Portability / Privacy | summary 是可删 Derived；不读取 workspace 外数据，未来导出遵循 S7/S4 |

## 9. 未决项

真实文本聚类、模型摘要质量、权限裁剪后的摘要、跨语言和长期后台调度均后置；它们不影响此决定成立。
