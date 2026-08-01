# FR 到 SPEC 需求追踪矩阵

## 1. 追踪规则

本矩阵覆盖 PRD §20 的全部 32 条功能需求，只维护一张权威映射，避免“规划表、实际表、最终表”彼此漂移。强制链路为：

```text
PRD Requirement
  -> SPEC Section
  -> Acceptance Test
  -> Implementation Module
  -> Verification Result
```

每行额外声明 `Coverage Level`：

| Level | 含义 | 可以声称什么 |
|---|---|---|
| `micro_required_slice` | Micro-MVP 当前必须物化并执行的合同切片；不代表整条 FR 的长期范围 | 只可声称切片合同已定义；通过必须等待真实 run |
| `specified_not_implemented` | 语义合同已足以指导后续实现，但不属于 Micro | 可声称已规范，不可声称已实现或验证 |
| `boundary_only_deferred` | 当前只锁定不变量、旁路禁止或对象边界，完整能力明确后置 | 不可声称该 FR 已完成规范闭环 |

Micro 9 条 `micro_required_slice` 的历史运行记录保留在 `docs/testing/results/micro-task009-lf-20260717.json`，其 applicability 为 `superseded`。当前实现已由提交 `6dd4288` 的 official runner 在 `docs/testing/results/micro-ws01-6dd4288-20260718.json` 验证：49 个 required result IDs 均为 `passed`，exit code `0`。其他 FR 的 Implementation Module 仍为 `TBD`，其 Verification Result 保持 `not_executed`。`micro_required_slice` 的通过不等于该 FR 的长期范围完成。依据：PRD v0.5 §6.14、§22.1；S6 v0.5。

Test Ref 简写采用固定语法：`PREFIX-AT-001/004/009` 表示同 prefix 的离散集合，`PREFIX-AT-001-009` 表示含首尾的连续范围，“`PREFIX-AT-001` 至 `PREFIX-AT-009`”与连续范围等价。静态校验必须展开简写并确认每个 ID 存在；不得使用无法解析的自然语言代替 Test Ref。

## 2. 规范基线

| 代号 | SPEC | 版本 | 状态 |
|---|---|---|---|
| S1 | Semantic Object Model | v0.7 | `Approved` |
| S2 | Bitemporal & Evidence | v0.6 | `Approved` |
| S3 | ChangeSet & Consistency | v0.5 | `Approved` |
| S4 | Privacy & Access Policy | v0.5 | `Approved` |
| S5 | Shiling Policy | v0.5 | `Approved` |
| S6 | Semantic Test Harness | v0.6 | `Approved` |
| S7 | Storage, Index & Portability | v0.4 | `Approved` |
| S8 | MCP Contract | v0.4 | `Approved` |
| S9 | Ingestion & Migration | v0.5 | `Approved` |

批准表示语义合同经审查，不表示 suite 已物化、执行或通过。

## 3. Micro-MVP 边界

Micro 只实现一条合成链路，required 场景为 `MM-001` 至 `MM-010`：

```text
synthetic text Source
  -> one contact State candidate/ChangeSet
  -> user confirmation
  -> atomic L1 publication
  -> person_card + relationship_timeline at the safe revision
  -> historical State retained and protected semantics unchanged
  -> whole ChangeSet compensation
  -> both Core Views consistent again
```

Micro 不包含通用抽取、模糊时间解析、实体消歧、权限运行时、MCP、连接器、同步、财务、健康、决策或真实迁移。FR-105 只取 L2 传播失败与 stale 检测的最小切片。

## 4. 权威追踪

