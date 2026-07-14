# 多模型最终独立审计报告

## 1. 执行摘要

本轮按“先正文、后报告”完成独立审计。当前审查基线为 detached HEAD `15e3ff87cd4c773b637a3bab9fba0cb614eaff45`；该提交同时是 `main`/`origin/main` 当前指向。`PRDv04.md` 当前 checkout 的原始字节 SHA-256 为 `5B1C02A327F3CB8DC942571BF827B8062FA1589DDCFE09D55B1368CDBF0F6674`，LF 归一化后为项目记录的 `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC`。

核心语义架构没有需要推倒重来的 P0：Source/Canonical/Ledger/Derived 边界、双时态、EvidenceAssessment 派生边界、ChangeSet 原子发布、补偿撤销、seal/retention/retrieval 正交、MCP execution/answer/freshness 分轴等主体设计成立。

但是，当前基线不应直接进入 Micro-MVP 实现。独立复核确认 7 项 P1：正式产品门禁没有可复核批准记录；Source 策略字段无法由 Intake 唯一初始化；ChangeSet 发布前复检失败没有合法终态；MM-006 的历史证据 oracle 与 fixture 矛盾；MM-007 的 trust/closeness/personality 保护可平凡通过；最近静态验证在当前 checkout 实际失败且记录了脚本不存在的隐私扫描；S6 Verification Result 枚举不能形成唯一 runner schema。

因此本报告结论是：**no**。这里只是否定“按当前正式基线开始实现”，不否定继续做一个严格限于 P1 的规范修订。

完整逐项判定见 `docs/reviews/MULTI_MODEL_FINDINGS_LEDGER.md`。

## 2. 审查基线与报告可信度

待整合的四份外部报告中，只有 `doubao.txt` 写明审查 commit `b497c2c`。该提交是当前 HEAD 的直接祖先，之后只变更 `PROJECT_STATE.md` 的备份记录，因此其对 S1-S9/Micro/Matrix 的行级观察仍可对照。`deepseek.md`、`opus.txt`、`sol.txt` 均未注明审查 commit；`sol.txt` 还未注明日期和模型。三者只作为线索，所有采纳意见均已重新用当前 HEAD 证明。

文件名不能证明模型身份。本报告只使用 `DeepSeek/Doubao/Opus/sol` 作为来源标签，不把它们当作者事实。

## 3. 有效 Findings

### P0

无。

### P1：进入 Micro 实现前必须关闭

| ID | 结论 | 直接后果 | 最小方向 |
|---|---|---|---|
| `MMF-001` | PRD 仍是 Draft，§27.3 实现门禁没有 commit/hash 绑定的批准事件 | 无法证明已获开工授权 | 产品负责人显式批准或拒绝当前门禁 |
| `MMF-002` | S9 Intake 无法唯一产生 S4 要求及 Micro 期待的 Source policy/subject 字段 | Source 可能过宽暴露，或 append 被迫混入语义解析 | 定义保守默认、unknown、补充修订流程并修 fixture |
| `MMF-003` | `approved -> publishing` 前复检失败没有合法状态转换 | stale base/权限失效的状态、receipt、重试会分叉 | 补 preflight failure/conflict 终态或重定检查时点 |
| `MMF-004` | 旧 active State 是 missing evidence，MM-006 却要求旧查询返回 Source evidence | 诚实实现失败，错误证据绑定反而可通过 | 为旧状态补独立 Source，或明确返回 missing |
| `MMF-005` | protected trust/closeness/personality fixture 全为空 | 破坏既有判断的实现仍可通过 | 增加非空 opinion；personality 保护范围需显式决定 |
| `MMF-006` | 当前静态命令实际失败 38 项；隐私扫描不在脚本中 | `LATEST_STATIC_VALIDATION=PASSED` 不可复现 | 规范换行/hash、修 CRLF 正则、记录真实命令/artifact |
| `MMF-008` | S6 把 test/run/suite/superseded 结果混在不一致枚举中 | 无法稳定物化 Micro runner/result schema | 拆分四类状态枚举并统一 Matrix 语义 |

### P2：不阻止规范修订，但相关阶段前必须关闭

