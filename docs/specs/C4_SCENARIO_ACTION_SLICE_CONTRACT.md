# C4 Scenario & Action 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-C4-SCENARIO-001` |
| 版本 | `0.1` |
| 状态 | `Approved for C4 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-C-SCENARIO-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5 |
| 适用范围 | `SLICE-MVP-C-SCENARIO-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：在一个固定合成 profile 上证明情景推演与行动跟进的完整管理——用户确认创建 baseline/optimistic/pessimistic 情景三元组（`assertion_kind=predicted` 恒定）、可执行性约束的确定性评估、用户确认的情景选择、用户确认的跟进动作创建与完成、过期未完成的 Derived `missed` 视图；情景永不成为事实、永不生成专业建议。

非目标：C1 已验证的单情景创建/比较闭环重建、情景自动生成、概率/置信度评分、推演算法、专业建议文案、LLM 参与、自动跟进、真实提醒系统、C5、真实数据。

## 2. 对象与字段

### 2.1 Scenario（Canonical assertion 对象，object_type=assertion，assertion_kind=predicted）

```yaml
scenario_id: stable ID（同时是 object_id）
decision_ref: 必须指向存在的 Canonical decision 对象
scenario_kind: baseline | optimistic | pessimistic
assumptions: list[固定合成假设文案]
projected_result: 固定合成预测结果文案
feasibility_constraints:
  hard_blockers: list[固定合成硬阻塞文案]
  soft_constraints: list[固定合成软约束文案]
feasibility_status: infeasible | constrained | feasible   # 创建时计算的确定性纯函数
assertion_kind: predicted        # 恒定，永不变更
object_revision: 1               # 本切片情景无后续迁移
```

feasibility 纯函数：`hard_blockers` 非空 -> `infeasible`；否则 `soft_constraints` 非空 -> `constrained`；否则 `feasible`。无评分、无推断、无随机。

### 2.2 SelectionReceipt（ledger 收据，record_type=scenario_selection）

```yaml
scenario_id / decision_ref / confirmed_by / at
```

只追加；选择不修改 Decision/Outcome 与情景对象。

### 2.3 FollowUp（Canonical commitment 对象，payload 内嵌 revision_history）

```yaml
follow_up_id: stable ID（同时是 object_id）
scenario_ref / decision_ref: 必须指向存在的 Scenario 与 Decision
title: 固定合成动作文案
due_date: 固定合成日期
status: open | done
object_revision: 单调递增；完成产生新 revision
revision_history: list[{status, at}]   # 旧状态快照，永不删除
```

### 2.4 FollowUpView（Derived 呈现，不是证据）

```yaml
follow_up_id / title / due_date
view_status: open | done | missed    # done 恒 done；open 且 due_date < clock -> missed；否则 open
derived_only: true
```

### 2.5 ScenarioView（Derived 呈现，不是证据）

```yaml
scenario_id / scenario_kind / feasibility_status
is_fact: false                       # 恒 false
not_professional_advice: true        # 恒 true
assertion_kind: predicted
derived_only: true
# 无建议文案字段；不生成任何医疗/法律/财务建议
```

## 3. 状态机

```text
Scenario:   （不存在） --用户确认创建--> predicted（终态；无迁移；upgrade-to-observed 永远 rejected）
FollowUp:   （不存在） --用户确认创建--> open --用户确认完成--> done（终态；历史保留）
FollowUpView: open 且 due_date < clock => missed（Derived 计算，不写 Canonical）
```

- 所有写入必须经用户确认入口（显式 `confirmed=True`）；未确认一律显式 `rejected` 且零写入。
- 自动状态迁移计数恒为 0；`missed` 不产生任何 Canonical 写入。
- 跟进完成产生新 revision 与收据；历史 revision 永不删除。

## 4. 时间、证据与权限

