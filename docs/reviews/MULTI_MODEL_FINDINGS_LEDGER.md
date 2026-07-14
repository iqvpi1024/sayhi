# 多模型审查 Finding 台账

## 1. 审计基线

| 项目 | 值 |
|---|---|
| 审计日期 | 2026-07-14 |
| 工作区 | `C:\Users\Administrator\.codex\worktrees\2abe\sayhi` |
| Branch | detached HEAD；`main` 与 `origin/main` 均包含并指向该提交 |
| HEAD | `15e3ff87cd4c773b637a3bab9fba0cb614eaff45` |
| PRD 当前文件原始字节 SHA-256 | `5B1C02A327F3CB8DC942571BF827B8062FA1589DDCFE09D55B1368CDBF0F6674` |
| PRD LF 归一化 SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 工作树 | 审计开始时无 tracked/untracked 变更 |

当前 checkout 的 `PRDv04.md` 有 1301 个 CRLF，原始字节 hash 因此不是项目文件和校验器记录的 LF hash。Git 语义内容未显示修改；这是校验器可移植性问题，不是 PRD 语义变更。

## 2. 待整合报告

报告没有自证具体模型身份时，下表的模型名只按文件名标记，不作为作者身份事实。

| 报告 ID | 文件 | 作者/模型 | 报告日期 | 声明的审查 commit | 基线可信度 |
|---|---|---|---|---|---|
| `R-DS` | `D:\sayhi\Review-report\deepseek.md` | 自称“独立首席审计员”；`DeepSeek` 仅由文件名推定 | 2026-07-14 | 未注明；只给 PRD LF hash | medium：可作线索，不能单独证明当前缺陷 |
| `R-DB` | `D:\sayhi\Review-report\doubao.txt` | 自称“独立第三方首席审计员”；`Doubao` 仅由文件名推定 | 2026-07-14 | `b497c2c` / `spec-suite-v0.2-audited` | medium-high：`b497c2c` 是当前 HEAD 祖先；其后只修改 `PROJECT_STATE.md` 的备份记录 |
| `R-OP` | `D:\sayhi\Review-report\opus.txt` | 自称“独立第三方首席审计员”；`Opus` 仅由文件名推定 | 2026-07-14 | 未注明 | medium-low：行号与版本大体匹配，但没有 commit/hash 绑定 |
| `R-SOL` | `D:\sayhi\Review-report\sol.txt` | 未注明作者或模型；`sol` 仅为文件名 | 未注明；文件 mtime 为 2026-07-14 | 未注明 | low：不能直接作为当前证据；其中若干意见已由当前仓库独立复核证实 |

历史对照材料：`PRDv04-opus审查报告.md`、`PRD_V04_READINESS_REVIEW.md`、`SPEC_SUITE_COMPLETION_REVIEW.md`、`INDEPENDENT_BASELINE_AUDIT_2026-07-14.md`。它们均未在报告正文注明审查 commit；前三份已自标历史或 superseded，不能作为当前缺陷的单独证据。

## 3. 判定口径

- Finding 以当前 HEAD 的正文证据成立，不以报告数量成立。
- 同一实质问题只保留一个 Finding，并列全部来源。
- `P1` 表示进入 Micro 实现或物化 required suite 前必须关闭；`P2` 表示相关阶段前关闭；`P3` 表示维护债务。
- `影响 Micro-MVP=yes` 不等于建议扩张 Micro，只表示该问题会影响当前链路或门禁。

## 4. Findings

### MMF-001：正式进入实现的产品门禁未形成可复核批准记录

