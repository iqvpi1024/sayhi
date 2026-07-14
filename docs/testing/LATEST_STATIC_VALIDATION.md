# 最近静态验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-14 |
| 分支 | `codex/micro-gate-corrective-revision` |
| 命令 | `& .\tools\validate_spec_baseline.ps1` |
| PowerShell / OS | `5.1.26100.8655` / `Microsoft Windows NT 10.0.26200.0` |
| 当前工作树结果 | exit code `0`；`PASSED (static contract checks only; no business test was executed)` |
| LF/CRLF 可移植性 | 两个隔离副本 exit code 均为 `0`；去除临时 Root 行后的输出完全一致 |
| 校验器 SHA-256 | `0ce3e134fe674ead48573c727de08720885df9c55da6a8a2f43b075943706d9e` |
| 当前工作树输出 digest | `cc5e3d5cd478c631dd14698842dbf2efef96475aed25d99d699ca665fb02bbb0` |
| LF/CRLF 共同输出 digest | `d0ea0400b123c49b11c112dbc2f39f30880ecd2927d5796c208210ffd2dd30d3` |
| Git 绑定 | 最终提交由 tag `micro-gate-corrective-v0.1-validated` 绑定；tag 创建后复跑同一命令 |
| 范围 | PRD/SPEC/追踪/Micro/权威测试与决策文档的静态合同检查 |
| 业务测试 | `not_executed` |

本文件只记录校验器实际执行的检查。`docs/reviews` 中的审计环境元数据不属于合成 fixture/合同隐私扫描语料；其内容由审计保存流程单独控制。

## 2. 校验器检查项

- PRD 按 UTF-8 + canonical LF 计算 SHA-256，checkout 的 CRLF/LF 不改变产品基线判定。
- `.gitattributes` 明确 Markdown、PowerShell、YAML 等文本的 EOL policy。
- 9 份 SPEC 的 §0-§21、版本、Approved 状态和四个 suite flag。
- SPEC Test ID 连续/唯一，以及 invariant 在 §19 结构化映射到存在的本套 Test ID。
- `MM-001..010`、两个合成 Source 的 UTF-8 hash/byte locator，以及 exact required upstream mapping。
- 32 条 PRD FR、Coverage Level 和矩阵 Test Ref。
- 12 个跨规范封闭枚举的正向值集合，并保留已知 alias/conflation 反向检查。
- 对 PRD、SPEC、testing、traceability、decisions 和 PROJECT_STATE 执行 phone-like、email-like、本机 user-directory path 启发式扫描。
- 全仓 Markdown fence parity。

## 3. 本次结果

| 检查 | 结果 |
|---|---|
| PRD canonical LF hash / EOL policy | passed |
| SPEC Test ID | passed：269 个连续且唯一 |
| Invariant mapping | passed：128 条均结构化映射到存在的本套 Test ID |
| Micro | passed：10 个场景、两个 58-byte Source、39 个去重 required upstream tests |
| FR / Matrix | passed：32 条 FR、9/8/15 Coverage Level、168 个 Test Ref |
| Closed enum | passed：12 个正向值集合 |
| Privacy heuristic | passed：17 份权威合同/测试文件未命中配置模式 |
| Markdown fence | passed：24 个 Markdown 文件成对 |
| 业务合同 | `not_executed` |

## 4. 未证明

- 没有机器 suite manifest、fixture artifact、runner 或 Implementation Module。
- 所有 suite 仍为 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。
- 静态检查不能证明业务原子性、权限隔离、撤销、删除或性能 SLO。
- 隐私启发式不是法律或取证级证明；它只证明声明语料中未命中配置模式。

本文件可以证明上述静态检查在声明环境和 EOL 条件下通过；不得引用它证明任何业务合同通过。
