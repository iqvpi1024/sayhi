# Implementation Plan：C6 MVP Release Gate

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-C-C6-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-C-RELEASE-001` |
| Decision | `DEC-MVP-C-RELEASE-001` |
| Contract | `SPEC-C6-RELEASE-001` v0.1 |
| ADR / Architecture | `ADR-0018` / `ARCH-C6-RELEASE-001` |
| Suite | `tests/c6_suite_manifest.json`，materialized |

## 1. 施工原则

- 审计只读；不修改任何已 verified artifact、不移动 tag、不写业务库。
- 任一审计项失败即 overall failed；不得跳过或文档化代替。
- 首年非目标保持关闭；beta_ready 不等于已发布。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `C6-TASK-001` | `run_c6_release_audit.py` 八项审计 + validator + manifest | §2/§4 | 审计 runner 可执行；validator materialized PASSED | `completed` |
| `C6-TASK-002` | 审计真实执行与 immutable result 绑定 | §6 | 同一次 run 8/8 passed；manifest 绑定 | `completed`；run1 failed（validator 自哈希滞后 + 旧 fixture 字段口径）已修正并留痕 `c6-audit-run1-failed-20260726.json`，run2 8/8 passed 绑定 `c6-20260726.json` |
| `C6-TASK-003` | Beta 门禁复核文档 | §3/§7 | 引用同一次 passed result；非目标关闭清单完整 | `completed`；`BETA_GATE_REVIEW_2026-07-26.md` beta_ready=true |
| `C6-TASK-004` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、tag 仅在审查通过后创建 | `completed`；Gate Review `C6_RELEASE_GATE_REVIEW_2026-07-26.md` P0=0/P1=0，recovery tag `c6-mvp-release-gate-rp-20260726` |

## 3. 固定顺序

C6-TASK-001 -> C6-TASK-002 -> C6-TASK-003 -> C6-TASK-004。任何 Task 不得修改已 verified 切片的 fixture/oracle/结果。
