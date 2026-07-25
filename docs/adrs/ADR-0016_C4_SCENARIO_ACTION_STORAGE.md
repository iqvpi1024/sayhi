# ADR-0016：C4 情景与行动跟进的存储与执行形态

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-26 |
| Slice | `SLICE-MVP-C-SCENARIO-001` |
| Contract | `SPEC-C4-SCENARIO-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

C4 切片需要三个同层技术裁决：情景三元组的存储形态（复用 assertion 还是新类型）；跟进动作的存储与状态历史形态（commitment 对象 + 内嵌历史还是专用表）；`missed` 视图与专业建议禁令的执行形态。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §8.1、§20.3 FR-204/FR-206；`DEC-MVP-C-SCENARIO-001` |
| SPEC | `SPEC-C4-SCENARIO-001` §2..§7；S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5 |
| Acceptance Test | `C4-001..010` |
| Traceability | 矩阵 §4.18 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；SQLite PRAGMA 沿用 ADR-0001；零 schema 变更优先。
- 所有写入必须显式 `confirmed=True`；自动状态迁移计数恒为 0（`C4-INV-002`）。
- 情景 `assertion_kind` 恒 `predicted`；feasibility 为确定性纯函数（`C4-INV-001/003`）。
- `missed` 只 Derived；历史保留不覆盖（`C4-INV-005/006`）。
- 不决定：自动生成、评分算法、建议文案、提醒系统、真实数据。

## 4. 候选方案

### Option A：复用 canonical_objects（assertion + commitment）+ ledger 收据，payload 内嵌 revision_history

- 做法：情景存为 `canonical_objects(object_type=assertion, assertion_kind=predicted)`（C1 先例，schema CHECK 已允许）；跟进存为 `canonical_objects(object_type=commitment)`，完成时 `replace_canonical_object` 递增 `object_revision` 并把旧状态快照追加进 payload `revision_history`（C2 先例）；选择收据与跟进迁移收据进 `ledger_records`（record_type=`scenario_selection`/`follow_up_transition`）。`missed` 视图与 feasibility 为模块内纯函数。
- 优点：零 schema 变更；复用已验证的对象/revision/digest 能力；payload 自包含历史满足独立可读；与 C1/C2/C3 模式一致。
- 代价与风险：跟进历史需解析 payload JSON；本切片规模固定合成，无实际风险。
- 可逆性：纯新增模块，可整体回退。

### Option B：新增 scenario/follow_up 专用类型与表

- 优点：查询直接、语义独立。
- 代价与风险：canonical_objects CHECK 约束需 schema 迁移；与既有 assertion(commitment) 语义重复建设；收益不抵成本。

### Option C：跟进纯事件溯源（ledger 折叠当前态）

- 优点：审计性最强。
- 代价与风险：当前态需折叠计算；与全仓"当前行 + revision 历史"模式不一致。

## 5. 决定

采纳 Option A。

**5.1 模块**：`src/noetide_micro/scenarios.py` 公开七个入口，全部显式 `confirmed` 参数（`True` 才执行，否则 `rejected` 零写入）：
- `create_scenario_set(store, decision_ref, specs, confirmed, at)`：校验 decision_ref 存在且为 decision；逐 spec 计算 feasibility；`add_canonical_object` 创建 assertion 对象。
- `select_scenario(store, scenario_id, confirmed, at)`：校验情景存在且 `assertion_kind=predicted`；`put_ledger_record` 写选择收据；不改任何 Canonical 对象。
- `create_follow_ups(store, scenario_id, actions, confirmed, at)`：校验情景已被选择（存在选择收据）；逐 action 创建 commitment 对象（status=open，revision_history=[]）。
- `complete_follow_up(store, follow_up_id, confirmed, at)`：校验存在且 status=open；快照进 revision_history、status=done、object_revision+1、`replace_canonical_object`；写迁移收据。
- `follow_up_view(store, scenario_id, clock_date)`：Derived 纯计算；done 恒 done，open 且 due_date<clock 为 missed，否则 open；零写入。
- `present_scenario(store, scenario_id)`：`{scenario_id, scenario_kind, feasibility_status, assertion_kind, is_fact=False, not_professional_advice=True, derived_only=True}`；无建议文案字段。
- `attempt_mark_observed(store, scenario_id)`：无条件 `rejected` 零写入。

**5.2 feasibility 纯函数**：`hard_blockers` 非空 -> `infeasible`；否则 `soft_constraints` 非空 -> `constrained`；否则 `feasible`。

## 6. 后果

- 正面：零 schema 变更落地完整生命周期；证据/FK 约束复用既有表；payload 自包含历史；与 A/B/C 系列 digest、对账能力兼容。
- 代价：跟进历史查询需解析 payload JSON；专用历史表当前不需要。
- 回退：删除 `scenarios.py`、`c4_testing_adapter.py` 与对应 suite；canonical 中合成对象随 fixture 消失，无迁移负担。
