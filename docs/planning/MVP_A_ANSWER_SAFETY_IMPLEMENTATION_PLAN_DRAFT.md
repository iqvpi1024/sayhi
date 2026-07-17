# Implementation Plan Draft：MVP-A Answer Safety

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-AS-IMPL-001` |
| Status | `Draft - blocked by suite_materialized=false` |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Product Decision | `DEC-MVP-A-AS-001` |
| SPEC Review | `REVIEW-MVP-A-AS-SPEC-001` |
| Trace | Requirements Matrix §4.1 |
| ADR / Architecture | `ADR-0002` / `ARCH-MVP-A-AS-001` |
| Acceptance | `ACCEPT-MVP-A-AS-001` |
| Suite | `absent` |

本计划完整描述未来施工顺序，但当前不是 Approved Implementation Plan。suite materialized 和开发前 Gate 通过前，任何模型都不得执行 `AS-TASK-*`。

## 1. 目标

实现一个完全本地、固定合成、只读的六态 AnswerEnvelope 切片，并证明新增能力不破坏已验证 Micro 变更链路。

## 2. 预期模块边界

| Planned Module | 责任 | 禁止责任 |
|---|---|---|
| `schema.sql` / `store.py` 增量 | Coverage/Assertion fixture seed、只读 digest | 不以 trigger 判状态，不改 Micro 语义 |
| `answers.py` | Evidence/Coverage/Conflict/Answer evaluation | 不写 Canonical/Ledger/View，不调用模型 |
| `answer_testing_adapter.py` | test-only factory、case isolation、failure injection | 不成为产品 API |
| A1 suite artifacts | 证明 Acceptance | 不从 actual 生成 expected |

文件名以 ADR-0002 为默认；若 suite materialization 发现协议需要不同名称，只能做机械调整，不增加抽象层。

## 3. 未来业务任务

| Task ID | 范围 | 主要场景 | 完成条件 | 当前状态 |
|---|---|---|---|---|
| `AS-TASK-001` | store/schema 的 A1 additive seed | AS-010 | Coverage/Assertion fixture 幂等 seed；Micro seed/PRAGMA/外键测试不回归 | `blocked` |
| `AS-TASK-002` | AnswerEnvelope 类型与 evidence selector | AS-001/002/008/009 | direct Source only；scope/fictional/Derived 边界字段级正确 | `blocked` |
| `AS-TASK-003` | Coverage evaluator | AS-005/007 | not_covered 与 unknown 严格分离，Coverage/gap 可解释 | `blocked` |
| `AS-TASK-004` | explicit freshness evaluator | AS-006 | fixture policy 下 stale；历史查询不因年龄自动 stale | `blocked` |
| `AS-TASK-005` | conflict detector | AS-004 | 同 scope/time/perspective 冲突并列，不自动选值 | `blocked` |
| `AS-TASK-006` | unconfirmed + deterministic read-only | AS-003/010 | candidate 不进 Canonical；重复查询语义稳定；全层 digest 不变 | `blocked` |
| `AS-TASK-007` | result failure/hardening | AS-011 | artifact 写失败不发布 pass；隐私/网络/path 失败安全 | `blocked` |
| `AS-TASK-008` | full A1 run + Micro regression | 全部 | A1 35/35 required 同 run passed；新 Micro current run 49/49 passed | `blocked` |
| `AS-TASK-009` | Trace/Gate/Recovery | Process | result/模块回填；P0/P1=0；commit/tag/push 可恢复 | `blocked` |

## 4. 固定顺序

```text
AS-PRE-001..005 suite materialization
-> Plan Review and Approval
-> AS-TASK-001..007 implementation
-> AS-TASK-008 verification
-> independent audit
-> debug/re-verification if needed
-> AS-TASK-009 recovery point
```

不得并行让实现领先于 oracle。独立审计使用 `MODEL_HANDOFF_PROTOCOL.md`，实现者自查不能替代。

## 5. 每 Task 验证

每个业务 Task 至少执行：

- 该 Task 的定向 A1 semantic tests。
- 受影响 Micro 定向 tests。
- Product/SPEC/static suite validators。
- `git diff --check`。

定向 pass 不能拼接成 A1 suite passed。只有 AS-TASK-008 使用统一 runner 产生 current result。

## 6. Micro 回归与 Applicability

任何共享 `store.py`、`schema.sql`、`testing_adapter.py` 或查询模块变化都会使旧 Micro result 对新实现提交的适用性需要复核：

1. 旧 result 文件保持不可变 passed historical。
2. 在新实现提交上运行 Micro runner，输出新文件。
3. 49 required IDs 必须同一次 passed。
4. 若失败，A1 Gate closed；不能只让 A1 suite 通过。
5. 更新 Micro manifest latest result 时保留旧 result path/history。

## 7. 停止条件

- 需要默认 freshness policy 或强直接 world-claim verification rule。
- 需要处理两个以上主状态同时成立的 precedence。
- 需要写 Canonical、ChangeSet、Projection 或第三个 View。
- 需要 S4/S5/S8/S9 runtime、第三方包、外部服务或在线模型。
- 只能通过修改 Acceptance expected 或旧 Micro expected。
- 发现真实数据、凭据、工作区外读取或无法归属的相关改动。

## 8. 完成定义

- [ ] A1 suite materialized，Plan 升为 Approved。
- [ ] AS-TASK-001..009 全部 completed。
- [ ] A1 35/35 required 同一次 current run passed。
- [ ] Micro 49/49 在同一新 regression run passed。
- [ ] Matrix module/result 回填。
- [ ] 独立 Audit P0=0/P1=0。
- [ ] Recovery commit/tag/remote 可解析。

当前全部未勾选；这不是未完成工作的失败，而是开发前诚实状态。
