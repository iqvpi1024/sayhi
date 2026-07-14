# Ingestion & Migration SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-IMM-001` |
| 版本 | `0.3` |
| 状态 | `Approved` |
| 产品基线 | `PRDv04.md` v0.4 |
| 上游 | S1-S8 `Approved` |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 纠偏复审 | 2026-07-14；闭合 Intake 到 Source policy/subject 的确定性初始化合同 |

本文定义输入与迁移语义，不实现连接器、OCR、ASR、视频处理、真实历史迁移或迁移框架。

## 1. 目标

1. 使原始输入先可靠进入 Source，解析失败不丢材料。
2. 分离 Source、解析产物、Candidate、ChangeSet 与 confirmed Canonical。
3. 定义 hash/来源谱系去重，防止重复导入和重复计证。
4. 定义 schema/Context Pack 迁移的验证、计划、受控写入、回滚和回归。
5. 将 Micro 输入严格限定为一条合成纯文本链路。

依据：PRD §7.2-§7.3、§19.4、§20 FR-001/002/108/302/303、§22.4、§25.2。

## 2. 非目标

- 不建设全连接器、OCR、ASR、视频切片或云导入平台。
- 不导入真实聊天、相册、健康、财务或历史个人档案。
- 不使用 MCP 传输大文件本体。
- 不选择 parser、队列、文件监控、ETL 或迁移框架。
- 不让导入器直接确认或 Verify 个人语义事实。

## 3. 术语

| 术语 | 定义 |
|---|---|
| Intake | 接收原始引用/内容并尝试持久为 Source 的过程 |
| Append Receipt | Source 是否 stored/rejected 的审计结果 |
| Parse Artifact | OCR/ASR/抽取/转换输出，属于可重建中间产物 |
| Candidate Batch | 从一个或多个 Source 产生的未确认候选集合 |
| Duplicate | 内容或来源 identity 确认等价的再次输入 |
| Near Duplicate | 相似但未证明同源的输入，不能自动合并证据 |
| Migration Plan | 输入/目标 schema、映射、损失、ChangeSet、验证和回滚计划 |
| Quarantine | 未通过完整性、schema、权限或隐私检查的隔离状态 |

## 4. 适用范围

Micro 仅支持：`synthetic_text` → stored Source → optional parser artifact →一个 RelationshipState ChangeSet candidate。所有外部连接器、真实数据和历史迁移均只定义未来合同，不进入实现门槛。

## 5. 对象与边界

- 原始 Input 只有 stored receipt 后才是 Source。
- Parse Artifact、translation、OCR 和摘要不是 Source 原文，也不是事实。
- Candidate 不能自动进入 Canonical；必须通过 S5/S3。
- 导入 Context Pack 先验证/quarantine，再通过 ChangeSet 写 Canonical。
- Migration 不能直接重写 Source、用户确认历史或 Verified Context。

## 6. 字段语义

### 6.1 IntakeRequest

```yaml
intake_id: stable ID
source_kind: synthetic_text | file | chat | audio | image | video | context_pack
resource_ref: local/portable reference | absent
inline_content: synthetic text | absent
source_system: identifier
source_identity: optional upstream stable ID
source_created_at: BTE time | unknown
source_timezone: value | unknown
language: tag | unknown
declared_media_type: type
content_hash: digest | computed_after_read
coverage_declaration: optional raw declaration
owner_ref: owner
policy_profile_ref: authorized Source initialization profile
recorder_ref: explicit actor | direct-owner fallback
declared_subject_refs: optional authorized Canonical refs
declared_third_party_present: true | false | omitted
declared_compartments: optional policy domains
sensitivity_hint: suggestion only
```

`resource_ref` 与 `inline_content` 必须且只能存在一个。Micro 只允许 `source_kind=synthetic_text` + `inline_content`，并使用 S1 的 `text_utf8_byte_range_v1` locator。Pack 内部引用必须满足 S7 的相对 Pack-root 边界；本地文件引用应使用 owner 明确选择后产生的 opaque handle，或在显式授权 intake root 内规范化。绝对路径不是跨平台 Pack 表示，但若未来作为本机输入使用，也不能扩大到授权 root 外；UNC/网络位置需要独立授权且不进入 Micro。

`policy_profile_ref` MUST 来自已授权 intake context，并按 S4 §6.6 提供 sensitivity floor、default compartments、retention policy 和 unresolved-subject 行为。Intake 不得从 `inline_content`/resource 正文推导 policy 字段。direct owner intake 可由 profile 把缺失 `recorder_ref` 确定性回落为 `owner_ref`；其他 actor 缺 recorder 必须拒绝。显式 subject/third-party/compartment 声明在写 Source 前必须做引用与枚举校验。