| PRD Requirement | Coverage Level | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| FR-001 | `micro_required_slice` | S1 §6.2；S4 §6.6；S9 §4-§7、§14 | `SOM-AT-026/027`、`PAP-AT-029/030`、`IMM-AT-001` 至 `IMM-AT-006`、`IMM-AT-029/030`、`MM-001` | `intake.py`、`store.py`、`testing_adapter.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-002 | `micro_required_slice` | S1 §6.2、§7.1；S2 §6.4-§6.7；S4 §6.6；S7 §6；S9 §6 | `SOM-AT-004/019/020/026/027/028`、`BTE-AT-011` 至 `BTE-AT-019`、`BTE-AT-037`、`PAP-AT-029/030`、`SIP-AT-001/003/010`、`IMM-AT-001`、`IMM-AT-007` 至 `IMM-AT-010`、`IMM-AT-029/030`、`MM-001/002` | `store.py`、`intake.py`、`candidate.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-003 | `micro_required_slice` | S1 §5-§6；S5 §4-§7 | `SOM-AT-002/013/014/025`、`SHP-AT-001/002/004/005`、`MM-002/007` | `candidate.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-004 | `micro_required_slice` | S3 §5-§9、§14 | `CS-AT-001` 至 `CS-AT-005`、`CS-AT-008/025`、`CS-AT-029` 至 `CS-AT-031`、`MM-003/004/009` | `changesets.py`、`store.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-005 | `micro_required_slice` | S3 §6.4-§6.7；S5 §6 | `CS-AT-006/007`、`SHP-AT-004/005/032`、`MM-002/003` | `candidate.py`、`testing_adapter.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-006 | `micro_required_slice` | S3 §6.4-§6.5、§8-§14 | `CS-AT-013` 至 `CS-AT-016`、`MM-005/010` | `views.py`、`changesets.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-007 | `micro_required_slice` | S3 §6.2、§6.5、§7.3、§14-§15 | `CS-AT-016` 至 `CS-AT-019`、`CS-AT-027` 至 `CS-AT-029`、`CS-AT-032`、`MM-004/008` | `changesets.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-008 | `specified_not_implemented` | S1 §3、§6.4；S2 §6.8-§7.3；S8 §6 | `SOM-AT-007/008/018/021`、`BTE-AT-020` 至 `BTE-AT-030`、`BTE-AT-038`、`MCP-AT-007/008/026` | `TBD` | `not_executed` |
| FR-009 | `micro_required_slice` | S1 §6.6；S2 §5-§10 | `SOM-AT-015/024`、`BTE-AT-001` 至 `BTE-AT-010`、`BTE-AT-033`、`MM-004/006` | `queries.py`、`store.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-010 | `specified_not_implemented` | S1 §7.3、§13；S2 §5.3、§13；S3 §13 | `SOM-AT-021`、`BTE-AT-030` 至 `BTE-AT-032`、`CS-AT-008` | `TBD` | `not_executed` |
| FR-011 | `boundary_only_deferred` | S1 §6.3、§7.2、§15；S3 §6.2 | `SOM-AT-017`；完整 merge/split 原子与回滚 suite `TBD` | `TBD` | `not_executed` |
| FR-012 | `specified_not_implemented` | S3 §6.2；S4 §5-§14；S8 §6、§12 | `CS-AT-032`、`PAP-AT-001` 至 `PAP-AT-010`、`PAP-AT-022/028/031`、`MCP-AT-001` 至 `MCP-AT-003`、`MCP-AT-027` | `TBD` | `not_executed` |
| FR-101 | `boundary_only_deferred` | S5 §5-§7、§11 | `SHP-AT-003/011-014`；完整聚合/去重/排序算法 suite `TBD` | `TBD` | `not_executed` |
| FR-102 | `specified_not_implemented` | S5 §6.2-§6.3、§8-§10 | `SHP-AT-011` 至 `SHP-AT-013`、`SHP-AT-032` | `TBD` | `not_executed` |
| FR-103 | `boundary_only_deferred` | S1 §5.1、§6.9；S5 §6.5、§11 | `SHP-AT-025`；完整 Episode/分层摘要 suite `TBD` | `TBD` | `not_executed` |
| FR-104 | `boundary_only_deferred` | S1 §5.2、§6.9；S5 §6.5 | `SOM-AT-003`、`SHP-AT-026`；完整 Commitment 生命周期/提醒 suite `TBD` | `TBD` | `not_executed` |
| FR-105 | `micro_required_slice` | S3 §8-§14；S6 §6-§14 | `CS-AT-021/022`、`MM-010` | `views.py`、`changesets.py` | `micro-ws01-6dd4288-20260718.json: passed/current` |
| FR-106 | `specified_not_implemented` | S3 §6.3、§15 | `CS-AT-020` | `TBD` | `not_executed` |
| FR-107 | `specified_not_implemented` | S3 §6.7、§7；S5 §6.2、§8 | `CS-AT-007/028`、`SHP-AT-009/010/032/034` | `TBD` | `not_executed` |
| FR-108 | `specified_not_implemented` | S7 §10-§11；S9 §6.3、§10-§11 | `SIP-AT-011`、`IMM-AT-011/013` | `TBD` | `not_executed` |
| FR-201 | `boundary_only_deferred` | S1 §5.1、§6.9；S2 §11；S5 §6.5 | `SOM-AT-010`、`BTE-AT-016` 至 `BTE-AT-018`、`SHP-AT-030`；完整生命周期 suite `TBD` | `TBD` | `not_executed` |
| FR-202 | `boundary_only_deferred` | S1 §5.2、§6.9；S5 §6.5 | `SOM-AT-003`、`SHP-AT-031`；完整闭环 suite `TBD` | `TBD` | `not_executed` |
| FR-203 | `boundary_only_deferred` | S5 §6.5、§11 | `SHP-AT-027`；完整复盘 suite `TBD` | `TBD` | `not_executed` |
| FR-204 | `boundary_only_deferred` | S1 §6.4、§11；S5 §6.5 | `SOM-AT-018`、`SHP-AT-028`；完整情景 suite `TBD` | `TBD` | `not_executed` |
| FR-205 | `boundary_only_deferred` | S2 §10.3-§10.4；S5 §6.5 | `BTE-AT-003/004/033`；跨阶段行为比较 suite `TBD` | `TBD` | `not_executed` |
| FR-206 | `boundary_only_deferred` | S5 §5、§6.5、§12、§14 | `SHP-AT-029`；行动跟进 suite `TBD` | `TBD` | `not_executed` |
| FR-301 | `boundary_only_deferred` | S7 §2、§10、§16、§20 | 加密同步、设备冲突与密钥恢复 suite `TBD`（Year 2）；当前没有功能验收测试 | `TBD` | `not_executed` |
| FR-302 | `boundary_only_deferred` | S9 §2、§4、§14、§20 | 连接器能力 suite `TBD`（Year 2）；当前只有输入旁路边界 | `TBD` | `not_executed` |
| FR-303 | `specified_not_implemented` | S7 §6-§16；S9 §6.5、§7.2、§13-§16 | `SIP-AT-001` 至 `SIP-AT-009`、`SIP-AT-012` 至 `SIP-AT-016`、`SIP-AT-020/025/026`、`IMM-AT-015` 至 `IMM-AT-021`、`IMM-AT-027/028/031` | `TBD` | `not_executed` |
| FR-304 | `boundary_only_deferred` | S4 §6、§12；S8 §6、§12 | 专业 Agent 权限模板 suite `TBD`；`PAP-AT-001/008` 与 `MCP-AT-001-003/006` 只证明通用授权及不可逆动作边界 | `TBD` | `not_executed` |
| FR-305 | `boundary_only_deferred` | S4 §2、§12-§16、§20 | 家庭授权/数字遗产工作流 suite `TBD`；当前明确非目标 | `TBD` | `not_executed` |
| FR-306 | `boundary_only_deferred` | S8 §2、§4-§9、§20 | A2A/互操作能力 suite `TBD`；`MCP-AT-025` 只证明未知协议不能旁路 | `TBD` | `not_executed` |

## 4.1 Historical Slice：MVP-A Answer Safety

本节保留 `SLICE-MVP-A-ANSWER-SAFETY-001` 的窄范围追踪。上表 Coverage Level 继续描述整条 FR 的长期状态；A1 只选择其中固定合成子集，不把 FR-008/010 的全部未来范围声明为已实现。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Exact Upstream Test Ref | Implementation Module | Verification Result |
|---|---|---|---|---|---|---|
| `FR-002` | CoverageWindow、直接 Source evidence 和 Derived exclusion | S1 §5.3/§6.2；S2 §6.5-§6.8、§11；S7 §5 | `AS-005/008/010` | `SOM-AT-009`、`BTE-AT-012/013/034`、`SIP-AT-006`、`HTH-AT-006/007/008/009/013` | `src/noetide_micro/answers.py` | `a1-ws02-85240c5-20260718.json: passed/current` |
| `FR-008` | 六态 AnswerEnvelope 与 verification scope | S1 §6.4；S2 §6.8-§7.3、§14 | `AS-001/002/003/004/005/006/007/008/009` | `SOM-AT-008/009/018/021`、`BTE-AT-012/013/020/021/024/025/026/027/030/034` | `src/noetide_micro/answers.py` | `a1-ws02-85240c5-20260718.json: passed/current` |
| `FR-010` | 同 claim/时间/perspective 冲突检测和并列呈现 | S1 §13；S2 §5.3、§13 | `AS-004` | `SOM-AT-021`、`BTE-AT-030` | `src/noetide_micro/answers.py` | `a1-ws02-85240c5-20260718.json: passed/current` |

Harness required refs `HTH-AT-002/019/020/023` 由 `AS-011` 证明，不单独归属某一 FR。exact scenario-to-upstream 映射以 `docs/testing/MVP_A_ANSWER_SAFETY_ACCEPTANCE.md` §7 为唯一权威；本节必须与其机械一致。

历史 A1 状态：`traceable=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`；`src/noetide_micro/answers.py` 已由固定合成 runner 的 35 个 required result IDs 验证。该结果不扩大 A1 或 FR 的长期范围。

## 5. 验证结果语义

