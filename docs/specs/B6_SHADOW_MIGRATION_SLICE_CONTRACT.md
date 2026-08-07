# B6 Shadow Migration 与压测消歧传播切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-B6-SHADOW-MIGRATION-001` |
| 版本 | `0.1` |
| 状态 | `Approved for B6 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-B-SHADOW-MIGRATION-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-B-SHADOW-MIGRATION-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：在一个固定合成复杂 profile 上证明两类能力——影子迁移（v1->v2 模拟变换写入影子副本，迁移后深度对账逐分区 match/mismatch，原始库零改动，失败无部分写入）与压测消歧传播（成规模合成相似实体的确定性候选计数、未确认不自动合并、已确认合并传播计数确定、批量处理计数可复现、bitemporal 历史随迁移完整保留）。

非目标：真实历史迁移、真实连接器、真实数据、wall-clock 性能 SLO、并发迁移、增量实时同步、多设备、自动消歧合并、LLM、真实 schema 演进合同。

## 2. 对象与字段

### 2.1 ShadowCopy（非 Canonical 可丢弃副本，不是证据）

```yaml
shadow_id: stable ID within the run
source_profile_id: b6_shadow_migration_v1
migration_version: v1_to_v2
state: created -> migrating -> reconciled | failed | discarded
transform_log: list[{transform_id, kind, count}]   # 确定性计数
derived_only: true
```

### 2.2 DisambiguationCandidate（候选，不是事实）

```yaml
candidate_id: stable ID
entity_pair: [entity_ref_a, entity_ref_b]
match_key: fixed synthetic normalized name key
status: proposed        # 唯一初始态；本切片无自动合并
```

### 2.3 MergePropagation（已确认合并的确定性传播报告）

```yaml
merge_ref: stable ID
propagated_references: int      # 确定性计数
batch_count: int                # 确定性批次数
history_preserved: true
```

影子副本、消歧候选与传播报告都不是 Canonical 证据来源；迁移程序不绕过 ChangeSet 修改原始库 Canonical（本切片原始库完全只读）。

## 3. 状态机

ShadowCopy：`created -> migrating -> reconciled | failed -> discarded`；失败影子只能 discarded，不得转正。DisambiguationCandidate：`proposed`（本切片无自动转换；已确认合并仅作用于显式给定的 merge 指令）。迁移运行失败：显式 `failed`，原始库零部分写入。

## 4. 时间、证据与权限

- 全部使用固定 synthetic clock；迁移不回填任何 recorded_at。
- 影子副本与压测报告可引用对象 ID 与计数，但不含 profile 外数据；固定 synthetic profile 外输入 fail closed 且无写入。
- 深度对账复用 B4 合同（SPEC-B4-RECONCILIATION-001）的逐分区 match/mismatch 语义。

## 5. 系统不变量

- `B6-INV-001`：原始库在任何影子迁移（成功或失败）后语义不变（digest 前后一致）。
- `B6-INV-002`：迁移程序不绕过 ChangeSet 修改原始库 Canonical；影子副本不是 Canonical 证据。
- `B6-INV-003`：未确认消歧候选不因压力或迁移自动合并或升级为事实（auto_merge 恒为 0）。
- `B6-INV-004`：迁移与传播保留全部 bitemporal 历史（revision、快照、翻译历史、撤销记录逐条对应）。
- `B6-INV-005`：压测计数确定性可复现（候选对数、传播数、批次数为固定值）。
- `B6-INV-006`：迁移失败无部分写入原始库；失败影子只能 discarded。
- `B6-INV-007`：profile 外输入 fail closed 且无写入。

## 6. 失败、撤销与审计

- 迁移中途故障注入：返回显式 `failed` 与故障点；原始库 digest 不变；影子标记可丢弃。
- 影子对账 mismatch：报告分区与 digest 对；不静默修复、不回写原始库。
- 审计：迁移与压测结果只在测试 oracle 与 verification result 中绑定；不新增 Canonical 审计对象。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `B6-001` | 固定合成复杂 profile / 执行 v1->v2 影子迁移并深度对账 | 影子三分区 `match`；原始库 digest 不变 |
| `B6-002` | 同上 / 校验变换正确性 | transform_log 计数确定；影子内容符合 v2 期望；原始库不变 |
| `B6-003` | 注入迁移中途故障 / 执行迁移 | 显式 `failed` + 故障点；原始库零部分写入；影子 `discarded` |
| `B6-004` | 迁移后向影子注入偏差 / 深度对账 | 报告 mismatch 分区与 digest 对；不静默修复；原始库不变 |
| `B6-005` | 12 个合成相似实体（4 组同名变体）/ 消歧扫描 | 候选对计数确定（12 对）；`auto_merges=0`；候选全部 `proposed` |
| `B6-006` | 显式给定一次已确认合并 / 传播引用 | `propagated_references` 计数确定；历史保留；未涉及实体不受影响 |
| `B6-007` | 12 条合成输入、batch_size=5 / 批量处理 | `batches=3`、`processed=12` 计数确定可复现；无部分批次丢失 |
| `B6-008` | 含多 revision、快照、翻译历史的 profile / 影子迁移 | revision、快照、翻译历史逐条对应；undo 历史完整 |
| `B6-009` | 迁移与压测完成后 / 证据边界检查 | 影子与压测报告 `derived_only=true`；Canonical 不引用影子 |
| `B6-010` | 全旅程后 / 横切检查 + profile 外输入 | 原始库 digest 不变；历史完整；候选未自动合并；profile 外输入 fail closed 无写入 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `B6-001..010` passed result 存在，且所有 `B6-INV-*` 有正/反证明时，B6 才能标记 `verified`。未执行时必须保持 `not_executed`。
