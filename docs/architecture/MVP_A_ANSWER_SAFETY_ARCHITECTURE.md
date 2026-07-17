# MVP-A Answer Safety Architecture View

## 0. 元数据

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-MVP-A-AS-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Product | `PRDv05.md` v0.5 |
| Decision | `DEC-MVP-A-AS-001` |
| ADR | `ADR-0002` |
| Verification | `not_executed` |

## 1. 组件职责

| Component | 责任 | 禁止责任 |
|---|---|---|
| `AnswerFixtureLoader` | 加载固定合成 case、Clock、Coverage、policy | 不读取工作区外数据，不生成 expected |
| `SemanticStore` | seed Source/Canonical/Coverage，提供只读 snapshot/digest | 不在 trigger 中判断 Answer Status |
| `EvidenceSelector` | 只选择授权直接 Source Evidence，排除 Derived | 不判断权限 runtime，不补造 locator |
| `CoverageEvaluator` | 计算目标 valid scope 的 window/gap 充分性 | 不把零结果当未发生 |
| `ConflictDetector` | 比较 subject/predicate/time/perspective/value | 不自动选胜者或写裁决 |
| `AnswerEvaluator` | 按固定 case 合同生成 AnswerEnvelope | 不写 Canonical/Ledger/View，不调用模型 |
| `AnswerTestingAdapter` | 暴露 test-only 查询、snapshot 和 failure injection | 不成为产品 API |
| `AnswerSuiteRunner` | 执行 AS-001..011、聚合 35 required IDs、保存 result | 不读取实现生成 expected，不拼接跨 run pass |

## 2. 数据流

```text
versioned synthetic fixture
  -> Source + Canonical Assertion + CoverageWindow seed
  -> authorized EvidenceSelector
  -> CoverageEvaluator + ConflictDetector
  -> AnswerEvaluator
  -> AnswerEnvelope actual
  -> independent oracle compare
  -> immutable Verification Result
```

AnswerEnvelope、EvidenceAssessment 和运行结果均不得回写为事实 Evidence。

## 3. 读取屏障与只读证明

每个 case 开始前记录：

- `data_revision`。
- Canonical payload digest。
- Ledger row count/digest。
- Source row count/digest。
- Projection row count/digest。

查询结束和重复执行后逐项比较。任何差异使 `AS-INV-008` 失败；即使 Answer Status 正确也不能通过。

## 4. 六态 case 隔离

每个 case 使用独立数据库和 mutually isolated fixture profile：

- `verified`：只查询 confirmed viewpoint 或 statement occurrence scope。
- `unconfirmed`：有未审 candidate，无 confirmed world claim。
- `disputed`：同 scope 的不兼容直接证据，时间重叠。
- `not_covered`：目标时间在 coverage 外或 continuity unknown 的否定查询。
- `stale`：显式 policy 下唯一证据超期。
- `unknown`：覆盖充分、无 candidate/conflict/verification/freshness failure。

本切片不组合多个主状态条件，不由实现发明全局 precedence。

## 5. 失败边界

| Failure Point | 安全结果 |
|---|---|
| fixture seed failure | 无部分 seed；case errored/failed |
| invalid direct evidence | 不 verified；明确 invalid assessment |
| Derived-only evidence | unknown + forbidden reason；Canonical 不变 |
| policy/clock missing | case 初始化失败，不读墙钟补值 |
| result write failure | 无 current passed artifact |
| network attempt | suite failed |
| shared-store regression | A1/Micro Gate closed，保留失败结果 |

## 6. 排除范围

无 UI、API、MCP、权限 runtime、Shiling candidate generation、冲突裁决、ChangeSet 写入、第三个 View、Context Pack、安装包或部署脚本。

## 7. 当前证据状态

- A1 manifest/fixture/oracle/runner 已物化并通过静态 validator；这只证明工件结构可运行。
- A1 业务测试 `not_executed`。
- Implementation Plan/Task Cards 已通过独立开发前 Gate；下一步只允许执行 `AS-TASK-001`，Architecture Accepted 或 suite materialized 均不表示业务通过。