- Matrix 的 `Verification Result` 使用 `not_executed|passed|failed|errored|partial`；`skipped_with_reason` 只属于 individual test，`superseded` 只属于 artifact/result applicability。当前每行的 applicability 均为 `current`；未来旧 run superseded 时保留历史 artifact，并把当前合同切片恢复为新的 `not_executed/current`，不得把 `superseded` 填进执行结果。
- 32/32 条 FR 已登记且有责任归属，不等于 32/32 已完成规范闭环。
- `micro_required_slice` 共 9 条 FR；每条只代表进入 Micro 的部分，FR-105 只覆盖传播失败切片。
- `specified_not_implemented` 共 8 条 FR。
- `boundary_only_deferred` 共 15 条 FR；其中 FR-301/302/304/305/306 的功能验收仍为显式 `TBD`。
- 在 fixture、manifest、runner 与 implementation 不存在时，Acceptance Test 表中的 ID 只是合同目录，不能产生 passed 结果。
- 后续每次真实 run 必须回填模块、命令、环境、时间、exit code、artifact digest 与单项结果；SPEC 升版会使旧结果 superseded。

## 6. Required suite authority 与下一门禁

`MICRO_MVP_ACCEPTANCE.md` §6 的 `micro_required_contract_slices` 是唯一 required upstream Test Ref 映射：10 个 MM 场景与 39 个去重后的 SOM/BTE/CS/PAP/SHP/IMM tests。Matrix 的长期 FR Test Ref 不是 Micro runner required 清单。进入 Micro 实现前只物化该映射；任何未列测试和 `boundary_only_deferred` FR 都不得借“完善架构”被隐式提升。

当前 A1 的唯一 required 映射是 `MVP_A_ANSWER_SAFETY_ACCEPTANCE.md` §7 和 `tests/answer_safety_suite_manifest.json`：11 个 `AS-*` 场景、24 个唯一 upstream refs，共 35 个 result IDs；提交 `85240c5` 的官方结果为 `passed/current`。A1 实施授权已被 `PLAN-NOETIDE-E2E-RC-001` 的 `WS-02` 取代；Matrix 长期 FR 行、旧 Micro required 集和其他 SPEC tests 均不得被隐式并入 A1。

## 4.2 Active Workstream：WS-06 Synthetic Ingestion

`WS-06` 仅证明 S9 §4-§7、§14 的四条合成 Source append 失败/重试边界，不声称完整 S9 31 项验收测试、连接器或真实迁移已完成。

| PRD Requirement | Workstream Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-001` | explicit synthetic Source append、durable stored receipt、reject/duplicate/idempotency/subject-ref failures | S9 §4-§7、§14 | `SI-001/002/003/004` | `src/noetide_micro/importer.py`、`src/noetide_micro/store.py` | `synthetic-ingestion-ws06-2d689ea-20260718.json: 4/4 passed/current` |

## 4.3 Workstream：WS-07 Context Pack Portability

`WS-07` 仅实现 owner-private synthetic Context Pack 的结构化导出与 dry-run verifier。它不声称完成分享导出、真实迁移、sealed runtime、删除或完整 S7/S9 27/31 项验收。

| PRD Requirement | Workstream Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-303` | JSON/Markdown/Source/Ledger/manifest/checksums、unknown extension semantic round-trip、hash/path rejection | S7 §5-§16；S9 §5、§13-§14 | `CP-001/002/003/004/005/006` | `src/noetide_micro/portability.py`、`src/noetide_micro/store.py` | `context-pack-ws12-7f0bb28-pyspath-20260718.json: 6/6 passed/current` |

## 4.4 Workstream：WS-04 B1 Candidate Review

此窄范围只验证候选持久化、保守预算、审查审计和 critical 优先级；不将候选升级为 Canonical 事实。

| Requirement Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|
| `FR-101`、`FR-102` 的 B1 合成子集 | S5 §5-§10 | `B1-001/002/003/004/005` | `src/noetide_micro/b1.py`、`candidate_aggregator.py`、`review_budget.py` | `b1-ws12-a603085-pyspath-20260718.json: 5/5 passed/current` |

## 4.5 Workstream：WS-05 C1 Decision/Outcome

此窄范围只验证固定合成 Decision、Outcome 与 predicted Assertion 的 ChangeSet 写入边界；它不代表完整 MVP-C 决策室或 `DQ-006` 已裁决。

| Requirement Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|
| `FR-202`、`FR-204` 的 C1 合成子集 | S1 §5.2、§6.4、§6.9；S3 §5-§9 | `C1-001/002/003/004/005/006/007` | `src/noetide_micro/c1.py`、`decision.py`、`outcome.py`、`scenario.py` | `c1-ws12-5a324f9-pyspath-20260718.json: 7/7 passed/current` |

## 4.6 Active Slice：B2 Episode 与分层摘要

`SLICE-MVP-B-EPISODE-SUMMARY-001` 只实现 FR-103 的固定合成子集。它不将摘要变成事实、证据或 ChangeSet trigger，也不代表 Episode、分层摘要或 FR-103 的长期范围完成。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-103` | fixed synthetic Episode candidate/publish、day/phase Derived summary、stale/rebuild/Derived-evidence rejection | `SPEC-B2-EPISODE-SUMMARY-001` §4-§19；S1 §5/§6；S2 §9-§14；S3 §6/§8/§14；S5 §6/§11；S6 §4-§14；S7 §7 | `B2-001/002/003/004/005/006/007/008` | `store.py`、`episodes.py`、`summaries.py`、`b2_testing_adapter.py` | `b2-a810513-20260719.json: 8/8 passed/current` |

状态：`product_decided=true`、`spec_approved=true`、`traceable=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`。B2 仅完成 FR-103 的固定合成切片，完整长期范围仍为 deferred。

## 4.7 Active Slice：B3 Commitment

`SLICE-MVP-B-COMMITMENT-001` 只实现 FR-104 的固定合成子集：受控 Commitment 生命周期和 Derived due-status。它不代表真实提醒、自动处理、日历连接器或完整 FR-104。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-104` | fixed synthetic Commitment candidate、publish、complete/cancel、compensation revert、Derived due-status | `SPEC-B3-COMMITMENT-001` §2-§8；S1 §5/§6；S2 时间语义；S3 §5-§14；S5 §6.5；S6 §4-§14；S7 §7 | `B3-001/002/003/004/005/006/007/008` | `src/noetide_micro/commitments.py`、`due_status.py`、`store.py`、`b3_testing_adapter.py` | `passed`（`docs/testing/results/b3-20260722.json` 8/8 current） |

状态：`product_decided=true`、`spec_approved=true`、`traceable=true`、`adr_accepted=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`。B3 official suite 8/8 passed/current，Gate Review P0=0/P1=0；切片 verified，下一步回到 Product Decision。

## 4.8 Active Slice：A2 current_state Core View

