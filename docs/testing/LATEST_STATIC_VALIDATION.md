# 最近静态与规划门禁验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-17 17:53:47 +08:00 |
| 分支 | `codex/mvp-a-answer-safety-planning` |
| 起始 HEAD | `264d975271f91f1118238f78fa8fb37303e8caa0` + 当前未提交交接规划工作树 |
| Product 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` |
| SPEC 命令 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1` |
| Micro artifact 命令 | `python .\tools\validate_micro_suite.py` |
| Diff 命令 | `git diff --check` |
| PowerShell / OS | Windows PowerShell `5.1.26100.8875`；host `7.6.3`；`Windows-11-10.0.26200-SP0` |
| Runtime | Python `3.12.8`；SQLite `3.45.3`；stdlib only |
| Product 最终结果 | exit code `0`；产品基线静态检查通过 |
| SPEC 最终结果 | exit code `0`；SPEC、主 Matrix 和既有 Micro 静态合同检查通过 |
| Micro artifact 结果 | exit code `0`；既有 manifest/artifact/hash 检查通过；未执行业务 runner |
| Diff 结果 | exit code `0` |
| A1 Business Verification | `not_executed` |

## 2. 本轮机器核对

| 检查 | 真实结果 |
|---|---|
| Product baseline | PRD v0.4 immutable hash 与 PRD v0.5 current hash 均匹配；32 FR、12 核心对象和 DQ-001..013 队列通过 |
| SPEC baseline | 275 个 Test ID、133 个 Invariant、20 个 closed enum、32 条权威 FR 主表、64 个隐私扫描文件和 83 个 Markdown fence 文件通过 |
| Matrix refs | 185 个唯一 Test Ref 可解析；长期 Coverage 仍为 9/8/15 |
| A1 exact mapping | 按 Matrix 简写规则展开后，Acceptance 与 Matrix 均为 11 个 `AS-*`、24 个唯一 upstream refs，集合差异为 0；共 35 个 required result IDs，exit code `0` |
| A1 artifact state | Acceptance 已定义；manifest/fixture/oracle/runner 不存在，`suite_materialized=false` |
| A1 phase | SPEC applicability、Trace、ADR-0002、Architecture 和 Pre-Suite Gate 已闭合到 `architecture_decided` |
| Current handoff | 标准交接包 required fields 缺失数为 0；唯一下一动作为 `AS-PRE-001` |
| Role prompt pack | Suite Materializer、Planning Gate、Implementer、Verifier、Auditor、Debugger、Re-auditor、Recovery Releaser、Public Releaser 共 9 类角色，缺失数为 0 |
| Protected paths | `git diff --name-only -- PRDv04.md PRDv05.md docs/specs src tests/fixtures tests/integration tests/runner tests/semantic` 返回 0 项 |
| Privacy/scope | 新增 A1 文档只使用中性 synthetic ID；Product/SPEC privacy heuristic 通过；未读取工作区外个人资料 |
| Git hygiene | `git diff --check` exit code `0`；`.workbuddy/` 与 `Review-report/` 不在交付范围 |

## 3. Digest

| 产物 | SHA-256 |
|---|---|
| Product validator | `a596ede5e91f493b9836795902ecf653605f4c9d050ea0ff95b23110e25820a2` |
| SPEC validator | `df7e719675acaf6314b4222b85082fe1cd88fedc71adb087e2364446e06720dc` |
| Micro artifact validator | `667358517066d0997a732777dbb98a30738d0d75373a60b6928fa7fc50020e96` |
| A1 Acceptance（当前工作树） | `e0ea00cd6919651d6bcdaf5129d38d9370921f0c64bcea6f7391462d82081ce1` |
| Micro manifest（validator 输出） | `b6e71a2fb4ca3c7f7c8e54a60ae6f8a1cd18808013f472d2fde2fe6a93ae58d6` |
| Current Handoff（当前工作树） | `a6ca0f051e9eba27de0c9c965252dba0bdd851595f3e90e639d690bf79dcd83c` |
| AI Execution Prompts（当前工作树） | `b2d0b0b8c2a8d5f41db065e2099d40143902e29946fd9db5651d338772f776fe` |

## 4. 诊断与修正记录

1. 本轮第一次运行 SPEC validator 时 exit code `1`，唯一错误为 `Authoritative matrix rows do not match the 32 PRD FR IDs`。原因是旧校验器把 A1 active-slice 子表中三个无代码标记的 FR 单元格计为第二套权威主表行。
2. 修正只把 A1 子表的 `FR-002/008/010` 单元格改为 Markdown code identifiers；没有改变 FR、SPEC、Test Ref 或验证状态。复跑 SPEC validator exit code `0`。
3. 环境探测第一次读取 Windows PowerShell 版本时因外层变量展开产生 parser error；使用单引号重新执行后得到 `5.1.26100.8875`。该失败不属于产品、SPEC 或业务测试。
4. 第一次附加比对脚本没有展开 `AS-001/002`、`BTE-AT-012/013` 简写，因此产生错误集合差异；按 Matrix §1 的简写规则展开后，Acceptance/Matrix 场景数均为 11、upstream refs 均为 24，两个集合差异均为 0。
5. Windows sandbox 登录会话曾连续三轮使 `apply_patch` 返回 helper error；未使用替代写入方式。用户恢复 unrestricted permission 后，所有本文档变更均重新通过 `apply_patch` 完成。

失败尝试被保留在本记录中，不被最终通过覆盖或描述为业务失败。

## 5. 上一 Micro 证据边界

- `docs/testing/results/micro-task009-lf-20260717.json` 继续记录提交 `195a8fb2dfe3716c1f97a19edd8d7ec5c34d80de` 上 49/49 required IDs passed。
- 本轮只重新运行 `validate_micro_suite.py` 验证既有工件、hash 与隐私边界，没有重新运行 `tests.runner.run_micro_suite`。
- 本轮只改规划文档，未改 `src/noetide_micro` 或 Micro suite 工件，因此旧业务结果未被改写；未来 A1 修改共享实现后必须产生新的 Micro regression run。

## 6. 未证明

- A1 manifest、fixture、oracle、adapter protocol、semantic tests 和 runner 尚不存在。
- A1 35 个 required result IDs 全部 `not_executed`；没有 A1 business result artifact。
- 未证明 A1 六态 evaluator、Coverage 集成、冲突并列、只读 digest 或 result failure 行为。
- 未证明 UI、API、权限 runtime、MCP、导出、迁移、安装包或一键部署。
- 当前验证只允许从 `AS-PRE-001` 开始物化 suite，不允许执行 `AS-TASK-*`。
