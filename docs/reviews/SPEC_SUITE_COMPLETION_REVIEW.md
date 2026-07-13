# 九份 SPEC 完成审查报告

## 1. 审查信息

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-13 |
| 产品基线 | `PRDv04.md` v0.4 |
| PRD SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 审查对象 | S1-S9、OPEN_QUESTIONS、REQUIREMENTS_MATRIX、MICRO_MVP_ACCEPTANCE、PROJECT_STATE |
| 数据边界 | 只使用工作区文件与用户明确提供的两份 Fable5 评审附件；未扫描工作区外个人资料 |
| 实现状态 | 无业务代码、无数据库、无依赖安装 |
| 测试状态 | 合同测试已定义；未执行、未通过 |

## 2. 授权与门禁

产品负责人明确授权代理连续完成并审查全部九份 SPEC，无需逐份等待新的聊天确认。该授权只替代本轮逐份确认等待，不扩大为以下权限：

- 不修改 `PRDv04.md`。
- 不实现业务代码或数据库。
- 不导入真实数据。
- 不提前建设多租户、多 Agent、A2A、数字遗产、全连接器或多设备同步。
- 不把未执行测试描述为通过。

## 3. 恢复与失配审查

发现并处理两个中断造成的仓库失配：

1. 状态、README 和追踪矩阵曾声称 S3 草案存在，但仓库没有 S3 文件。现已创建 S3，并继续按顺序完成 S4-S9。
2. Fable5 的 S2 评审基于过期的 S1 v0.1/不完整 Micro 测试快照，错误声称 S1 未批准以及 `MM-008` 至 `MM-010` 不存在。仓库证据显示 S1 v0.2 已 Approved，且 Micro 文件已定义 MM-001 至 MM-010；因此未执行倒退修订。

Fable5 其余有效意见已纳入 S2 v0.2：移除 Schema 过程占位、统一 `object_revision`、明确 `lexical_locator`、CoverageWindow/Evidence Family 宿主与写入边界、verification scope 和 FR-205 范围。

## 4. SPEC 审查结论

| SPEC | 核心审查点 | 结论 |
|---|---|---|
| S1 Semantic Object Model | 12 对象闭包、三轴分离、Source/Canonical/View、Micro 六对象 | Approved v0.2 |
| S2 Bitemporal & Evidence | 四时间、半开区间、CoverageWindow、七维证据、六态回答 | Approved v0.2 |
| S3 ChangeSet & Consistency | 唯一写路径、全局 revision、L1/L2/L3、撤销/对账 | Approved v0.1 |
| S4 Privacy & Access Policy | 默认拒绝、舱室交集、sealed、删除/导出诚实性 | Approved v0.1 |
| S5 Shiling Policy | 单协调内核、候选/确认、Review Budget、Prompt injection | Approved v0.1 |
| S6 Semantic Test Harness | defined/executed/passed、fixture、oracle、trace、SLO | Approved v0.1 |
| S7 Storage, Index & Portability | 四逻辑层、Context Pack、round-trip、rebuild、未知字段 | Approved v0.1 |
| S8 MCP Contract | 最小能力、权限/revision/freshness、幂等、禁止 A2A 扩张 | Approved v0.1 |
| S9 Ingestion & Migration | Source-first、解析隔离、去重、quarantine、迁移回滚 | Approved v0.1 |

每份 SPEC 均包含 §0-§21，保留目标、非目标、术语、范围、字段、状态机、不变量、时间、证据、权限、冲突、失败、撤销、兼容、正反例、验收、未决和完成定义。

## 5. 产品裁决审查

- `BQ-001` 至 `BQ-005` 全部 decided。
- `IQ-001` 至 `IQ-018` 全部 decided。
- `DQ-001` 至 `DQ-010` 保持 deferred，并注明重开阶段。
- 任何 deferred 能力都没有被当前 SPEC 解释为 Micro/首年实现承诺。

关键保守裁决：

- Micro Core View 仅人物卡和关系时间线。
- `base_revision` 使用全局 Canonical revision；对象记录最后变化 revision。
- 撤销产生补偿 revision，不擦除历史。
- 多舱室取最严格交集，无法求交即 deny。
- 硬删除逐层回执，备份可 pending，外部副本明确 out of control。
- 私有完整导出与外部分享策略分离。
- 模糊时间不虚构精确日期；未知与无限严格分离。

## 6. 需求追踪审查

权威链路位于 `docs/traceability/REQUIREMENTS_MATRIX.md` §19：

```text
32 PRD FR
  -> 已批准 SPEC Section
  -> 已定义 Acceptance Test
  -> Implementation Module = TBD
  -> Verification Result = not_executed
```

该状态表示规范追踪完整，但实现验证尚未开始。

## 7. Micro-MVP 范围审查

Micro 仍只有一条合成链路：Source → contact State ChangeSet → 用户确认 → 原子发布 → 人物卡/关系时间线 → 历史保留 → protected semantics 不变 → 整包撤销 → View 一致。

未纳入 Micro：通用 NLP、模糊时间解析、实体消歧、提醒、Commitment、冲突来源、权限舱室运行时、MCP、连接器、同步、财务、健康、决策、真实迁移。

## 8. 残余风险与控制

| 风险 | 控制 |
|---|---|
| 规范被误当实现 | 所有 SPEC 明示实现未开始，所有 suite 未执行 |
| 后续技术选型反向改变语义 | 先立 ADR，ADR 不得覆盖 Approved SPEC |
| 长期 FR 诱发提前建设 | 追踪只定义边界，路线图 deferred 明确保留 |
| 删除承诺失真 | 分层 receipt、pending/out_of_control/partial failure |
| 权限旁路 | Derived 继承限制，错误/计数/摘要均不得泄露 |
| 外部评审基线过期 | 每次评审必须引用文件版本、hash 和 Git commit |
| 测试被误报 | HTH 三态、真实命令/exit code/artifact 门禁 |

## 9. 最终结论

九份 SPEC 的语义基线、产品裁决和 FR 追踪已经完成，可以进入 Micro-MVP 实现前的最小技术规划与 ADR 阶段。

这不是“产品已经开发完成”，也不是“测试已经通过”。在实现前仍需选择最小技术方案、建立真实测试运行器，并让 Micro-MVP 的全部 required test 实际执行通过。
