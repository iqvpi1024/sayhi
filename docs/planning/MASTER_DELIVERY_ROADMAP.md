# 识海 Noetide 总交付路线图

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Roadmap ID | `ROADMAP-NOETIDE-001` |
| Status | `Active Planning Baseline` |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Date | 2026-07-17 |
| Current Completed Slice | `SLICE-MICRO-RELATIONSHIP-001` |
| Current Active Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |

本路线图只规定交付顺序、切片边界和门禁。它不替代 PRD、Product Decision、SPEC、ADR、suite 或单切片 Implementation Plan，也不授权提前实现后续能力。

## 1. 最终目标

识海最终应成为一个普通用户能够安装、使用、纠正、导出和恢复的 Local-first 个人上下文产品，并在 GitHub 上具备可审计、可复现、可回滚的发布链路。

最终交付必须同时满足：

1. 产品行为符合当前 Approved PRD 和逐切片 Product Decision。
2. 规范语义由 SPEC 定义，代码不补写产品规则。
3. 每个切片有独立 suite、Verification Result、Gate Review 和 Git Recovery Point。
4. 所有演示、fixture 和自动测试只使用合成数据。
5. 非技术用户可以通过安装包完成安装；开发者可以通过一个入口命令完成本地启动。
6. Source、Canonical Context、Revision Ledger 和导出内容不依赖当前软件仍可读取。
7. GitHub Release 包含校验值、恢复说明、已知限制和实际支持平台。

## 2. 当前基线

`SLICE-MICRO-RELATIONSHIP-001` 已完成 `TASK-001..010`，49 个 required result IDs 在同一次 current run 中全部通过，Recovery tag 为 `micro-mvp-v0.1-validated`。

这只证明固定合成 RelationshipState 链路。它不是可供普通用户使用的完整应用，也不证明 MVP-A、MVP-B、MVP-C 或公共发布已经完成。

## 3. 统一切片流程

每个切片固定执行：

```text
Product Baseline
-> Product Decision
-> SPEC Applicability / Revision
-> Traceability
-> ADR + Architecture View（仅在需要时）
-> Executable Suite
-> Implementation Plan
-> Development
-> Verification
-> Independent Audit
-> Debug / Re-verification
-> Gate Review
-> Git Recovery Point
```

任何阶段失败都回到产生问题的权威层，不得通过降低测试、扩大默认权限或修改 expected 来制造通过。

## 4. MVP-A：可信变化核心

### A1：回答安全与最小冲突

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Primary FR | FR-008；FR-010 的检测与并列呈现切片 |
| 状态 | `architecture_decided` |
| 目标 | 一个固定事实查询根据证据、覆盖、冲突和新鲜度返回六态 `AnswerEnvelope` |
| 非目标 | 通用问答、LLM、权限 runtime、MCP、冲突裁决、Canonical `value=unknown` |
| 下一门禁 | 执行 `AS-PRE-001..005`，完成 Suite Materialization Gate |

该切片只使用固定合成 Canonical snapshot 和固定查询，证明 `verified`、`unconfirmed`、`disputed`、`not_covered`、`stale`、`unknown` 严格分离，并禁止 Derived View 成为事实证据。

当前已经完成 SPEC applicability、35-ID exact contract、Trace、ADR-0002、Architecture 和 Pre-Suite Gate。A1 suite 尚未物化，Implementation Plan 仍为 blocked Draft，业务实现不存在。当前单一入口见 `docs/process/CURRENT_HANDOFF.md`。

### A2：第三个 Core View 与通用当前状态读取

- 目标：将 PRD §24.2 的 `current_state` 从 Micro 两个 View 的受控读取结果提升为第三个 MVP-A Core View。
- 主要 FR：FR-006、FR-008、FR-105 的 MVP-A 切片。
- 依赖：A1 的 `AnswerEnvelope` 与 freshness 语义通过。
- 禁止：扩展 Commitment、提醒、权限模板或 L3 画像。

### A3：实体合并候选与拆分回滚

- 目标：只证明两个合成 Person Entity 的 merge proposal、用户确认、引用重定向和 split compensation。
- 主要 FR：FR-011。
- 依赖：A1 回答安全、既有 ChangeSet 原子性和审计历史。
- 禁止：自动人物合并、模糊身份模型、真实联系人导入。

### A4：查询层权限与舱室强制执行

- 目标：证明单用户本地调用者在字段、舱室、目的和时间约束下 fail closed。
- 主要 FR：FR-012。
- 依赖：A1 AnswerEnvelope；S4 applicability review。
- 需要重开：仅与该切片直接相关的 Privacy Product Decision；`DQ-003` 若涉及 sealed 紧急恢复仍保持 deferred。
- 禁止：家庭授权、数字遗产、外部 Agent runtime。

### A5：自然语言审查与最小可用应用壳

- 目标：让普通用户在本地完成记录、预览、确认、读取和撤销，不要求理解 ChangeSet。
- 主要 FR：FR-001、FR-005、FR-006、FR-007 的可用性扩展。
- 依赖：A1-A4 的核心行为稳定。
- 技术选择：必须在该切片 ADR 中决定，不在本路线图预选 Web、桌面框架或打包工具。
- 禁止：营销首页、云账户、多租户、在线强依赖。

### A6：MVP-A 硬化与本地 Alpha

- 目标：完成 PRD §24.2 的 12 个可执行语义变更场景、Reference Profile、错误恢复和本地 Alpha 发布。
- 主要范围：MVP-A 尚未完整覆盖的 FR-001..012。
- 出口：所有 P0/P1 关闭；干净机器可启动；用户数据路径、备份、导出和卸载语义可解释。
- 该阶段仍不进入 MVP-B 功能。

