# ADR-0002：Answer Safety 运行时与持久化增量

## 0. 元数据

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0002` |
| Status | `Accepted` |
| Date | 2026-07-17 |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Product Decision | `DEC-MVP-A-AS-001` |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

如何在不破坏已验证 Micro 行为、不引入外部服务或第三方依赖的前提下，持久化固定 CoverageWindow/Assertion fixture 并计算只读六态 AnswerEnvelope？

## 2. 约束

- Python 3.12 标准库与单进程 SQLite 已由上一切片验证，但不是长期技术栈承诺。
- A1 只读查询不得创建 Canonical revision、ChangeSet、Ledger 或 Projection 写入。
- Coverage declaration 可追溯；EvidenceAssessment/AnswerEnvelope 是 Derived、可重算结果。
- 六个状态使用固定合成 case、固定 Clock、显式 freshness policy、零网络。
- 现有 Micro suite 必须能够独立重跑；A1 不修改其 expected。
- 不实现通用规则引擎、RAG、LLM、权限 runtime 或 API 服务。

## 3. 方案比较

### Option A：在现有 Python/SQLite 基线上做加法式 A1 扩展

- 新增最小 CoverageWindow/fixture 存储和纯只读 evaluator。
- 复用 SQLite 连接/事务配置，但不改 Micro 业务状态机。
- A1 使用独立 adapter、manifest、fixture、runner result。
- 优点：无依赖、与当前 Canonical snapshot 直接集成、可验证只读不变量。
- 代价：`noetide_micro` 名称继续作为原型包；未来产品 runtime 仍需独立 ADR。
- 可逆性：高，新增表/模块可从合成 fixture 重建。

### Option B：纯内存 JSON evaluator

- 优点：实现最少、完全隔离。
- 问题：不能证明与实际 SQLite Canonical/Source 数据边界集成，也无法验证查询前后持久状态不变。
- 可逆性：高，但验证价值不足。

### Option C：引入规则引擎或独立查询服务

- 优点：未来可扩展复杂策略。
- 问题：新增依赖、服务边界和部署成本；A1 固定六态不需要通用平台。
- 可逆性：中，容易提前固化 API 和规则 DSL。

### Option D：等待 A5 UI/runtime 再决定

会阻止 A1 suite 的 storage integration 和只读验证，不可接受。

## 4. 决定

选择 Option A。

A1 延续 Python 3.12 stdlib + 单进程 SQLite，仅作以下增量：

- 在现有逻辑层中保存固定合成 CoverageWindow 和 A1 seed metadata。
- Assertion/Source 继续使用 Canonical/Source 逻辑边界；不得写 Projection 作为 Evidence。
- `EvidenceAssessment` 和 `AnswerEnvelope` 默认运行时计算，不持久化为 Canonical。
- 新建窄模块 `src/noetide_micro/answers.py` 和 test-only `answer_testing_adapter.py`；不建立 Web API/CLI/插件/服务总线。
- A1 测试数据和 runner 与 Micro 独立；共享 store 改动后必须重跑 Micro suite。
- 评估规则只覆盖 `ACCEPT-MVP-A-AS-001` 的固定、互相隔离 case；不声称通用复合 precedence。

物理表名、索引和列属于实施细节，但必须满足：外键开启、显式 schema 初始化、无业务 trigger、重复 seed 幂等、不同 fixture 冲突拒绝。

## 5. 失败行为

| 失败 | 行为 |
|---|---|
| Coverage fixture 非合成或缺字段 | 拒绝 seed，不部分写入 |
| Source/evidence locator 缺失 | 不返回 verified；按合同 unknown/unconfirmed 或明确 invalid assessment |
| freshness policy 缺失 | 不声称 stale/fresh；当前固定 case 初始化失败 |
| 冲突评估异常 | 不选值；返回失败结果，suite failed |
| Derived evidence 输入 | 拒绝其作为 Evidence；不复制到 Source |
| evaluator 尝试写 Canonical/Ledger/View | transaction/测试失败；revision 不变 |
| result artifact 写失败 | 不发布 suite passed |

## 6. 安全、隐私与可移植性

- data root 继续限定在仓库内测试临时目录。
- 所有 fixture、日志和 result 执行隐私扫描。
- 运行时不读取工作区外文件、不访问网络。
- A1 新增数据结构必须可从版本化合成 fixture 重建；不导入真实数据。
- 本 ADR 不决定 Context Pack、备份、加密、用户数据目录或安装包。

## 7. 验证

- A1 exact 11 场景 + 24 upstream refs 在同一次 run 执行。
- 查询前后 revision、Canonical/Ledger/Source/Projection digest 不变。
- 六态、scope、coverage、evidence、reason 和 policy 字段级 oracle 通过。
- A1 result 与 manifest/fixture/commit/environment hash 绑定。
- 对当前实现提交重新运行既有 Micro suite；A1 pass 不能替代 Micro regression。

## 8. 回退

若 A1 扩展破坏 Micro 或无法保持只读：停止实现，保留失败 result，从 `mvp-a-answer-safety-planning-v0.1-approved` 建修复分支；必要时将本 ADR 标为 Superseded 并选择独立 evaluator。不得修改旧 Micro expected 来保住通过。

## 9. 后续影响

- 创建 A1 Architecture View。
- 物化独立 A1 suite。
- Implementation Plan 在 suite materialized 后才可 Approved。
- A5 用户 runtime/包命名/部署仍需新 ADR，本决定不得外推。