| ID | 结论 | 阶段 |
|---|---|---|
| `MMF-007` | invariant 覆盖正则可被无关三位数字满足；枚举检查只是 11 项历史黑名单 | Micro 静态门禁增强 |
| `MMF-009` | MCP 不可逆动作 gate 漏掉 `unconfirmed/disputed` | MCP runtime 前 |
| `MMF-010` | MCP denied 响应的 `withheld/not_applicable/[]` 枚举不一致 | MCP runtime 前 |
| `MMF-011` | S1 Source Append 与 S9 Intake/AppendReceipt 复用名称但状态集合不同 | duplicate ingestion 前 |
| `MMF-012` | Migration 多 ChangeSet 部分成功后没有合法 rollback 路径 | migration 前 |
| `MMF-013` | unseal/restore/unarchive 没有明确 ChangeSet operation 映射 | privacy mutate 前 |
| `MMF-014` | “预授权自动处理最大范围”未进入 OPEN_QUESTIONS 队列 | FR-107/MVP-B 前 |
| `MMF-015` | Canonical `value=unknown` 与 Answer `unknown/verified` 的组合未裁决 | 含 unknown State 的查询前 |
| `MMF-016` | “直接依赖的 Micro Test Ref”没有唯一 required 集合 | Micro manifest 物化时 |

### P3

`MMF-017`：257 个 SPEC Test ID 的 oracle 深度不一致。该债务已被 `suite_materialized=false` 诚实披露，不应在本轮一次性扩展成 257 项修订；按进入实现的阶段逐套物化。

## 4. 现有审计中的错误

1. `INDEPENDENT_BASELINE_AUDIT_2026-07-14.md:7-9` 的“所有可推导问题已修复、没有新增 blocking/important”结论过度。MMF-002、003、004、005、006、008 都能从当前仓库直接证明。
2. `LATEST_STATIC_VALIDATION.md:9-26` 与 `PROJECT_STATE.md:98-114` 的当前 `PASSED` 记录不可复现。同一命令在当前 HEAD 返回 38 个错误；报告还把脚本中不存在的隐私启发式扫描列为结果。
3. `deepseek.md` 把 proposal 级 `protected_paths` 视为必然错误、把不同 SPEC minor version 当问题，均缺乏语义依据；其“24/32 已规范、8 条 boundary”还与当前矩阵的 9/8/15 分布矛盾。
4. `doubao.txt` 声称 `risk_level` 枚举未定义，但 S3 与 S5 都明确写出 `low|medium|high|critical`；该意见是事实错误。
5. `opus.txt` 正确发现 invariant coverage 正则盲区，但把规范字段分层问题描述为唯一未闭合项，漏掉 Source 初始化、状态机和 Micro oracle 的直接矛盾。
6. `sol.txt` 虽未绑定 commit，仍准确指出 Source 初始化、preflight 状态、历史证据 oracle、migration rollback 与隐私逆向操作；这些意见是靠当前正文复核成立，而不是因其报告结论被采纳。

## 5. 被拒绝或已过期意见

- **给 Micro 增加权限 runtime/MM-011**：拒绝。PRD、Micro 和 Matrix 都明确把权限舱室 runtime 排除在当前链路外；这是范围扩张。Source 的 policy 初始化缺口应在现有 schema 边界内修，不等于建设权限引擎。
- **Evidence Family ID 未选物理算法阻止 Micro**：拒绝。S2 已明确它是 Derived 并后置 S7/ADR；Micro 只有一个 Source。
- **把 `protected_paths` 强制提升为 ChangeSet 字段**：拒绝。proposal 级约束可以在发布时取 union/整包检查；仓库没有证据证明字段必须换层。
- **S1/S2 v0.3 与 S3-S9 v0.2 必须齐步**：拒绝。独立版本号不是语义缺陷。
- **Micro fixture 携带 S4 字段等于实现 policy engine**：拒绝。携带上游边界字段不等于启用运行时功能。
- **PRD 十种 Assertion、五态措辞、SPEC 顺序仍是未裁决缺陷**：已过期。BQ-002、IQ-016 已给出当前规范解释；不得在本轮借维护便利修改 PRD hash。
- **历史 root 报告的 34 条 FR、删除撤销/关系时间线以缩小 Micro**：错误或已过期。当前是 32 条 FR；IQ-001、IQ-008 已决定保留两个 View 与补偿撤销。
- **`HTH` 缩写、自载 Approved 状态**：风格偏好，不升级为语义缺陷。

## 6. 报告之间的真正分歧