- 提出报告：`R-SOL P1-01`；本次独立复核。
- 精确依据：`PRDv04.md:7` 仍为 `Draft for Review`；`PRDv04.md:1265-1275` 要求 PRD 批准后再编写 SPEC；`PRDv04.md:1277-1286` 要求门禁确认后才进入实现；`docs/PROJECT_STATE.md:24-28` 同时记录 “Audited Specification Baseline”、九份 Approved SPEC 与 PRD 仍为 Draft；`docs/PROJECT_STATE.md:156-160` 已建议进入实现规划。
- 问题描述：仓库有多项“产品负责人确认/整体授权”的二级记录，但没有一个当前、明确、可复核的 PRD 批准或 §27.3 实现门禁批准事件。不能用 SPEC 的 `Approved` 状态替代产品基线批准。
- 实际后果：团队无法从仓库唯一判断“可以开始实现”还是“只能继续规范审查”；任何一方都可选择对自己有利的状态解释。
- 严重度：`P1`。
- 类型：产品问题 / 维护问题。
- 判定：`requires_product_decision`。
- 判定理由：PRD 自身设置了实现前产品门禁；仓库状态没有消除 Draft 与开工建议之间的张力。
- 建议修复方向：由产品负责人显式记录“批准/不批准当前 PRD 与 §27.3 门禁”，并绑定 commit/hash；若批准伴随产品语义变化，必须发布新 PRD 基线，不能由 SPEC 暗改。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-002：Source Append 的必需策略字段没有确定初始化合同

- 提出报告：`R-SOL P1-02`；`R-DS P1-01` 与 `R-OP P2-01` 的字段接缝意见部分并入；本次独立复核。
- 精确依据：`docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md:72-86` 要求 policy subject 字段；`docs/specs/09_INGESTION_MIGRATION_SPEC.md:63-80` 的 IntakeRequest 只提供 `owner_ref` 与非权威 `sensitivity_hint`；`docs/specs/09_INGESTION_MIGRATION_SPEC.md:172-175` 禁止 hint 降低敏感度但没有初始化规则；`docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md:160-179` 要求 Source Append 不等待语义处理；`docs/testing/MICRO_MVP_ACCEPTANCE.md:51-62` 的输入没有 subject/recorder/compartment/retention 字段，但 `:76-95` 的 expected Source 已确定这些字段，甚至包含从正文才能识别的 `person_beta`。
- 问题描述：fixture 预先裁决了 `private/personal/user_controlled_v1`、recorder 和第三方 subject，但 S4/S9 没有说明这些值来自请求、保守默认、同步解析还是后续 ChangeSet。
- 实际后果：实现可能在 Source 暴露前使用过宽默认值，或为满足 fixture 把语义解析塞进必须快速完成的 append 边界；不同实现会生成不同 Source schema/policy 状态。
- 严重度：`P1`。
- 类型：SPEC 问题 / 测试问题。
- 判定：`valid`。
- 判定理由：这不是要求 S1 重复 S4 字段表，而是当前输入无法唯一产生当前 expected Source。
- 建议修复方向：定义 append 前最小授权与保守默认、unknown subject 表达、recorder 来源、hint 升格条件，以及解析后通过受控操作补充 subject/compartment 的流程；同步修正 Micro fixture/oracle。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-003：ChangeSet 发布前复检失败没有合法终态

- 提出报告：`R-SOL P1-03`；本次独立复核。
- 精确依据：`docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md:141-151` 只允许 `approved -> publishing -> published|failed`；`:153-157` 又把权限、base revision、引用与 protected paths 复检设为 `approved -> publishing` 的前置条件；`:209-214` 要求 stale base 返回 conflict；`:290` 与 `:305` 分别要求 stale base、权限失效得到 conflict/failed；`docs/testing/MICRO_MVP_ACCEPTANCE.md:415-430` 要求 stale base 明确失败但未给 ChangeSet 状态 oracle。
- 问题描述：前置复检失败时，ChangeSet 既不能合法进入 `publishing`，也不能从 `approved` 进入 `failed/conflict`。
- 实际后果：实现会分叉为“保持 approved”“非法跳到 failed”或“先 publishing 再检查”；重试、receipt 和幂等语义随之不一致。
- 严重度：`P1`。
- 类型：SPEC 问题。
- 判定：`valid`。
- 判定理由：状态机、前置条件和验收结果三者不能同时成立。
- 建议修复方向：明确 durable publish-attempt 的建立点；增加合法的 preflight failure/conflict 终态或规定进入 `publishing` 后才执行复检，并补齐 receipt、`retry_of`、MM-009 oracle。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-004：MM-006 历史证据 oracle 与固定 fixture 互相矛盾

