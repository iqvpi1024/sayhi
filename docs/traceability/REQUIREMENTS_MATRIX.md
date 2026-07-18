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
| S1 | Semantic Object Model | v0.6 | `Approved` |
| S2 | Bitemporal & Evidence | v0.5 | `Approved` |
| S3 | ChangeSet & Consistency | v0.4 | `Approved` |
| S4 | Privacy & Access Policy | v0.4 | `Approved` |
| S5 | Shiling Policy | v0.4 | `Approved` |
| S6 | Semantic Test Harness | v0.5 | `Approved` |
| S7 | Storage, Index & Portability | v0.3 | `Approved` |
| S8 | MCP Contract | v0.3 | `Approved` |
| S9 | Ingestion & Migration | v0.4 | `Approved` |

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
| `FR-303` | JSON/Markdown/Source/Ledger/manifest/checksums、unknown extension semantic round-trip、hash/path rejection | S7 §5-§16；S9 §5、§13-§14 | `CP-001/002/003/004/005/006` | `src/noetide_micro/portability.py`、`src/noetide_micro/store.py` | `context-pack-ws07-f27d686-20260718.json: 6/6 passed/current` |

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
