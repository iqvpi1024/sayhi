# 最近静态与开发前验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-16 13:58:55 +08:00 |
| 分支 | `codex/micro-development-readiness` |
| 内容提交 | `581e2838093b21db6a9f80c348d3980878c275ae` |
| 产品命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` |
| SPEC 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1` |
| Suite 命令 | `python .\tools\validate_micro_suite.py` |
| Gate 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_pre_development_gate.ps1` |
| Diff 命令 | `git diff --check` |
| PowerShell / OS | Windows PowerShell `5.1.26100.8875`；host `7.6.3`；`Microsoft Windows NT 10.0.26200.0` |
| Runtime | Python `3.12.8`；SQLite `3.45.3`；stdlib only |
| 产品结果 | exit code `0`；静态产品检查通过 |
| SPEC 结果 | exit code `0`；静态合同 + suite 物化预检通过 |
| Suite 结果 | exit code `0`；只验证物化工件 |
| Gate 结果 | exit code `0`；开发前产物检查通过 |
| Diff 结果 | exit code `0` |
| 业务测试 | `not_executed` |

## 2. Digest

| 产物 | SHA-256 |
|---|---|
| Product validator | `a596ede5e91f493b9836795902ecf653605f4c9d050ea0ff95b23110e25820a2` |
| SPEC validator | `df7e719675acaf6314b4222b85082fe1cd88fedc71adb087e2364446e06720dc` |
| Suite validator | `c67961f3058d6e48923ed470858be52ede427c6333951407b73efdc20e80e543` |
| Development Gate validator | `2b01f38491338f27054e3d50aacc6387734ce01b9138e0707871da65d7cdf0f8` |
| Suite manifest | `54d70b993dbd5ce117605f6b07c305d2b97eba67df6a782c0e75f3afc28a5390` |
| Product output canonical LF | `92f46bd4f05ea824fd612eab5344614e88690e44ce9fd9706c5d61430fd48ee4` |
| SPEC output canonical LF | `ac54d0481ba2760ca414cdc1de9994ba1f21c85804d836a7bd4ad713c001d2b1` |
| Gate output canonical LF | `d68a7ef77ebe122a9aa3d0b6ca90b4077f08bb4cd15ddc967ebe1d37304138e1` |

输出 digest 使用 UTF-8 + canonical LF，并包含当前工作树 `Root` 行。

## 3. 当前实际证明

| 检查 | 结果 |
|---|---|
| 产品基线 | v0.4 历史 hash 与 v0.5 当前 hash passed；索引指向一致 |
| SPEC | S1 v0.6；S2 v0.5；S3-S5 v0.4；S6 v0.5；S7-S8 v0.3；S9 v0.4 |
| Test ID / Invariant | 275 个连续唯一 Test ID；133 个 Invariant 均结构化映射 |
| Trace | 32 FR；174 唯一 Test Ref；Coverage 9/8/15 |
| Micro contract | 10 场景、39 unique upstream refs、两个 58-byte Source |
| Suite artifact | 8 个 manifest artifact digest；3 个非空 protected seed；10 个 executable test methods |
| Privacy | suite 数据工件与权威 Markdown 启发式均未命中配置模式 |
| Architecture / Plan | ADR Accepted；Architecture baseline；Plan Approved；10 tasks pending |
| Development Gate | 产品问题 0；无业务源码、依赖、数据库实例或 business result；PRD diff=0 |

## 4. 诊断失败记录

- SPEC 修订首次校验 exit code 1：S6 产品基线单元格缺少明确 `PRD v0.5` 文本；修正元数据后通过。
- Suite 物化首次预检 exit code 1：runner 源码中的本地路径检测正则自匹配；数据工件扫描与 runner 运行时扫描分离后通过。
- Development Gate 校验器有 5 次未成功执行：StrictMode 空集合、补丁正则转义、Windows PowerShell 5.1 UTF-8 无 BOM 中文 token。最终改为显式数组、`[|]` 与 ASCII token 后通过。
- 上述均不是业务测试失败，也未被覆盖或描述为业务通过。

## 5. EOL 与可恢复性

- `.gitattributes` 当前固定 `*.md`、`*.ps1`、`*.py`、`*.json`、`*.yaml`、`*.yml`、`*.txt` 为 LF。
- manifest 按 raw file bytes 记录 artifact SHA-256，suite 预检已实际重算一致。
- `git diff --check` exit code 0。
- 2026-07-15 的全仓 LF/CRLF 隔离复验是历史证据，本轮未重复执行全仓双副本转换；不得把旧隔离 run 伪装成本轮执行。

## 6. 未证明

- `src/noetide_micro` 与 `noetide_micro.testing_adapter` 不存在。
- 没有执行 `tests.runner.run_micro_suite`，也没有 business result artifact。
- 未证明 L1 原子性、stale conflict、bitemporal query、L2 safe fallback、protected semantics 或 compensation。
- 未证明性能 SLO、权限 runtime、删除、迁移、MCP、同步或长期 portability。
- 当前验证只允许进入 TASK-001，不能声称产品或 Micro-MVP 已实现。