- 提出报告：`R-SOL P1-04`；本次独立复核。
- 精确依据：`docs/testing/MICRO_MVP_ACCEPTANCE.md:192-220` 的初始 `active` State 是 `evidence_refs: []`、`evidence_status: missing`；`:360-374` 的 MM-006 要求 transition 前后两次查询都回到 State revision 与 Source evidence。
- 问题描述：旧 `active` State 没有 Source evidence，却被要求返回 Source evidence；新断联 Source 也不能反向证明旧 active。
- 实际后果：诚实实现会失败，错误实现可把新 Source 误作历史证据而通过。
- 严重度：`P1`。
- 类型：测试问题。
- 判定：`valid`。
- 判定理由：固定输入与 Then 断言无法同时满足，oracle 不确定。
- 建议修复方向：为旧 active State 增加独立合成 Source/locator，或把旧查询 oracle 改为明确返回 `evidence_status=missing`，同时禁止复用新断联 Source。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-005：MM-007 对 trust/closeness/personality 的保护可平凡通过

- 提出报告：`R-OP:208-210`（原报告降为可选增强）；本次独立复核提升严重度。
- 精确依据：`PRDv04.md:1069-1071` 与 `:1179-1184` 把 trust、closeness、人格判断不被误改列入 Micro/Case A 结果；`docs/testing/MICRO_MVP_ACCEPTANCE.md:221-224` 将三类集合全部设为空；`:378-391` 又声称验证它们语义不变且不新增。
- 问题描述：空集合能检测“错误新增”，不能检测“实现会改写已有 trust/closeness/personality 记录”。origin 和 role 有非空 fixture，三类判断没有。
- 实际后果：一个会破坏既有 trust Assertion 的实现仍可能通过全部 MM 场景，Micro 不能证明其宣称的 protected-change 命题。
- 严重度：`P1`。
- 类型：测试问题。
- 判定：`valid`。
- 判定理由：验收声称的保护范围大于 fixture 可观察范围；不是要求实现推断能力。
- 建议修复方向：至少加入一条非空 trust/closeness opinion Assertion；对 personality 明确选择“仅禁止新增”还是允许一个只读的既有 Hypothesis fixture。后者若改变 S1 的 Micro 对象闭包，必须先由产品负责人裁决，不能静默扩张。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-006：最近静态验证结论在当前 checkout 不可复现，且包含脚本未执行的检查

- 提出报告：`R-SOL P2-06`（指出隐私扫描不存在）；本次独立复核发现 CRLF 失败。
- 精确依据：`tools/validate_spec_baseline.ps1:20-25` 对原始字节做固定 LF hash；`:65-73` 与 `:126-140` 的逐行正则未处理 CRLF；`:242-260` 只检查 Markdown fence，没有电话/本机路径/email 的隐私扫描；`docs/testing/LATEST_STATIC_VALIDATION.md:7-26` 与 `docs/PROJECT_STATE.md:90-116` 却记录 `PASSED` 和隐私启发式扫描。当前 HEAD 实际执行同一命令得到 38 个错误：1 个 PRD hash、36 个 suite YAML 行、1 个 Micro inline_content。
- 问题描述：校验器把 checkout 换行方式当成基线内容，且报告把不存在于该脚本的隐私扫描列为同一命令结果。
- 实际后果：Windows checkout 无法通过正式静态门禁；团队可能引用不可复现的 `PASSED`，也可能误以为隐私扫描已执行。
- 严重度：`P1`。
- 类型：测试问题 / 维护问题。
- 判定：`valid`。
- 判定理由：当前命令输出可复现；LF 归一化 hash 恰为已记录值，证明是可移植性缺陷而非 PRD 语义变更。
- 建议修复方向：规定并校验 canonical bytes（例如仓库 `.gitattributes`）或在脚本中显式归一化；正则兼容 CRLF；验证结果绑定 commit、环境、exit code 和 artifact digest；若隐私扫描是独立步骤，记录真实命令，否则删除该通过声明。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-007：静态校验器可误判不变量覆盖并漏掉新的枚举漂移