`SLICE-MVP-A-CURRENT-STATE-001` 只实现 FR-006/FR-008/FR-105 的固定合成 MVP-A 子集：第三个 Core View `current_state` 的构建、stale、重建等价与 Derived 不作证。它不代表通用查询、权限 runtime 或完整 FR-105 对账。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-006` | current_state 发布后更新或失效（fresh/stale/unavailable） | `SPEC-A2-CURRENT-STATE-001` §2-§8；S3 §6.4-§6.5、§8-§14 | `A2-001/003/004/005/007`（`tests/a2_suite_manifest.json`，8/8 passed） | `src/noetide_micro/current_state.py`、`src/noetide_micro/store.py`、`src/noetide_micro/a2_testing_adapter.py` | `passed` |
| `FR-008` | 复用 A1 freshness/六态语义，不重复实现；视图不得伪装 current | `SPEC-A2-CURRENT-STATE-001` §4-§5；S1 §3；S2 §6.8-§7.3 | `A2-003/004/008` | `src/noetide_micro/current_state.py`、`src/noetide_micro/a2_testing_adapter.py` | `passed` |
| `FR-105` | current_state 的 stale 检测与重建等价（MVP-A 切片；增量对账/失败队列属 B4） | `SPEC-A2-CURRENT-STATE-001` §3、§5-§7；S3 §8-§14；S6 §6-§14 | `A2-004/005/006/007` | `src/noetide_micro/current_state.py`、`src/noetide_micro/store.py`、`src/noetide_micro/a2_testing_adapter.py` | `passed` |

状态：`product_decided=true`、`spec_approved=true`、`traceable=true`、`adr_accepted=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`。official runner `a2-20260722.json` 8/8 passed/current 已绑定；Gate Review P0=0/P1=0，切片 verified，recovery tag `a2-current-state-rp-20260722`。

## 4.9 Active Slice：A3 实体合并候选与拆分回滚

`SLICE-MVP-A-ENTITY-MERGE-001` 只实现 FR-011 的固定合成 MVP-A 子集：两个合成 Person Entity 的 merge proposal、用户确认的原子发布（引用重定向 + `merged_into` + `merge_record`）与 split compensation 等价恢复。它不代表自动合并、模糊身份匹配、非 Person 合并或权限 runtime。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-011` | merge proposal → 确认 → ChangeSet 原子发布；split compensation 等价恢复 | `SPEC-A3-ENTITY-MERGE-001` §2-§9；S1 Entity 状态机/`merged_into`/SOM-AT-017；S3 merge/split operation | `A3-001..008`（`tests/a3_suite_manifest.json`，8/8 passed） | `src/noetide_micro/entity_merge.py`、`src/noetide_micro/store.py`、`src/noetide_micro/a3_testing_adapter.py` | `passed` |

状态：`product_decided=true`、`spec_approved=true`、`traceable=true`、`adr_accepted=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`。official runner `a3-20260724.json` 8/8 passed/current 已绑定；Gate Review P0=0/P1=0，切片 verified，recovery tag `a3-entity-merge-rp-20260724`。

## 4.10 Active Slice：A4 查询层权限与舱室强制执行

`SLICE-MVP-A-ACCESS-POLICY-001` 只实现 FR-012 的固定合成 MVP-A 子集：单用户本地调用者在身份+目的+舱室+字段+时间约束下的查询层判决（`allow/allow_with_redaction/deny`），多策略最严格交集，判决零写入。它不代表多用户、Grant 管理 UI、外部 Agent runtime 或完整权限平台。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-012` | 查询层判决强制执行与 fail closed；字段过滤；拒绝非泄露 | `SPEC-A4-ACCESS-POLICY-001` §2-§8；S4 §6.2-§6.4、§9、§12-§14；S1 Policy Subject 字段 | `A4-001..008`（`tests/a4_suite_manifest.json`，8/8 passed/current） | `src/noetide_micro/access_policy.py`、`src/noetide_micro/a4_testing_adapter.py`、`src/noetide_micro/store.py`（只读辅助） | `passed`（`docs/testing/results/a4-20260724.json`） |

状态：`product_decided=true`、`spec_approved=true`、`traceable=true`、`adr_accepted=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`。official runner `a4-20260724.json` 同一次 run 8/8 passed/current；Gate Review `A4_ACCESS_POLICY_GATE_REVIEW_2026-07-24.md` 结论 P0=0/P1=0；recovery tag `a4-access-policy-rp-20260724` 已推送。

## 4.11 Active Slice：A5 自然语言审查与最小可用应用壳

`SLICE-MVP-A-APP-SHELL-001` 只实现 FR-001/005/006/007 的固定合成 MVP-A 可用性扩展：单一本地入口完成记录、自然语言审查、影响预览、确认发布、Core View 读取、回执、历史与撤销的完整旅程。它不代表 Web/桌面 UI、云账户、多租户、通用 NLP 或完整应用。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-001` | 壳 `record` 命令：Source append + receipt | `SPEC-A5-APP-SHELL-001` §2-§8；S3 导入语义；S7 数据目录 | `A5-001` | `intake.py`（经 `cli.py` record / `a5_testing_adapter.py`） | `passed`（`a5-20260725.json`） |
| `FR-005` | 自然语言审查与影响预览（Derived 呈现） | `SPEC-A5-APP-SHELL-001` §2-§8；S5 §6.1 Candidate Envelope | `A5-002`、`A5-003`、`A5-008` | `app_shell.py` | `passed`（`a5-20260725.json`） |
| `FR-006` | 发布后 Core View 更新（person_card/relationship_timeline fresh） | `SPEC-A5-APP-SHELL-001` §2-§8；S3；A2 视图语义 | `A5-005`、`A5-007` | `views.py`（CoreViewReader/Projector，经 adapter） | `passed`（`a5-20260725.json`） |
| `FR-007` | ChangeSet 回执、历史与撤销 | `SPEC-A5-APP-SHELL-001` §2-§8；S3 ChangeSet 语义 | `A5-004`、`A5-006`、`A5-007` | `changesets.py`（publish/revert/receipt，经 adapter/`cli.py`） | `passed`（`a5-20260725.json`） |

状态：`product_decided=true`、`spec_approved=true`、`traceable=true`、`adr_accepted=true`、`suite_defined=true`、`suite_materialized=true`、`suite_executed=true`、`suite_passed=true`。official runner `docs/testing/results/a5-20260725.json` 同一次 run 8/8 passed/current，manifest 已绑定 current result；Gate Review `A5_APP_SHELL_GATE_REVIEW_2026-07-25.md` 结论 P0=0/P1=0，切片 `verified`。
## 4.12 Active Slice：A6 MVP-A 硬化与本地 Alpha

