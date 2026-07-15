# PRD v0.5 最近验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-15 |
| 分支 | `codex/spec-v05-compatibility` |
| 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` |
| PowerShell / OS | `5.1.26100.8875` / `Microsoft Windows NT 10.0.26200.0` |
| 当前工作树结果 | exit code `0`；`PASSED (product baseline static checks only; no SPEC compatibility or business test was executed)` |
| LF/CRLF 可移植性 | 两个隔离副本 exit code 均为 `0`；去除临时 Root 行后的输出完全一致 |
| 校验器 SHA-256 | `a596ede5e91f493b9836795902ecf653605f4c9d050ea0ff95b23110e25820a2` |
| 当前工作树输出 digest | `92f46bd4f05ea824fd612eab5344614e88690e44ce9fd9706c5d61430fd48ee4` |
| LF/CRLF 共同输出 digest | `9879e2661244494616691b1b1883b606b1058e7a3367059d320d9e9ba4db6278` |
| SPEC Compatibility | 独立 `validate_spec_baseline.ps1` 与 Gate Review 已通过；本产品命令本身不证明兼容 |
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

- 本文件中的产品命令本身不证明 S1-S9 兼容；兼容证据见 `docs/testing/LATEST_STATIC_VALIDATION.md` 与 `docs/reviews/PRD_V05_SPEC_COMPATIBILITY_REVIEW.md`。
- 没有物化、执行或通过业务 suite。
- 没有实现代码、依赖、数据库或最终技术选型。
- 静态产品校验不能证明原子性、权限隔离、撤销、删除或性能行为。
