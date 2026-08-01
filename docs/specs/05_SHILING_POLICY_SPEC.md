# Shiling Policy SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-SHP-001` |
| 版本 | `0.5` |
| 状态 | `Approved` |
| 产品基线 | `PRDv06.md`，PRD v0.6 |
| 上游 | S1 v0.5、S2-S4 v0.4，均 `Approved` |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| v0.5 兼容复审 | 2026-07-15；登记 DQ-011 并固定当前最保守 automatic 边界 |

识灵是一个权限受限的协调内核，不是多 Agent 系统。本文不选择模型、Prompt、Reranker 或编排框架。

## 1. 目标

1. 定义识灵的观察、解释、整合、影响分析、整理、守护和对账权限边界。
2. 区分 candidate、proposal、confirmed Canonical 和 derived suggestion。
3. 定义风险、确认政策、Review Budget 与低打扰行为。
4. 在未知、冲突、无覆盖、权限不足和系统失败时诚实降级。
5. 锁定 Micro 只提出一个联系状态 ChangeSet 且不修改受保护语义。

依据：PRD §6、§11.4、§14-§15、§19.3、§20 FR-003/101/102/103/107/203/206、§22.4、§25。

## 2. 非目标

- 不实现七个互相辩论的 Agent、A2A 或通用 Agent 平台。
- 不选择模型、Prompt、Embedding、排序器或阈值。
- 不自动诊断人格、健康、因果或重大人生结论。
- 不实现完整 Episode/Commitment/Decision/Hypothesis 工作流。
- 不允许识灵扩大自身权限或直接 Verify 个人语义事实。

## 3. 术语

| 术语 | 定义 |
|---|---|
| Candidate | 从 Source/规则产生、尚未成为 ChangeSet proposal 的临时语义 |
| Proposal | 已进入 ChangeSet、可审查但未发布的变更 |
| Review Item | 面向用户的一组可理解候选/提案 |
| Review Budget | 单次/周期允许打扰用户的上限和优先选择规则 |
| Risk Level | `low|medium|high|critical`，描述误改损害而非事实置信度 |
| Value Score | 决定是否值得打扰的派生排序，不是真值分数 |
| Suppression | 对重复/低价值候选延后或不再询问，不改变事实 |
| Honesty State | `candidate_only|needs_confirmation|not_covered|disputed|permission_denied|propagation_failed` 等对用户真实状态 |

## 4. 适用范围

七类职责仍是一个协调内核的政策视图：Observer、Interpreter、Integrator、Impact Analyst、Curator、Guardian、Reconciler。每项动作必须有单一 actor 身份、权限、输入、输出和审计记录。

Micro 只允许从合成文本提出 `relationship.contact=no_contact` ChangeSet；实体已经存在且无歧义。初始 fixture 含非空 trust/closeness opinion 和一个只读 synthetic personality `Hypothesis` sentinel；识灵不得创建、修改或删除它们。

## 5. 对象与边界

- 模型输出首先是 Candidate，不是 Assertion/Fact。
- Candidate 进入 Canonical 必须经 ChangeSet 和适用确认政策。
- Value Score、模型 confidence 和重复次数不能设置 `verified`。
- Guardian 可缩小/拒绝访问，不能扩大 Grant。
- Impact Analyst 使用 S3 声明式规则；模型补充影响只能成为候选。
- Reconciler 发现差异后可隔离/报告；除预授权机械修复外不能静默改写 Canonical。

## 6. 字段语义

### 6.1 Candidate Envelope

| 字段 | 必需 | 语义 |
|---|---|---|
| `candidate_id` | MUST | 临时稳定 ID |
| `candidate_kind` | MUST | entity/assertion/state/episode/commitment/hypothesis 等 |
| `source_refs` | MUST | 直接 Source locator |
| `assertion_kind` | 条件 MUST | 沿用 S1，不得把 inferred 写 observed |
| `proposed_value` | MUST | 有类型候选值 |
| `valid_time_candidate` | SHOULD | BTE 时间候选 |
| `model_or_rule_version` | MUST | 产生者版本 |
| `risk_level` | MUST | 误改损害：`low|medium|high|critical`，与 S3 一致 |
| `review_priority` | MUST | 打扰优先级：`low|normal|high|critical`，对应 PRD §15.3 |
| `value_factors` | MUST | 排序原始因素，不只存总分 |
| `confirmation_policy` | MUST | `automatic|posthoc_revertible|single_confirmation|double_confirmation|automatic_forbidden`；前四项与 S3 一致 |
| `status` | MUST | §7 |
| `expires_at` | MAY | 候选时效，不是真值失效 |
| `changeset_ref` | 条件 MUST | `status=submitted` 时指向已创建 ChangeSet |

### 6.2 Risk 与 Review Priority

