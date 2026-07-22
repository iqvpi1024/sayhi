# A2 current_state Core View 任务卡

## 0. 使用规则

本卡集属于 `PLAN-MVP-A-A2-IMPL-001`。每轮只执行 `CURRENT_HANDOFF.next_single_action` 指向的一张卡；完成后更新状态并转到下一张，不得跳卡。

共同禁止：修改 PRD、A2 Contract、fixture/oracle 预期以适配实现；读取工作区外数据；加入依赖、网络、模型、查询引擎、真实输入、权限/MCP runtime 或 A3 及后续能力。

## 1. A2-TASK-001：current_state 投影存储辅助

- 入口：`current_phase=implementation_planned`，无 A2 实现改动。
- 实现：current_state rebuild receipt 表、投影删除与 stale 辅助的窄 store 方法。
- 禁止：视图语义进 trigger、改写既有 projection_rows 语义、Canonical 写入。
- 验证：schema 初始化、PRAGMA、receipt 持久化、Derived 删除不动 Canonical/Ledger。
- 完成后：`A2-TASK-002`。

## 2. A2-TASK-002：current_state projector / reader

- 入口：TASK-001 已完成并有定向记录。
- 实现：当前有效纯函数判定、build/read/stale/rebuild 等价、注入失败降级 unavailable、Derived evidence/trigger 拒绝。
- 禁止：写 Canonical、产生新 revision、用旧投影冒充 fresh、从视图构造事实。
- 验证：`A2-001..008` 定向行为和 Derived delete/rebuild。
- 完成后：`A2-TASK-003`。

## 3. A2-TASK-003：测试 adapter

- 入口：TASK-002 已完成。
- 实现：只实现 `a2_current_state_adapter_protocol.py` 的 `create_system`、`run_case`、`layer_snapshot`、`inject_failure`。
- 禁止：修改 fixture/oracle 或使 contract test 在未实现时伪通过。
- 验证：八个 test case 能加载、各 case 使用独立临时数据库。
- 完成后：`A2-TASK-004`。

## 4. A2-TASK-004：验证与绑定

- 入口：TASK-003 已完成。
- 实现：运行 A2 official runner；仅在真实 8/8 passed 后更新 manifest current result binding。
- 验证：全量 semantic regression、所有现有 suite validator、Product/SPEC baseline、隐私扫描、`git diff --check`。
- 禁止：跳过 A2 case、合并跨 run result、把 skipped 写成 passed。
- 完成后：`A2-TASK-005`。

## 5. A2-TASK-005：独立审计与恢复点

- 入口：TASK-004 的同一适用 commit 所有 required A2 case passed。
- 实现：独立 audit、P0/P1 处理、PROJECT_STATE/Matrix/记录和可恢复 tag。
- 禁止：移动旧 tag、混入不相关文件或把 D1 Release 升格为 D2/D3。
- 完成后：根据 audit 结论选择下一 Product Decision。
