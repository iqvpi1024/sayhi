# ADR-0015：C3 复盘报告与跨阶段比较的 Derived 存储与确定性计算方式

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-26 |
| Slice | `SLICE-MVP-C-REVIEW-001` |
| Contract | `SPEC-C3-REVIEW-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

C3 切片需要三个同层技术裁决：ReviewReport 与 PhaseComparison 的 Derived 存储形态（是否新增表、历史版本如何保留、删除如何实现）；freshness 判定依据（全局 digest 还是窗口输入 digest）；指标与 delta 的确定性计算来源。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §12 L3、§16.2、§20.3 FR-203/FR-205、§23.5；`DEC-MVP-C-REVIEW-001` |
| SPEC | `SPEC-C3-REVIEW-001` §2..§7；S1 v0.6、S2 v0.5、S6 v0.5 |
| Acceptance Test | `C3-001..010` |
| Traceability | 矩阵 §4.17 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；SQLite PRAGMA 沿用 ADR-0001。
- 报告与比较为 Derived：不作 Canonical 证据、不被 Canonical 引用、写入不经 ChangeSet（B2/B5/B6 先例）。
- 同窗口历史版本保留不覆盖；可删除可重建且重建等价（`C3-INV-003/004`）。
- 指标与 delta 确定性可复现；指标只从 Canonical 层计算，不读 Derived 输入（`C3-INV-002`）。
- 不决定：自然语言生成、因果/趋势推断、北极星看板、真实数据。

## 4. 候选方案

### Option A：复用 ledger_records（record_type=review_report / phase_comparison），窗口输入 digest 判定 freshness

- 做法：每次显式生成向 `ledger_records` 追加一行（零 schema 变更；record_type 无 CHECK 约束）；同窗口历史版本即 append-only 行天然保留；`view_revision` 取该窗口现存最大版本 +1。payload 存 `source_digest` = 该窗口指标输入的确定性 digest（窗口内 Episode、相关 Commitment/Decision、全量 Hypothesis 状态快照的 canonical JSON 哈希）；freshness 为读取时纯函数：当前窗口输入 digest 等于 `source_digest` 则 fresh 否则 stale。删除 = 新增 store 窄方法 `delete_ledger_record(record_id)` 物理删除 Derived 行；重建 metrics 与同 Canonical 时点等价。
- 优点：零 schema 变更；append-only 天然满足历史不覆盖；窗口输入 digest 精确实现"相关窗口 stale"而非全局误伤；record_id 稳定可定位使删除语义干净；与 B5/B6 的 Derived 收据先例一致。
- 代价与风险：需给 store 增加一个窄删除方法；窗口输入 digest 需要模块内稳定实现（复用 `_canonical_json` 同款规范化）。
- 可逆性：纯新增模块加一行级删除方法，可整体回退。

### Option B：复用 summary_projections（新增 kind=review_report / phase_comparison）

- 优点：B2 freshness 机制现成。
- 代价与风险：kind CHECK 约束需 schema 迁移；projection 表语义是"单一当前投影"，同窗口历史版本保留需要额外设计；删除重建语义与 B2 重建收据耦合，收益不抵成本。

### Option C：新建 review_reports / phase_comparisons 专用表

- 优点：查询直接、语义独立。
- 代价与风险：schema 迁移与 digest/对账/导出适配面扩大；本切片规模（固定合成个位数窗口）下重复建设 ledger 已有能力。

## 5. 决定

采纳 Option A。

**5.1 存储**：`src/noetide_micro/reviews.py` 以 `SemanticStore.put_ledger_record` 追加报告/比较行。ReviewReport payload：`review_id`（`review:{kind}:{start}:{end}:v{n}`）、`review_kind`、`window_start`、`window_end`、`metrics`（七项确定性计数）、`view_revision`、`source_digest`、`generated_at`（固定 synthetic clock）、`derived_only=true`。PhaseComparison payload：`comparison_id`、`metric_set_id`、`window_a`、`window_b`、`deltas`（逐指标 signed delta，含 hypothesis_status_counts 逐状态 delta）、`generated_at`、`derived_only=true`。

**5.2 freshness**：模块内 `_window_input_digest(store, kind, start, end)` 对窗口指标输入（窗口内 episode 对象、相关 commitment/decision 对象、全部 hypothesis 对象的规范化 JSON 排序列表）做 SHA-256；`present_review` 读取时重算并比较 `source_digest`，返回 `freshness=fresh|stale`，不回写历史行。

**5.3 删除与重建**：`store.delete_ledger_record(record_id)`（本 ADR 新增的窄方法，事务内单条 DELETE，只用于 Derived 记录）；删除后同窗口重建，`view_revision` 按现存最大版本 +1 计算（全删后回到 1），metrics 与同 Canonical 时点等价。

**5.4 计算来源**：指标只从 `canonical_object_summaries()` 的 Canonical payload 计算（object_type in episode/commitment/decision/hypothesis），fixture 定义字段：`episode.occurred_on`、`commitment.status/due_at/completed_at/cancelled_at`、`decision.reviewed_at`（存在即已复盘）、`hypothesis.status`。比较入口校验两窗口同 `review_kind`、同长度、同 `metric_set_id` 且日期合法，否则显式 `rejected` 零写入。

## 6. 后果

- 正面：零 schema 变更落地 Derived 报告/比较；历史保留由 append-only 天然保证；窗口输入 digest 避免全局 digest 的无关 stale；与全仓对账/导出兼容。
- 代价：`delete_ledger_record` 是 store 层新增的删除能力，必须被约束为仅 Derived 记录使用（reviews 模块只传 review/phase_comparison 的 record_id；Canonical 审计行不经此入口）。
- 回退：删除 `reviews.py`、`c3_testing_adapter.py` 与对应 suite；ledger 中合成报告行随 fixture 消失，无迁移负担。
