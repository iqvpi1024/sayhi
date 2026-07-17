# 识海交付流程

## 1. 目的

本文是识海 Noetide 的长期交付流程基线。它解决三个问题：

1. 新任务不依赖聊天上下文即可恢复当前状态。
2. 产品、语义、架构、测试、实现和验证各自有唯一职责，不能互相越权。
3. 每个可交付切片都有明确门禁、失败回退和 Git 恢复点。

流程按“切片”运行，不表示整个项目一次性从左走到右。`SLICE-MICRO-RELATIONSHIP-001` 已完成并发布恢复点；当前切片是 `SLICE-MVP-A-ANSWER-SAFETY-001`，只覆盖合成 AnswerEnvelope 六态与最小冲突呈现。

依据：PRD v0.5 §6、§10-§12、§20-§22、§24-§27；S6 v0.5；`DEC-PRD-V05-001`。

## 2. 权威链路

```text
PRD
  -> Product Decisions
  -> SPEC
  -> Traceability
  -> ADR
  -> Executable Tests
  -> Implementation Plan / TODO
  -> Development
  -> Verification
  -> Review
  -> Release / Recovery Point
```

`TODO` 只是实施计划中的施工清单，不能代替产品裁决、SPEC、ADR、测试 oracle 或 Verification Result。

当 SPEC、测试或实现发现会改变用户可见行为的产品歧义时，必须回到 Product Decision；需要改变当前 PRD 时发布新版本，再对全部下游做 compatibility/applicability 复核。不得把 Decision 永久堆在旧 PRD 旁边形成语义补丁链。

## 3. 每次任务恢复顺序

必须依次读取：

1. `docs/product/CURRENT_PRODUCT_BASELINE.md`
2. 读取其中 `current_prd_path` 指向的完整 PRD
3. `docs/PROJECT_STATE.md`
4. `docs/decisions/OPEN_QUESTIONS.md`
5. `docs/process/README.md`
6. `docs/process/CURRENT_HANDOFF.md`（存在时）
7. 当前切片适用的 Approved SPEC
8. `docs/traceability/REQUIREMENTS_MATRIX.md`
9. 当前 suite 合同、manifest 和最近 Verification Result
10. 当前适用 ADR、Implementation Plan 和最近 Gate Review

没有对应文件时，必须明确写 `absent` 或 `not_executed`，不得用记忆补齐。

## 4. 每次任务结束要求

结束前必须：

1. 更新 `docs/PROJECT_STATE.md` 的当前阶段、已完成内容、验证结果、未决问题、风险和下一步唯一建议动作。
2. 运行与变更范围相称的检查，并记录真实命令、环境、exit code 和结果。
3. 校验当前 PRD hash 与产品基线索引一致，检查所有历史 PRD 未被修改，并检查是否引入真实个人数据。
4. 对上游语义变化执行下游失效分析；需要时标记旧 ADR、suite、plan 或 result 为 `superseded`。
5. 只提交本任务范围文件；不得混入其他工作树或用户未跟踪资料。
6. 达到恢复点条件时创建 commit、annotated tag 并推送；未达到时不得伪造 release/recovery 状态。

## 5. 切片阶段状态

以下机器可读枚举是流程状态的权威集合：

```yaml
delivery_phase_values: [product_defined, product_decided, spec_approved, traceable, architecture_decided, suite_materialized, implementation_planned, implementing, verified, review_passed, recovery_point_published]
```

阶段状态属于某个切片，不属于整个产品。一个切片处于 `implementing` 时，其他切片仍可处于 `product_defined` 或 deferred。

## 6. 阶段与门禁

| 阶段 | 核心产物 | 进入条件 | 通过条件 | 失败时回退 |
|---|---|---|---|---|
| `product_defined` | PRD | 产品问题被提出 | 目标、用户、范围、非目标、价值验收明确 | 回到 PRD 评审；不得写 SPEC 补业务规则 |
| `product_decided` | OPEN_QUESTIONS / Decision | 产品基线存在 | 当前切片 blocking 决定全部 `decided`，决定绑定基线 | 保持门禁 closed，等待产品裁决 |
| `spec_approved` | SPEC | 产品决定稳定 | 字段、状态机、不变量、失败、撤销、权限和测试合同闭合 | 修 SPEC 并升版；不改测试迎合实现 |
| `traceable` | Requirements Matrix | SPEC Approved | PRD→SPEC→Test 完整，Coverage Level 诚实，无过度声称 | 修追踪或缩小切片 |
| `architecture_decided` | Accepted ADR + 必要 architecture view | 语义合同稳定 | 只决定当前切片必需技术，替代方案/代价/回退明确 | ADR 保持 Proposed/Rejected；禁止开工 |
| `suite_materialized` | Manifest + Fixture + Oracle + runner contract | ADR 足以支持可运行测试 | required 集精确、合成/离线/确定、runner 可读取；`suite_materialized=true` | 保持 false，补齐 artifact；不得称测试通过 |
| `implementation_planned` | Implementation Plan + TODO | suite 已物化 | 每项任务回到 SPEC/Test/ADR，模块和完成条件明确 | 修 plan；不得让 TODO 自创业务规则 |
| `implementing` | Code + Tests | plan 通过 | 只实现计划内薄片，变更同步追踪，未扩大范围 | 停止并走 Change Control |
| `verified` | Verification Result | 实现和 runner 存在 | 同一次 current run 中 required 全部 passed，命令/环境/artifact 完整 | 修实现或合同；新 run，旧结果保留 |
| `review_passed` | Gate Review | Verification current | 无 P0/P1；P2 有明确后置；范围、隐私、回滚可接受 | 回到对应上游阶段 |
| `recovery_point_published` | Commit + annotated tag + pushed refs + Recovery Record | Review passed | 工作树清楚、tag 可解析到提交、远端可验证、恢复步骤可执行 | 不合并/不发布，修复 Git 或验证问题 |