`SLICE-MVP-A-HARDENING-001` 不引入新产品能力，把 FR-001..012 的既有证明组装为 MVP-A 发布级验收：21 个场景在同一个版本化 Reference Profile `a6_mvp_a_reference_v1` 上顺序执行、共享同一系统状态，并补齐错误恢复壳层表面与本地 Alpha 可解释性。FR-003 生成侧（Entity/Assertion 候选生成）为显式记录的已知限制，见 `SPEC-A6-HARDENING-001` §1.1。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-001`/`FR-002` | Source append + 独立 receipt；Canonical 不变 | `SPEC-A6-HARDENING-001` §3/§7；S3 导入语义 | `A6-001` | `intake` + `a6_journey.record_source` | passed（`a6-20260725.json`，official 21/21） |
| `FR-003` | 候选不成事实（生成侧为已知限制，§1.1） | `SPEC-A6-HARDENING-001` §1.1/§7；S5 Candidate Envelope | `A6-002` | `candidate` + `app_shell.render_review` + `a6_journey` | passed（`a6-20260725.json`，official 21/21） |
| `FR-004` | 规范写入全部经 ChangeSet；Source append 独立 | `SPEC-A6-HARDENING-001` §7；S3 ChangeSet 语义 | `A6-003` | `store` ledger audit + `a6_journey.write_path_audit` | passed（`a6-20260725.json`，official 21/21） |
| `FR-005` | 自然语言审查 + 影响预览与发布一致 | `SPEC-A6-HARDENING-001` §7；`SPEC-A5-APP-SHELL-001` | `A6-004` | `candidate` + `changesets` + `app_shell.render_impact_preview` + `a6_journey` | passed（`a6-20260725.json`，official 21/21） |
| `FR-006` | 发布后三个 Core View 更新或显式失效 | `SPEC-A6-HARDENING-001` §2/§7；S3；A2 视图语义 | `A6-005` | `views.CoreViewReader` + `current_state` + `a6_journey.read_core_views` | passed（`a6-20260725.json`，official 21/21） |
| `FR-007` | 回执、历史、撤销补偿完整可审计 | `SPEC-A6-HARDENING-001` §6/§7；S3 ChangeSet 语义 | `A6-006` | `changesets.revert` + `a6_journey.revert_and_audit` | passed（`a6-20260725.json`，official 21/21） |
| `FR-008` | 六态回答严格分离 | `SPEC-A6-HARDENING-001` §7；A1 回答安全语义 | `A6-007` | `answers.AnswerEvaluator` + `a6_journey.run_answer_battery` | passed（`a6-20260725.json`，official 21/21） |
| `FR-009` | 双时态历史查询区分 valid/recorded | `SPEC-A6-HARDENING-001` §4/§7；S2 双时态语义 | `A6-008` | `store` 双时态字段 + `a6_journey.bitemporal_probe` | passed（`a6-20260725.json`，official 21/21） |
| `FR-010` | 冲突检测与并列呈现，不自动裁决 | `SPEC-A6-HARDENING-001` §7；S1/S2 冲突语义 | `A6-009` | `answers` disputed 语义 + `a6_journey.conflict_probe` | passed（`a6-20260725.json`，official 21/21） |
| `FR-011` | 实体合并候选与拆分回滚 | `SPEC-A6-HARDENING-001` §7；`SPEC-A3-ENTITY-MERGE-001` | `A6-010` | `entity_merge` + `a6_journey.merge_split_cycle` | passed（`a6-20260725.json`，official 21/21） |
| `FR-012` | 权限与舱室在查询层 fail closed | `SPEC-A6-HARDENING-001` §4/§7；`SPEC-A4-ACCESS-POLICY-001` | `A6-011` | `access_policy` + `a6_journey.restricted_query_probe` | passed（`a6-20260725.json`，official 21/21） |
| 横切（PRD §10/§21） | trust/closeness/人格判断与历史不自动修改；stale base 拒绝；L2 fallback | `SPEC-A6-HARDENING-001` §5/§7；S3 | `A6-012` | `a6_journey.cross_cutting_check` | passed（`a6-20260725.json`，official 21/21） |
| PRD §21.2/§24.2 硬化 | 错误恢复壳层表面五项固定预期 | `SPEC-A6-HARDENING-001` §6/§7 | `A6-013..017` | `start.py` + `store.py` + `changesets`/`views` 失败路径 + `a6_testing_adapter` 沙箱 | passed（`a6-20260725.json`，official 21/21） |
| PRD §21.2/§21.4 可解释性 | 数据路径/路径分离/备份/导出/卸载语义 | `SPEC-A6-HARDENING-001` §7；S7 可移植语义 | `A6-018..020` | `alpha_explainability` + `portability` + `a6_testing_adapter` | passed（`a6-20260725.json`，official 21/21） |
| PRD §21.2 SLO | 固定 SLO 检查实际结果绑定 profile 记录，不外推 | `SPEC-A6-HARDENING-001` §2/§7；S6 IQ-014/HTH-INV-009 | `A6-021` | `a6_journey.SloCollector` + `slo_report` | passed（`a6-20260725.json`，official 21/21） |

状态：`product_decided=true`、`spec_approved=true`（`A6-CONTRACT-REVIEW-001`，2026-07-25）、`traceable=true`、`adr_accepted=true`（`ADR-0010`，2026-07-25）、`suite_defined=true`、`suite_materialized=true`（2026-07-25）、`suite_executed=true`、`suite_passed=true`（2026-07-25，official runner 同一次 run 21/21 passed/current，immutable result `docs/testing/results/a6-20260725.json`，manifest 已绑定）、`gate_review_passed=true`（`A6_HARDENING_GATE_REVIEW_2026-07-25.md`，P0=0/P1=0）、`verified=true`（recovery tag `a6-hardening-rp-20260725`）。

## 4.13 Active Slice：B4 Reconciliation 与 Semantic Diff

`SLICE-MVP-B-RECONCILIATION-001` 在一个固定合成 profile 上验证写后校验与日常增量对账、周期深度对账、只读 Semantic Diff。对账发现只隔离 + 报告，不静默修复；Semantic Diff 为查询时派生，不持久化、不作证据。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-105` | 写后校验 + 干净增量对账（无发现） | `SPEC-B4-RECONCILIATION-001` §2.1/§7；S3 写后校验 | `B4-001` | `noetide_micro.reconciliation`（ADR-0011） | `passed`（b4-20260725.json） |
| `FR-105` | 失败队列检出（隔离+报告，不修复） | `SPEC-B4-RECONCILIATION-001` §2.1/§7；S3 | `B4-002` | `noetide_micro.reconciliation` | `passed`（b4-20260725.json） |
| `FR-105` | stale 视图检出 | `SPEC-B4-RECONCILIATION-001` §2.1/§7；S3 stale 语义 | `B4-003` | `noetide_micro.reconciliation` | `passed`（b4-20260725.json） |
| `FR-105` | 孤儿引用检出 | `SPEC-B4-RECONCILIATION-001` §2.1/§7 | `B4-004` | `noetide_micro.reconciliation` | `passed`（b4-20260725.json） |
| `FR-105` | 未消费 ChangeSet 检出 | `SPEC-B4-RECONCILIATION-001` §2.1/§7；S3 | `B4-005` | `noetide_micro.reconciliation` | `passed`（b4-20260725.json） |
| `FR-105` | 深度对账三分区 match | `SPEC-B4-RECONCILIATION-001` §2.1/§7；S7 投影重建 | `B4-006` | `noetide_micro.reconciliation` | `passed`（b4-20260725.json） |
| `FR-105` | 深度对账 mismatch 报告，不静默改写 | `SPEC-B4-RECONCILIATION-001` §6/§7；S7 | `B4-007` | `noetide_micro.reconciliation` | `passed`（b4-20260725.json） |
| `FR-106` | Semantic Diff：当前状态/联系状态字段级差异 | `SPEC-B4-RECONCILIATION-001` §2.2/§7；S2 revision 语义 | `B4-008` | `noetide_micro.semantic_diff` | `passed`（b4-20260725.json） |
| `FR-106` | Semantic Diff：Hypothesis 变化 + no_change；diff 不持久化不作证据 | `SPEC-B4-RECONCILIATION-001` §2.2/§5/§7；S1/S2 Derived 边界 | `B4-009` | `noetide_micro.semantic_diff` | `passed`（b4-20260725.json） |
| 横切（PRD §10.5/§25.3） | trust/closeness/人格/历史不变；profile 外 fail closed | `SPEC-B4-RECONCILIATION-001` §5/§7 | `B4-010` | `noetide_micro.reconciliation` / `noetide_micro.semantic_diff` | `passed`（b4-20260725.json） |

