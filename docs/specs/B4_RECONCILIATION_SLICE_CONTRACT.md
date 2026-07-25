# B4 Reconciliation 与 Semantic Diff 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-B4-RECONCILIATION-001` |
| 版本 | `0.1` |
| 状态 | `Approved for B4 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-B-RECONCILIATION-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-B-RECONCILIATION-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：在一个固定合成 profile 上证明三类对账能力——写后校验与日常增量对账（失败队列、stale 视图、孤儿引用、未消费 ChangeSet）、周期深度对账（从 Canonical 重建核心投影并比较）、以及只读 Semantic Diff（两个 revision 间的字段级差异呈现）。

非目标：多设备同步、自动静默修复或机械修复执行器、后台调度器、重大升级对账的完整回归编排、性能 SLO、通用图 diff、真实数据、LLM、连接器。

## 2. 对象与字段

### 2.1 ReconciliationReport（只读派生产物，不进入 Canonical）

```yaml
report_id: stable ID within the run
profile_id: b4_reconciliation_v1
mode: incremental | deep
generated_at: fixed synthetic clock
findings: list[Finding]
finding_kinds (incremental): failure_queue | stale_view | orphan_reference | unconsumed_changeset
deep_result: match | mismatch   # deep mode only, per projection partition
summary: {finding_count, quarantined: true, auto_repair_attempted: false}
```

```yaml
finding_id: stable ID
kind: failure_queue | stale_view | orphan_reference | unconsumed_changeset
subject_ref: affected projection / record / changeset ID
detail: fixed synthetic description
disposition: quarantined_reported    # 唯一允许值；绝不 silently_repaired
```

### 2.2 SemanticDiff（查询时派生，不持久化）

```yaml
diff_id: stable ID within the run
object_ref: Canonical object ID
base_revision: rev_010
target_revision: rev_011 | rev_012
change_type: create | modify | no_change
field_diffs: list[{field_path, before, after}]
derived_only: true
```

`ReconciliationReport` 与 `SemanticDiff` 都不是 Canonical 对象，不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。深度对账按投影分区（person_card / relationship_timeline / current_state）逐一重建比较，不要求整图重算。

## 3. 状态机

对账运行：`requested -> scanning -> report_issued`（无 auto_repair 分支）。发现处置唯一终态为 `quarantined_reported`。Semantic Diff 无状态机：每次查询即时派生，不缓存为事实。

## 4. 时间、证据与权限

- 报告与 diff 使用固定 synthetic clock；diff 不回填或修改任何 `recorded_at`。
- 对账只读 Canonical、L2 投影与 revision ledger；任何修复性写入（本切片不实现）都必须经 ChangeSet。
- 报告可引用对象 ID 与 revision，但不含 profile 外数据；固定 synthetic profile 外输入 fail closed 且无写入。

## 5. 系统不变量

- `B4-INV-001`：对账发现只隔离 + 报告；不得静默改写 Canonical 语义（`auto_repair_attempted=false` 恒成立）。
- `B4-INV-002`：Semantic Diff 是 Derived；不持久化、不作证据、不触发写入（diff 查询前后 Canonical digest 不变）。
- `B4-INV-003`：深度对账增量/分区执行，逐投影重建比较，不要求整图重算。
- `B4-INV-004`：未确认 candidate 不因对账或 diff 成为事实。
- `B4-INV-005`：trust、closeness、人格判断不因对账或 diff 被自动修改。
- `B4-INV-006`：撤销历史与补偿 revision 不因对账被擦除。
- `B4-INV-007`：profile 外输入 fail closed 且无写入。

## 6. 失败、撤销与审计

- 对账自身失败：返回显式 unavailable 的报告壳，不得返回空报告冒充"无发现"。
- 深度对账检出 mismatch：报告 mismatch 分区与期望/实际投影 digest，原投影不被改写。
- diff 目标 revision 不存在：显式拒绝，不猜测。
- 审计：报告与 diff 结果只在测试 oracle 与 verification result 中绑定；不新增 Canonical 审计对象。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `B4-001` | 干净 profile（rev_010 + 受控发布后）/ 执行写后校验 + 增量对账 | L1/L2 revision 一致；报告 `finding_count=0`；`auto_repair_attempted=false` |
| `B4-002` | 注入投影失败条目 / 增量对账 | 检出 `failure_queue` 发现；`disposition=quarantined_reported`；原投影不被改写 |
| `B4-003` | 制造 stale 视图（L2 投影停留旧 revision）/ 增量对账 | 检出 `stale_view` 发现并报告 subject |
| `B4-004` | 注入孤儿引用（派生记录指向不存在对象）/ 增量对账 | 检出 `orphan_reference` 发现 |
| `B4-005` | 存在 proposed/approved 未发布 ChangeSet / 增量对账 | 检出 `unconsumed_changeset` 发现 |
| `B4-006` | 干净 profile / 深度对账三分区 | 逐分区 `match`；投影不被改写 |
| `B4-007` | 注入投影偏差 / 深度对账 | 检出 `mismatch` 分区与期望/实际 digest；原投影不被改写；不静默修复 |
| `B4-008` | 发布后 / 查询 `state_contact_001` rev_010 vs rev_011 的 Semantic Diff | `change_type=modify`；字段级 before/after 与发布一致；含 revision 引用 |
| `B4-009` | Hypothesis 对象存在 / 查询 diff 与 no_change 对象 | Hypothesis 变化可呈现；未变对象 `no_change`；diff 查询前后 Canonical digest 不变；diff 不持久化 |
| `B4-010` | 全旅程后 / 横切检查 + profile 外输入 | trust/closeness/人格/历史不变；撤销历史保留；profile 外输入 fail closed 无写入 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `B4-001..010` passed result 存在，且所有 `B4-INV-*` 有正/反证明时，B4 才能标记 `verified`。未执行时必须保持 `not_executed`。
