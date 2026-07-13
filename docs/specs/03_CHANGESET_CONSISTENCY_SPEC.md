# ChangeSet & Consistency SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-CS-001` |
| 版本 | `0.2` |
| 状态 | `Approved` |
| 产品基线 | `PRDv04.md`，PRD v0.4 |
| 上游基线 | `SPEC-SOM-001` v0.3、`SPEC-BTE-001` v0.3，均 `Approved` |
| 产品裁决 | `IQ-001`、`IQ-002`、`IQ-005`、`IQ-008`、`IQ-017`、`IQ-018`，2026-07-13 已决定 |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 独立审计 | 2026-07-14；统一枚举、收紧发布回执与并发撤销语义 |

本文只定义变更和一致性语义，不选择数据库事务、消息系统、锁、队列或事件框架。用户已授权按保守推荐方案完成全部 SPEC；批准不代表实现或测试通过。

## 1. 目标

1. 使 ChangeSet 成为 Canonical Context 唯一语义写入口。
2. 定义全局 revision、对象 revision、并发拒绝、幂等和 L1 原子发布。
3. 定义 L2 会话一致、L3 最终一致、失效和安全降级。
4. 使一次确认、发布、回执、撤销和对账可审计、可测试。
5. 完整锁定 RelationshipState Micro-MVP 的发布与恢复 oracle。

依据：PRD §6.9、§10-§12、§20 FR-004/005/006/007/105/106/107、§21、§25.2、§26 Case A。

## 2. 非目标

- 不选择物理事务、事件日志、队列、缓存或锁实现。
- 不定义证据真值、权限策略或识灵候选排序。
- 不实现单 proposal 撤销；Micro 只支持整包撤销。
- 不扩大 Micro Core View 到提醒、Commitment 或其他长期视图。
- 不实现多设备冲突、连接器、财务、健康或决策工作流。

## 3. 术语

| 术语 | 定义 |
|---|---|
| `data_revision` | Canonical Context 每次成功发布后产生的全局单调 revision |
| `object_revision` | 对象最近一次发生语义变化时对应的 `data_revision` |
| `base_revision` | ChangeSet 提案所依据的全局 `data_revision` |
| L1 | Canonical 规范层原子一致性 |
| L2 | 当前会话必须读取新 revision 或明确不可用的 Core View 层 |
| L3 | 可返回旧 payload 但必须立即标 stale 的可重建派生层 |
| Publish Barrier | 发布响应与后续同会话读取之间的最小一致性屏障 |
| Impact Rule | 由规范 predicate/object 到受影响 View 的声明式依赖规则 |
| Receipt | 对规范发布、传播、等待、失败和跳过项的逐项结果 |
| Compensation Revision | 撤销已发布 ChangeSet 时恢复先前等价语义的新 revision |
| Semantic Diff | 两个 revision 间规范语义与派生影响的可追踪差异 |

## 4. 适用范围

### 4.1 Micro 对象

只允许 Source 已存在后，通过一个 ChangeSet 结束旧 `relationship.contact` State 并新增 `no_contact` State；不得触达 `origin`、`role`、`trust`、`closeness` 或人格 Hypothesis。

### 4.2 Micro Core View

经 `IQ-001` 裁决，Micro Core View 封闭集合仅为：

```text
person_card
relationship_timeline
```

PRD §10.3 的其余四类是 MVP 后续白名单，不是 Micro 发布门槛。

## 5. 对象与边界

- Source Append receipt 不是 ChangeSet；它不得修改 Canonical 语义。
- proposal 不是 Canonical 对象当前值，只有 `published` ChangeSet 的 proposal 才生效。
- CoverageWindow 原始声明可随 Source Append 保存；进入 Canonical 查询的规范化/纠正版本必须经 ChangeSet。
- archive、seal、soft_delete、hard_delete 等 Canonical 语义操作必须经 ChangeSet；纯 Derived 重建、缓存清除和索引失效不是规范写入。
- Impact Rule 是版本化规则数据，不由 LLM 临时决定；模型只能提出额外影响候选。