状态：`product_decided=true`（`DEC-MVP-B-RECONCILIATION-001`，2026-07-25）、`spec_approved=true`（`B4-CONTRACT-REVIEW-001`，2026-07-25）、`traceable=true`、`adr_accepted=true`（`ADR-0011`，2026-07-25）、`suite_defined=true`、`suite_materialized=true`（2026-07-25）、`suite_executed=true`、`suite_passed=true`（2026-07-25，official runner 同一次 run 10/10 passed/current，immutable result `docs/testing/results/b4-20260725.json`，manifest 已绑定）、`gate_review_passed=true`（`B4_RECONCILIATION_GATE_REVIEW_2026-07-25.md`，P0=0/P1=0）、`verified=true`（recovery tag `b4-reconciliation-rp-20260725`）。

## 4.14 Active Slice：B5 Multilingual 原文与翻译对照

`SLICE-MVP-B-MULTILINGUAL-001` 在一个固定合成 profile 上验证原文/翻译分离存储、对照读取与证据完整性。翻译不得覆盖原文，Evidence Ref 永远解析到原文，对照视图为 Derived。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `FR-108` | 双语 Source 分离存储（原文 Vault + 独立翻译记录） | `SPEC-B5-MULTILINGUAL-001` §2.1/§7；S7 Source Vault | `B5-001` | `noetide_micro.bilingual`（ADR-0012） | `passed`（b5-20260725.json） |
| `FR-108` | 原文读取与 Evidence Ref 解析到原文 | `SPEC-B5-MULTILINGUAL-001` §4/§7；S2 Evidence | `B5-002` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |
| `FR-108` | 对照视图 paired 并排读取 | `SPEC-B5-MULTILINGUAL-001` §2.2/§7 | `B5-003` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |
| `FR-108` | 以翻译覆盖原文被拒绝 | `SPEC-B5-MULTILINGUAL-001` §5/§7；PRD §21.5 | `B5-004` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |
| `FR-108` | 缺失翻译显式降级 | `SPEC-B5-MULTILINGUAL-001` §2.2/§5/§7 | `B5-005` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |
| `FR-108` | 翻译修订历史保留 | `SPEC-B5-MULTILINGUAL-001` §3/§7；S2 revision 语义 | `B5-006` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |
| `FR-108` | orphan 翻译记录报告不静默配对 | `SPEC-B5-MULTILINGUAL-001` §6/§7 | `B5-007` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |
| `FR-108` | 横切：原文/hash 不变、翻译不作证据、profile 外 fail closed | `SPEC-B5-MULTILINGUAL-001` §5/§7 | `B5-008` | `noetide_micro.bilingual` | `passed`（b5-20260725.json） |

状态：`product_decided=true`（`DEC-MVP-B-MULTILINGUAL-001`，2026-07-25）、`spec_approved=true`（`B5-CONTRACT-REVIEW-001`，2026-07-25）、`traceable=true`、`adr_accepted=true`（`ADR-0012`，2026-07-25）、`suite_defined=true`、`suite_materialized=true`（2026-07-25）、`suite_executed=true`、`suite_passed=true`（2026-07-25，official runner 同一次 run 8/8 passed/current，immutable result `docs/testing/results/b5-20260725.json`，manifest 已绑定）、`gate_review_passed=true`（`B5_MULTILINGUAL_GATE_REVIEW_2026-07-25.md`，P0=0/P1=0）、`verified=true`（recovery tag `b5-multilingual-rp-20260725`）。

## 4.15 Active Slice：B6 Shadow Migration 与压测消歧传播

`SLICE-MVP-B-SHADOW-MIGRATION-001` 在一个固定合成复杂 profile 上验证影子迁移（原始库零改动、失败无部分写入、迁移后深度对账）与压测消歧传播（确定性计数、未确认不自动合并、历史完整保留）。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `PRD-§24.3` | 影子迁移 + 深度对账 match | `SPEC-B6-SHADOW-MIGRATION-001` §2.1/§7；B4 对账语义 | `B6-001` | `noetide_micro.shadow_migration`（ADR-0013） | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 变换正确性与确定性 transform_log | `SPEC-B6-SHADOW-MIGRATION-001` §2.1/§7 | `B6-002` | `noetide_micro.shadow_migration` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 迁移故障：显式 failed、零部分写入、影子可丢弃 | `SPEC-B6-SHADOW-MIGRATION-001` §3/§6/§7 | `B6-003` | `noetide_micro.shadow_migration` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 影子偏差 mismatch 报告不静默修复 | `SPEC-B6-SHADOW-MIGRATION-001` §6/§7 | `B6-004` | `noetide_micro.shadow_migration` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 消歧候选确定性计数、无自动合并 | `SPEC-B6-SHADOW-MIGRATION-001` §2.2/§5/§7 | `B6-005` | `noetide_micro.disambiguation` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 已确认合并传播计数确定、历史保留 | `SPEC-B6-SHADOW-MIGRATION-001` §2.3/§7；S3 | `B6-006` | `noetide_micro.disambiguation` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 批量处理计数可复现 | `SPEC-B6-SHADOW-MIGRATION-001` §5/§7 | `B6-007` | `noetide_micro.disambiguation` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | bitemporal 历史随迁移完整 | `SPEC-B6-SHADOW-MIGRATION-001` §4/§7；S2 | `B6-008` | `noetide_micro.shadow_migration` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 影子/报告不作证据 | `SPEC-B6-SHADOW-MIGRATION-001` §2/§5/§7 | `B6-009` | `noetide_micro.shadow_migration / noetide_micro.disambiguation` | `passed`（b6-20260725.json） |
| `PRD-§24.3` | 横切：原始库不变、历史完整、fail closed | `SPEC-B6-SHADOW-MIGRATION-001` §5/§7 | `B6-010` | `noetide_micro.shadow_migration / noetide_micro.disambiguation` | `passed`（b6-20260725.json） |

状态：`product_decided=true`（`DEC-MVP-B-SHADOW-MIGRATION-001`，2026-07-25）、`spec_approved=true`（`B6-CONTRACT-REVIEW-001`，2026-07-25）、`traceable=true`、`adr_accepted=true`（`ADR-0013`，2026-07-25）、`suite_defined=true`、`suite_materialized=true`（2026-07-25）、`suite_executed=true`、`suite_passed=true`（2026-07-25，official runner 同一次 run 10/10 passed/current，immutable result `docs/testing/results/b6-20260725.json`，manifest 已绑定）、`gate_review_passed=true`（`B6_SHADOW_MIGRATION_GATE_REVIEW_2026-07-25.md`，P0=0/P1=0）、`verified=true`（recovery tag `b6-shadow-migration-rp-20260725`）。

## 4.16 Active Slice：C2 Hypothesis Lifecycle

