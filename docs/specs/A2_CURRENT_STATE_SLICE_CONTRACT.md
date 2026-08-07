# A2 current_state Core View 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-A2-CURRENT-STATE-001` |
| 版本 | `0.1` |
| 状态 | `Approved for A2 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-A-CURRENT-STATE-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-A-CURRENT-STATE-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：证明第三个 MVP-A Core View `current_state` 可在固定合成 Canonical snapshot 上构建 fresh 投影、在 Canonical 变更后显式 stale、重建等价，且永不反向成为事实证据。

非目标：通用查询语言、自由文本检索、UI/应用壳、权限/舱室 runtime、实体合并、六态回答重实现、Commitment/提醒扩展、L3 画像、B4 对账/失败队列/Semantic Diff、多设备、连接器、真实数据。

## 2. 对象与字段

`current_state` 是一个 Derived Core View，不是 Canonical 对象。视图名固定为 `current_state`。

```yaml
view_name: current_state
data_revision: 构建时的全局 Canonical revision
view_revision: 投影内容对应的 revision
freshness_status: fresh | stale | updating | unavailable
payload:
  objects: 按 object_id 排序的当前有效对象列表
    object_id: stable ID
    object_type: entity | relationship | state | assertion
    object_revision: global data_revision
    valid_time: [start, end|null]
  object_count: objects 数量
synthetic_profile_id: a2_current_state_v1
```

只收录 `entity`、`relationship`、`state`、`assertion` 四类 Canonical 对象中在 fixture clock 下当前有效者：`valid_time.start <= clock`，且 `valid_time.end` 为 `null` 或 `> clock`。已结束的历史区间只保留在 Canonical/Ledger，不进入 `current_state` payload。

## 3. 状态机

```text
Projection: absent -> fresh
fresh -> stale -> rebuilding -> fresh
stale|rebuilding -> unavailable
```

- `fresh`：`data_revision == view_revision == 当前全局 revision`。
- Canonical 每次经 ChangeSet 发布新 revision 后，既有投影必须 stale，不得伪装 current。
- `unavailable` 只表示受控失败后的显式不可用；Canonical 仍可读。

## 4. 时间、证据与权限

- "当前有效"只由 fixture clock 与对象 `valid_time` 判定；clock 推进本身不产生 Canonical revision。
- `current_state` 没有 `evidence_refs`；其内容不得作为 Evidence Ref、Assertion input 或 ChangeSet trigger。
- A2 不实现权限 runtime。无法解释 caller/profile 时 fail closed。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `A2-INV-001` | `current_state` 是 Derived；绝不写回 Canonical；candidate/projection 不是 Canonical。 |
| `A2-INV-002` | Historical State 不被 Current 覆盖；视图只含 fixture clock 下当前有效区间的对象。 |
| `A2-INV-003` | 视图 revision 与全局 `data_revision` 不对齐时必须 stale/unavailable，不得伪装 fresh/current。 |
| `A2-INV-004` | 删除投影后可仅从 Canonical 与 Source 等价重建（payload 逐字段一致）。 |
| `A2-INV-005` | 视图内容不得作为 Evidence Ref、Assertion input 或 ChangeSet trigger。 |
| `A2-INV-006` | 非合成 profile、未知 view 或未知对象类型均 fail closed 且无写入。 |
| `A2-INV-007` | Canonical 变更只经既有 ChangeSet 边界；视图构建/重建不产生新 Canonical revision。 |

## 6. 失败、撤销与审计

- preflight 失败：记录受控 failure，不写投影、不产生 revision。
- rebuild 失败：Canonical 可读；投影为 stale/unavailable，保存非证据 rebuild receipt。
- Derived 删除只删除 Derived 行和其 receipt，不删除 Canonical、Source 或 Ledger。
- 每次构建/重建保存 receipt（非证据），可由审计读取。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `A2-001` | 固定合成 snapshot（含当前与历史 State） | 构建视图 | fresh 投影，payload 只含当前有效对象且字段/排序确定 |
| `A2-002` | 非合成 profile 或未知 view | 尝试构建/读取 | fail closed，无投影、无 revision 写入 |
| `A2-003` | fresh 投影 | 读取 | 返回对象集合、object_revision 与 revision 对齐信息 |
| `A2-004` | fresh 投影存在 | Canonical 经 ChangeSet 发布新 revision | 投影 stale，不以 current 呈现 |
| `A2-005` | stale 投影 | 重建 | fresh 且与从 Canonical 直接计算的结果等价 |
| `A2-006` | fresh 投影 | 删除后重建 | 等价重建，仅依赖 Canonical 与 Source |
| `A2-007` | 已有投影 | 注入 rebuild 失败 | Canonical 可读、投影 unavailable、保存 failed receipt、无 revision 变化 |
| `A2-008` | fresh 投影 | 用作 evidence/trigger 或尝试回写 Canonical | 拒绝，Canonical 不变 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `A2-001..008` passed result 存在，且所有 `A2-INV-*` 有正/反证明时，A2 才能标记 `verified`。未执行时必须保持 `not_executed`。

## 9. 未决问题

无 blocking。A1 freshness 语义复用方式已在 §4 固定；如发现与 S3 的 Core View stale 义务冲突，回到 Change Control。
