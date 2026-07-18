# B2 Episode 与分层摘要切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-B2-EPISODE-SUMMARY-001` |
| 版本 | `0.1` |
| 状态 | `Approved for B2 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-B-EPISODE-SUMMARY-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S5 v0.4、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-B-EPISODE-SUMMARY-001`，仅固定合成数据 |

本合同补齐 B2 的窄范围实现语义；未改变基础九份 SPEC 的全局合同，也不授权现实数据能力。

## 1. 目标

在固定合成 Source 与 Canonical Context 上，建立经 ChangeSet 发布的 `Episode`，并基于显式 dependency set 生成 `day_summary` 与 `phase_summary` 两种 Derived Projection。用户能从 summary 回到 Episode 和 Source；summary 永远不能成为事实证据。

## 2. 非目标

- 通用 NLP、LLM、Embedding、RAG、模型供应商、外部网络和真实材料。
- 自动从自然语言创建 Canonical Episode；本切片只接受 fixture 定义的 Episode candidate。
- 人格/因果/Hypothesis 升格、Commitment、提醒、Semantic Diff、实体合并、权限/MCP runtime、连接器、同步和迁移。
- 对基础 S1-S7 的未实现长期能力作完成声明。

## 3. 术语

| 术语 | 定义 |
|---|---|
| `Episode` | 有时间边界的一段 Canonical 经历集合；不是 Fact 摘要，也不是 Derived View。 |
| `EpisodeCandidate` | 固定合成输入产生、尚未发布的 Episode 提案；不是 Canonical。 |
| `SummaryProjection` | 从 Episode、Source locator 和允许的 Canonical metadata 确定性计算的 Derived summary。 |
| `dependency_set` | summary 读取的 Episode/Source/Canonical revision 引用集合；不含 summary 或 receipt。 |
| `summary_level` | `day` 或 `phase`；它描述展示分辨率，不提升证据等级。 |

## 4. 对象与边界

### 4.1 Episode

```yaml
episode_id: stable ID
episode_kind: synthetic_relationship_event | synthetic_project_event
participant_refs: [Entity ID]
valid_time: BTE ValidTime interval
recorded_at: RFC3339 UTC instant
source_refs: [direct Source locator]
assertion_refs: [optional Canonical Assertion ID]
narrative_locator: optional direct Source locator
review_status: unreviewed | user_confirmed
object_revision: global data_revision
synthetic_profile_id: fixture profile ID
```

`source_refs` MUST 至少有一个直接 Source locator。`SummaryProjection`、ChangeSet receipt、candidate 和其他 Derived 字段 MUST NOT 出现在 `source_refs`、`assertion_refs` 或 `narrative_locator` 中。

### 4.2 SummaryProjection

```yaml
projection_id: stable ID
projection_kind: day_summary | phase_summary
summary_level: day | phase
time_window: BTE ValidTime interval
dependency_set:
  episode_refs: [Episode ID]
  source_refs: [direct Source locator]
  data_revision: global data_revision
summary_text: deterministic Derived text
view_revision: generated data_revision
freshness_status: fresh | stale | rebuilding | unavailable
generated_at: RFC3339 UTC instant
generator_policy_id: B2 deterministic policy version
```

`summary_text` MUST 由 approved deterministic template 生成；它不携带 `evidence_refs`，不得成为任何 Canonical 写入或事实型回答的 evidence input。

## 5. 状态机

```text
EpisodeCandidate: proposed -> approved -> published
EpisodeCandidate: proposed|approved -> rejected | failed

SummaryProjection: absent -> fresh
fresh -> stale -> rebuilding -> fresh
stale|rebuilding -> unavailable
unavailable -> rebuilding -> fresh
```

`EpisodeCandidate -> published` 只能由符合 S3 的 ChangeSet 成功发布触发。`fresh -> stale` 在任一 dependency 的 Canonical revision 不等于 `view_revision` 时必须立即发生。`stale` payload 可以保留供诊断，但读取响应必须显式标记 stale，且不得作为 current evidence。

## 6. 允许与禁止的转换

允许：固定合成 candidate 经用户确认发布 Episode；Canonical Episode 变化后 summary 失效；从授权 dependency 重建 summary；Derived 重建失败后保留 `unavailable` 或带状态的旧 payload。

禁止：直接写 Episode 绕过 ChangeSet；由 summary 创建 Assertion/Fact/Hypothesis；把 summary 当 Source locator；用 summary 覆盖 valid_time、recorded_at 或历史 Episode；固定合成 profile 以外的文本/对象进入 B2。

## 7. 系统不变量

| ID | 不变量 |
|---|---|
| `B2-INV-001` | Episode 是 Canonical；其发布必须经 ChangeSet，candidate/summary 不是 Canonical。 |
| `B2-INV-002` | summary 永远不能成为 Evidence Ref、Assertion input 或 ChangeSet trigger evidence。 |
| `B2-INV-003` | Episode 的 Source locator 必须直接、存在且与 fixture 合成 profile 一致。 |
| `B2-INV-004` | summary 的 `dependency_set.data_revision`、`view_revision` 和 `freshness_status` 必须一致。 |
| `B2-INV-005` | Canonical dependency 改变后旧 summary 立即 `stale` 或 `unavailable`，不得冒充 current。 |
| `B2-INV-006` | 删除全部 Derived summary 后，只读取 Canonical/Episode/Source 仍可确定性重建等价 summary。 |
| `B2-INV-007` | B2 失败不得创建半完成 Episode、增加 revision 或修改既有事实/关系/人格保护对象。 |
| `B2-INV-008` | 非合成输入 fail closed，拒绝不产生 Source receipt、Episode、summary 或 revision。 |