## 7. 不可跳过的门禁

### 7.1 开始架构设计前

- PRD 基线与当前切片范围已批准。
- 当前切片 blocking 产品问题为 0。
- 适用 SPEC Approved，追踪链存在。

### 7.2 开始测试物化前

- 必要 ADR 为 `Accepted`。
- ADR 没有改变或补充未经确认的业务语义。
- required Test Ref 只有一个权威集合。

### 7.3 开始业务编码前

- 当前切片阶段至少达到 `architecture_decided`。
- `suite_materialized=true`，但允许 `suite_executed=false`、`suite_passed=false`。
- Implementation Plan 已审查，TODO 每项都有 SPEC/Test/完成条件。
- 没有 blocking/P1。

### 7.4 声称验证通过前

- 使用同一 commit、同一适用 suite/fixture/implementation/environment 的 run。
- required tests 全部实际执行且 passed。
- required skip、缺失或跨 run 拼接只能得到 `partial`。
- Verification Result 已写入仓库，包含 artifact digest。

### 7.5 合并或建立恢复点前

- Gate Review 无 P0/P1。
- PRD 未被静默修改，隐私扫描通过。
- 分支、commit、tag 和远端指向可复核。
- 未执行测试仍明确为 `not_executed`。

## 8. 产物职责

| 产物 | 回答的问题 | 不得回答的问题 | 路径 |
|---|---|---|---|
| PRD | 为什么做、为谁做、必须表现成什么样 | 数据库/框架怎么选 | `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的当前 PRD |
| Decision | 开放产品问题如何裁决 | 用代码事实替代产品决定 | `docs/decisions/` |
| SPEC | 语义合同、状态机、不变量、失败和验收 | 最终技术实现选择 | `docs/specs/` |
| Traceability | 要求如何到测试和结果 | 证明未执行测试通过 | `docs/traceability/` |
| Architecture View | 当前切片组件/边界/数据流如何组织 | 为什么选择某技术 | `docs/architecture/` |
| ADR | 为什么选择，以及放弃什么 | 新增产品业务规则 | `docs/adrs/` |
| Executable Tests | 如何机器证明 SPEC | 用 fixture 反向定义产品 | `tests/` |
| Implementation Plan | 以什么顺序修改哪些模块 | 越过 SPEC 自定语义 | `docs/planning/` |
| Verification Result | 实际运行了什么、结果是什么 | 把静态检查当业务通过 | `docs/testing/results/` |
| Gate Review | 是否可以进入下一阶段 | 改写历史结果 | `docs/reviews/` |
| Recovery Record | 如何定位、验证和恢复一个 Git 点 | 代替产品发布说明 | `docs/releases/` |

## 9. Stop-the-line 条件

出现以下任一情况必须停止当前阶段：

- 产品需求有两种合理解释且会改变行为。
- SPEC、fixture 和实现的 oracle 不一致。
- required tests 无法在同一 run 执行。
- 发现真实个人数据、凭据或工作区外数据进入项目。
- PRD hash 变化但没有新产品基线批准。
- ChangeSet、历史、证据、权限或删除不变量可能被绕过。
- 当前任务需要引入 deferred 功能才能继续。
- Git 工作树混入无法归属的相关改动。

停止后把问题写入 OPEN_QUESTIONS、Finding 或 Gate Review；不得只在聊天中说明。

## 10. 当前与上一切片

| 字段 | 当前值 |
|---|---|
| Active Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Active Phase | `architecture_decided` |
| 当前 PRD | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-AS-001` decided |
| SPEC Applicability | `passed`：S1/S2/S3/S6/S7 keep current |
| Trace / ADR / Architecture | Matrix §4.1 complete；`ADR-0002` Accepted；`ARCH-MVP-A-AS-001` Accepted Design Baseline |
| Suite | `defined=true`、`materialized=false`、`executed=false`、`passed=false` |
| Plan | suite-only Plan Approved；Implementation Plan Draft blocked |
| Business Implementation | `absent` |
| Business Verification | `not_executed` |
| Previous Slice | `SLICE-MICRO-RELATIONSHIP-001` = `recovery_point_published`；49/49 required passed |

下一步唯一动作是执行 `PLAN-MVP-A-AS-SUITE-001` 的 `AS-PRE-001`，只创建固定合成 fixture/oracle。`AS-PRE-001..005` 完成并通过 Suite Materialization Gate 前不得批准 Implementation Plan 或编写 A1 业务代码。

## 11. 相关说明与模板

- 变更控制：`docs/process/CHANGE_CONTROL.md`
- 架构职责：`docs/architecture/README.md`
- ADR 规则与模板：`docs/adrs/README.md`、`docs/adrs/ADR_TEMPLATE.md`
- 实施规划：`docs/planning/README.md`、`docs/planning/IMPLEMENTATION_PLAN_TEMPLATE.md`
- 测试与结果：`docs/testing/README.md`
- Gate Review：`docs/reviews/README.md`
- Git 恢复点：`docs/releases/README.md`
- 可执行测试目录：`tests/README.md`
- 总路线图：`docs/planning/MASTER_DELIVERY_ROADMAP.md`
- 模型接力：`docs/process/MODEL_HANDOFF_PROTOCOL.md`
- 当前唯一交接：`docs/process/CURRENT_HANDOFF.md`
- AI 角色提示词：`docs/process/AI_EXECUTION_PROMPTS.md`
- 一键部署：`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`