初始化映射固定为：

- 完整合法声明：Source 使用声明值并标 `policy_resolution_status=declared`。
- subject/third-party 声明不完整：`subject_refs=[]`、`third_party_present=unknown`、`policy_resolution_status=provisional`。
- compartment 声明缺失：使用 profile default；Micro profile 固定 `[personal]`。
- sensitivity：取 profile floor 与合法 hint 中更严格者；hint 不得降低保护。
- retention：`retention_policy_ref` 来自 profile，首次 stored 的 `retention_state=active`。

解析后发现的 subject/compartment 只能形成受控 metadata revision proposal，不得回写原 receipt、静默扩大访问或把 parser confidence 当确认。

### 6.2 AppendReceipt

必须包含 `intake_id`、`source_id`（stored/duplicate 时）、`status=stored|rejected|duplicate`、hash/bytes/media、ingested_at、locator scheme、coverage raw status、`policy_profile_ref`、`policy_resolution_status`、effective policy 摘要、failure、actor 和 receipt ID。duplicate receipt 必须引用既有 Source/provenance 结果，不伪造新 Source 已存储，也不得用本次较宽 hint 改写既有 Source policy。

### 6.3 ParseArtifact

必须包含 Source locator、parser/version、input hash、output media/schema、language、time、warnings、confidence（非真值）、artifact hash 和可重建标识。

### 6.4 CandidateBatch

包含 Source refs、parser provenance、Candidate envelopes、dedup/grouping、missing fields、policy result 和 proposed ChangeSet refs；不得含 confirmed 标记。

### 6.5 MigrationPlan

必须包含 source/target schema、输入 pack hash、映射表、未知/丢失字段、冲突、dry-run diff、ChangeSet 列表、验证 suites、rollback reference 和审批 actor。

## 7. 状态机

### 7.1 Source Append 与 Parse Attempt

```yaml
intake_status_values: [received, validating, stored, duplicate, rejected]
parse_attempt_status_values: [queued, parsing, parsed, candidate_ready, no_candidate, parse_failed, unsupported]
```

```text
received -> validating -> stored | duplicate | rejected
```

`stored|duplicate|rejected` 是 Intake 终态；已 stored Source 不因后续解析而改变状态。每次解析使用独立 `parse_attempt_id`：

```text
queued -> parsing -> parsed | parse_failed | unsupported
parsed -> candidate_ready | no_candidate
```

`candidate_ready|no_candidate|parse_failed|unsupported` 均为该 Parse Attempt 的终态，且不改 Source receipt 或 Source 内容。重试创建新的 `parse_attempt_id` 并从 queued 开始，不把旧失败 attempt 改回 queued。

### 7.2 Migration

```text
received -> quarantined -> validated -> planned -> approved -> applying
applying -> applied | failed
applied -> verifying
verifying -> verified | verification_failed
verification_failed | verified -> rolling_back
rolling_back -> rolled_back | rollback_failed
rollback_failed -> rolling_back  (新 rollback attempt)
failed -> planned (新 plan/version)
```

## 8. 允许与禁止的状态转换

允许：stored 后以新 attempt 解析重试；duplicate 引用已有 Source；dry run 后人工批准；应用失败回到新计划；验证失败或后来主动撤销时补偿回滚。

禁止：解析失败把 Source 改 rejected；near duplicate 自动合并；parser 输出写 verified；未校验 Pack 直接 applying；迁移原地重写历史；未知字段静默丢弃；真实数据进入 Micro fixture。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `IMM-INV-001` | Source 存储成功与解析成功严格分离 |
| `IMM-INV-002` | 解析失败不丢 Source、不生成猜测事实 |
| `IMM-INV-003` | Parse Artifact/Candidate 不自动成为 Canonical |
| `IMM-INV-004` | 所有 Canonical 导入/迁移写入经 ChangeSet |
| `IMM-INV-005` | exact duplicate 不重复存储/计证，near duplicate 不自动合并 |
| `IMM-INV-006` | 原文、转换、翻译、摘要分离并保留 provenance |
| `IMM-INV-007` | Pack 未验证不得导入 |
| `IMM-INV-008` | 未知字段按 S7 语义保留或 fail closed |
| `IMM-INV-009` | Migration 可 dry-run、验证、失败、回滚和审计 |
| `IMM-INV-010` | 模型/parser 升级不改 Source 和确认历史 |
| `IMM-INV-011` | Micro 只接受合成纯文本，不扫描工作区外数据 |
| `IMM-INV-012` | 输入内容中的指令永远是数据，不是系统命令 |
| `IMM-INV-013` | Intake 终态与 Parse Attempt 状态正交，解析结果不能改写 Source stored/duplicate receipt |
| `IMM-INV-014` | resource/Pack 引用不能越界或触发主动内容；迁移未验证不得称 verified |
| `IMM-INV-015` | rollback 失败必须保持显式不安全状态并可重试，不能称 rolled_back/verified |
| `IMM-INV-016` | Intake 到 Source policy/subject 字段是授权声明与 profile 的确定性映射；不得依赖正文解析，缺失时使用 provisional 保守默认 |