- 提出报告：`R-OP P3-01`、`R-DS P1-02`、`R-DB P3-05`、`R-SOL P2-06`；本次独立复核。
- 精确依据：`tools/validate_spec_baseline.ps1:94-99` 只要全文出现同尾号三位数字即可满足 compact coverage；`:205-217` 只列 11 个历史黑名单模式，没有解析正向 schema/枚举。
- 问题描述：`rev_015` 等无关数字可以替 `*-INV-015` 伪造覆盖；新枚举漂移不在黑名单时也会漏过。
- 实际后果：未来删除真实 invariant-to-test 映射或引入新别名后，脚本仍可能 `PASSED`。
- 严重度：`P2`。
- 类型：测试问题。
- 判定：`valid`。
- 判定理由：正则弱点可从代码直接证明；当前人工复核未发现 123 条映射实际缺失，所以不是当前 P1 业务缺陷。
- 建议修复方向：结构化解析每份 SPEC 的 invariant 表与覆盖映射，验证右侧 Test ID 存在；对封闭枚举采用单一机器可读定义或正向集合校验。
- 是否影响 Micro-MVP：`yes`，影响门禁可信度但不要求扩张业务范围。
- 置信度：`high`。

### MMF-008：S6 的 Verification Result 枚举自相不一致

- 提出报告：本次独立复核；`R-SOL P2-04` 的测试状态质疑提供线索。
- 精确依据：`docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md:41-48` 把 Verification Result 定义为 `not_executed|passed|failed|errored|skipped_with_reason`；`:64-79` 的 `latest_run_result` 改为 `not_executed|passed|failed|errored|partial|superseded`；`:97-108` 又分别定义 run 的 `partial` 与 individual test 的 `skipped_with_reason`，并要求 required skip 导致 run=partial。
- 问题描述：同名结果概念混合了 individual test、run、suite/current applicability 三种枚举，`superseded` 和 `partial` 的归属不唯一。
- 实际后果：Micro runner manifest、矩阵 Verification Result 和历史 run 的 schema 会分叉，可能错误设置 `suite_executed/suite_passed`。
- 严重度：`P1`。
- 类型：测试问题。
- 判定：`valid`。
- 判定理由：S6 自身的封闭枚举与状态机不能形成唯一机器 schema，正好在下一步 suite 物化时触发。
- 建议修复方向：分别定义 `individual_test_result`、`run_result`、`suite_artifact_state`、`verification_status`，明确 `superseded` 是适用性/历史状态而非执行结果，并更新矩阵字段语义。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`high`。

### MMF-009：MCP 不可逆操作的 Answer gate 漏掉 `unconfirmed` 与 `disputed`

- 提出报告：本次独立复核。
- 精确依据：`PRDv04.md:850-855` 要求 stale、无权限或证据不足时拒绝/降级；`docs/specs/08_MCP_CONTRACT_SPEC.md:18-24` 承诺 stale/无证据不驱动不可逆行动；`:123-127` 只明确 stale；`MCP-INV-004`（`:133-137`）只列 stale/unknown/not_covered/denied；`MCP-AT-006..009`（`:228-231`）没有“unconfirmed/disputed + irreversible”组合 oracle。
- 问题描述：`result_status=ok` 且 `answer_status=unconfirmed|disputed` 的响应没有明确禁止驱动不可逆外发/动作。
- 实际后果：未来 MCP 实现可在证据未确认或冲突时执行不可恢复动作，违反 PRD 的安全降级原则。
- 严重度：`P2`。
- 类型：SPEC 问题。
- 判定：`valid`。
- 判定理由：MCP runtime 明确 deferred，不影响 Micro；但进入 MCP 阶段前必须闭合。
- 建议修复方向：定义不可逆动作所需的最小 Answer/authorization/freshness 条件，默认把所有非 `verified` 事实型答案视为不可驱动，并增加组合测试；若有例外需产品决定。
- 是否影响 Micro-MVP：`no`。
- 置信度：`high`。

