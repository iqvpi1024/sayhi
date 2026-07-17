# MVP-A Answer Safety Suite Materialization Plan

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-A-AS-SUITE-001` |
| Status | `Completed` |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Acceptance | `ACCEPT-MVP-A-AS-001` |
| ADR | `ADR-0002` |
| Business Code Authorized | `false` |

本计划只允许创建可执行测试工件，不允许实现 `answers.py`、修改业务 Schema 或让任何 A1 scenario 通过。

## 1. 目标工件

| Role | Planned Path | 要求 |
|---|---|---|
| manifest | `tests/answer_safety_suite_manifest.json` | 绑定 PRD/Decision/SPEC/ADR/Trace、35 required IDs、artifact hash |
| fixture | `tests/fixtures/answer_safety_v1/fixture.json` | 11 个独立合成 case、固定 Clock、Coverage、policy、initial digest |
| oracle | `tests/fixtures/answer_safety_v1/oracles.json` | AnswerEnvelope 字段级 expected、forbidden writes、result failure |
| scenario plan | `tests/integration/answer_safety_scenarios.json` | AS-001..011 动作和 exact upstream refs |
| adapter protocol | `tests/runner/answer_safety_adapter_protocol.py` | test-only Protocol；业务方法允许先抛 `NotImplementedError` |
| semantic tests | `tests/semantic/test_answer_safety_contract.py` | 恰好映射 AS-001..011，不读取实现生成 expected |
| offline runner | `tests/runner/run_answer_safety_suite.py` | 单 run 聚合、离线、不可覆盖 result、LF 输出 |
| validator | `tools/validate_answer_safety_suite.py` | hash、映射、隐私、AST/stdlib、状态四态；不执行业务 |

路径可在物化前因现有工具约束调整一次，但必须同步本计划、Acceptance 和 Matrix；不得用路径调整改变语义。

## 2. Manifest 合同

物化后初始状态必须为：

```yaml
suite_id: mvp_a_answer_safety_v1
slice_id: SLICE-MVP-A-ANSWER-SAFETY-001
suite_defined: true
suite_materialized: true
suite_executed: false
suite_passed: false
suite_artifact_state: materialized
latest_verification_result: not_executed
latest_run_applicability: not_applicable
required_scenario_ids: [AS-001..AS-011]
required_upstream_count: 24
required_result_count: 35
implementation_module: TBD
```

不得把既有 Micro pass 或定向 unittest 复制为 A1 result。

## 3. Fixture 合同

- 11 个 case 使用独立 initial database identity，禁止跨 case 状态泄漏。
- 使用中性 synthetic IDs，不包含真实人物/地址/组织/邮箱/电话/凭据等。
- Clock、timezone、locale、seed、ID strategy 固定。
- Source payload、byte length、hash、locator、CoverageWindow 全部可重算。
- viewpoint/reported/fictional/conflict/candidate 记录在 fixture 中分组，不能让 evaluator 读取 oracle。
- explicit freshness policy 只用于 stale case，包含 `policy_id`、window、evaluated_at；不声明产品默认。
- 每个 case 记录 pre-query Source/Canonical/Ledger/Projection digest oracle。

## 4. Oracle 合同

每个场景至少断言：

- exact `answer_status`、`answer_value`、scope/null。
- valid time、recorded_as_of、evaluated_at。
- direct evidence refs 或空集合。
- CoverageWindow/gap 和 stable reason codes。
- `data_revision` 与 pre-query 一致。
- 所有 forbidden layer digest 不变。
- 不出现 Derived evidence、Canonical unknown State、隐藏字段或真实数据。

AS-011 还必须注入 result output failure，证明不存在 current passed artifact。

## 5. Runner 合同

- Python 3.12 stdlib only；网络强制 blocked。
- 数据根为仓库内 `tmp/answer-safety-runs/<run_id>`。
- 业务时间只读 fixture Clock，运行 duration 使用 monotonic clock。
- 输出文件必须不存在，写入 UTF-8 LF；失败不覆盖历史 result。
- required skip/缺失为 partial；assertion mismatch 为 failed；runner/environment error 为 errored。
- result 绑定 git commit、manifest/fixture/oracle/implementation hash 和环境。
- 隐私模式命中使 run failed/errored，并最小化日志。

## 6. 物化任务

| Task | 内容 | 完成条件 | 状态 |
|---|---|---|---|
| `AS-PRE-001` | 创建 fixture/oracle | 11 case 完整、hash/locator/digest 可重算，synthetic scan 通过 | `completed` |
| `AS-PRE-002` | 创建 scenario plan + protocol | AS-001..011 与 Acceptance §7 exact mapping 一致 | `completed` |
| `AS-PRE-003` | 创建 semantic test module + runner | 测试可发现；缺实现时诚实失败/errored，不伪造 pass | `completed` |
| `AS-PRE-004` | 创建 manifest + validator | 8 类工件 raw hash 匹配，状态 materialized/not_executed | `completed` |
| `AS-PRE-005` | Suite Materialization Gate | Product/SPEC/Trace/ADR 静态通过；业务 tests 仍未执行 | `completed` |

## 7. 验证命令要求

物化任务必须记录真实命令和 exit code，至少包括：

```powershell
python .\tools\validate_answer_safety_suite.py
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
git diff --check
```

不得在物化阶段执行完整 A1 runner并声称业务失败/通过；允许做 test discovery 和 expected `NotImplementedError` 检查，但必须标为 bootstrap check。

## 8. 停止条件

- 任何 expected 不能从 Approved SPEC 唯一推导。
- 需要定义复合六态 precedence、默认 freshness 阈值或 world-claim verification rule。
- 需要权限 runtime、S5 model policy、MCP 或外部服务。
- 需要修改既有 Micro fixture/oracle 才能物化。
- 隐私扫描或路径约束失败。

出现以上任一项必须停止并回 Decision/SPEC，不得让测试代产品裁决。

## 9. 出口

`AS-PRE-001..005` 已全部完成，Suite Materialization Gate P0=0/P1=0。Implementation Plan 已经独立 Planning Gate 审查并改为 Approved；开发模型只能从 `CURRENT_HANDOFF` 指向的 `AS-TASK-001` 开始。
