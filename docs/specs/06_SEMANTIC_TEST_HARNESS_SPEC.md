# Semantic Test Harness SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-HTH-001` |
| 版本 | `0.1` |
| 状态 | `Approved` |
| 产品基线 | `PRDv04.md` v0.4 |
| 上游 | S1-S5 `Approved` |
| 产品裁决 | `IQ-014`，2026-07-13 已决定 |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_executed=false`、`suite_passed=false` |

本文定义如何证明 SPEC，不实现测试运行器、不选择测试框架，也不把文档场景当成已执行结果。

## 1. 目标

1. 统一 fixture、确定性时钟、输入、ChangeSet、预期 Canonical、View 和禁止变化 oracle。
2. 机器可检查地区分 defined、executed、passed。
3. 覆盖正常、反例、冲突、权限、失败、撤销、重放和迁移。
4. 建立 PRD→SPEC→Test→Module→Result 的可追踪结果合同。
5. 把 Micro-MVP 作为第一套必须实现的离线合成测试。

依据：PRD §6.14、§21-§23、§24、§26。

## 2. 非目标

- 不编写业务实现或测试运行器。
- 不选择语言、框架、CI、容器或基准硬件。
- 不用真实个人数据、外部网络或非确定性在线模型。
- 不要求 Micro 阶段实现 PRD 12 类长期场景全部业务。
- 不把静态审查称为实现测试通过。

## 3. 术语

| 术语 | 定义 |
|---|---|
| Fixture Pack | 初始状态、Source、动作、时钟、policy 和期望结果的版本化包 |
| Oracle | 可观察且确定的预期断言 |
| Forbidden Change Oracle | 必须保持语义/字节不变的路径集合 |
| Test Run | 某 suite/version 在明确环境中的一次执行 |
| Verification Result | `not_executed|passed|failed|errored|skipped_with_reason` |
| Reference Profile | 仅描述测量资源/数据规模的版本化环境，不锁供应商 |
| Golden QA | 查询输入、权限、时间、期望答案状态和证据的合成集合 |
| Semantic Replay | 从初始 revision 重放 Source/ChangeSet 并比较最终语义 |

## 4. 适用范围

适用于 S1-S9 的合同验收。Micro 首套只执行 `MM-001` 至 `MM-010`，并复用 SOM/BTE/CS/PAP/SHP 中与该链路相关的测试；其他测试保持 defined/not_executed 直到对应实现存在。

## 5. 对象与边界

- Test result 不是 Canonical 事实证据。
- Fixture Pack 只能含合成数据，不得从工作区外个人资料生成。
- Expected View 是 oracle，不得被实现反向读取形成实际结果。
- Golden QA 证明回答合同，不代替 ChangeSet 状态测试。
- Benchmark 证明特定 profile 下的表现，不是所有设备承诺。

## 6. 字段语义

### 6.1 Suite Manifest

```yaml
suite_id: stable ID
suite_version: version
spec_refs: [SPEC section]
prd_refs: [FR/NFR]
fixture_refs: [fixture pack]
suite_defined: true|false
suite_executed: true|false
suite_passed: true|false
```

`suite_passed=true` 仅在 `suite_executed=true` 且全部 required test 为 passed 时合法。

### 6.2 Fixture Pack

必须包含：`fixture_id`、schema/spec 版本、synthetic 声明、固定时钟、初始 Source/Canonical/View、权限 policy、动作序列、故障注入、期望 revision、期望 View、forbidden paths 和 cleanup scope。

### 6.3 Test Result

必须包含：`test_id`、suite/fixture/version、开始/结束、环境 profile、命令/runner ID、exit code、result、失败断言、实际/期望摘要、artifact refs 和数据隐私扫描结果。

### 6.4 Trace Row

```text
PRD Requirement -> SPEC Section -> Acceptance Test -> Implementation Module -> Verification Result
```

任何 `TBD` 必须显式；不存在模块时不得填虚构名称。

## 7. 状态机

```text
undefined -> defined
defined -> executing
executing -> passed | failed | errored
failed | errored -> executing (新 run_id)
defined -> superseded
passed -> superseded (SPEC/fixture/implementation 改变)
```

Manifest flags由最新适用 run 派生；历史 run 不覆盖。

## 8. 允许与禁止的状态转换

允许：修复实现后新 run；SPEC 变更使旧 pass superseded；不适用测试带批准原因 skipped。

禁止：defined 直接 passed；失败只改 flag；只运行子集却标完整 suite passed；在线模型漂移影响离线 Micro；删除失败产物；用真实数据提高“真实性”。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `HTH-INV-001` | 未执行永远不能 passed |
| `HTH-INV-002` | 每个结果绑定 SPEC/fixture/implementation/environment 版本 |
| `HTH-INV-003` | 所有 fixture 仅合成、离线、固定时钟 |
| `HTH-INV-004` | Expected 与 actual 数据源隔离 |
| `HTH-INV-005` | Forbidden paths 必须字段级检查 |
| `HTH-INV-006` | 失败、错误、跳过严格区分 |
| `HTH-INV-007` | 每条 required invariant 至少一个验收测试 |
| `HTH-INV-008` | 追踪链缺一环即不得声称需求已验证 |
| `HTH-INV-009` | SLO 结果只对声明的 Reference Profile 有效 |
| `HTH-INV-010` | 历史 run 与产物不被新结果覆盖 |

## 10. 时间语义

- 业务时间使用 fixture clock；运行计时使用单调测量时钟，两者分离。
- 经 `IQ-014` 裁决，SLO 起点为请求被本地核心接受，终点为满足合同的响应可供调用者读取；后台未完成项另记。
- 每个结果记录 wall time、monotonic duration 和时区。
- 超时是 failed/errored（按原因），不能当 skipped。

## 11. 证据语义

- Test artifact 是“实现是否满足合同”的证据，不是用户世界事实证据。
- 每个 pass 必须引用实际输出、断言和环境，不只记录布尔值。
- 截图/日志不能替代机器断言；可作为辅助 artifact。
- 重复运行不得掩盖 flaky，必须保留全部 run。

## 12. 权限要求

- Fixture policy 必须覆盖 allow、deny、redaction、sealed 和 destructive 场景。
- 测试产物不得包含真实密钥、令牌、路径外数据或敏感正文。
- 失败日志也执行隐私扫描和最小披露。

## 13. 冲突行为

- SPEC 与测试冲突时先修正/裁决 SPEC，不改 oracle 迎合实现。
- 同一测试在不同 profile 结果不同，分别记录，不选“漂亮结果”。
- Golden QA 与状态测试不一致时 suite failed 并保留两类 artifact。

## 14. 失败与降级

| 失败 | 行为 |
|---|---|
| runner 不存在 | not_executed，不称 pass |
| dependency 缺失 | errored，记录环境 |
| assertion 失败 | failed，保留 diff |
| artifact 写失败 | run errored，不发布 pass |
| privacy scan 失败 | failed 并隔离 artifact |
| flaky | failed/quarantined，不计 required pass |
| benchmark profile 不匹配 | skipped_with_reason，不外推 SLO |

## 15. 撤销与审计

- Test result 不可原地改写；纠错创建 amendment 或新 run。
- 保留命令、exit code、时间、版本、artifact digest 和 actor。
- 删除敏感误产物时保留无正文的隔离/删除证明。

## 16. 兼容与迁移

- Fixture 和 result 带 schema version。
- 未知字段语义保留；未知 required enum fail closed。
- SPEC 版本变化必须显式声明测试是否仍适用。
- Runner 升级先重跑基准 suite，不复用旧 pass。

## 17. 正例

Micro fixture 固定 `now`，执行确认、原子发布、两个 View、历史查询、protected paths 和整包撤销；输出实际命令、exit code、每条断言及 artifact digest。

## 18. 反例

- 只创建 Markdown 场景就把 `suite_passed` 改 true。
- 只测人物卡而把整个 Micro suite 标 passed。
- 测试从实现导出的 current 值同时生成 expected 值。
- 使用在线真实账号或个人聊天作为 fixture。

## 19. 可执行验收测试

```yaml
suite_id: semantic_harness_contract_v0_1
suite_defined: true
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `HTH-AT-001` | defined 未执行 | passed=false |
| `HTH-AT-002` | required 全 pass | suite passed=true |
| `HTH-AT-003` | 一项 failed | suite failed |
| `HTH-AT-004` | runner error | errored != failed |
| `HTH-AT-005` | skipped 无原因 | 拒绝结果 |
| `HTH-AT-006` | fixture 读取机器当前业务时间 | 拒绝非确定性 |
| `HTH-AT-007` | fixture 含外部网络 | 拒绝 Micro run |
| `HTH-AT-008` | fixture 隐私扫描 | 仅合成数据 |
| `HTH-AT-009` | expected/actual 同源 | 拒绝 oracle |
| `HTH-AT-010` | forbidden path 改变 | test failed |
| `HTH-AT-011` | revision/View mismatch | test failed |
| `HTH-AT-012` | 撤销历史被擦除 | test failed |
| `HTH-AT-013` | trace row 缺 module/result | requirement unverified |
| `HTH-AT-014` | 未实现模块 | 显式 TBD/not_executed |
| `HTH-AT-015` | SLO 在 reference profile | 记录边界与 profile |
| `HTH-AT-016` | profile 不匹配 | 不外推结论 |
| `HTH-AT-017` | SPEC 升版 | 旧 pass superseded |
| `HTH-AT-018` | 重跑失败 suite | 新 run，旧结果保留 |
| `HTH-AT-019` | artifact 写失败 | 不发布 pass |
| `HTH-AT-020` | 失败日志含敏感模式 | 隔离并 fail |

不变量覆盖：001→AT001-003；002→015/017；003→006-008；004→009；005→010-012；006→003-005；007→静态映射；008→013/014；009→015/016；010→017/018。

## 20. 未决问题

本 SPEC 无 blocking open question。`IQ-014` 已决定：SLO 使用版本化 Reference Profile 与明确计时边界；具体硬件/OS/运行器由后续 ADR 记录，不进入产品语义。真实 CI、runner 和 artifact 存储待实现阶段选择。

## 21. 完成定义

- 三态测试、fixture、result、trace、SLO 和隐私合同完整。
- 10 条不变量、20 个测试有映射。
- Micro suite 被指定为首套 required，但仍未执行。
- 未选择测试框架；没有伪造 Implementation Module。

当前结论：本 SPEC v0.1 经整体授权于 2026-07-13 标记 `Approved`。允许进入 S7；所有 suite 仍是未执行、未通过。