## 6. 字段语义

### 6.1 ChangeSet Envelope

| 字段 | 必需 | 语义 |
|---|---|---|
| `changeset_id` | MUST | stable ID，不复用 |
| `schema_version` | MUST | ChangeSet 解释版本 |
| `base_revision` | MUST | 全局 Canonical revision |
| `actor` | MUST | 发起 actor：user、shiling、external_agent、importer、migration；审批 actor 另存 review event |
| `requested_at` | MUST | 创建提案时间，不是发布时间 |
| `trigger_sources` | MUST | Source locator 集合，可为空但必须说明原因 |
| `proposals` | MUST | 至少一个原子 proposal |
| `impact_set` | MUST | Canonical、L2、L3、提醒/缓存影响预览 |
| `risk_level` | MUST | `low|medium|high|critical` |
| `confirmation_policy` | MUST | `automatic|posthoc_revertible|single_confirmation|double_confirmation` |
| `status` | MUST | §7 状态 |
| `idempotency_key` | MUST | 同一逻辑请求的稳定去重键 |
| `published_revision` | 条件 MUST | published/reverted 相关 revision |
| `receipt` | 条件 MUST | terminal/published 结果 |
| `reversibility` | MUST | `reversible|irreversible`；不可逆只允许经 S4 强授权的 destructive operation |
| `rollback_reference` | reversible published MUST | 整包补偿所需引用；不可逆操作 MUST 显式为空并在预览中警告 |
| `retry_of` | MAY | failed/stale-base 后新 ChangeSet 引用 |

review/approval event MUST 记录 `review_actor`、决定、时间、policy/revision 和确认界面摘要 digest。`actor` 不得在批准时被确认者覆盖，否则无法区分“谁提出”和“谁批准”。

### 6.2 Proposal

```yaml
proposal_id: stable ID within ChangeSet
operation: add | correct | end | merge | split | archive | seal | soft_delete | hard_delete
target_ref: Canonical object/path
before_digest: expected semantic digest | absent
after_value: typed semantic value | tombstone intent
valid_time: BTE ValidTime
evidence_refs: direct Source refs
protected_paths: paths that MUST remain semantically equal
```

Micro 只允许 `end` 旧 State 与 `add` 新 State 两个不可分 proposal。

### 6.3 Revision

经 `IQ-018` 裁决，`base_revision` 是全局 `data_revision`。成功发布只产生一个新 `data_revision`；发生变化的对象把 `object_revision` 设为该 revision，未变化对象 payload 和 `object_revision` 均保持不变。

### 6.4 Impact Set

每项必须包含 `dependency_rule_id`、目标、预计动作 `update|invalidate|rebuild|none`、一致性等级和原因。Micro 的 Derived View 子集必须且只能列出 `person_card` 与 `relationship_timeline`；Canonical proposal 目标仍须完整列出。禁止把“可能影响”伪装成确定依赖。

### 6.5 Receipt

Receipt MUST 包含：`changeset_id`、旧/新 revision、Canonical 原子结果、每个 View 的目标/实际 revision、`freshness_status`、失败/等待/跳过原因、审计时间和可重试性。L1 发布的 durable outcome 至少包含 ChangeSet terminal/published 状态、revision 绑定和 receipt summary；三者必须与 Canonical 原子结果在同一恢复边界内持久化。详细 L2/L3 项可随后追加，但不得改写 L1 结果。

### 6.6 Review Preview

面向用户必须用自然语言列出：会改变什么、不会改变什么、依据、影响 View、风险、确认政策和撤销能力。`reversibility=irreversible` 时必须在确认前明确说明不可撤销及分层删除边界。高级字段可展开，但技术术语不得成为确认前提。

### 6.7 自动与事后撤销

`automatic` 只允许确定性机器元数据或预授权无语义机械修复。`posthoc_revertible` 仍必须明显标识、进入摘要、可整包撤销且不得驱动高风险外部行动；具体识灵准入由 S5 定义。

