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
| 当前阶段 | Phase 1：Semantic Object Model SPEC |
| 阶段状态 | `awaiting_spec_review` |
| PRD 文件 | `PRDv04.md` |
| PRD 状态 | `Draft for Review` |
| PRD SHA-256 基线 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | 1/9 已形成草案，0/9 已批准 |
| 实现代码 | 无 |
| 已安装依赖 | 无 |
| 数据库/技术栈决定 | 无 |
| Git 状态 | 已初始化；分支 `main`；SSH-over-443 远程 `ssh://git@ssh.github.com:443/iqvpi1024/sayhi.git` |
| GitHub 备份 | 私有仓库；SSH 身份已验证；回滚标签 `phase-0-baseline` |

## 3. 当前阶段结论

`BQ-001` 至 `BQ-005` 与 `IQ-016` 已由产品负责人明确裁决。Semantic Object Model SPEC v0.1 已形成 `Draft for Review`，完整锁定 12 对象共同边界，并只深定义 Micro-MVP 六对象。

当前不得开始第二份 SPEC 或实现代码，直到产品负责人逐份审查并批准 `docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md`。依据：PRD §6-§13、§20、§24、§27及已记录产品裁决。

## 4. 已完成内容

- 完整读取 `PRDv04.md`，UTF-8 共 1301 行。
- 建立 PRD 内部矛盾、重复、未定义术语、不可验收要求、层级混淆、MVP 扩张和隐私/删除缺口审查。
- 把开放问题分为 `blocking`、`important`、`deferred`。
- 建立全部 32 条 FR 到九份 SPEC 的追踪矩阵。
- 定义九份 SPEC 的顺序、边界、依赖和完成标准；当前仅 S1 形成正式草案。
- 定义一条全合成 RelationshipState Micro-MVP 的 Given/When/Then 场景和禁止变化 oracle。
- 明确 Micro-MVP 不包含通用 NLP、实体消歧、提醒、Commitment、外部 Agent、权限模板、连接器、同步、财务、健康、决策和迁移。
- 记录 `BQ-001..005` 与 `IQ-016` 的产品裁决。
- 创建 `docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` v0.1 草案。
- 同步 Micro 验收 fixture、S1 需求追踪和 SPEC 工作顺序。

## 5. Phase 0 与 Phase 1 产物

| 文件 | 职责 | 状态 |
|---|---|---|
| `docs/reviews/PRD_V04_READINESS_REVIEW.md` | PRD 就绪审查与范围结论 | created |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | FR -> SPEC -> Test -> Module -> Result 追踪 | created |
| `docs/specs/README.md` | 九份 SPEC 边界、依赖与 DoD | created |
| `docs/decisions/OPEN_QUESTIONS.md` | 产品裁决队列 | created |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | Micro-MVP 合成验收场景 | created |
| `docs/PROJECT_STATE.md` | 可恢复项目状态 | created |
| `docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` | 第一份正式 SPEC | draft_for_review |

## 6. 验证结果

| 检查 | 结果 |
|---|---|
| PRD 完整读取 | completed |
| PRD 前后 SHA-256 一致 | passed：仍为 `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| S1 必备章节 | passed：21/21，无缺失 |
| S1 不变量与验收 | passed：14 个不变量、23 个唯一测试 ID，全部有映射 |
| 全部 FR 追踪 | passed：PRD 与矩阵均为 32 个唯一 FR，无缺失或额外项 |
| 产品裁决状态 | passed：`BQ-001..005` 与 `IQ-016` 均为 decided |
| 文档结构与隐私静态扫描 | passed：代码围栏成对；新增文档未复制 PRD 合成人物名 |
| GitHub 备份 | passed：SSH 认证成功，`main` 与 `phase-0-baseline` 已推送到私有远程仓库 |
| 测试套件 | Micro 与 SOM 均 `suite_defined=true`、`suite_executed=false`、`suite_passed=false` |
| 实现/集成测试 | 未执行；没有实现代码 |

最近验证结果的权威记录就是本节。不得把文档存在解释为实现通过。

## 7. 已裁决产品问题

- `BQ-001`：`RelationshipState` 是 `State` 的语义配置，不新增核心对象。
- `BQ-002`：`assertion_kind`、`review_status`、`answer_status` 三轴正交，事实回答采用六态。
- `BQ-003`：Source Append 使用独立审计回执，Canonical 语义写入必须经过 ChangeSet。
- `BQ-004`：Obligation/viewpoint/Calibration/Snapshot 映射到既有对象或 Projection。
- `BQ-005`：12 对象共同边界 + Micro 六对象深定义。
- `IQ-016`：采用 `docs/specs/README.md` 当前九份顺序。

其余 important/deferred 问题保持开放，并由对应后续 SPEC 处理；不得由实现自行裁决。
## 8. 风险

| 风险 | 当前控制 |
|---|---|
| SPEC 通过定义细节暗改产品语义 | 六项裁决已持久记录；S1 仍需逐份批准 |
| PRD §27.2 与当前 SPEC 顺序分叉 | `IQ-016` 已决定采用项目顺序；PRD 原文不改 |
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

**产品负责人审查并明确批准 `docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` v0.1，或逐项提出需要修改的语义。**

批准前不开始 Bitemporal & Evidence SPEC，不编写实现代码。

## 11. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | 建立 PRD 就绪审查、开放问题、需求矩阵、SPEC 计划、Micro 验收和持久状态；未改 PRD、未写代码、未选技术栈 |
| 2026-07-13 | Git 基线 | 初始化 `main`，配置私有 GitHub SSH 远程和 `phase-0-baseline` 回滚标签 |
| 2026-07-13 | Phase 1 | 记录产品裁决，形成 Semantic Object Model SPEC v0.1 草案并完成静态验证；未执行实现测试 |
