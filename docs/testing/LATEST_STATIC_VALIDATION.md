# 最近静态验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-15 23:10 +08:00 |
| 分支 | `codex/spec-v05-compatibility` |
| 产品命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` |
| SPEC 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1` |
| PowerShell / OS | Windows PowerShell `5.1.26100.8875`；host `7.6.3`；`Microsoft Windows NT 10.0.26200.0` |
| 产品结果 | exit code `0`；`PASSED (product baseline static checks only; no SPEC compatibility or business test was executed)` |
| SPEC 结果 | exit code `0`；`PASSED (static contract checks only; no business test was executed)` |
| 产品校验器 SHA-256 | `a596ede5e91f493b9836795902ecf653605f4c9d050ea0ff95b23110e25820a2` |
| SPEC 校验器 SHA-256 | `b071a6da451c91176a425a615ab58b6a2fa9d9d16d7f245f175bf9fafecceda6` |
| 当前产品输出 digest | `92f46bd4f05ea824fd612eab5344614e88690e44ce9fd9706c5d61430fd48ee4` |
| 当前 SPEC 输出 digest | `8600188298ffcaa6a78a35c1f68644a1872d86ec480685ee7d8fc19758ab2606` |
| 业务测试 | `not_executed` |

输出 digest 使用 UTF-8 + canonical LF，包含当前工作树 `Root` 行；隔离副本 digest 在去除各自 `Root` 行后比较。

## 2. 当前工作树实际证明

| 检查 | 结果 |
|---|---|
| 产品基线 | v0.4 历史 hash 与 v0.5 当前 hash 均 passed；索引指向一致 |
| SPEC | S1 v0.5；S2-S6 v0.4；S7-S8 v0.3；S9 v0.4，均 Approved 且绑定 PRD v0.5 |
| Test ID | passed：275 个连续且跨 suite 唯一 |
| Invariant | passed：133 个均在 §19 结构化映射到存在的本 suite Test ID |
| Micro | passed：10 个场景、两个 58-byte Source、39 个去重 required upstream tests |
| FR / Matrix | passed：32 条 FR、9/8/15 Coverage Level、174 个唯一 Test Ref |
| Closed enum | passed：20 个机器可读正向闭集 |
| Privacy heuristic | passed：42 份权威合同/测试文件未命中 phone-like、email-like、本机 user-directory path |
| Markdown | passed：55 个 Markdown 文件 fence parity 成对 |
| 兼容 Gate | `PRD_V05_SPEC_COMPATIBILITY_REVIEW.md` 结论 `yes`，P0=0、P1=0、P2=0、P3=1 accepted debt |

## 3. LF/CRLF 隔离复验

最终复验在 `C:\tmp\noetide-spec-eol-final-0c70c8a36ed649808d6badcbc0c89d49` 的两个临时副本运行，完成后已验证路径并删除。

| 校验器 | LF exit | CRLF exit | 共同输出 digest |
|---|---:|---:|---|
| Product | 0 | 0 | `9879e2661244494616691b1b1883b606b1058e7a3367059d320d9e9ba4db6278` |
| SPEC | 0 | 0 | `78852fbba3b24451935dac3233db9a8167ddc9b19c43a88fe7e5cfe12f3ec9b0` |

中间诊断曾产生一次真实失败：首次换行转换把原本带 UTF-8 BOM 的 `validate_product_baseline.ps1` 改为无 BOM，Windows PowerShell 5 将中文字符串按 ANSI 解析并在 parse 阶段 exit code 1。随后隔离转换改为保留每个文件原始 BOM 属性，产品与 SPEC 的 LF/CRLF 四次运行全部 exit code 0。该失败不是业务测试失败，也没有从记录中删除。

## 4. 未证明

- 没有机器 suite manifest、fixture artifact、runner 或 Implementation Module。
- 所有 suite 仍为 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。
- 静态检查不能证明业务原子性、权限隔离、撤销、删除、迁移回滚或性能 SLO。
- 隐私启发式不是法律或取证级证明。
- 当前验证只允许切片恢复到 `traceable`，不表示 ADR、Implementation Plan 或业务开发已获完成。