## 7. 状态机

### 7.1 生命周期

```text
proposed -> reviewing
reviewing -> approved | rejected
approved -> publishing
publishing -> published | failed
published -> reverted  (仅 reversible，且补偿 ChangeSet 已成功发布)
```

`rejected`、`failed`、`reverted` 为终态。重试必须创建新 `changeset_id` 并使用 `retry_of`；不得执行 `failed -> publishing`。

### 7.2 前置条件

- `reviewing -> approved` 必须满足 confirmation policy、权限与完整预览。
- `approved -> publishing` 必须重新检查权限、`base_revision`、引用和 protected paths。
- `publishing -> published` 必须完成全部 L1 proposal；任何 L1 失败导致整包 failed 且不增加 revision。

### 7.3 撤销

经 `IQ-008` 裁决，`published -> reverted` 通过新的 Compensation ChangeSet/Revision 恢复发布前等价语义。补偿必须以执行时 current revision 为 `base_revision` 并重新计算 impact/protected paths；若原发布后存在触达相同语义的后续变更，必须进入 conflict/review，不得覆盖后续变更。只有补偿发布成功后，原 ChangeSet 才可标 `reverted`。原 revision、原 ChangeSet 和中间可见历史不得删除；`reversibility=irreversible` 不允许此转换。

## 8. 允许与禁止的状态转换

允许：用户确认后发布；stale base 拒绝后创建新 ChangeSet；L1 成功后异步重建 L3；整包撤销产生补偿 revision。

禁止：跳过 reviewing；部分 L1 发布；原地修改 published ChangeSet；重用旧 `published_revision`；用 View 写回 Canonical；把旧 L2 标为 current；自动修改 protected paths。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `CS-INV-001` | 所有 Canonical 语义写入只经 ChangeSet |
| `CS-INV-002` | 一个 ChangeSet 的 L1 要么全部成功要么完全失败 |
| `CS-INV-003` | stale `base_revision` 不得覆盖当前 revision |
| `CS-INV-004` | 成功发布产生唯一新全局 revision，未变对象 revision 不动 |
| `CS-INV-005` | proposal/preview 不改变 Canonical 或 View current 值 |
| `CS-INV-006` | Micro 只影响 contact State 与两个 Core View |
| `CS-INV-007` | L2 不得把旧 payload 冒充最新 |
| `CS-INV-008` | L3 旧 payload 必须标 stale 且可重建 |
| `CS-INV-009` | 撤销产生补偿 revision，不擦除历史 |
| `CS-INV-010` | 幂等重放不重复发布 |
| `CS-INV-011` | Receipt 完整反映成功、等待、失败与跳过项 |
| `CS-INV-012` | protected paths 在发布与撤销后保持语义不变 |
| `CS-INV-013` | 补偿撤销基于执行时 current revision，不能覆盖介入变更；不可逆操作不能伪造 rollback |
| `CS-INV-014` | Canonical L1 结果、revision、ChangeSet outcome 与 receipt summary 具有同一恢复边界 |

## 10. 时间语义

- `requested_at`、approval time、publish time 和 BTE `valid_time` 必须分离。
- `recorded_at` 使用成功发布时刻；不得回填为 `valid_from`。
- 发布顺序由全局 revision 决定，不替代 valid-time 顺序。
- 同 revision 内所有 L1 proposal 共享原子可见点。

## 11. 证据语义

- `trigger_sources` 和 proposal `evidence_refs` 只能指向 Source locator。
- ChangeSet receipt、View、Diff 和模型解释不能成为事实证据。
- 冲突双方证据必须保留；确认一方不删除另一方。
- 变更理由与证据缺失必须显式，不允许用高 confidence 替代 Source。

## 12. 权限要求

- 创建、审查、批准、发布、撤销和 destructive operation 分别授权。
- 权限在 publishing 前重新检查；批准后权限失效则 failed，不部分发布。
- Receipt 和 Diff 必须按调用者权限裁剪，不能泄露隐藏路径。
- S4 定义具体策略；本 SPEC fail closed。