`SLICE-MVP-C-HYPOTHESIS-001` 在一个固定合成 profile 上验证 Hypothesis 生命周期：用户确认创建（active + valid_scope + 支持证据）、用户确认的证据/反例追加、用户确认的状态迁移（active -> challenged -> weakened，含纠正性回退与 retired/restore）、反例不自动改状态、历史 revision 永不删除、tentative 呈现、永不升级为 Fact。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `PRD-§20.2 FR-201` | 用户确认创建 Hypothesis（scope + 支持证据） | `SPEC-C2-HYPOTHESIS-001` §2.1/§7 | `C2-001` | `noetide_micro.hypotheses`（ADR-0014） | `passed`（c2-20260726.json） |
| `PRD-§20.2 FR-201` | 支持证据追加、状态保持、revision 递增 | `SPEC-C2-HYPOTHESIS-001` §2.1/§2.2/§7 | `C2-002` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§26 Case G` | 反例进入 evidence_against 不自动改状态 | `SPEC-C2-HYPOTHESIS-001` §2.2/§3/§7；S2 | `C2-003` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§26 Case G` | 确认迁移 active->challenged，历史保留，tentative | `SPEC-C2-HYPOTHESIS-001` §3/§7；S3 | `C2-004` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§26 Case G` | 确认迁移 challenged->weakened，反例累计 | `SPEC-C2-HYPOTHESIS-001` §3/§7 | `C2-005` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§26 Case G` | 呈现 tentative、is_fact=false、事实证据集隔离 | `SPEC-C2-HYPOTHESIS-001` §2.3/§5/§7 | `C2-006` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§5.2-7` | upgrade_to_fact fail closed | `SPEC-C2-HYPOTHESIS-001` §5/§6/§7；S1 | `C2-007` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§5.2` | 纠正性回退、retire、restore 各产生新 revision | `SPEC-C2-HYPOTHESIS-001` §3/§7；S3 | `C2-008` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§5.2-7` | 未确认操作 rejected 无写入、auto_transitions=0 | `SPEC-C2-HYPOTHESIS-001` §6/§7；S3 | `C2-009` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |
| `PRD-§23` | 横切：revision 链完整、证据真实、fail closed、无关层不变 | `SPEC-C2-HYPOTHESIS-001` §4/§5/§7；S2 | `C2-010` | `noetide_micro.hypotheses` | `passed`（c2-20260726.json） |

状态：`product_decided=true`（`DEC-MVP-C-HYPOTHESIS-001`，2026-07-26）、`spec_approved=true`（`C2-CONTRACT-REVIEW-001`，2026-07-26）、`traceable=true`、`adr_accepted=true`（`ADR-0014`，2026-07-26）、`suite_defined=true`、`suite_materialized=true`（2026-07-26）、`suite_executed=true`、`suite_passed=true`（2026-07-26，official runner 同一次 run 10/10 passed/current，immutable result `docs/testing/results/c2-20260726.json`，manifest 已绑定）、`gate_review_passed=true`（`C2_HYPOTHESIS_GATE_REVIEW_2026-07-26.md`，P0=0/P1=0）、`verified=true`（recovery tag `c2-hypothesis-lifecycle-rp-20260726`）。
## 4.17 Active Slice：C3 Review & Calibration

`SLICE-MVP-C-REVIEW-001` 在一个固定合成 profile 上验证两类 Derived 能力：周期性复盘报告（周/月/年度确定性计数、fresh/stale、历史版本保留、删除重建等价）与跨阶段比较（同指标集 signed delta、不合法比较 fail closed）。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `PRD-§20.3 FR-203` | 周复盘确定性计数、fresh、view_revision=1 | `SPEC-C3-REVIEW-001` §2.1/§7 | `C3-001` | `noetide_micro.reviews`（ADR-0015） | `passed`（c3-20260726.json） |
| `PRD-§20.3 FR-203` | 月/年度复盘、半开窗口边界归属 | `SPEC-C3-REVIEW-001` §2.1/§2.3/§7 | `C3-002` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§16.2` | Canonical 变化后窗口报告 stale、不改写历史 | `SPEC-C3-REVIEW-001` §3/§5/§7；S2 | `C3-003` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§16.2` | 重建成新版本、旧版本保留不覆盖 | `SPEC-C3-REVIEW-001` §3/§7；S2 | `C3-004` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§12 L3` | 删除后重建等价、Canonical digest 不变 | `SPEC-C3-REVIEW-001` §3/§5/§7 | `C3-005` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§20.3 FR-205` | 同指标集两窗口 signed delta 精确 | `SPEC-C3-REVIEW-001` §2.2/§7 | `C3-006` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§20.3 FR-205` | 指标集不一致 fail closed 无写入 | `SPEC-C3-REVIEW-001` §2.2/§6/§7 | `C3-007` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§20.3 FR-205` | 窗口不合法 fail closed 无写入 | `SPEC-C3-REVIEW-001` §2.3/§6/§7 | `C3-008` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§12 L3` | 报告/比较不进事实证据集、Canonical 无反向引用 | `SPEC-C3-REVIEW-001` §2/§5/§7；S1 | `C3-009` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |
| `PRD-§23` | 横切：版本链完整、digest 不变、profile 外 fail closed | `SPEC-C3-REVIEW-001` §4/§5/§7；S2 | `C3-010` | `noetide_micro.reviews` | `passed`（c3-20260726.json） |

状态：`product_decided=true`（`DEC-MVP-C-REVIEW-001`，2026-07-26）、`spec_approved=true`（`C3-CONTRACT-REVIEW-001`，2026-07-26）、`traceable=true`、`adr_accepted=true`（`ADR-0015`，2026-07-26）、`suite_defined=true`、`suite_materialized=true`（2026-07-26）、`suite_executed=true`、`suite_passed=true`（2026-07-26，official runner 同一次 run 10/10 passed/current，immutable result `docs/testing/results/c3-20260726.json`，manifest 已绑定）、`gate_review_passed=true`（`C3_REVIEW_GATE_REVIEW_2026-07-26.md`，P0=0/P1=0）、`verified=true`（recovery tag `c3-review-calibration-rp-20260726`）。
## 4.18 Active Slice：C4 Scenario & Action

