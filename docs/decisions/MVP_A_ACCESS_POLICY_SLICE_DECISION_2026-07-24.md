# MVP-A 查询层权限与舱室强制执行切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-A-ACCESS-POLICY-001` |
| Date | 2026-07-24 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-A-ENTITY-MERGE-001`（已发布 recovery point `a3-entity-merge-rp-20260724`） |
| Current Slice | `SLICE-MVP-A-ACCESS-POLICY-001`（A4） |

## 1. 决定内容

选择 MVP-A 的 A4 作为下一条窄切片：只证明一个固定合成的单用户本地调用者在字段、舱室、目的和时间约束下被查询层强制执行——无权时少回答并显式拒绝，绝不跨舱室猜测。

顺序理由：按路线图 MVP-A 顺序 A1→A2→A3→A4；前三者均已 verified；A4 是 A5（最小可用应用壳）之前的最后一个核心安全行为，且其查询层复用 A1 已验证的 AnswerEnvelope 语义。

## 2. 产品依据

- PRD §20 FR-012：权限和舱室在查询层强制执行。
- PRD §10 原则 10：隐私先于便利；无权限时系统应少回答，而不是跨舱室猜测。
- PRD §17.2：舱室是访问控制与上下文编译的策略边界；一条记录可属多域，策略取最严格交集——字段 allow 取交集、deny 取并集，无法安全求交时默认拒绝。
- PRD §17.4：权限按身份、目的、舱室、字段、时间和动作综合判断。
- PRD §19：工具响应必须包含权限判定；无权限或证据不足时必须拒绝或降级。
- PRD §26 验收 8：Restricted 字段权限过滤；§26 指标：权限泄漏事件数。

## 3. 切片范围

- 单一固定合成 profile：一个本地调用者身份、若干带 compartments/sensitivity 的合成对象（entity/assertion/state）、一组显式权限策略（字段 allow/deny、舱室、目的、时间约束）。
- 查询层判决器：对固定合成查询按身份+目的+舱室+字段+时间求值，返回 `allowed`（含过滤后字段集）或 `denied`（含拒绝原因码）；拒绝时不返回任何被拒字段的内容或侧信道提示。
- 多舱室对象按 PRD §17.2 取最严格交集；allow 交集、deny 并集；无法安全求交默认拒绝。
- 复用 A1 AnswerEnvelope 六态语义表达"无权回答"的降级，不重复实现六态。

## 4. 非目标

- 多用户、家庭授权、托管人、数字遗产工作流（`DQ-004`/`DQ-009` 保持 deferred）。
- sealed 内容紧急访问与恢复策略（`DQ-003` 保持 deferred）。
- 外部 Agent runtime、MCP runtime、专业 Agent 权限模板（FR-304，后置）。
- 权限策略的管理 UI、策略编辑器、自然语言策略。
- 真实个人数据。

## 5. 不变量

- 判决只在查询层发生；判决过程不产生任何 Canonical revision 或写入。
- 拒绝响应不得泄露被拒字段的内容、存在性侧信道超出合同允许范围。
- 多策略冲突默认拒绝；未知身份、未知目的、未知舱室、策略缺失均 fail closed。
- 权限判决不得修改 trust、closeness、人格判断或任何 Canonical 对象。
- Derived View 内容不得作为权限证据绕过判决。

## 6. 授权与下一步

本决定只授权 S1/S3/S4/S6 的 A4 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 A4 业务代码。`DQ-003`、`DQ-004`、`DQ-009` 保持 deferred，不在本切片重开。
