# ADR-0009：A5 应用壳的 stdlib CLI 形态与呈现层 Derived 化

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Slice | `SLICE-MVP-A-APP-SHELL-001` |
| Contract | `SPEC-A5-APP-SHELL-001` |

## 决定

A5 应用壳实现为 Python 标准库 CLI（argparse），扩展既有 `cli.py` 入口：新增 `guide`（引导式旅程）、`receipts`、`history`、`current-state` 命令；自然语言审查与影响预览由独立的 `app_shell.py` 呈现层模块生成。呈现层是纯函数：输入为 Candidate Envelope 与 Canonical 对象（只读），输出为自然语言呈现结构；呈现结果不持久化。壳的写路径只调用已验证核心能力（intake/candidate/changesets/views），不新增任何直接写 Canonical 或 Projection 的代码路径。本决定与 `DEC-PHASE8-UI-DEPLOY-001`（stdlib CLI、无 Web/桌面 UI、无新依赖）一致。

## 不采用的方案

- Web UI（http.server 或框架）：引入网络服务面与前端复杂度，超出固定合成切片；`DEC-PHASE8-UI-DEPLOY-001` 已明确后置。
- 桌面 UI（tkinter/Electron/Tauri）：打包与跨平台验证成本高；DEC-PHASE8 已后置。
- 把自然语言呈现持久化为 Canonical 对象：会把 Derived 伪装为事实，违反 A5-INV-002。
- 在壳层实现"快速写入"便捷路径：绕过 ChangeSet 审查，违反 A5-INV-001。
- 引入 CLI 增强第三方库（rich/click 等）：违反 stdlib-only 约束。

## 后果与验证

- 呈现层纯函数可在 suite 中逐案例断言输出形状；零绕过由"壳模块不出现 store 写方法调用"的静态检查 + 行为测试证明。
- 影响预览与实际发布一致性以对象集/视图集比较断言（A5-008）。
- 引导旅程的每步可观察结果（source_id、changeset_id、published_revision、receipt_id、视图 freshness）由 fixture/oracle 固定。
- A5 suite 必须证明：旅程全步骤、自然语言呈现形状、预览/发布一致、撤销后视图恢复、零绕过、trust/closeness/人格判断不变。