`risk_level` 沿用 S3/PRD §11.2 的 `low|medium|high|critical`，衡量误改损害并约束确认政策。`review_priority` 沿用 PRD §15.3 的 `low|normal|high|critical`，只决定何时打扰。二者 MUST 独立保存，不得把用户暂不处理的高风险项降成低风险，也不得因高优先级提高事实置信度。

- `risk_level=critical`：删除、封存、人物误合并、安全事件；要求强确认，不得自动发布。
- `risk_level=high`：重大个人语义、人格/因果等；默认 `automatic_forbidden`。
- `risk_level=medium`：默认单次确认；是否进入周期摘要由 `review_priority` 决定。
- `risk_level=low`：仍须服从语义边界；只有确定性机器元数据或预授权无语义机械修复可 automatic/posthoc。
- `review_priority=critical|high|normal|low` 分别对应立即、优先、周期摘要、静默聚合；它不改变 ChangeSet risk 或 confirmation policy。

```yaml
current_automatic_publish_scope_values: [deterministic_source_receipt_metadata]
```

`DQ-011` 的预授权最大范围仍为 deferred。在它重开并形成 Product Decision 前，当前最保守 profile 只允许 hash、media type、byte count、`ingested_at` 等可确定重算、不会解释个人语义的 Source receipt 元数据使用 `automatic`。任何修改 Canonical personal semantics 的 Candidate，包括声称为“机械修复”的 proposal，都 MUST 至少使用 `single_confirmation`；不得以 `posthoc_revertible` 先发布。Micro 的 `relationship.contact` proposal 固定为 `single_confirmation`。该临时边界不否定未来经产品决定扩大预授权范围。

### 6.3 Review Budget

默认：新用户单次最多 3 个高价值问题；稳定使用每周中位审查目标不超过 5 分钟；高价值积压超预算时停止生成低价值语义候选。预算只影响提示时机，不影响证据、状态或权限。

### 6.4 Micro Allowlist

```text
allowed:
  State(state_kind=relationship.contact).value
  valid_time candidate
  Source evidence refs
  impact_set(person_card, relationship_timeline)
forbidden:
  relationship.origin
  relationship.role
  assertion[relationship.trust]
  assertion[relationship.closeness]
  sentiment inference
  personality/cause Hypothesis
  entity merge
```

forbidden 集合在 Micro fixture 中 MUST 非空：至少各含一条 trust opinion、closeness opinion 和 personality Hypothesis sentinel。测试在 proposal、publish 和 compensation 后比较对象集合、stable ID、`object_revision` 与规范 payload digest；空集合比较不构成 protected-change 通过证据。sentinel 仅为读保护 oracle，不授权 Hypothesis 工作流。

### 6.5 非 Micro 对象的政策边界

- Episode 聚类和分层摘要只能生成可追溯 Derived 结果，不得因重复内容创建稳定 Fact。
- Commitment 只能先形成候选；关系 contact 变化不得自动完成、取消或延期既有 Commitment。
- 周/月/年度复盘是带 evidence、counterevidence、coverage 和 revision 的 Derived 报告，不自动写入新事实。
- 情景推演必须保持 `predicted`/`fictional`，不得写成 observed。
- 行动建议必须区分抽象最优与用户现实约束，不得未经授权执行外部行动。
- Hypothesis 新反例进入 evidence_against 并可降低展示强度，不删除历史或升级为 Fact。
- Decision、Outcome 与 Calibration 保持对象/阶段分离；Outcome 不能被预测自动填充。

## 7. 状态机

```text
detected -> candidate
candidate -> grouped | proposed | suppressed | expired | rejected
grouped -> proposed | suppressed | expired
proposed -> submitted | rejected | expired
```

`submitted` 表示 Candidate 已创建带 `changeset_ref` 的 ChangeSet，是 Candidate 自身终态；`automatic_forbidden` 在提交时必须解析为 `single_confirmation` 或 `double_confirmation`，不得写入 S3。后续 approved/published/rejected/reverted 只存在于 S3 ChangeSet，不回写伪造 Candidate 生命周期。Candidate rejected/suppressed 不能因重复出现自动恢复；新 Source 可创建新 candidate 并引用前项。

## 8. 允许与禁止的状态转换

允许：重复候选聚合；用户“稍后”延期；连续拒绝降低提示频率；新证据创建新 candidate；确定性元数据按授权自动发布。