`SLICE-MVP-C-SCENARIO-001` 在一个固定合成 profile 上验证情景推演与行动跟进：用户确认创建 predicted 情景三元组、确定性可执行性评估、用户确认选择、跟进创建/完成、Derived missed 视图；情景永不成为事实、永不生成专业建议。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `PRD-§20.3 FR-204` | 确认创建三元组、predicted、确定性 feasibility | `SPEC-C4-SCENARIO-001` §2.1/§7 | `C4-001` | `noetide_micro.scenarios`（ADR-0016） | `passed`（c4-20260726.json） |
| `PRD-§5.2` | 未确认创建 rejected 零写入 | `SPEC-C4-SCENARIO-001` §6/§7；S3 | `C4-002` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§8.1` | upgrade-to-observed rejected、predicted 恒定 | `SPEC-C4-SCENARIO-001` §3/§5/§7；S1 | `C4-003` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§20.3 FR-204` | 确认选择、Decision/Outcome 不变 | `SPEC-C4-SCENARIO-001` §2.2/§5/§7 | `C4-004` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§20.3 FR-206` | 确认创建跟进、open、引用正确 | `SPEC-C4-SCENARIO-001` §2.3/§7 | `C4-005` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§20.3 FR-206` | 确认完成、新 revision、历史保留 | `SPEC-C4-SCENARIO-001` §3/§7；S2 | `C4-006` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§20.3 FR-206` | missed Derived 视图精确、无 Canonical 写入 | `SPEC-C4-SCENARIO-001` §2.4/§5/§7 | `C4-007` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§20.3 FR-206` | feasibility 确定性纯函数 | `SPEC-C4-SCENARIO-001` §2.1/§5/§7 | `C4-008` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§8.1` | 呈现隔离、非专业建议、不进事实证据集 | `SPEC-C4-SCENARIO-001` §2.5/§5/§7；S1 | `C4-009` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |
| `PRD-§23` | 横切：链完整、fail closed、无关层不变 | `SPEC-C4-SCENARIO-001` §4/§5/§7；S2 | `C4-010` | `noetide_micro.scenarios` | `passed`（c4-20260726.json） |

状态：`product_decided=true`（`DEC-MVP-C-SCENARIO-001`，2026-07-26）、`spec_approved=true`（`C4-CONTRACT-REVIEW-001`，2026-07-26）、`traceable=true`、`adr_accepted=true`（`ADR-0016`，2026-07-26）、`suite_defined=true`、`suite_materialized=true`（2026-07-26）、`suite_executed=true`、`suite_passed=true`（2026-07-26，official runner 同一次 run 10/10 passed/current，immutable result `docs/testing/results/c4-20260726.json`，manifest 已绑定）、`gate_review_passed=true`（`C4_SCENARIO_GATE_REVIEW_2026-07-26.md`，P0=0/P1=0）、`verified=true`（recovery tag `c4-scenario-action-rp-20260726`）。
## 4.19 Active Slice：C5 Context Pack & Encrypted Backup

`SLICE-MVP-C-PACK-001` 在一个固定合成 profile 上验证：Markdown+JSON Pack（确定性渲染 + fail-closed 校验）、本地加密备份（密文非明文、字节一致恢复、错误密钥拒绝）、删除与恢复诚实性（八成分回执）。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `PRD-§24.x` | Markdown+JSON Pack 导出、manifest 含 markdown 条目 | `SPEC-C5-PACK-001` §2.1/§7 | `C5-001` | `noetide_micro.pack_backup`（ADR-0017） | `passed`（c5-20260726.json） |
| `PRD-§24.x` | 渲染确定性、独立可读 | `SPEC-C5-PACK-001` §2.1/§7 | `C5-002` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§20.4 FR-303` | 校验 validated、篡改 rejected | `SPEC-C5-PACK-001` §2.1/§6/§7；S7 | `C5-003` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§20.4 FR-303` | 未知/缺失文件 fail closed | `SPEC-C5-PACK-001` §6/§7；S7 | `C5-004` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§24.x` | 加密备份密文非明文、receipt、read-only | `SPEC-C5-PACK-001` §2.2/§5/§7 | `C5-005` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§24.x` | 正确密钥字节一致恢复、源库不变 | `SPEC-C5-PACK-001` §2.3/§3/§7 | `C5-006` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§24.x` | 错误密钥 fail closed 零写入 | `SPEC-C5-PACK-001` §6/§7 | `C5-007` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§534` | 八成分回执、pending_expiry/out_of_control | `SPEC-C5-PACK-001` §2.4/§7；S1 | `C5-008` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§534` | partial failure 显式报告 | `SPEC-C5-PACK-001` §2.4/§6/§7 | `C5-009` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |
| `PRD-§23` | 横切：digest 不变、不覆盖源库、fail closed | `SPEC-C5-PACK-001` §4/§5/§7 | `C5-010` | `noetide_micro.pack_backup` | `passed`（c5-20260726.json） |

状态：`product_decided=true`（`DEC-MVP-C-PACK-001`，2026-07-26）、`spec_approved=true`（`C5-CONTRACT-REVIEW-001`，2026-07-26）、`traceable=true`、`adr_accepted=true`（`ADR-0017`，2026-07-26）、`suite_defined=true`、`suite_materialized=true`（2026-07-26）、`suite_executed=true`、`suite_passed=true`（2026-07-26，official runner 同一次 run 10/10 passed/current，immutable result `docs/testing/results/c5-20260726.json`，manifest 已绑定）、`gate_review_passed=true`（`C5_PACK_GATE_REVIEW_2026-07-26.md`，P0=0/P1=0）、`verified=true`（recovery tag `c5-context-pack-backup-rp-20260726`）。
## 4.20 Active Slice：C6 MVP Release Gate

`SLICE-MVP-C-RELEASE-001` 以可执行审计证明发布就绪：全量回归零 skip、安全审计（隐私/依赖/网络隔离/manifest 绑定）、数据恢复演练、公开 Beta 门禁；首年非目标保持关闭。

| PRD Requirement | Slice Scope | SPEC Section | Acceptance Scenario | Implementation Module | Verification Result |
|---|---|---|---|---|---|
| `路线图 C6` | 全部 suite validator 通过 | `SPEC-C6-RELEASE-001` §2.2 | `C6-001` | `tests.runner.run_c6_release_audit`（ADR-0018） | `passed`（c6-20260726.json） |
| `路线图 C6` | 全量回归零 skip | `SPEC-C6-RELEASE-001` §2.2/§4 | `C6-002` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |
| `PRD-§23` | 隐私边界扫描 | `SPEC-C6-RELEASE-001` §2.2/§4 | `C6-003` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |
| `PRD-§23` | 依赖审计 stdlib-only | `SPEC-C6-RELEASE-001` §2.2/§4 | `C6-004` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |
| `PRD-§23` | 网络隔离审计 | `SPEC-C6-RELEASE-001` §2.2/§4 | `C6-005` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |
| `PRD-§23` | manifest 绑定审计 | `SPEC-C6-RELEASE-001` §2.2/§4 | `C6-006` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |
| `路线图 C6` | 数据恢复演练字节一致 | `SPEC-C6-RELEASE-001` §2.2/§4；S7 | `C6-007` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |
| `路线图 C6` | Beta 门禁文档核验 | `SPEC-C6-RELEASE-001` §2.2/§3 | `C6-008` | `tests.runner.run_c6_release_audit` | `passed`（c6-20260726.json） |

状态：`product_decided=true`（`DEC-MVP-C-RELEASE-001`，2026-07-26）、`spec_approved=true`（`C6-CONTRACT-REVIEW-001`，2026-07-26）、`traceable=true`、`adr_accepted=true`（`ADR-0018`，2026-07-26）、`suite_defined=true`、`suite_materialized=true`（2026-07-26）、`suite_executed=true`、`suite_passed=true`（2026-07-26，审计 runner 同一次 run 8/8 passed，immutable result `docs/testing/results/c6-20260726.json`，manifest 已绑定；run1 失败留痕）、`gate_review_passed=true`（`C6_RELEASE_GATE_REVIEW_2026-07-26.md`，P0=0/P1=0）、`verified=true`（recovery tag `c6-mvp-release-gate-rp-20260726`）。