### MMF-010：MCP denied 响应的字段枚举与文字规则不一致

- 提出报告：本次独立复核。
- 精确依据：`docs/specs/08_MCP_CONTRACT_SPEC.md:78-93` 的 `answer_status` 只允许 BTE status 或 `not_applicable`，`evidence_refs` 只允许授权 refs 或空数组；`:95` 却说 denied 时 revision/freshness/answer/evidence/payload 均按策略 `withheld|not_applicable`；`MCP-AT-027`（`:249`）又允许 evidence withheld/空。
- 问题描述：`withheld` 是否是 `answer_status`/`evidence_refs` 的合法 literal 没有唯一答案。
- 实际后果：客户端 schema 与服务端拒绝响应会不兼容，或用错误字段差异泄露隐藏资源。
- 严重度：`P2`。
- 类型：SPEC 问题。
- 判定：`valid`。
- 判定理由：这是直接的字段枚举冲突；不需要等实现才能证明。
- 建议修复方向：为每个 denied 字段给出唯一 literal/absence 规则；建议 answer=`not_applicable`、evidence=`[]`、payload=`withheld`，但最终格式应在 S8 内统一而非由实现猜测。
- 是否影响 Micro-MVP：`no`。
- 置信度：`high`。

### MMF-011：S1 Source Append 与 S9 Intake/AppendReceipt 状态集合发生名称碰撞

- 提出报告：`R-SOL P2-01`；本次独立复核。
- 精确依据：`docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md:341-348` 的 Source Append Receipt 只有 `received -> stored|rejected`；`docs/specs/09_INGESTION_MIGRATION_SPEC.md:84-86` 的 AppendReceipt 增加 `duplicate`；`:102-115` 又定义 `received -> validating -> stored|duplicate|rejected`，并称其为 Intake 终态。
- 问题描述：S9 可能是在细化 Intake 而非修改 Source 状态，但它复用 `Source Append/AppendReceipt` 名称且未声明与 S1 的包含/映射关系。
- 实际后果：重复摄取时，有的实现会生成 Source receipt `duplicate`，有的只生成 Intake receipt 并引用旧 Source；审计和幂等 schema 分叉。
- 严重度：`P2`。
- 类型：SPEC 问题。
- 判定：`partially_valid`。
- 判定理由：Micro 的 stored 路径一致，故不构成当前阻塞；非 Micro duplicate 路径确有术语/枚举不闭合。
- 建议修复方向：分开命名 `IntakeStatus` 与 `SourceAppendReceiptStatus`，明确 duplicate 不创建新 Source，并给出两个 receipt 的引用关系。
- 是否影响 Micro-MVP：`no`。
- 置信度：`medium`。

### MMF-012：Migration applying 部分成功后的补偿路径不在状态机中

- 提出报告：`R-SOL P2-02`；本次独立复核。
- 精确依据：`docs/specs/09_INGESTION_MIGRATION_SPEC.md:96-99` 允许一个 plan 含 ChangeSet 列表；`:117-128` 只有 `applying -> applied|failed`，回滚入口仅来自 `verification_failed|verified`；`:194-196` 又要求 migration partial failure 执行 S3 原子失败或补偿回滚。
- 问题描述：多个 ChangeSet 中前项已发布、后项失败时，需要补偿，但 `failed` 没有到 `rolling_back` 的合法路径。
- 实际后果：迁移实现可能留下部分 Canonical revision，或非法跳状态并误报 failed/rolled_back。
- 严重度：`P2`。
- 类型：SPEC 问题。
- 判定：`valid`。
- 判定理由：单个 ChangeSet 原子性不自动提供整个 MigrationPlan 的原子性。
- 建议修复方向：明确 plan 是单一原子 ChangeSet 还是多 revision saga；若后者，增加 applied subset、rollback_required/rolling_back/rollback_failed 状态与测试。
- 是否影响 Micro-MVP：`no`。
- 置信度：`high`。

### MMF-013：unseal/restore/unarchive 没有明确 ChangeSet operation 映射

