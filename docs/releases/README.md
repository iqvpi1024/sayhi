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

最近的开发前恢复点为 tag `micro-development-ready-v0.1-approved`，记录见 `MICRO_DEVELOPMENT_READY_V0.1_RECOVERY_POINT.md`。它只证明当前 Micro 已达到 `implementation_planned`，不证明业务实现或业务测试通过。