## 8. 时间语义

Episode 使用 S2 `valid_time` 与 `recorded_at` 的正交语义。`day_summary` 按 valid-time UTC 日窗口聚合；`phase_summary` 的窗口由 fixture 显式给出，禁止从模糊文本猜测。summary 的 `generated_at` 只表示 Derived 计算时间，不能替代 Episode 的有效/记录时间。

## 9. 证据语义

Episode 只能引用直接 Source locator 和可选 Canonical Assertion ID。summary 可展示 dependency locator 的受控引用，但不是证据层对象。任何 API/存储尝试把 `projection_id`、`summary_text`、summary digest 或 rebuild receipt 作为 `evidence_refs` MUST 返回 `derived_evidence_forbidden`。

## 10. 权限要求

B2 不实现权限 runtime。fixture 仅含 owner 可读、`normal` 合成数据；实现仍 MUST 保留上游 S4 的最小披露边界。若 future caller/compartment 输入无法安全解释，B2 MUST 拒绝而不是默认聚类或摘要。

## 11. 冲突行为

相同时间窗口内的 Episode 可以并列；B2 不裁决 Assertion/State 冲突。若 dependency 中存在 unresolved `disputed` Canonical 内容，summary MUST 保留冲突标识或降级为 unavailable，不能选择一方生成确定结论。

## 12. 失败与降级

| 失败 | 行为 |
|---|---|
| candidate 缺 Source/Entity/时间引用 | ChangeSet preflight failed；不增加 revision |
| 非合成 profile 或未知字段 | `synthetic_input_required` / `fixture_profile_mismatch`；无写入 |
| dependency 缺失或类型不匹配 | summary=`unavailable`，不读取替代对象 |
| rebuild 失败 | 旧 summary 标 `stale` 或无 payload `unavailable`；Canonical/Episode 继续可读 |
| Derived 被当 evidence | `derived_evidence_forbidden`，不写 Canonical |
| deterministic policy 版本未知 | fail closed，不返回假定 fresh summary |

## 13. 撤销与审计

Episode 的撤销遵循 S3 整包补偿 revision；summary 不单独撤销 Canonical。每次 summary rebuild 记录 `generator_policy_id`、dependency digest、目标/实际 revision、结果和失败原因，但该 receipt 是 Derived 审计，不得作事实证据。

## 14. 兼容与迁移

Episode 与 SummaryProjection 均携带 schema/policy version。未知 required `episode_kind`、`projection_kind`、状态或 summary level MUST fail closed；未知非 required 扩展按 S7 namespaced extension 语义保留。迁移不得把旧 summary 直接提升为 Episode 或 Assertion。

## 15. 正例

固定合成 Source 中的关系事件形成 `EpisodeCandidate`。用户确认后，ChangeSet 发布一条 Episode。`day_summary` 显示该 Episode 的时间窗口和回源 locator；后来补偿撤销 Episode 后，summary 标 stale 并重建为不包含该 Episode 的版本。

## 16. 反例

- 从 summary_text 推断“某关系已结束”并写入 State。
- 将 summary 的 hash 填入 Assertion `evidence_refs`。
- Canonical revision 已改变而仍返回 old summary 作为 fresh。
- 将工作区外文本作为 Episode fixture 直接存入 Canonical。

## 17. 可执行验收测试

```yaml
suite_id: b2_episode_summary_v1
required_scenario_ids: [B2-001, B2-002, B2-003, B2-004, B2-005, B2-006, B2-007, B2-008]
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

| Test ID | Given / When | Then |
|---|---|---|
| `B2-001` | 合成 Episode candidate 经确认发布 | Episode 经 ChangeSet 发布，direct Source locator 保留 |
| `B2-002` | candidate 缺失直接 Source 或 Entity | preflight failed，无 revision |
| `B2-003` | 从已发布 Episode 生成 day/phase summary | 两种 projection fresh，dependency set 与 revision 正确 |
| `B2-004` | Canonical Episode 被补偿撤销 | 旧 summary stale，重建后不含已撤销 Episode |
| `B2-005` | 删除全部 Derived summary 后 rebuild | 仅从规范层重建语义等价 summary |
| `B2-006` | summary 被作为 evidence 或 ChangeSet trigger | 拒绝 `derived_evidence_forbidden`，Canonical 不变 |
| `B2-007` | summary rebuild 注入失败 | Canonical 可读，summary stale/unavailable，失败可审计 |
| `B2-008` | 非合成输入或 profile mismatch | 拒绝且无 Source/Episode/summary/revision 写入 |

## 18. 未决问题

无当前 blocking 产品问题。模型摘要质量、真实多模态材料、权限 runtime、跨语言与跨设备摘要均不在本切片，按 PRD 路线后置。

## 19. 完成定义

只有 fixture、oracle、manifest、offline runner、Implementation Plan 与上述八个场景的同一次 immutable passed result 存在，且 B2 不变量均有正/反证明时，本切片才可标 `verified`。未执行时只能标 `suite_defined` 或 `suite_materialized`。
