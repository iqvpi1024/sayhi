# 实施规划说明

## 1. 职责

Implementation Plan 把已批准的 SPEC、ADR 和已物化 suite 分解为可施工任务。TODO 只是计划内的短清单，不能替代语义合同、技术决定或验收 oracle。

## 2. 创建门禁

只有同时满足以下条件才可将计划标记为 `Approved`：

- 当前切片已达到 `architecture_decided`。
- exact required suite 已物化，`suite_materialized=true`。
- 每项任务都有 SPEC Section、Test Ref、目标模块和完成条件。
- 没有任务引入 deferred 能力或真实个人数据。
- 计划包含失败处理、撤销/恢复、追踪更新和验证结果写入。

在 suite 物化前可以记录探索性笔记，但不得把它命名为已批准实施计划，也不得开始业务编码。

## 3. 任务粒度

每项任务应当能独立审查并回答：

1. 满足哪条合同。
2. 修改哪些明确模块。
3. 由哪些 required tests 证明。
4. 完成与失败的可观察条件是什么。
5. 是否改变数据、接口、隐私或恢复风险。

模板见 `IMPLEMENTATION_PLAN_TEMPLATE.md`。

## 4. 当前状态

`SLICE-MICRO-RELATIONSHIP-001` 的 Approved Plan 已全部完成并发布 Recovery Point。当前 active slice 为 `SLICE-MVP-A-ANSWER-SAFETY-001`，已达到 `implementation_planned`。

`MVP_A_ANSWER_SAFETY_SUITE_MATERIALIZATION_PLAN.md` 的 `AS-PRE-001..005` 已完成。`MVP_A_ANSWER_SAFETY_IMPLEMENTATION_PLAN.md` 与 `MVP_A_ANSWER_SAFETY_TASK_CARDS.md` 已通过开发前门禁；当前只授权执行 `CURRENT_HANDOFF.next_single_action` 指向的 `AS-TASK-001`。

跨切片路线见 `MASTER_DELIVERY_ROADMAP.md`。路线图不是 future slice 的业务开工批准；A1 的 Approved Plan 也不能授权 A2 或跳过单 Task handoff。

当前单一执行入口见 `docs/process/CURRENT_HANDOFF.md`；把任务交给其他模型时使用 `docs/process/AI_EXECUTION_PROMPTS.md`，不得把本目录中的长期 TODO 直接当作实施授权。