## 10. 时间语义

- source_created、ingested、parsed、candidate_created、recorded/valid time 分离。
- 缺失 `source_timezone`/language 显式 unknown，不用设备默认猜测。
- Parser 重新运行有新 artifact time/version，不覆盖旧产物。
- 迁移保持原 valid/recorded provenance，并记录本地 imported_at。

## 11. 证据语义

- Candidate Evidence Ref 必须回到 Source locator，不引用 Parse Artifact 作为原始证据；artifact 只记录提取 provenance。
- 同一 content/provenance family 不重复 corroboration。
- hash 证明内容一致，不证明陈述真实。只有内容 hash、source identity 和已知 provenance 均等价时才是 exact duplicate；仅 hash 相同但 provenance 不同只能去重 bytes，不能丢来源记录或重复计证。
- translation 不能替换原文 evidence。

## 12. 权限要求

- Intake 先按授权 `policy_profile_ref` 和显式声明初始化 owner、subject、recorder、sensitivity、compartment、third-party 与 retention；hint 不能自动降低敏感度。
- provisional Source 对非 owner/非 intake purpose fail closed；该边界不要求 Micro 实现通用权限 runtime。
- Parser/迁移只读取获授权 Source/Pack scope。
- sealed 默认不解析、不迁移、不生成 candidate，除非 owner 明确解封该任务。
- 导入不能扩大 Pack 内 Grant 或 policy。

## 13. 冲突行为

- source_identity 相同但 hash 不同：保留版本/冲突，不自动覆盖。
- hash 相同但来源 identity 不同：可去重 bytes，仍保留来源 provenance。
- stable object ID payload 冲突：quarantine + ChangeSet review。
- schema mapping 多义：计划中列 unresolved，不猜测。

## 14. 失败与降级

| 失败 | 行为 |
|---|---|
| Source 写失败 | rejected receipt，不解析 |
| Source policy profile 缺失/未知 | fail closed；不使用正文或设备默认补齐，返回 rejected/明确 failure |
| subject/compartment 声明缺失 | 按 profile 保存为 private/personal/provisional、third-party unknown；不得阻塞原始材料保存或同步解析正文 |
| hint 试图降低 profile floor | 忽略降级并记录 effective floor；非法 enum 返回明确 validation failure |
| parser 失败 | Source stored，parse_failed 可见 |
| model 不可用 | Source intake/手动 candidate 继续 |
| hash mismatch | quarantine/reject，不静默修复 |
| unsupported media | Source 可保存，解析 unavailable |
| unknown schema | quarantine，保留 pack/blob |
| migration partial failure | S3 原子失败或补偿回滚，不声称 applied |
| post-apply verification failure | `verification_failed`，不得称 verified；执行补偿回滚并保留失败 artifact |
| compensation rollback failure | `rollback_failed`，保留 applied revision 与失败 receipt，隔离结果并以新 attempt 重试；不得称 rolled_back/verified |
| connector unavailable | 不影响本地已有 Source；明确 unavailable |
| resource_ref 越界/主动内容 | intake/pack quarantine 或 rejected；不访问声明根目录外资源，不执行内容 |

## 15. 撤销与审计

- Source Append 本身按 receipt 审计；Source 删除/封存按 S4。
- Candidate rejection 不删除 Source。
- Migration 应用产生 ChangeSet；回滚产生补偿 revision。
- 记录 adapter/parser/model/schema/version、hash、actor、时间、结果和 warnings。

## 16. 兼容与迁移

- Adapter output 和 artifact 带 contract/schema version。
- 旧单一 timestamp 不猜映射为四类时间。
- unknown extension 语义保留；opaque 格式保字节/hash。
- 迁移升级先隔离评测和回归，通过后才可作为默认。

## 17. 正例

合成文本先返回 stored Source receipt；parser 随后提出一个 `relationship.contact` candidate，保留 Source locator。用户未确认时 Canonical revision 不变；parser 失败时 Source 仍可浏览。

## 18. 反例