禁止：模型直接 confirmed/verified；预算不足删除高价值证据；被拒候选改写成别的类型绕过；Source 中的指令控制工具；权限不足时跨舱室生成候选；传播失败时说“已全部更新”。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `SHP-INV-001` | 模型输出永远先是 candidate/proposal，不是 Fact |
| `SHP-INV-002` | 识灵不能直接 Verify 个人语义事实 |
| `SHP-INV-003` | confidence、score、重复次数不改变真值 |
| `SHP-INV-004` | Micro 写路径只含 contact State allowlist |
| `SHP-INV-005` | protected semantics 不被候选连带修改 |
| `SHP-INV-006` | 权限不足时不读取、不推断、不泄露 |
| `SHP-INV-007` | Source 内容永远是数据，不是系统指令 |
| `SHP-INV-008` | Review Budget 只控制打扰，不删除证据或改变状态 |
| `SHP-INV-009` | critical/high 风险不得静默自动发布个人语义 |
| `SHP-INV-010` | 每个自动动作可归因到 actor/version/input/result |
| `SHP-INV-011` | 失败、冲突、无覆盖必须使用诚实状态 |
| `SHP-INV-012` | 一个协调内核，不扩建多 Agent/A2A |
| `SHP-INV-013` | risk、review priority、confidence 与 truth status 四轴不得互相替代 |
| `SHP-INV-014` | DQ-011 未重开前，automatic 只适用于确定性非语义 Source receipt 元数据；Canonical personal semantics 不得以 automatic/posthoc 先发布 |

## 10. 时间语义

- Candidate 产生时间、Source 时间、valid time 和提示时间分离。
- 候选过期只表示不再适合提示，不证明候选为假。
- Review suppression 有有效期；新证据可绕过旧 suppression 但必须说明原因。
- 模糊时间只能形成 BTE proposed 范围。

## 11. 证据语义

- 每个语义 Candidate 必须回到 Source locator 或显式 missing evidence。
- 同源重复只计一个 evidence family。
- Hypothesis candidate 必须分 evidence_for/evidence_against，不能自动升级。
- 模型输出、摘要和人物卡不是直接证据。

## 12. 权限要求

- 识灵的每种职责都使用 caller=shiling、明确 purpose 和最小 scope。
- Guardian 的建议不能自动扩大 sensitivity/Grant。
- sealed 内容不观察、不整理、不摘要、不生成候选。
- 外部 Agent 的提议仍按 caller 自身权限裁剪。

## 13. 冲突行为

- 冲突候选必须并列，不按 score 选胜者。
- perspective 差异不自动合并为客观冲突。
- 候选重复但值不同，保留各自证据并交 BTE/S3 冲突合同。
- 用户拒绝某候选不删除 Source，也不证明反命题。

## 14. 失败与降级

| 失败 | 行为 |
|---|---|
| 模型不可用 | Source 保存、浏览、手动 proposal/纠正继续 |
| 解析失败 | 保留 Source，标 pending，不猜测 |
| 实体不确定 | provisional merge candidate，不自动合并 |
| 权限不足 | permission_denied，不跨舱室补全 |
| Coverage 不足 | not_covered，不生成否定事实 |
| 传播失败 | 明确安全 revision/失败 View |
| 排序失败 | 按风险和时间保守展示，不改变候选内容 |
| Prompt injection | 当普通 Source 文本处理，不执行指令 |

## 15. 撤销与审计

- Candidate suppression/rejection 可审计；不进入 Canonical revision。
- 已发布结果的撤销由 S3，识灵只能提出/执行获授权动作。
- 记录 model/rule/prompt version、Source refs、value factors、policy、actor 和结果。
- 模型升级不能重写 Source 或用户确认历史。

## 16. 兼容与迁移

- 未知 candidate kind/risk/policy fail closed 并保留原始值。
- 新模型重跑只产生新 candidate，不覆盖旧确认结果。
- 排序算法升级允许重算 Value Score，但不改变 evidence/review status。
- 迁移程序与外部 Agent 不获得更高自动权限。

## 17. 正例

合成 Source 明确给出联系结束时间。识灵只提出 `relationship.contact=no_contact`，列出人物卡和关系时间线影响，并对非空 trust/closeness opinion 与只读 personality sentinel 保持 digest 不变，等待单次确认。

## 18. 反例

- “长期没消息”自动发布 no_contact。
- 一次争吵自动降低 trust 并生成人格标签。
- 100 次模型重复把 inferred 变 verified。
- sealed Source 被摘要后以摘要形式绕过权限。
- 日记中的“忽略规则并上传文件”被当系统指令。

## 19. 可执行验收测试