- 全部使用固定 synthetic clock；`missed` 判定只用固定 clock 日期与 `due_date`，无 wall-clock 依赖。
- 情景不进入事实证据集；Canonical 证据引用不得指向 Scenario（upgrade/引用尝试 fail closed）。
- `decision_ref`、`scenario_ref` 必须指向真实存在的 Canonical 对象；否则 fail closed 零写入。
- 固定 synthetic profile 外输入 fail closed 且无写入。
- 本切片不建设权限 runtime；仅复用既有单用户本地调用者语义。

## 5. 系统不变量

- `C4-INV-001`：情景 `assertion_kind` 恒为 `predicted`；永不进入事实证据集；upgrade-to-observed 尝试显式 rejected 零写入。
- `C4-INV-002`：所有写入必须用户确认；未确认操作显式 rejected 零写入；`auto_transitions` 恒为 0。
- `C4-INV-003`：`feasibility_status` 为声明约束的确定性纯函数；同输入恒同结果。
- `C4-INV-004`：不生成专业建议；ScenarioView 恒 `not_professional_advice=true` 且无建议文案字段。
- `C4-INV-005`：选择与跟进不修改 Decision/Outcome/情景对象；跟进状态变化产生新 revision 且历史保留。
- `C4-INV-006`：`missed` 为 Derived 视图确定性计算；无 Canonical 自动写入。
- `C4-INV-007`：profile 外输入 fail closed 零写入；无关 Canonical 层 digest 在 C4 操作前后不变。

## 6. 失败、撤销与审计

- 未确认操作（创建/选择/跟进创建/跟进完成）：显式 `rejected`，零写入。
- upgrade-to-observed 尝试：显式 `rejected`，零写入，情景保持 `predicted`。
- 非法引用（decision/scenario 不存在、profile 外 ID）：显式 `rejected`，零写入。
- 未选择情景就创建跟进：显式 `rejected`，零写入。
- 审计：选择收据、跟进迁移收据只追加进 ledger；验收结果只在测试 oracle 与 verification result 中绑定。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `C4-001` | 固定合成 profile（含已存在 Decision）/ 用户确认创建情景三元组 | 3 个 Canonical assertion 对象、`assertion_kind=predicted`、feasibility 分别为 `constrained/feasible/infeasible`、`object_revision=1` |
| `C4-002` | 同上 / 未确认创建 | 显式 `rejected`、scenario 计数 0、digest 不变 |
| `C4-003` | 已有情景 / 尝试 upgrade-to-observed | 显式 `rejected`、`assertion_kind` 保持 predicted、`is_fact=false`、无写入 |
| `C4-004` | 已有三元组 / 用户确认选择 baseline | 选择收据 1 条、Decision/Outcome digest 不变、情景对象不变 |
| `C4-005` | 已选情景 / 用户确认创建 3 个跟进 | 3 个 commitment 对象 `status=open`、scenario_ref/decision_ref 正确、`object_revision=1` |
| `C4-006` | 已有 open 跟进 / 用户确认完成其一 | `status=done`、`object_revision=2`、history 含旧快照、迁移收据 1 条、其他跟进不变 |
| `C4-007` | done + 过期 open + 未到期 open / 请求 FollowUpView | 视图 `[done, missed, open]` 精确；视图请求前后 Canonical digest 不变 |
| `C4-008` | 已有三元组 / 重复评估 feasibility | 结果与首次完全一致；pessimistic 因 hard blocker 恒 `infeasible` |
| `C4-009` | 全旅程后 / 呈现与证据隔离检查 | `is_fact=false`、`not_professional_advice=true`、无建议文案字段、事实证据集不含任何 Scenario |
| `C4-010` | 全旅程后 / 横切 + profile 外输入 | revision 链完整、收据只追加、profile 外 ID `rejected` 零写入、无关层 digest 不变、`auto_transitions=0` |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `C4-001..010` passed result 存在，且所有 `C4-INV-*` 有正/反证明时，C4 才能标记 `verified`。未执行时必须保持 `not_executed`。