| 分歧 | 报告立场 | 本审计裁决 |
|---|---|---|
| 是否存在 P1 | Doubao/Opus：0；DeepSeek：4；sol：5 | 当前正文证明 7 个 P1；不采票数 |
| S1/S4 字段接缝 | DeepSeek=P1，Opus=P2，Doubao未列，sol聚焦 Source 初始化 | 广义“字段分层”只属维护问题；无法从 Intake 产生 expected Source 是具体 P1 |
| 是否扩张 Micro 权限 | Doubao/sol 建议最小 deny；DeepSeek/Opus接受排除 | 拒绝扩张；只修 Source 初始化与现有字段 oracle |
| `value=unknown` 如何回答 | DeepSeek要求产品裁决；其他报告认为无缺口 | 确为非 Micro 产品选择，列 MMF-015/P2 |
| `protected_paths` 归属 | DeepSeek要求 ChangeSet 级；其他报告接受 proposal 级 | 不存在唯一产品推导，拒绝强制迁移 |
| 是否可开始实现 | 三份长报告均 yes with conditions；sol 不建议直接开始 | 因当前 static gate 失败且 Micro oracle 矛盾，当前结论为 no |

## 7. 尚需产品负责人裁决

1. **当前门禁批准**：是否正式批准 PRD v0.4 及 §27.3 六项门禁，并授权进入 Micro 实现。必须绑定当前 commit 与 PRD hash。
2. **Personality protected oracle**：Micro 只验证“不新增人格判断”，还是允许加入一个只读既有 Hypothesis 以验证“不修改”。后者会触及 S1 的 Micro 对象闭包。
3. **预授权自动处理最大范围**：作为独立 deferred question 进入 OPEN_QUESTIONS；不在本审计自行裁决。
4. **Canonical unknown 的回答表达**：`verified + value=unknown` 与 `answer_status=unknown` 的产品含义及文案。
5. **MCP 不可逆动作例外**：默认应只允许满足安全验证条件的事实驱动；任何允许非 verified 答案驱动的例外必须由产品决定。

第 3-5 项不阻止当前 Micro 规范修订；第 1-2 项影响当前门禁。

## 8. 最小修订集合

### Micro 门禁修订

1. 记录 MMF-001 的产品批准/拒绝事件，绑定 commit/hash。
2. 联合修订 S1/S4/S9/Micro：闭合 Source append policy/subject 初始化与后续修订流程。
3. 修订 S3 与 MM-009：闭合 preflight conflict/failure 状态、receipt、retry 和幂等 oracle。
4. 修订 Micro fixture：解决旧 active evidence；加入非空 trust/closeness opinion；对 personality 采用产品裁决后的最小 oracle。
5. 修订 S6：拆分 test/run/suite/applicability 状态；在 manifest 中明确 Micro required upstream Test Ref。
6. 修订校验器：CRLF/canonical hash、结构化 invariant coverage、正向枚举检查、真实隐私扫描命令；重跑后生成绑定 HEAD、环境、exit code、artifact digest 的新结果。

### 阶段后置修订

- MCP 阶段处理 MMF-009/010。
- ingestion/migration 阶段处理 MMF-011/012。
- privacy mutate 阶段处理 MMF-013。
- MVP-B/查询语义评审处理 MMF-014/015。

## 9. 不应修改的内容

- 不修改 PRD 产品语义、五态/十种 Assertion 措辞或 SPEC 顺序，除非产品负责人发布新的 PRD 基线。
- 不删除双时态、两个 Micro Core View、补偿撤销、protected-change、stale-base 和 L2 失败场景。
- 不把权限 runtime、MCP、连接器、同步、真实迁移、决策、健康、财务或多 Agent 带入 Micro。
- 不选择数据库、编程语言、测试框架、模型、队列或加密方案来替代语义修订。
- 不把 257 个合同 ID 批量伪装成已物化测试，也不把静态检查描述为业务通过。
- 不改变 Source/Canonical/Ledger/Derived、时间/证据/Answer/View freshness 的既有正交边界。

## 10. 是否建议进入 Micro-MVP

**no**。

允许继续的只有“Micro 门禁规范修订”；在 MMF-001/002/003/004/005/006/008 关闭并由新静态结果复核前，不应开始技术选型、ADR、runner 或业务实现。

## 11. 下一步唯一建议动作

**发起一次严格限于 MMF-001、002、003、004、005、006、008 的 `Micro Gate Corrective Revision`：先取得产品负责人对当前门禁与 personality oracle 的显式裁决，再完成最小规范/fixture/校验器修订并重新独立审计。**

该动作不得夹带 deferred 功能、技术选型或业务代码。
