# A3 实体合并候选与拆分回滚切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-A3-ENTITY-MERGE-001` |
| 版本 | `0.1` |
| 状态 | `Approved for A3 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-A-ENTITY-MERGE-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5 |
| 适用范围 | `SLICE-MVP-A-ENTITY-MERGE-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：证明两个固定合成 Person Entity 的 merge proposal 经用户确认的 ChangeSet 原子发布（来源实体 `identity_status=merged`、`merged_into` 指向目标、全部 Canonical 引用重定向），以及 split compensation 经新 ChangeSet 精确恢复合并前引用与活跃状态；全程历史不删除、trust/closeness/人格判断不被自动修改。

非目标：自动人物合并、模糊身份匹配/消歧、合并候选自动评分、真实联系人导入、权限/舱室 runtime、UI/应用壳、非 Person 实体合并、批量或跨 profile 合并、多设备同步。

## 2. 对象与字段

```yaml
merge_proposal:
  operation: merge
  source_entity_ref: Entity ID (Person, identity_status=active)
  target_entity_ref: Entity ID (Person, identity_status=active)
  reason: non-empty string
  synthetic_profile_id: a3_entity_merge_v1

merge_record (Canonical 审计记录, 随 merge 发布原子写入):
  merge_id: stable ID
  source_entity_ref: Entity ID
  target_entity_ref: Entity ID
  pre_merge_references: [{ref_kind, object_id, field, old_value}]
  published_revision: global data_revision

split_proposal:
  operation: split
  merge_ref: merge_id
  reason: non-empty string
  synthetic_profile_id: a3_entity_merge_v1
```

`ref_kind ∈ {relationship_party, state_subject, assertion_subject}`。`pre_merge_references` 是 split 等价恢复的唯一依据，必须完整记录合并时全部受影响引用；它随 merge ChangeSet 原子产生，不得事后补写。

合并发布后：source Entity `identity_status=merged`、`merged_into=target_entity_ref`；target Entity 保持 `active`。两个实体的全部历史（Source、Assertion、区间、revision 链）保留。`merge_record` 不是第 13 个核心对象，是 ChangeSet 发布的审计组成部分。

## 3. 状态机

```text
Candidate: proposed -> approved -> published
Entity(source): active -> merged            (仅经用户确认的 merge ChangeSet)
Entity(source): merged -> active            (仅经用户确认的 split ChangeSet)
Entity(target): active 恒保持 active
```

允许的转换必须由单一用户确认的 ChangeSet 发布。`merge` 要求 source≠target、两者均 `active`、均属于同一 synthetic profile、reason 非空。`split` 要求引用的 `merge_record` 存在且对应 source 当前仍为 `merged`。split 不得用于撤销其他 split，历史链只增不改。

## 4. 引用重定向、原子性与视图

- merge 发布在同一 ChangeSet 内原子完成：source `identity_status`/`merged_into` 更新 + 全部受影响引用重定向到 target + `merge_record` 写入；任一失败则整体不应用，无部分重定向。
- 每个被重定向的对象产生新 `object_revision`（指向 merge 发布的全局 revision）；未被引用的对象 revision 不变。
- split 发布在同一 ChangeSet 内原子完成：按 `merge_record.pre_merge_references` 逐条恢复原始引用值、source 恢复 `active` 并清除 `merged_into`；恢复后每个受影响对象 payload 与合并前逐字段一致。
- merge/split 发布后，人物卡、关系时间线与 `current_state` 三个 Core View 必须显式 stale 或重建一致，不得伪装 fresh。
- 合并/拆分不得修改 trust、closeness、人格判断、Source 内容或其他无关对象。

## 5. 时间、证据与权限

- `merge_record.recorded_at` 是系统记录时间；实体与引用对象的历史 `valid_time` 区间不因合并/拆分被改写或覆盖。
- 所有 proposal 保留直接 Source locator；`merge_record` 的 `pre_merge_references` 是审计数据，不是 Evidence Ref 的替代品。
- A3 不实现权限 runtime。无法解释 caller/profile/compartment 时 fail closed。

## 6. 系统不变量

| ID | 不变量 |
|---|---|
| `A3-INV-001` | merge 与 split 都是规范写入，仅经用户确认的 ChangeSet 原子发布；candidate 不是 Canonical。 |
| `A3-INV-002` | merge 发布原子完成状态更新、全部引用重定向与 `merge_record` 写入；失败时无任何部分应用。 |
| `A3-INV-003` | 被合并实体的历史（Source、Assertion、区间、revision 链）永不删除或覆盖；原 Source identity 保留。 |
| `A3-INV-004` | split 按 `merge_record` 精确恢复合并前引用；恢复后受影响对象 payload 与合并前逐字段一致。 |
| `A3-INV-005` | trust、closeness、人格判断与无关对象不因 merge/split 被自动修改。 |
| `A3-INV-006` | merge/split 发布后三个 Core View 显式 stale 或重建一致，不得伪装 fresh。 |
| `A3-INV-007` | 非合成 profile、source=target、非 active 实体、缺 reason、未知 merge_ref 或重复 split 均 fail closed 且无 Canonical/revision 写入。 |

## 7. 失败、撤销与审计

- preflight 失败：记录受控 failure，不增加 revision，不创建半完成 merge。
- 重定向中途失败：整个 ChangeSet 不发布；Canonical 保持合并前状态且可读。
- 撤销 merge 的唯一路径是 split compensation ChangeSet；不回拨全局 revision，不删除 merge 发布记录与 `merge_record`。
- 审计可回答：谁在哪个 revision 合并了什么、影响了哪些引用、何时被拆分恢复。

## 8. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `A3-001` | 两个固定合成 active Person Entity，各有 Relationship/State/Assertion | 用户确认 merge proposal | ChangeSet 原子发布：source=merged + `merged_into`、全部引用重定向、`merge_record` 完整 |
| `A3-002` | 缺 reason/source=target/非 active/非 profile | 尝试发布 merge | fail closed，无 revision、无 `merge_record`、引用不变 |
| `A3-003` | merge 已发布 | 读取 source 历史与三个 Core View | 历史完整可见；视图 stale 或重建一致，不伪装 fresh |
| `A3-004` | merge 已发布 | 注入重定向中途失败 | 整体不应用；Canonical 保持合并前状态且可读 |
| `A3-005` | merge 已发布 | 用户确认 split proposal | 新 ChangeSet 恢复全部原始引用，source 恢复 active，受影响对象与合并前逐字段一致 |
| `A3-006` | split 已发布 | 读取审计链 | merge 与 split 记录完整可查，历史只增不改 |
| `A3-007` | merge/split 已发布 | 检查 trust、closeness、人格判断与无关对象 | 全部未被修改 |
| `A3-008` | 未知 merge_ref / 重复 split / source 非 merged | 尝试 split | fail closed，无 revision 写入 |

## 9. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `A3-001..008` passed result 存在，且所有 `A3-INV-*` 有正/反证明时，A3 才能标记 `verified`。未执行时必须保持 `not_executed`。