- 提出报告：`R-SOL P2-03`；本次独立复核。
- 精确依据：`docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md:104-115` 的 operation 枚举只有 add/correct/end/merge/split/archive/seal/soft_delete/hard_delete；`docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md:121-145` 定义 unseal、soft-delete restore、unarchive；`:206-211` 要求这些操作可撤销且经审计。
- 问题描述：逆向操作究竟使用 `correct`、新 operation 还是 compensation ChangeSet 未定义。
- 实际后果：权限/retention 审计、确认政策与幂等键无法跨实现一致。
- 严重度：`P2`。
- 类型：SPEC 问题。
- 判定：`valid`。
- 判定理由：S4 要求受控状态转换，但 S3 的封闭 operation 无显式映射。
- 建议修复方向：在 S3/S4 给出每个正向/逆向转换的 operation、reversibility、确认政策和 receipt 映射。
- 是否影响 Micro-MVP：`no`。
- 置信度：`high`。

### MMF-014：PRD 的“预授权自动处理最大范围”未进入开放问题队列

- 提出报告：`R-SOL P2-05`；历史 `PRDv04-opus审查报告.md:D-11`；本次独立复核。
- 精确依据：`PRDv04.md:1253-1261` 明列该产品问题；`docs/decisions/OPEN_QUESTIONS.md:287-300` 的 DQ-001..010 没有对应条目；`docs/specs/05_SHILING_POLICY_SPEC.md:85-93` 给出保守边界，`:277-279` 却称无 blocking open question。
- 问题描述：S5 的保守默认与 PRD 已有原则一致，但“用户预授权最大范围”仍未由产品负责人决定，也未被 deferred 队列追踪。
- 实际后果：进入 FR-107/自动处理实现时，团队可能把 S5 默认误作最终产品裁决，或无门禁扩大自动权限。
- 严重度：`P2`。
- 类型：产品问题。
- 判定：`requires_product_decision`。
- 判定理由：无法从 PRD 唯一推导最大授权范围；当前单次确认 Micro 不触发。
- 建议修复方向：在 OPEN_QUESTIONS 增加独立 DQ，绑定 FR-107/MVP-B 重开阶段；不要在本轮自行决定范围。
- 是否影响 Micro-MVP：`no`。
- 置信度：`high`。

### MMF-015：Canonical `value=unknown` 与查询 `answer_status` 的组合语义未唯一化

- 提出报告：`R-DS P1-03`；本次独立复核。
- 精确依据：`docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md:254-266` 允许 RelationshipState `value=unknown` 并强调与 `answer_status=unknown` 正交；`docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md:279-294` 定义六态，但没有规定“已确认 unknown 值”应返回 `verified + answer_value=unknown` 还是 `unknown + null`。
- 问题描述：两个轴已经分开，但组合规则没有产品语义。
- 实际后果：用户界面和 API 会混淆“已知该状态未确定”与“系统无法回答”。
- 严重度：`P2`。
- 类型：产品问题 / SPEC 问题。
- 判定：`requires_product_decision`。
- 判定理由：两种表达都能保持轴正交，无法从 PRD 唯一选定；Micro 只用 active/no_contact。
- 建议修复方向：由产品负责人决定组合语义、文案和 AnswerEnvelope 例子，再补 S2 组合测试。
- 是否影响 Micro-MVP：`no`。
- 置信度：`medium`。

### MMF-016：Micro required upstream Test Ref 的集合不够明确

- 提出报告：`R-SOL P1-05`；本次独立复核。
- 精确依据：`docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md:50-53` 说首套只执行 MM-001..010 并复用相关测试；`docs/traceability/REQUIREMENTS_MATRIX.md:64-80` 在 micro 行混列完整 S1/S2/S3/S9 Test Ref；FR-009 的 `BTE-AT-001..010` 包含 Micro 明确排除的模糊时间；`docs/traceability/REQUIREMENTS_MATRIX.md:106-108` 又要求物化 MM 及“直接依赖切片”，但未列唯一集合。
- 问题描述：MM-001..010 的 required 集合明确，但哪些上游 `*-AT-*` 也属于同一 required run 不明确。
- 实际后果：实现团队可能把非 Micro 模糊时间带入首轮，或只跑 MM 而漏掉真正的 schema 前置断言。
- 严重度：`P2`。
- 类型：测试问题 / 维护问题。
- 判定：`partially_valid`。
- 判定理由：MM required 集本身明确，因此不接受原报告的 P1；“直接依赖”仍需在 manifest 物化前精确列出。
- 建议修复方向：在机器 manifest 中逐 Test Ref 标 `required_for_micro|reused_optional|deferred`，不要把 coverage level 仅停留在 FR 行级。
- 是否影响 Micro-MVP：`yes`。
- 置信度：`medium`。

