# DEC-MVP-A-AS-001：下一切片选择回答安全

## 1. 决定信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-A-AS-001` |
| Status | `decided` |
| Date | 2026-07-17 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Selected Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Delivery Phase | `product_decided` |
| Product Owner Direction | 继续下一步；先完成全路线规划和文档，再交由其他模型开发、审计与 Debug |

本决定选择已批准 MVP-A 范围内的下一条施工切片，不新增 FR、不修改 PRD，也不授权业务编码。

## 2. 比较方案

| Option | 内容 | 优点 | 当前问题 | 结论 |
|---|---|---|---|---|
| A | 六态 AnswerEnvelope + 最小冲突呈现 | 补齐可信回答核心；只读、合成、可确定测试；复用 Micro 存储 | 需复核 S1/S2/S6/S7 applicability | `selected` |
| B | 第三个 `current_state` Core View | 扩展 MVP-A View | 若 Answer Status 未稳定，View 会固化错误回答边界 | 后置 A2 |
| C | Entity merge/split | 覆盖 FR-011 | 引用重定向与补偿面更大，依赖安全回答 | 后置 A3 |
| D | 权限 runtime | 高价值 | 会重开 Privacy 产品问题并显著扩大失败/泄漏面 | 后置 A4 |
| E | 用户 UI/安装包 | 早期可见 | 当前测试适配器不是稳定产品接口，先做 UI 会反向固化实现 | 后置 A5/A6 |

## 3. 产品目标

对一个固定合成事实查询，系统必须基于授权可见的 Canonical evidence、CoverageWindow、review status、valid time 和显式 freshness requirement，返回且只返回六态之一：

```yaml
answer_status_values: [verified, unconfirmed, disputed, not_covered, stale, unknown]
```

六个状态分别由独立合成场景证明，不能通过同一个默认值或异常分支伪装。

## 4. 切片范围

包含：

- `AnswerEnvelope` 的固定查询入口和六态派生判定。
- viewpoint scope 下的 `verified`，不扩大为 world claim verified。
- 存在未审 candidate 时的 `unconfirmed`。
- 适用来源冲突时的 `disputed`，并列返回证据，不自动选值。
- CoverageWindow 不覆盖目标时间时的 `not_covered`。
- 显式 freshness policy 不满足时的 `stale`。
- 覆盖充分但无法安全判断时的 `unknown`，`answer_value=null`。
- Derived View/summary/receipt 不得作为事实 Evidence Ref。
- 所有场景固定 Clock、固定合成数据、离线执行。

不包含：

- 通用自然语言问答、LLM、搜索排序或 RAG。
- 用户冲突裁决、冲突修正 ChangeSet 或自动选取可信来源。
- Canonical `State.value=unknown`；因此 `DQ-012` 本切片不重开。
- 权限 runtime、sealed 内容、MCP、外部 Agent、连接器或迁移。
- 第三个 Core View、用户 UI、安装包或一键部署。

## 5. 产品不变量

1. `verified` 必须绑定明确 `verification_scope`；viewpoint 确认不能验证 world claim。
2. `not_covered` 与 `unknown` 严格区分：前者缺覆盖，后者有覆盖但无法判断。
3. `stale` 描述 evidence currentness，不等于 View freshness。
4. `disputed` 保留并列证据，不自动选择更顺眼的值。
5. 未确认 candidate 只能得到 `unconfirmed`，不能进入 Canonical fact。
6. Derived View 不反向作证。
7. 查询为只读；不得产生 Canonical revision 或修改 Micro 历史。
8. 无法唯一判定时 fail closed，不猜测隐藏或缺失内容。

## 6. 适用规范与候选测试

下一阶段必须逐份复核：

- S1 v0.6：Assertion kind、review status、Derived boundary。
- S2 v0.5：AnswerEnvelope、CoverageWindow、freshness、conflict。
- S3 v0.4：只读查询不得绕过 Canonical 写边界。
- S6 v0.5：新 suite 四态、fixture、oracle、result。
- S7 v0.3：当前 SQLite 表达与未来 portability 边界。

以下仅是 applicability review 候选，不是当前 required 权威集合：`SOM-AT-007/008/018/021`、`BTE-AT-012/020/024/025/026/030/034`、相关 `HTH-AT-*`。exact required 集必须在 Traceability 阶段唯一确定。

S4、S5、S8、S9 默认不进入实现范围；若 applicability review 发现必须依赖这些 SPEC，应先说明原因并重新审查切片是否扩张。

## 7. Deferred 问题处理

- `DQ-012` 不重开：本切片 unknown 由“覆盖充分但无法判断”产生，不写 Canonical unknown State。
- `DQ-003`、`DQ-004`、`DQ-007..010` 与当前切片无关，保持 deferred。
- `DQ-011` 在 MVP-B/FR-107 前重开；A1 不自动发布任何语义。
- 未发现当前切片 blocking 产品问题。

## 8. 门禁结论

Product Decision Gate：`yes`，仅允许进入 `SPEC applicability review`。

当前明确状态：

```yaml
product_decided: true
spec_approved_for_slice: false
traceable: false
architecture_decided: false
suite_defined: false
suite_materialized: false
suite_executed: false
suite_passed: false
implementation_planned: false
business_implementation: absent
```

## 9. 下一步唯一动作

对 S1/S2/S3/S6/S7 执行 `SLICE-MVP-A-ANSWER-SAFETY-001` applicability review；先证明现有合同是否足够，再决定保持版本或升版修订。
