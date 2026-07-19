# B3 Commitment 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-B3-COMMITMENT-001` |
| 版本 | `0.1` |
| 状态 | `Approved for B3 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-B-COMMITMENT-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S5 v0.4、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-B-COMMITMENT-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：证明一个固定合成 Commitment 可经用户确认的 ChangeSet 创建、完成、带原因取消和补偿撤销；固定 clock 产生可失效的 Derived `due_status`。

非目标：自然语言提取、模型、真实通知、后台调度、日历/邮件/任务连接器、自动完成/取消/延期、财务/健康/法律语义、权限/MCP runtime、同步和真实数据。

## 2. 对象与字段

```yaml
commitment_id: stable ID
object_type: commitment
commitment_kind: synthetic_obligation
responsible_ref: Entity ID
statement_locator: direct Source locator
due_time: RFC3339 UTC instant
status: open | completed | cancelled
cancel_reason: required only when cancelled
valid_time: [start, end|null]
recorded_at: RFC3339 UTC instant
review_status: unreviewed | user_confirmed
object_revision: global data_revision
synthetic_profile_id: b3_commitment_v1
```

`Obligation` 是 `Commitment` 的语义配置，不是新对象。`statement_locator` 必须是直接、存在、同一 synthetic profile 的 Source locator。Derived `due_status` 只能是 `upcoming | due | overdue | closed`，不得进入 Canonical、Evidence Ref 或 ChangeSet trigger。

## 3. 状态机

```text
Candidate: proposed -> approved -> published(open)
published(open) -> completed | cancelled
published(completed|cancelled) -> reverted-by-compensation(open)

DueProjection: absent -> fresh
fresh -> stale -> rebuilding -> fresh
stale|rebuilding -> unavailable
```

允许的 Canonical 转换必须由单一用户确认的 ChangeSet 发布。`cancelled` 必须带非空 `cancel_reason`；`completed` 不得借此修改 Source、Relationship、trust、closeness、Hypothesis 或其他 Commitment。任何关系变化都不得自动完成、取消、延期或重分配 Commitment。

## 4. 时间、证据与权限

- `due_time` 是承诺到期语义；`recorded_at` 是系统记录时间，二者不得互换。
- 固定 B3 clock 只用于 Derived `due_status`；clock 推进不会产生 Canonical revision。
- 所有 Canonical 状态变更保留直接 Source locator；due projection 没有 `evidence_refs`。
- B3 不实现权限 runtime。无法解释 caller/profile/compartment 时 fail closed。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `B3-INV-001` | Commitment 创建、完成、取消和补偿撤销均经 ChangeSet；candidate/due projection 不是 Canonical。 |
| `B3-INV-002` | 关系状态或 Derived due-status 不自动改变 Commitment。 |
| `B3-INV-003` | `cancelled` 必有原因；`completed`/`cancelled` 的历史与 revision 保留。 |
| `B3-INV-004` | due-status 是固定 clock 的 Derived，revision 不对齐时 stale/unavailable，不伪装为 current。 |
| `B3-INV-005` | Derived due-status 不能作为 Evidence Ref、Assertion input 或 ChangeSet trigger。 |
| `B3-INV-006` | 非合成 profile、未知 required status、缺 Source/Entity/time 或无取消原因均 fail closed 且无 Canonical/revision 写入。 |
| `B3-INV-007` | 删除全部 due projection 后，可仅从 Canonical Commitment、Source 和固定 clock 重建等价结果。 |

## 6. 失败、撤销与审计

- preflight 失败：记录受控 failure，不增加 revision，不创建半完成 Commitment。
- Derived rebuild 失败：Canonical Commitment 可读；projection 为 stale/unavailable，保存非证据 rebuild receipt。
- 撤销使用新的补偿 ChangeSet/revision 恢复等价 `open`，不回拨全局 revision，也不删除原发布、完成或取消记录。
- Derived 删除只删除 Derived 行和其 receipt，不删除 Canonical、Source 或 Ledger。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `B3-001` | 有固定合成 candidate | 用户确认发布 | open Commitment 经 ChangeSet 发布且保留 direct locator |
| `B3-002` | 缺 Source/Entity/due/profile | 尝试发布 | fail closed，无 Commitment、revision 或 Source receipt |
| `B3-003` | 已发布 open Commitment | 固定 clock 前/到期/后读取 | 得到确定性 upcoming/due/overdue Derived status |
| `B3-004` | open Commitment | 用户确认完成 | 新 revision、status=completed、due projection stale |
| `B3-005` | open Commitment | 用户确认取消 | 必须有原因；无原因 fail closed |
| `B3-006` | completed/cancelled Commitment | 补偿撤销 | 新 revision 恢复 open，历史 Ledger 保留 |
| `B3-007` | 已有 due projection | 删除并 rebuild 或注入失败 | 等价重建；失败时 Canonical 可读、projection stale/unavailable |
| `B3-008` | due projection 或关系状态变化 | 用作 evidence/trigger 或尝试自动改变 Commitment | 拒绝，Canonical 不变 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `B3-001..008` passed result 存在，且所有 `B3-INV-*` 有正/反证明时，B3 才能标记 `verified`。未执行时必须保持 `not_executed`。
