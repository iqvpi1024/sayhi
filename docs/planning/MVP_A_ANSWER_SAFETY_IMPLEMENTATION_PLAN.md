# Implementation Plan：MVP-A Answer Safety

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-AS-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Product Decision | `DEC-MVP-A-AS-001` |
| SPEC Review | `REVIEW-MVP-A-AS-SPEC-001` |
| Trace | Requirements Matrix §4.1 |
| ADR / Architecture | `ADR-0002` / `ARCH-MVP-A-AS-001` |
| Acceptance | `ACCEPT-MVP-A-AS-001` |
| Task Cards | `CARDS-MVP-A-AS-001`，`docs/planning/MVP_A_ANSWER_SAFETY_TASK_CARDS.md` |
| Suite | `tests/answer_safety_suite_manifest.json`；approval-time SHA-256 `759878a902c46f2b1eb424eb3146561d09b75ddb780dd697bc0cca598d2e32fc` |
| Approval Gate | `GATE-MVP-A-AS-DEVELOPMENT-READY-001` |

本计划已在 A1 suite 物化并通过开发前 Gate 后批准。业务实现只能从 `CURRENT_HANDOFF.next_single_action` 指向的单一 Task 开始；Approved 不授权并行或跨 Task 施工。

逐任务允许文件、必要行为、禁止行为、定向验证、停线和交接条件以 `CARDS-MVP-A-AS-001` 为本计划的强制伴随合同。摘要表不能单独作为施工授权；若任务卡与 materialized suite 冲突，Planning Gate 必须先修正计划并重新审查，不得让 Implementer 自行解释。

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
| `AS-TASK-001` | store/schema 的 A1 additive seed | AS-010 | Coverage/Assertion fixture 幂等 seed；Micro seed/PRAGMA/外键测试不回归 | `pending` |
| `AS-TASK-002` | AnswerEnvelope 类型与 evidence selector | AS-001/002/008/009 | direct Source only；scope/fictional/Derived 边界字段级正确 | `pending` |
| `AS-TASK-003` | Coverage evaluator | AS-005/007 | not_covered 与 unknown 严格分离，Coverage/gap 可解释 | `pending` |
| `AS-TASK-004` | explicit freshness evaluator | AS-006 | fixture policy 下 stale；历史查询不因年龄自动 stale | `pending` |
| `AS-TASK-005` | conflict detector | AS-004 | 同 scope/time/perspective 冲突并列，不自动选值 | `pending` |
| `AS-TASK-006` | unconfirmed + deterministic read-only | AS-003/010 | candidate 不进 Canonical；重复查询语义稳定；全层 digest 不变 | `pending` |
| `AS-TASK-007` | result failure/hardening | AS-011 | artifact 写失败不发布 pass；隐私/网络/path 失败安全 | `pending` |
| `AS-TASK-008` | full A1 run + Micro regression | 全部 | A1 35/35 required 同 run passed；新 Micro current run 49/49 passed | `pending` |
| `AS-TASK-009` | Trace/Gate/Recovery | Process | result/模块回填；P0/P1=0；commit/tag/push 可恢复 | `pending` |

### 3.1 Exact Task Contract Mapping

| Task | Acceptance Scenario | Exact Upstream Test Ref | Task Card |
|---|---|---|---|
| `AS-TASK-001` | `AS-010` 基础 | `HTH-AT-006/007/008/009/013` | Cards §3 |
| `AS-TASK-002` | `AS-001/002/008/009` | `SOM-AT-008/009/018`、`BTE-AT-020/021/034`、`SIP-AT-006` | Cards §4 |
| `AS-TASK-003` | `AS-005/007` | `BTE-AT-012/013/025` | Cards §5 |
| `AS-TASK-004` | `AS-006` | `BTE-AT-026/027` | Cards §6 |
| `AS-TASK-005` | `AS-004` | `SOM-AT-021`、`BTE-AT-030` | Cards §7 |
| `AS-TASK-006` | `AS-003/010` | `BTE-AT-024`、`HTH-AT-006/007/008/009/013` | Cards §8 |
| `AS-TASK-007` | `AS-011` | `HTH-AT-002/019/020/023` | Cards §9 |
| `AS-TASK-008` | `AS-001..011` | A1 manifest 全部 24 unique refs；另做 Micro 49-ID regression | Cards §10 |
| `AS-TASK-009` | Process | 不新增业务 Test ID | Cards §11 |

重复出现的 `AS-010`/HTH refs 分别表示 store 前置能力与 adapter/read-only 最终闭合，不能把两个 Task 的定向结果拼接为统一 suite pass。

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

- [x] A1 suite materialized，Plan 升为 Approved。
- [x] `CARDS-MVP-A-AS-001` 已与 materialized protocol/paths 复核并升为 Approved Companion。
- [ ] AS-TASK-001..009 全部 completed。
- [ ] A1 35/35 required 同一次 current run passed。
- [ ] Micro 49/49 在同一新 regression run passed。
- [ ] Matrix module/result 回填。
- [ ] 独立 Audit P0=0/P1=0。
- [ ] Recovery commit/tag/remote 可解析。

当前全部未勾选；这不是未完成工作的失败，而是开发前诚实状态。