## 13. 冲突行为

- stale base 返回 revision conflict，不自动 rebase。
- `before_digest` 不匹配返回 target conflict。
- BTE 语义冲突可并列发布为 disputed，但不得被一致性层静默选胜者。
- 两个 ChangeSet 触达同一路径时，后发布者必须基于当前 revision 重新审查。

## 14. 失败与降级

| 失败 | MUST 行为 |
|---|---|
| L1 校验/写入失败 | 不增加 revision，旧 Canonical 完整可读 |
| L1 成功、L2 失败 | 返回新 Canonical fallback 或无旧 payload 的 `updating/unavailable` |
| L3 失败 | 旧 payload 可读但立即 `stale`，加入重建队列 |
| stale base | 拒绝并返回 current revision，不自动覆盖 |
| L1 outcome/revision/receipt summary 任一不能持久化 | 整个 L1 不得提交；不得声称成功或产生不可审计 revision |
| 详细 L2/L3 receipt 追加失败 | L1 结果不回滚；返回 receipt incomplete，View 使用实际 revision/freshness，并进入可恢复对账 |
| 幂等键同、payload 不同 | 拒绝 `idempotency_mismatch` |
| 模型不可用 | 允许手动 proposal、审查、发布与撤销 |

经 `IQ-005` 裁决：发布前失败可继续读旧 L1；L1 成功后旧 L2 不能作为 current；L3 旧版只可带 stale；任何层都必须返回实际 revision。

## 15. 撤销与审计

- 原 ChangeSet、发起/确认 actor、published revision 和补偿 revision在审计生命周期内可追踪；硬删除后只保留 S4 允许的 content-free proof，不以“永久”承诺正文保留。
- 整包撤销重新计算所有影响，不复用旧 View payload 作为事实源。
- 原发布后若有相同路径的介入变更，撤销必须拒绝自动补偿并提供非破坏性 conflict preview；用户可据此创建新的显式 ChangeSet。
- Semantic Diff 必须区分新增、结束、纠正、撤销、后来补录和纯 View 重建。
- 单 proposal 撤销后置，不得由 Micro 实现。

## 16. 兼容与迁移

- 未知 operation/status 必须 fail closed 并保留原始扩展。
- 旧 ChangeSet 缺 `idempotency_key` 时迁移必须生成可审计映射，不重放发布。
- revision 机制迁移不得改变历史顺序、Source 或确认记录。
- 迁移程序修改 Canonical 仍必须产生 ChangeSet。

## 17. 正例

```yaml
changeset_id: cs_micro_001
base_revision: rev_010
proposals: [end_state_contact_001, add_state_contact_002]
impact_set: [person_card, relationship_timeline]
protected_paths:
  - relationship.origin
  - assertion[relationship.trust]
  - assertion[relationship.closeness]
status: published
published_revision: rev_011
```

同一 revision 原子结束 `active` 并新增 `no_contact`，两个 View 读取 rev_011 或明确 updating。

## 18. 反例

- 直接 update State 而无 ChangeSet。
- active 已结束但 no_contact 未新增却增加 revision。
- View 仍是 rev_010，却返回 `fresh/current`。
- 撤销删除 rev_011 并把指针退回 rev_010。
- stale base 自动覆盖当前 revision。

## 19. 可执行验收测试

