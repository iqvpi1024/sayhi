# B2 Episode 与分层摘要任务卡

## 0. 使用规则

本卡集属于 `PLAN-MVP-B-B2-IMPL-001`。每轮只执行 `CURRENT_HANDOFF.next_single_action` 指向的一张卡；完成后更新状态并转到下一张，不得跳卡。

共同禁止：修改 PRD、B2 Contract、fixture/oracle 预期以适配实现；读取工作区外数据；加入依赖、网络、模型、真实输入、权限/MCP runtime 或 B3 及后续能力。

## 1. B2-TASK-001：Episode / Summary storage foundation

- 入口：`current_phase=implementation_planned`，无 B2 实现改动。
- 实现：最小 Episode Canonical 表、Source/Entity ref 完整性、Derived summary 表和显式 schema version/migration 检查。
- 禁止：自动生成 Episode、trigger 语义、summary 作证、变更现有 Micro schema 语义。
- 验证：schema 初始化、PRAGMA、foreign key、重复初始化/seed、非合成 profile 拒绝。
- 完成后：`B2-TASK-002`。

## 2. B2-TASK-002：Episode ChangeSet 边界

- 入口：TASK-001 已完成并有定向记录。
- 实现：fixed candidate 的 Source/Entity/time 校验、review/approve/publish、补偿撤销与历史保留。
- 禁止：绕过 ChangeSet、直接从文本抽取、改变 Assertion/relationship/hypothesis。
- 验证：`B2-001/002/004/008` 的定向行为和既有 ChangeSet 回归。
- 完成后：`B2-TASK-003`。

## 3. B2-TASK-003：Derived summary projector / reader

- 入口：TASK-002 已完成。
- 实现：确定性 day/phase summary、dependency/revision、stale/rebuild/unavailable、Derived evidence 拒绝。
- 禁止：写 Canonical、使用 LLM、用旧 summary 冒充 fresh、从 summary 构造事实。
- 验证：`B2-003/004/005/006/007` 定向行为和 Derived delete/rebuild。
- 完成后：`B2-TASK-004`。

## 4. B2-TASK-004：测试 adapter

- 入口：TASK-003 已完成。
- 实现：只实现 `b2_episode_summary_adapter_protocol.py` 的 `create_system`、`run_case`、`layer_snapshot`、`inject_failure`。
- 禁止：修改 fixture/oracle 或使 contract test 在未实现时伪通过。
- 验证：八个 test case 能加载、各 case 使用独立临时数据库。
- 完成后：`B2-TASK-005`。

## 5. B2-TASK-005：验证与绑定

- 入口：TASK-004 已完成。
- 实现：运行 B2 official runner；仅在真实 8/8 passed 后更新 manifest current result binding。
- 验证：全量 semantic regression、所有现有 suite validator、Product/SPEC baseline、隐私扫描、`git diff --check`。
- 禁止：跳过 B2 case、合并跨 run result、把 skipped 写成 passed。
- 完成后：`B2-TASK-006`。

## 6. B2-TASK-006：独立审计与恢复点

- 入口：TASK-005 的同一适用 commit 所有 required B2 case passed。
- 实现：独立 audit、P0/P1 处理、PROJECT_STATE/Matrix/Release record 和可恢复 tag。
- 禁止：移动旧 tag、混入不相关文件或把 D1 Release 升格为 D2/D3。
- 完成后：根据 audit 结论选择下一 Product Decision。
