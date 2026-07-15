# PRD v0.5 与九份 SPEC 兼容复审

## 1. 审查结论

当前结论：`yes`。

九份 SPEC 已按 S1→S9 完成正文级兼容复核和最小升版；没有发现需要修改 PRD v0.5 或新增产品裁决的 P0/P1。当前工作树静态校验、LF/CRLF 隔离复验、追踪检查和隐私启发式均已实际通过。业务 suite 仍未物化、未执行、未通过。

Finding 计数：P0=0、P1=0、P2=0；P3=1（`MMF-017` 已接受并按切片偿还，不阻止 Micro）。

## 2. 审查基线

| 字段 | 值 |
|---|---|
| 当前产品基线 | `PRDv05.md` v0.5，`Approved Product Baseline` |
| canonical LF SHA-256 | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 历史只读基线 | `PRDv04.md` v0.4，hash `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 当前切片 | `SLICE-MICRO-RELATIONSHIP-001` |
| 审查日期 | 2026-07-15 |
| 实现/ADR/计划 | 均不存在；本轮未创建 |

审查依据：PRD v0.5 §6、§8-§12、§17、§19-§22、§24、§27；`OPEN_QUESTIONS.md`；多模型 Finding `MMF-009..015/017`；S1-S9 原 Approved 正文。

## 3. 逐份结论

| SPEC | 旧版 -> 当前版 | 结论 | 最小修订 | PRD 依据 |
|---|---|---|---|---|
| S1 Semantic Object Model | v0.4 -> v0.5 | `compatible_after_revision` | Source Append/Intake 状态统一为 `received|validating|stored|duplicate|rejected`；移除 v0.4 五态兼容措辞 | §8、§9.4、§11.1、FR-002/004 |
| S2 Bitemporal & Evidence | v0.3 -> v0.4 | `compatible_after_revision` | `DQ-012` 未重开前，Canonical `value=unknown` 的实际状态查询保守返回 Answer `unknown` | §9.4、§27.1 |
| S3 ChangeSet & Consistency | v0.3 -> v0.4 | `compatible_after_revision` | `unarchive|unseal|restore` 成为显式 proposal operation，不与 correct/整包 revert 混用 | §11、§12.3-§12.4 |
| S4 Privacy & Access Policy | v0.3 -> v0.4 | `compatible_after_revision` | Access action 与 S3 隐私生命周期 operation 一一映射 | §12.4、§17 |
| S5 Shiling Policy | v0.3 -> v0.4 | `compatible_after_revision` | `DQ-011` 未重开前，automatic 仅允许确定性非语义 Source receipt 元数据 | §11.4、§14-§15、§27.1 |
| S6 Semantic Test Harness | v0.3 -> v0.4 | `compatible` | 明确 defined/materialized/executed/passed 四态；保留 result/applicability 分轴 | §22.1 |
| S7 Storage, Index & Portability | v0.2 -> v0.3 | `compatible` | 仅更新产品/上游基线；Pack、删除、双导出和 unknown extension 合同无需改义 | §12.4、§17.5、§21.4 |
| S8 MCP Contract | v0.2 -> v0.3 | `compatible_after_revision` | 所有非 verified Answer 禁止驱动不可逆动作；denied 响应采用唯一 disclosure profile | §10.2、§19.3、§27.1 |
| S9 Ingestion & Migration | v0.3 -> v0.4 | `compatible_after_revision` | AppendReceipt 与 S1 对齐；多 ChangeSet 部分应用后必须补偿并保留 rollback_failed | §19.4、§22.4、§25.2 |

## 4. Finding 关闭性

| Finding | 本轮处置 | 当前状态 |
|---|---|---|
| `MMF-009` | S8 明确 `unconfirmed|disputed|not_covered|stale|unknown` 全部不能驱动不可逆动作 | `closed_by_spec` |
| `MMF-010` | denied 响应固定 revision/freshness/answer/missing/payload=`withheld`、evidence=[]、receipt=null | `closed_by_spec` |
| `MMF-011` | S1/S9 共用 Source append 生命周期，AppendReceipt 只使用终态子集 | `closed_by_spec` |
| `MMF-012` | S9 增加部分已发布 migration 的 failed→rolling_back→rolled_back/rollback_failed 路径 | `closed_by_spec` |
| `MMF-013` | S3/S4 固定 unarchive/unseal/restore 一一映射 | `closed_by_spec` |
| `MMF-014` | `DQ-011` 保持 deferred；S5 只规定重开前最保守行为 | `closed_by_queue_and_guardrail` |
| `MMF-015` | `DQ-012` 保持 deferred；S2 只规定重开前最保守行为 | `closed_by_queue_and_guardrail` |
| `MMF-017` | 不一次性物化全部长期合同；继续按切片物化 exact required 集 | `accepted_p3_debt` |

Finding 关闭不表示对应业务功能已实现或测试通过。

## 5. Micro 影响

- Micro 仍只有 `person_card` 与 `relationship_timeline` 两个 Core View。
- `MM-001..010` 和 39 个去重 upstream required Test Ref 保持不变。
- 新增的 S1/S2/S3/S4/S5/S9 长期验收 ID 不自动进入 Micro required 集。
- 权限 runtime、MCP runtime、迁移、连接器、同步、财务、健康、决策、多 Agent、A2A 和数字遗产仍在范围外。

## 6. 测试与门禁

```yaml
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
business_verification: not_executed
```

静态校验只能证明文档结构、引用、枚举、hash、隐私启发式和 EOL 可移植性；不能证明原子发布、权限隔离、撤销、删除、迁移回滚或性能行为。

实际验证：

| 检查 | 命令/结果 |
|---|---|
| 产品基线 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1`；exit code 0 |
| SPEC 基线 | `powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1`；exit code 0 |
| SPEC 结构 | 275 个连续唯一 Test ID；133 个 Invariant 均映射到存在的测试 |
| 追踪 | 32 个 FR；174 个唯一 Test Ref 全部可解析；Coverage Level 仍为 9/8/15 |
| 闭集 | 20 个机器可读正向枚举通过 |
| Micro | `MM-001..010`；39 个去重 required upstream tests，集合未扩张 |
| 隐私 | 42 份权威合同/测试文件未命中配置的 phone/email/local-user-path 启发式 |
| LF/CRLF | 产品与 SPEC 校验器在两个隔离副本均 exit code 0；同类输出 digest 一致 |

详细环境、校验器 hash、输出 digest 和中间诊断失败见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

## 7. 下一步唯一动作

当前切片恢复 `traceable`。下一步唯一动作是单独启动仅服务于 `SLICE-MICRO-RELATIONSHIP-001` 的最小 ADR；不得直接编码，也不得选择长期数据库平台。
