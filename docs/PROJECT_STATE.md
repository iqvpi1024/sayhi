# 项目状态

## 1. 恢复入口

任何新任务必须按以下顺序读取：

1. `PRDv04.md`
2. `docs/PROJECT_STATE.md`
3. `docs/decisions/OPEN_QUESTIONS.md`
4. 当前阶段对应的 SPEC
5. 当前阶段测试和最近验证结果

除 `PRDv04.md` 外，不使用工作区外或其他历史知识库作为产品事实来源。所有测试数据必须为合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 当前日期 | 2026-07-13 |
| 当前阶段 | Phase 0：PRD 就绪审查与项目建档 |
| 阶段状态 | `awaiting_product_decision` |
| PRD 文件 | `PRDv04.md` |
| PRD 状态 | `Draft for Review` |
| PRD SHA-256 基线 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | 0/9，均未开始 |
| 实现代码 | 无 |
| 已安装依赖 | 无 |
| 数据库/技术栈决定 | 无 |
| Git 状态 | 已初始化；分支 `main`；SSH 远程 `git@github.com:iqvpi1024/sayhi.git` |
| GitHub 备份 | 私有仓库；SSH 身份已验证；回滚标签 `phase-0-baseline` |

## 3. 当前阶段结论

PRD 的产品方向、语义红线和 Micro-MVP 主链路已经足够明确，但核心对象与认知状态仍有 blocking 问题。正式 Semantic Object Model SPEC 在 `BQ-001` 至 `BQ-005` 裁决前不得开始。

依据：PRD §6-§13、§20、§24、§27；详细审查见 `docs/reviews/PRD_V04_READINESS_REVIEW.md`。

## 4. 已完成内容

- 完整读取 `PRDv04.md`，UTF-8 共 1301 行。
- 建立 PRD 内部矛盾、重复、未定义术语、不可验收要求、层级混淆、MVP 扩张和隐私/删除缺口审查。
- 把开放问题分为 `blocking`、`important`、`deferred`。
- 建立全部 32 条 FR 到九份 SPEC 的追踪矩阵。
- 定义九份 SPEC 的顺序、边界、依赖和完成标准；没有编写正式 SPEC 正文。
- 定义一条全合成 RelationshipState Micro-MVP 的 Given/When/Then 场景和禁止变化 oracle。
- 明确 Micro-MVP 不包含通用 NLP、实体消歧、提醒、Commitment、外部 Agent、权限模板、连接器、同步、财务、健康、决策和迁移。

## 5. Phase 0 产物

| 文件 | 职责 | 状态 |
|---|---|---|
| `docs/reviews/PRD_V04_READINESS_REVIEW.md` | PRD 就绪审查与范围结论 | created |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | FR -> SPEC -> Test -> Module -> Result 追踪 | created |
| `docs/specs/README.md` | 九份 SPEC 边界、依赖与 DoD | created |
| `docs/decisions/OPEN_QUESTIONS.md` | 产品裁决队列 | created |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | Micro-MVP 合成验收场景 | created |
| `docs/PROJECT_STATE.md` | 可恢复项目状态 | created |

## 6. 验证结果

| 检查 | 结果 |
|---|---|
| PRD 完整读取 | completed |
| PRD 前后 SHA-256 一致 | passed：仍为 `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 只创建本轮允许文件 | passed：`docs/` 恰有 6 个允许文件 |
| 全部 FR 追踪 | passed：PRD 与矩阵均为 32 个唯一 FR，无缺失或额外项 |
| 开放问题 ID 一致性 | passed：33 个唯一 ID，定义与引用集合一致 |
| 文档路径引用 | passed：6 个引用路径均存在 |
| 禁止项扫描 | passed：无正式 SPEC、实现代码或数据库文件；未复制 PRD 合成人物名 |
| GitHub SSH | passed：账号认证成功，远程仓库为空，可安全建立首次提交 |
| Micro 测试套件 | `suite_defined=true`、`suite_executed=false`、`suite_passed=false` |
| 实现/集成测试 | 未执行；没有实现代码 |

最近验证结果的权威记录就是本节。不得把文档存在解释为实现通过。

## 7. Blocking 问题

- `BQ-001`：`RelationshipState` 的规范对象归属。
- `BQ-002`：Assertion 内容类型、审查状态、回答状态和 `unknown` 的正交关系。
- `BQ-003`：Source append 是否受 ChangeSet 唯一写路径约束。
- `BQ-004`：`Obligation`、`Snapshot`、`viewpoint`、`Calibration` 等未映射对象术语。
- `BQ-005`：第一份 Semantic Object Model SPEC 是全量 12 对象深定义，还是共同边界加 Micro 子集深定义。

完整问题、依据和决策模板见 `docs/decisions/OPEN_QUESTIONS.md`。

## 8. 风险

| 风险 | 当前控制 |
|---|---|
| SPEC 通过定义细节暗改产品语义 | blocking 问题未裁决前停止正式 SPEC |
| PRD §27.2 与当前任务的 SPEC 顺序分叉 | 记录为 `IQ-016`，不修改 PRD；暂按当前任务顺序建档 |
| P0 被误当成 Micro-MVP 全部范围 | 追踪矩阵单独标记 Micro 部分覆盖 |
| “场景已定义”被误报为“测试通过” | 三态测试字段固定记录为 defined/未执行/未通过 |
| 删除能力产生虚假承诺 | 删除范围、时限、备份和审计去正文进入 important 问题 |
| Core View 数量扩大第一条链路 | 暂只定义人物卡与关系时间线，待 `IQ-001` 裁决 |
| 工作区既有材料污染唯一 PRD 基线 | 其他既有审查材料未用作事实来源，也未修改 |

## 9. 范围锁

在 Micro-MVP 主链路通过前，禁止进入：

- 财务、健康、决策和成长闭环。
- 多设备同步、连接器、历史数据迁移。
- 多租户、多 Agent、A2A、数字遗产。
- 通用图数据库平台、全量依赖语言和最终技术栈选择。
- 真实个人数据、工作区外知识库或历史档案。

依据：PRD §24.1、§24.7、§25，以及 Phase 0 任务约束。

## 10. 下一步唯一建议动作

**产品负责人逐项裁决 `BQ-001` 至 `BQ-005`，并确认 `IQ-016` 的 SPEC 顺序基线。**

完成该动作并明确批准 Phase 0 门禁后，才开始第一份 Semantic Object Model SPEC；本轮到此停止。

## 11. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | 建立 PRD 就绪审查、开放问题、需求矩阵、SPEC 计划、Micro 验收和持久状态；未改 PRD、未写代码、未选技术栈 |
| 2026-07-13 | Git 基线 | 初始化 `main`，配置私有 GitHub SSH 远程和 `phase-0-baseline` 回滚标签 |