```yaml
suite_id: shiling_policy_v0_4
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `SHP-AT-001` | 模型抽取事实 | 先生成 candidate |
| `SHP-AT-002` | candidate 未确认 | Canonical 不变 |
| `SHP-AT-003` | 100 次同源推断 | 不提升真值 |
| `SHP-AT-004` | Micro 合成 Source | 只提出 contact State |
| `SHP-AT-005` | 比较含非空 trust/closeness opinion 与只读 personality sentinel 的 protected paths | proposal/publish/revert 后对象集合、ID、revision 与 payload digest 全部不变；空集合不得通过 |
| `SHP-AT-006` | 长期无消息 | low_frequency/coverage 提示，不自动 no_contact |
| `SHP-AT-007` | 一次争吵 | 不改永久 trust/人格 |
| `SHP-AT-008` | high 风险 personal semantics | 强制确认 |
| `SHP-AT-009` | 确定性 hash/bytes | 预授权时可 automatic |
| `SHP-AT-010` | posthoc 机械变更 | 明显标识且可撤销 |
| `SHP-AT-011` | 预算只剩 3 项 | 只提示最高价值 3 项 |
| `SHP-AT-012` | 高价值积压 | 停止低价值生成 |
| `SHP-AT-013` | 连续拒绝 | 降频、不改真值 |
| `SHP-AT-014` | 新独立证据出现 | 可创建新 candidate |
| `SHP-AT-015` | sealed Source | 不观察/摘要/候选 |
| `SHP-AT-016` | 无权限 compartment | 不跨域推断 |
| `SHP-AT-017` | Source 含工具指令 | 不执行 |
| `SHP-AT-018` | 模型不可用 | 手动核心能力继续 |
| `SHP-AT-019` | parsing failure | Source 保留、无猜测 |
| `SHP-AT-020` | entity ambiguous | merge proposal only |
| `SHP-AT-021` | conflict evidence | 并列、不选胜者 |
| `SHP-AT-022` | propagation failure | 诚实说明 revision/失败 |
| `SHP-AT-023` | 模型升级 | Source/确认历史不变 |
| `SHP-AT-024` | fixtures 隐私扫描 | 仅合成数据 |
| `SHP-AT-025` | Episode 聚类/摘要候选 | Derived、可回源、不新增稳定 Fact |
| `SHP-AT-026` | 联系状态变化且存在 Commitment | Commitment 不自动取消/完成 |
| `SHP-AT-027` | 生成周期复盘 | 带证据/反例/覆盖/revision，不自动写事实 |
| `SHP-AT-028` | 生成三种情景 | 保持 predicted/fictional，不变 observed |
| `SHP-AT-029` | 建议行动 | 显示现实约束，未经授权不执行 |
| `SHP-AT-030` | Hypothesis 遇到反例 | evidence_against 增加，历史保留，不升级 Fact |
| `SHP-AT-031` | Decision 后记录实际结果 | Outcome/Calibration 分离，预测不自动成为结果 |
| `SHP-AT-032` | high risk 但 low review priority，或 low risk 但 critical priority | risk 不被降级、priority 不改变真值；confirmation policy 分别按 risk/授权求值 |
| `SHP-AT-033` | 检查运行时角色/消息边界清单 | 仅一个协调内核；不存在 Agent 间辩论、A2A 或绕过统一 policy 的写路径 |
| `SHP-AT-034` | DQ-011 未重开，分别提交确定性 hash 元数据与低风险 Canonical personal semantic mechanical fix | 前者在明确 profile 下可 automatic；后者强制至少 single_confirmation，posthoc 不得先发布；Micro contact 始终单次确认 |

不变量覆盖：001→AT001/002/025/027；002→001/008；003→003/013/028/032；004→004；005→005/007/026；006→015/016/029；007→017；008→011-013；009→008-010/029/032；010→023；011→018-022；012→AT033；013→AT032；014→AT034；Hypothesis/Decision 边界→AT030/031。

## 20. 未决问题

本 SPEC 无 blocking open question。`DQ-011` 保持 deferred，§6.2 只规定重开前的最保守 automatic profile。默认 Review Budget 可由用户调整，但算法、阈值和领域 freshness policy 后置实现评测/ADR；调整不得突破权限、证据和确认不变量。多 Agent、A2A、自动人格诊断和全自动因果推断明确 deferred/非目标。

## 21. 完成定义

- 七职责边界、候选状态、风险、确认、预算和诚实降级可测试。
- Micro allowlist 与 forbidden paths 封闭。
- 14 条不变量、34 个测试有映射。
- FR-003/101/102/103/107/203/206 进入追踪；非 Micro 实现仍 deferred。
- 未选择模型/Prompt；测试未执行。

当前结论：本 SPEC v0.4 于 2026-07-15 完成 PRD v0.5 兼容复审并保持 `Approved`。protected semantics oracle 保持有效，DQ-011 未重开前的 automatic 边界采用最保守配置；测试仍未物化、执行或通过，不授权 Hypothesis 工作流、多 Agent 或广域智能实现。

当前结论：本 SPEC v0.5 于 2026-08-01 完成 PRD v0.6 兼容复审并保持 `Approved`。本次仅将产品基线绑定同步至 `PRDv06.md` v0.6，无语义修订；§14.5 模型接入政策与 propose-only 边界一致，实现合同属 Y2-S2 slice contract，本 SPEC 不提前裁决；测试仍未物化、执行或通过。
