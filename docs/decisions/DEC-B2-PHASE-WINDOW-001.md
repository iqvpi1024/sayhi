# DEC-B2-PHASE-WINDOW-001：固定 B2 phase window 解释

| 字段 | 值 |
|---|---|
| 状态 | `decided` |
| 日期 | 2026-07-19 |
| 适用范围 | `SLICE-MVP-B-EPISODE-SUMMARY-001` 的 `b2_episode_summary_v1` fixed synthetic profile |
| 上游 | `SPEC-B2-EPISODE-SUMMARY-001` §8；`DEC-MVP-B-EPISODE-SUMMARY-001` |

## 问题

`SPEC-B2-EPISODE-SUMMARY-001` §8 要求 `phase_summary` 的窗口由 fixture 显式给出。当前 B2 fixture 显式给出了每条 Episode candidate 的 `valid_time`，但没有第二个 phase-window 字段。

## 决定

在且仅在 `b2_episode_summary_v1` 中，`phase_summary.time_window` 取目标 Episode 已显式给出的 `valid_time`。它不推断更长阶段、不跨 Episode 聚合，也不成为未来通用 phase grouping 规则。

## 理由

这保留了 fixture 已有的确定性时间边界，避免从文本、关系或摘要内容推断 phase，同时允许 `day_summary` 与 `phase_summary` 都保持可重建、可追溯的 Derived Projection。

## 影响与边界

- `B2-TASK-003` 可实现 fixed deterministic projector/reader。
- 不修改 PRD、B2 Contract、fixture 或 oracle。
- 真实数据、跨 Episode phase、自动聚类和通用 phase 规则仍为后置范围，必须另行产品决定。
