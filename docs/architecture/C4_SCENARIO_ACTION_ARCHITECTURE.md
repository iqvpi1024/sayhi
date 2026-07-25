# C4 Scenario & Action 架构说明

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-C-SCENARIO-001` |
| Contract | `SPEC-C4-SCENARIO-001` v0.1 |
| ADR | `ADR-0016` |
| 日期 | 2026-07-26 |

## 1. 模块边界

```text
tests/fixtures/c4_scenario_action_v1/fixture.json   固定合成 profile（Decision + 情景三元组定义 + 跟进动作清单）
tests/fixtures/c4_scenario_action_v1/oracles.json   C4-001..010 精确期望
src/noetide_micro/c4_testing_adapter.py             fixture 播种 + scenario 分发 + layer 快照
src/noetide_micro/scenarios.py                      七入口（create/select/follow-ups/complete/view/present/upgrade-reject）
```

- 情景 = Canonical assertion（assertion_kind=predicted 恒定）；跟进 = Canonical commitment（payload 内嵌 revision_history）。
- 选择/迁移收据 = ledger_records（只追加）。
- missed/feasibility/呈现 = 模块内纯函数，零写入。

## 2. 数据流

```text
fixture --adapter seed--> Canonical decision 对象
create_scenario_set(confirmed) --计算 feasibility--> canonical assertion x3
select_scenario(confirmed) --append--> ledger(scenario_selection)
create_follow_ups(confirmed) --校验已选择--> canonical commitment xN (open)
complete_follow_up(confirmed) --快照+递增--> replace_canonical_object + ledger(follow_up_transition)
follow_up_view(clock) --纯计算--> open|done|missed（Derived，零写入）
```

## 3. 不变量落点

| 不变量 | 落点 |
|---|---|
| C4-INV-001 predicted 恒定 | attempt_mark_observed 无条件 rejected；呈现 is_fact=false |
| C4-INV-002 确认门禁 | 全部入口 confirmed-only；adapter 统计 auto_transitions=0 |
| C4-INV-003 确定性 feasibility | 纯函数 + oracle 精确匹配 |
| C4-INV-004 非专业建议 | ScenarioView 无建议字段、not_professional_advice 恒 true |
| C4-INV-005 选择/跟进不改 Decision | digest 断言 + revision_history |
| C4-INV-006 missed 只 Derived | follow_up_view 零写入 + digest 断言 |
| C4-INV-007 fail closed | profile 外 rejected + 无关层 digest 断言 |

## 4. 与其他切片关系

- 复用 C1 的 predicted assertion 持久化模式；不重建 C1 单情景创建/比较闭环。
- 复用 C2 的 revision_history 内嵌与迁移收据模式；复用 B4 的确定性 Derived 状态视图思路。
- 与 C3 复盘指标（commitments_completed 等）正交：C4 跟进是独立合成 profile，不进入 C3 fixture。