### MMF-017：257 个 SPEC Test ID 的 oracle 深度不一致

- 提出报告：`R-SOL P2-04`、`R-OP P3-02`；本次独立复核。
- 精确依据：`docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md:64-80` 要求 `suite_defined=true` 表示合同用例、oracle 和追踪写清，但同时明确无机器 fixture 时 `suite_materialized=false`；各 SPEC §19 的大量用例只有一行抽象 Given/Then，例如 `docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md:241-270`。
- 问题描述：有些条目是清晰的属性 oracle，有些仍需 fixture/policy 才能唯一判定；“257 tests defined”不能理解为 257 个可直接执行的确定 oracle。
- 实际后果：后续阶段可能低估物化工作量，但当前文件已明确所有 suite 未物化、未执行。
- 严重度：`P3`。
- 类型：测试问题。
- 判定：`partially_valid`。
- 判定理由：这是已披露的物化债务，不是 257 个当前业务缺陷；Micro 的两个具体 oracle 缺口已单列 MMF-004/005。
- 建议修复方向：按阶段逐套物化，不进行 257 项大爆炸式修订；每次物化时补固定输入、policy、required 标志和唯一断言。
- 是否影响 Micro-MVP：`no`，除已单列的 MM 问题。
- 置信度：`medium`。

## 5. 被拒绝、重复或已过期意见