## 5. MVP-B：识灵静默整合

| Slice | 主要范围 | 依赖 | 明确后置 |
|---|---|---|---|
| `B1-CANDIDATE-REVIEW` | FR-101、FR-102、FR-107；聚合、去重、Review Budget | MVP-A Alpha | 通用自动发布 |
| `B2-EPISODE-SUMMARY` | FR-103；Episode 与分层摘要 | B1；Source/Answer 安全 | 人格推断、决策引擎 |
| `B3-COMMITMENT` | FR-104；Commitment 状态、提醒、撤销 | B1/B2 | 财务、健康专业流程 |
| `B4-RECONCILIATION-DIFF` | FR-105 完整化、FR-106；对账与 Semantic Diff | A2、B3 | 多设备同步 |
| `B5-MULTILINGUAL` | FR-108；原文与翻译对照 | Source/portability 合同 | 覆盖所有语言 |
| `B6-SHADOW-MIGRATION` | 合成/匿名化复杂数据影子迁移与压力测试 | B1-B5 | 真实历史迁移、全连接器 |

进入 B1 前重开 `DQ-002` 和 `DQ-011`。任何默认自动处理范围必须由 Product Decision 明确，不得由模型置信度替代。

## 6. MVP-C：决策与成长

| Slice | 主要范围 | 必须保护 |
|---|---|---|
| `C1-DECISION-OUTCOME` | FR-202；Goal、Decision、Outcome、Calibration | 事实/预测/结果分离 |
| `C2-HYPOTHESIS-LIFECYCLE` | FR-201；支持、反例、范围、weakened/challenged | Hypothesis 不升级为 Fact |
| `C3-REVIEW-CALIBRATION` | FR-203、FR-205 | 历史版本、阶段可比性 |
| `C4-SCENARIO-ACTION` | FR-204、FR-206 | 情景不是预测事实；不替代专业意见 |
| `C5-CONTEXT-PACK-BACKUP` | FR-303 的首年切片；Markdown+JSON Pack、本地加密备份 | 独立可读、校验、删除与恢复诚实性 |
| `C6-MVP-RELEASE` | 首年完整回归、安全审计、数据恢复和公开 Beta 门禁 | 全部首年非目标保持关闭 |

进入 C1 前重开 `DQ-006`；任何健康、法律或财务专业建议仍不属于产品能力。

## 7. Year 2 与长期路线

以下仅保留路线，不建立当前 SPEC、ADR 或 Implementation Plan：

- FR-301：多设备加密同步。进入前重开 `DQ-007`。
- FR-302：2-3 个高价值连接器。进入前重开 `DQ-008`。
- FR-304：专业 Agent 权限模板。
- FR-305：家庭授权与数字遗产。进入前重开 `DQ-004`、`DQ-009` 并完成法律/伦理评审。
- FR-306：A2A 或其他 Agent 协议。进入前重开 `DQ-010`。
- Context Pack 生态、多模态档案、离线模型和长期自我模型保持 Year 3-5 规划项。

## 8. 发布与部署轨道

部署不是最后临时补上的脚本，而是从 MVP-A 开始逐级验收：

1. `D0 Reproducible Dev`：干净仓库一个入口命令运行测试和本地开发环境。
2. `D1 Evaluator Package`：评审者无需手工建库即可启动合成演示。
3. `D2 End-user Installer`：普通用户下载安装包后点击安装并启动，数据目录由用户拥有。
4. `D3 GitHub Release`：版本 tag、构建产物、校验值、签名、升级/回滚、SBOM、已知限制和恢复说明齐全。

详细门禁见 `docs/releases/ONE_CLICK_DELIVERY_PLAN.md`。

## 9. 公共发布完成定义

只有全部满足才可称“识海可一键部署”：

- 当前 Product Release Gate 无 P0/P1。
- 支持平台和最低环境被明确列出并在干净环境验证。
- 非技术用户路径不要求手工安装数据库、编辑配置或运行迁移命令。
- 首次启动、升级、失败回滚、备份恢复、导出、卸载均有真实测试。
- 默认离线可用；任何网络能力都需明确授权和失败降级。
- GitHub 仓库不含真实个人数据、凭据、工作区私有目录或不可重建缓存。
- Release artifact、源码 tag、校验值和 Verification Result 可互相定位。
- 用户明确批准仓库可见性和正式发布；技术代理不得自行把仓库改为 public。

## 10. 路线变更规则

- 切片顺序可因测试或产品风险调整，但必须记录 Decision 和下游影响。
- 未来路线不等于当前授权；只有 active slice 可以进入 SPEC applicability review。
- 任何切片若需要 deferred 能力才能通过，应缩小或停止，不得提前拉入长期平台。
- 每个已推送 Recovery tag 不移动；修订建立新 tag。

## 11. 模型执行与交接入口

- 当前唯一动作：`docs/process/CURRENT_HANDOFF.md`。
- 各角色可复制提示词：`docs/process/AI_EXECUTION_PROMPTS.md`。
- 角色职责与交接字段：`docs/process/MODEL_HANDOFF_PROTOCOL.md`。
- 普通用户安装与 GitHub Release 门禁：`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`。

Planner 负责把每个 future slice 推进到可施工门禁；Suite Materializer、Implementer、Verifier、Auditor、Debugger 和 Releaser 必须按角色顺序接力。后续模型不得从路线图直接跳到代码。