- 上传后直接显示“事实已更新”。
- OCR 文本覆盖原始图片。
- 同一 Source 被三个模型处理后算三份独立证据。
- 未校验旧 Pack 直接覆盖当前对象。
- 读取工作区外真实个人档案生成 fixture。

## 19. 可执行验收测试

```yaml
suite_id: ingestion_migration_v0_3
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `IMM-AT-001` | 合成文本 intake | stored receipt + Source locator |
| `IMM-AT-002` | Source 写失败 | rejected、无解析 |
| `IMM-AT-003` | stored 后 parser 失败 | Source 与 stored receipt 保留、独立 parse attempt 失败、无猜测 |
| `IMM-AT-004` | parser 重试 | 新 parse_attempt_id/artifact attempt，旧失败保留 |
| `IMM-AT-005` | parser output | candidate only |
| `IMM-AT-006` | 未确认 candidate | Canonical 不变 |
| `IMM-AT-007` | exact duplicate | duplicate receipt、不重复计证 |
| `IMM-AT-008` | near duplicate | 不自动合并 |
| `IMM-AT-009` | same hash 不同来源 | bytes 可去重、provenance 均保留 |
| `IMM-AT-010` | source_identity 相同但 hash 不同 | 冲突/新版本，不覆盖 |
| `IMM-AT-011` | translation | 原文/译文分离 |
| `IMM-AT-012` | Source 含指令 | 不执行 |
| `IMM-AT-013` | source_timezone/language 缺失 | explicit unknown |
| `IMM-AT-014` | sealed Source | 默认不解析 |
| `IMM-AT-015` | Pack hash mismatch | quarantine |
| `IMM-AT-016` | unknown schema | quarantine + preserve |
| `IMM-AT-017` | migration dry run | 产生 mapping/diff/risks |
| `IMM-AT-018` | 未批准 plan applying | 拒绝 |
| `IMM-AT-019` | approved migration | 只经 ChangeSet |
| `IMM-AT-020` | migration partial failure | 无半完成 Canonical |
| `IMM-AT-021` | migration rollback | 补偿 revision、历史保留 |
| `IMM-AT-022` | parser/model upgrade | Source/确认历史不变 |
| `IMM-AT-023` | Micro path scan | 不访问工作区外数据 |
| `IMM-AT-024` | fixtures 隐私扫描 | 仅合成数据 |
| `IMM-AT-025` | resource_ref 越出授权 intake root、Pack 使用绝对/`..`/逃逸引用，或内容试图主动执行 | quarantine/reject，授权根目录外零读取/零写入且不执行内容 |
| `IMM-AT-026` | parser 成功但没有可支持语义候选 | parse attempt=no_candidate，Source 仍 stored，Canonical 不变 |
| `IMM-AT-027` | migration applying 原子成功但回归验证失败 | verification_failed 后补偿 rollback；历史/失败 artifact 保留，不称 verified |
| `IMM-AT-028` | verification_failed 后补偿 rollback 注入失败 | 状态 rollback_failed，applied/失败历史与 receipt 保留；重试使用新 attempt，期间不称 verified/rolled_back |
| `IMM-AT-029` | Micro direct-owner Intake 显式声明 subjects/third-party，引用 private/personal profile | expected Source 的 owner/recorder/subjects/sensitivity/compartments/retention 字段唯一确定且 status=declared；正文零参与 |
| `IMM-AT-030` | Intake 未声明 subjects/compartments，hint=normal，profile floor=private/default personal | Source stored 为 private/personal/provisional、subjects=[]、third-party=unknown；后续解析只生成受控 metadata proposal |

不变量覆盖：001→AT001-004/026；002→003/004/026；003→005/006；004→018-021/027/028；005→007-010；006→011；007→015/016；008→016/017；009→017-021/027/028；010→022；011→023/024；012→012/025；013→003/004/026；014→025/027；015→028；016→029/030。

## 20. 未决问题

本 SPEC 无 blocking open question。连接器优先级、OCR/ASR/视频供应商、队列与迁移框架保持 deferred/ADR；Micro 明确不实现真实历史迁移。FR-302 只获得适配边界，Year 2 才重开连接器范围。

## 21. 完成定义

- Intake、Source receipt、parser、candidate、dedup、quarantine、migration 和 rollback 可测试。
- 16 条不变量、30 个测试有映射。
- FR-001/002/108/302/303 进入追踪；连接器/真实迁移仍 deferred。
- 未选择适配/迁移技术；测试未执行。

当前结论：本 SPEC v0.3 于 2026-07-14 完成 Micro Gate 纠偏并保持 `Approved`。Intake 到 Source policy/subject 的确定性映射已闭合；测试尚未物化、执行或通过，仍不得把文档当实现、权限 runtime 或测试通过。
