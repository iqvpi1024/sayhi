# 发布与 Git 恢复点说明

## 1. 区分两个概念

- Recovery Point：经过当前阶段校验、可由 commit/tag/remote 恢复的工程基线。
- Product Release：面向用户交付的可运行产品版本。

当前项目只有文档和规范恢复点，没有产品 Release。Git tag 不能证明业务功能存在或通过。

## 2. Recovery Point 门禁

创建恢复点前必须满足：

1. 当前 Gate Review 无 P0/P1。
2. 与变更范围相称的实际验证已运行并记录。
3. PRD hash、隐私边界、工作树范围和未执行项已核对。
4. commit 只包含当前任务文件。
5. 使用 annotated tag，tag 指向已验证 commit。
6. branch 和 tag 已推送，远端引用可解析。
7. Recovery Record 说明验证、限制和恢复命令。

## 3. 命名与不可改写

- 分支默认使用 `codex/<purpose>`。
- tag 建议使用 `<scope>-v<version>-validated`。
- 已推送 tag 不移动、不复用；修订后创建新 tag。
- Recovery Record 不删除旧记录，不把旧失败改写成成功。

## 4. 恢复验证

恢复说明至少包括：

- remote、branch、commit 和 tag。
- 如何 fetch、创建独立 worktree/checkout 和验证 tag 指向。
- 必须重新运行的校验命令。
- 哪些业务测试仍为 `not_executed`。
- 任何本地未跟踪文件不属于恢复点。

模板见 `RECOVERY_POINT_TEMPLATE.md`。

## 5. 当前已知基线

最近已验证的工程恢复点为 tag `micro-mvp-v0.1-validated`，记录见 `MICRO_MVP_V0.1_RECOVERY_POINT.md`。它证明固定合成 Micro 链路通过，不是面向普通用户的 Product Release。

从开发入口到安装包和 GitHub Release 的 D0-D3 门禁见 `ONE_CLICK_DELIVERY_PLAN.md`。当前尚未达到 D0，不得声称可一键部署。

当前规划恢复点为 tag `mvp-a-answer-safety-planning-v0.1-approved`，记录见 `MVP_A_ANSWER_SAFETY_PLANNING_V0.1_RECOVERY_POINT.md`。它只批准路线图和 A1 Product Decision，不授权 A1 业务开发。

当前 A1 architecture 恢复点为 tag `mvp-a-answer-safety-architecture-v0.1-approved`，记录见 `MVP_A_ANSWER_SAFETY_ARCHITECTURE_V0.1_RECOVERY_POINT.md`。它批准 SPEC applicability、exact contract、Trace、ADR-0002、Architecture 和 suite-only Plan；A1 suite 尚未物化，Implementation Plan 仍是 blocked Draft。

当前模型交接恢复点为 tag `mvp-a-answer-safety-handoff-v0.1-approved`，记录见 `MVP_A_ANSWER_SAFETY_HANDOFF_V0.1_RECOVERY_POINT.md`。它提供当前唯一动作和测试、开发、验证、审计、Debug、复审、Recovery/Public Release 角色提示词；不授权跳过 suite 物化门禁。

当前 A1 开发就绪恢复点为 tag `mvp-a-answer-safety-development-ready-v0.1-approved`，记录见 `MVP_A_ANSWER_SAFETY_DEVELOPMENT_READY_V0.1_RECOVERY_POINT.md`。它包含 materialized A1 suite、Approved Plan 和逐任务卡，只授权从 `AS-TASK-001` 开始；A1 业务测试仍为 `not_executed`。