| ID | 提出报告 / 意见 | 精确依据 | 实际后果 | 严重度 / 类型 | 判定与理由 | 建议方向 | 影响 Micro | 置信度 |
|---|---|---|---|---|---|---|---|---|
| `MMF-R01` | `R-DS P1-04`：必须把 `protected_paths` 从 proposal 提升到 ChangeSet | S1 `:285-312`、S3 `:104-125` 明确按 proposal 声明，S3 `CS-INV-012` 对整包发布检查 | 未证明现有模型会遗漏 union/整包校验 | P3 / SPEC | `false_positive`：字段位置是设计选择；仓库没有要求所有 proposal 的保护集合必须相同 | 保留 proposal 级；如实现采用 ChangeSet union，可在 ADR 说明 | no | high |
| `MMF-R02` | `R-DB P2-02`、`R-SOL:79`：Micro 增加权限 fail-closed 场景 | PRD `:1063-1073`、Micro `:20-34`、Matrix `:43-58` 明确排除权限运行时 | 会扩大当前 Micro，与范围锁冲突 | P3 / 产品 | `false_positive`：deferred 功能不能因“横切基础”被重新塞回 Micro；MMF-002 的 Source 初始化不是完整权限 runtime | 不新增 MM-011；在 S4 阶段执行 PAP suite | no | high |
| `MMF-R03` | `R-DB P2-01`：Evidence Family ID 未选算法/持久化是当前缺陷 | S2 `:219-244`、`:422-432` 明确 Derived 且机制后置 S7/ADR；Micro 单 Source | 当前没有错误行为；属于已声明 ADR | P3 / ADR | `false_positive`：报告把明确 deferred 的物理机制误报为 SPEC 缺失 | 到多 Source 实现前立 ADR | no | high |
| `MMF-R04` | `R-DS P2-01`：fixture 有 S4 字段就要求 Micro 实现 policy engine | Micro `:34` 排除权限；S4 字段仍是上游 schema 约束 | 仅携带字段不等于执行策略引擎 | P3 / 产品 | `false_positive`：把数据边界字段误当功能范围；具体初始化缺口已并入 MMF-002 | 不扩张 Micro runtime | no | high |
| `MMF-R05` | `R-DS P2-02`：MM 场景有依赖但未声明执行顺序 | MM-003/004/005/008 的 Given 已显式引用前态；S6 要求 fixture/action sequence | runner 可为每个测试隔离准备前态，不要求测试串行共享状态 | P3 / 测试 | `partially_valid`：manifest 应写 prerequisite，但不是语义缺陷 | 在 manifest 声明 setup/dependency，不把测试设计成共享可变顺序 | yes | medium |
| `MMF-R06` | `R-DS P2-04`：S1/S2 v0.3、S3-S9 v0.2 是问题 | 各 SPEC 有独立版本与明确上游版本 | 无语义后果 | P3 / 维护 | `false_positive`：版本号不要求整套齐步 | 保持独立语义版本 | no | high |
| `MMF-R07` | `R-DB P3-07`：risk_level 枚举未定义 | S3 `:92`、S5 `:77` 与 `:85-93` 均明确 `low|medium|high|critical` | 报告引用错误 | P3 / SPEC | `false_positive` | 无修复 | no | high |
| `MMF-R08` | `R-DB P3-06`：Micro 必须决定 narrative_context 物理细节 | S1 `:314-324`、S7 `:92-98` 已划分逻辑/物理边界；Micro fixture 不使用 narrative_context | 会引入不必要 ADR | P3 / ADR | `false_positive`：不是当前链路前提 | 相关功能实现时再定物理限制 | no | high |
| `MMF-R09` | `R-DB P3-04`：SPEC 自称 Approved 构成自我认证 | 每份 SPEC 同时明确实现未开始、suite 未执行；独立报告另存 | 不会把业务测试变 passed | P3 / 维护 | `false_positive`：文档 lifecycle 状态可自载；现有措辞已有外部审计引用 | 可选改善归因，不是缺陷 | no | medium |
| `MMF-R10` | `R-OP P3-04`：`HTH` 缩写应改 `STH` | S6、validator、matrix 内部一致 | 纯命名偏好，改名反而制造 churn | P3 / 维护 | `false_positive` | 不修改 | no | high |
| `MMF-R11` | `R-DS/R-DB/R-OP`：PRD 十种 Assertion、五态措辞、SPEC 顺序仍是当前缺陷 | `OPEN_QUESTIONS.md:32-47` 的 BQ-002 与 `:255-267` 的 IQ-016 已显式决定差异；PRD hash 锁定 | 新读者需读裁决记录，但当前实现语义唯一 | P3 / 维护 | `obsolete`：原始矛盾已由产品裁决关闭；本轮不得借审计改 PRD | 仅在未来经批准的新 PRD 基线同步，不改当前基线 | no | high |
| `MMF-R12` | 历史 root 报告“34 条 FR”、可删撤销/关系时间线 | `PRDv04.md:865-909` 实为 32 FR；IQ-001/IQ-008 已决定；Matrix `:97-103` 诚实分级 | 会造成错误范围缩减或追踪数字 | P2 / 产品 | `obsolete` 且部分 `false_positive` | 不恢复历史结论 | yes | high |
| `MMF-R13` | 历史 readiness/completion 报告中的 BQ/IQ、删除、六态等缺口 | 当前 `OPEN_QUESTIONS.md` 和 S1-S9 已逐项落地；历史报告自标 superseded | 不能证明当前仍有同一缺陷 | P3 / 维护 | `obsolete`；若有残余已由 MMF-001..017 重新以当前行号建立 | 只作溯源 | no | high |

## 6. 台账结论

- 当前有效/需决策：17 项，其中 P1 7 项、P2 9 项、P3 1 项。
- 直接影响 Micro 门禁的 P1：MMF-001、002、003、004、005、006、008。
- 不应因本审计扩张 Micro：权限 runtime、MCP、迁移、Evidence Family 物理算法仍按既定阶段后置。
- 报告数量未参与任何判定；`R-SOL` 虽缺 commit，其 4 项核心意见是由当前 HEAD 独立复核后才采纳。
