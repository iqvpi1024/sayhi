# PRD v0.5 最近验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-15 |
| 分支 | `codex/prd-v05-consolidation` |
| 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` |
| PowerShell / OS | `5.1.26100.8875` / `Microsoft Windows NT 10.0.26200.0` |
| 当前工作树结果 | exit code `0`；`PASSED (product baseline static checks only; no SPEC compatibility or business test was executed)` |
| LF/CRLF 可移植性 | 两个隔离副本 exit code 均为 `0`；去除临时 Root 行后的输出完全一致 |
| 校验器 SHA-256 | `a596ede5e91f493b9836795902ecf653605f4c9d050ea0ff95b23110e25820a2` |
| 当前工作树输出 digest | `825025a8763d87e26901044f97534cbe8d76821fc30664477e9e35d6bb18bc84` |
| LF/CRLF 共同输出 digest | `07656dcfd74149854a6ee8a287ab672d696703bd226525f639dbc8dc8b900501` |
| SPEC Compatibility | `not_executed` |
| Business Tests | `not_executed` |

## 2. 实际证明

- `PRDv04.md` canonical LF hash 保持不可变。
- `PRDv05.md` Approved hash 与产品基线索引一致。
- 顶层章节为 `1..27`，32 个 FR 与 v0.4 集合完全一致。
- 核心对象封闭为 12 个。
- `assertion_kind_values` 为 8 个内容类型，`answer_status_values` 为 6 个回答状态。
- v0.4 的五态、旧撤销指针、旧 SPEC 顺序和 Draft 状态措辞未残留在 v0.5。
- `DQ-001..013` 在 OPEN_QUESTIONS 中各出现一次。
- 配置的 phone-like、email-like、本机 user-directory path 启发式未命中。
- Markdown fence parity 正常。

## 3. 未证明

- 没有证明 S1-S9 与 PRD v0.5 兼容。
- 没有物化、执行或通过业务 suite。
- 没有实现代码、依赖、数据库或最终技术选型。
- 静态产品校验不能证明原子性、权限隔离、撤销、删除或性能行为。