```yaml
suite_id: changeset_consistency_v0_2
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `CS-AT-001` | 绕过 ChangeSet 写 Canonical | 拒绝 `changeset_required` |
| `CS-AT-002` | proposal 未确认 | revision 与 View 不变 |
| `CS-AT-003` | 两个 Micro proposal 发布 | 同一 revision 全成功 |
| `CS-AT-004` | 第二个 proposal 注入失败 | 两者均不发布，不加 revision |
| `CS-AT-005` | dangling ref/protected path 变化 | 整包拒绝 |
| `CS-AT-006` | 查看 review preview | 改变/不变/影响/风险/撤销完整 |
| `CS-AT-007` | 未授权语义使用 automatic | 拒绝或转人工确认 |
| `CS-AT-008` | stale base 发布 | conflict，无部分写 |
| `CS-AT-009` | 同幂等键同 payload 重放 | 返回原 receipt，不新增 revision |
| `CS-AT-010` | 同幂等键不同 payload | `idempotency_mismatch` |
| `CS-AT-011` | L1 发布成功 | changed object_revision=新 data_revision |
| `CS-AT-012` | 无关对象 | payload/object_revision 不变 |
| `CS-AT-013` | 同会话读两个 Micro View | 都读新 revision 或明确 updating |
| `CS-AT-014` | 一个 L2 更新失败 | 不返回旧值冒充最新 |
| `CS-AT-015` | L3 未重建 | 旧 payload 立即 stale |
| `CS-AT-016` | 发布 receipt | 逐项列成功/等待/失败/跳过 |
| `CS-AT-017` | published ChangeSet 整包撤销 | 产生补偿 revision |
| `CS-AT-018` | 撤销后审计 | 原发布与撤销均存在 |
| `CS-AT-019` | 撤销后 View | 两个 View 对齐补偿 revision |
| `CS-AT-020` | 比较 rev_010/rev_011 | Diff 区分状态演化与 protected 不变 |
| `CS-AT-021` | 写后对账发现 L2 不一致 | 隔离并记录，不改 L1 |
| `CS-AT-022` | 日常对账发现 stale/orphan | 进入失败队列和可重建状态 |
| `CS-AT-023` | 权限批准后发布前失效 | failed，无部分发布 |
| `CS-AT-024` | failed ChangeSet 重试 | 新 ID + retry_of，原记录终态 |
| `CS-AT-025` | Source Append | receipt 成功、Canonical revision 不变 |
| `CS-AT-026` | 全部 fixture 隐私扫描 | 仅合成数据 |
| `CS-AT-027` | 原发布后同一路径已有介入变更，再撤销原 ChangeSet | 补偿按 current revision 检测 conflict，不覆盖介入变更，原 ChangeSet 仍 published |
| `CS-AT-028` | `reversibility=irreversible` 的已发布 destructive ChangeSet | 拒绝 revert，预览与 receipt 均不声称存在 rollback |
| `CS-AT-029` | 注入 outcome/revision/receipt summary 任一持久化失败 | L1 全部不提交、revision 不增加；详细传播 receipt 失败则保留已提交 L1 并标 incomplete |

不变量覆盖：001→AT001/025；002→003/004；003→008；004→011/012；005→002；006→003/013；007→013/014；008→015/022；009→017-019；010→009/010；011→016/029；012→005/020；013→027/028；014→029。

## 20. 未决问题

本 SPEC 无 blocking open question。已决定：

- `IQ-001`：Micro Core View 仅人物卡、关系时间线。
- `IQ-002`：Publish Barrier 要求新值或明确 unavailable；5 秒是 SLO，不是返回旧值许可。
- `IQ-005`：L1/L2/L3 安全旧版本边界见 §14。
- `IQ-008`：撤销发布补偿 revision。
- `IQ-017`：Canonical archive/seal/delete 经 ChangeSet，纯 Derived 操作不经。
- `IQ-018`：`base_revision` 为全局 revision，`object_revision` 记录对象最后变化。

数据库机制、分布式锁和队列均后置 ADR；多设备冲突后置 Year 2。

## 21. 完成定义

- 上游 S1/S2 已批准。
- 六项产品问题已 decided。
- Micro 发布、两个 View、撤销和两个失败场景有确定 oracle。
- 14 条不变量与 29 个测试均有映射。
- FR-004/005/006/007/105/106/107 已进入追踪。
- 未选择技术栈；测试仍未执行。

当前结论：本 SPEC v0.2 于 2026-07-14 完成独立基线审计并保持 `Approved`。本次修订消除枚举别名，补齐可恢复发布、介入变更撤销和不可逆操作边界；测试尚未物化、执行或通过。
