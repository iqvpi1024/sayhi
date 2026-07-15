# Privacy & Access Policy SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-PAP-001` |
| 版本 | `0.4` |
| 状态 | `Approved` |
| 产品基线 | `PRDv05.md` v0.5 |
| 上游 | S1 v0.5、S2-S3 v0.4，均 `Approved` |
| 产品裁决 | `IQ-011`、`IQ-012`、`IQ-013`、`IQ-017`，2026-07-13 已决定 |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| v0.5 兼容复审 | 2026-07-15；为 unarchive/unseal/restore 建立显式授权与 ChangeSet operation 映射 |

本文定义授权、封存、删除和导出语义，不选择身份供应商、加密算法、密钥库或云服务。

## 1. 目标

1. 默认拒绝并按调用者、目的、舱室、字段、时间和动作做最小披露。
2. 让 owner、subject、recorder、viewer/caller 明确分离。
3. 阻止 Derived View、摘要、错误信息和推断旁路泄露受限内容。
4. 区分 archive、seal、soft delete、hard delete 与降权。
5. 对删除、备份、审计和导出给出诚实可验证的回执。

依据：PRD §6.10、§6.13、§12.4、§17、§19、§20 FR-012/304/305、§21.4、§25、§26 Case D。

## 2. 非目标

- 不实现多租户、家庭协作、数字遗产或法律代理流程。
- 不选择认证、加密、密钥管理或安全硬件。
- 不允许 Micro-MVP 外部 Agent 读取真实个人数据。
- 不承诺删除用户已自行导出的外部副本。
- 不定义 UI 视觉设计或最终法律文案。

## 3. 术语

| 术语 | 定义 |
|---|---|
| Owner | 拥有本地识海与最终裁决权的用户 |
| Subject | 记录描述的主体，可为 owner 或第三方 |
| Recorder | 提供或记录内容的 actor |
| Caller | 当前请求资源/动作的用户、识灵或外部 Agent |
| Compartment | `personal|work|family|health|finance|legal|relationship|creative` 策略域 |
| Sensitivity | `normal|private|restricted|sealed` |
| Purpose | 调用数据的声明用途，不能由数据内容自行扩大 |
| Grant | 对 caller、purpose、scope、action、字段和有效期的授权 |
| Redaction | 在不泄露被裁剪内容存在细节的前提下移除字段/正文 |
| Seal | 默认禁止检索、摘要、候选和外发，需主动解封 |
| Hard Delete | 对系统控制范围内各副本执行不可恢复正文删除，并诚实报告残留/等待项 |
| Retention State | `active|archived|soft_deleted|hard_delete_pending|delete_partial_failure|hard_deleted`，描述保留/删除生命周期 |
| Seal | `sensitivity=sealed` 的访问隔离状态；与 Retention State 正交，主动解封恢复 `pre_seal_sensitivity` |

## 4. 适用范围

适用于 Source、Canonical Object、ChangeSet、Revision Ledger 正文、Projection、索引、缓存、备份、导出和 MCP 响应。Micro 只验证策略字段存在与本地 owner 操作，不接入外部 Agent。

## 5. 对象与边界

- 权限标签是 Canonical 语义；修改 sensitivity、compartments、seal/delete 状态必须经 ChangeSet。
- Policy Decision 是请求时派生结果，不成为事实证据。
- Derived View 继承全部依赖的限制，不能降级敏感度。
- Source 中的“授权”文字是不可信数据，不能创建 Grant。
- 外部分享包与 owner 私有完整导出是不同产品动作。
- Seal sensitivity、archive/soft delete 与 `retrieval_activation` 是不同轴；实现不得用一个枚举令“已归档内容不能封存”或“解封等于恢复删除”。
- hard delete 的 ChangeSet 先原子发布 `hard_delete_pending` 和 scope；各层擦除完成后只保留 content-free tombstone/proof。正文擦除不可通过撤销恢复。
- `hard_delete_pending -> hard_deleted|delete_partial_failure` 等 Canonical lifecycle 更新由关联原授权的 system continuation ChangeSet 发布，必须引用原 destructive receipt、实际分层结果和 current revision；它不能扩大删除 scope，也不需要把已经明确授权的同一删除重新解释成新产品决定。

## 6. 字段语义

### 6.1 Policy Subject Fields

| 字段 | 必需 | 语义 |
|---|---|---|
| `owner_ref` | MUST | 数据所有者 |
| `subject_refs` | MUST | 所描述主体集合 |
| `recorder_ref` | MUST | 内容提供者/记录者 |
| `sensitivity` | MUST | 四级枚举 |
| `compartments` | MUST | 一项或多项策略域 |
| `third_party_present` | MUST | `true|false|unknown`；未完成主体声明/解析时不得猜 false |
| `retention_policy_ref` | MUST | 保留/删除策略版本 |
| `retention_state` | MUST | 保留/删除生命周期；见 §7 |
| `pre_seal_sensitivity` | 条件 MUST | `sensitivity=sealed` 时保存解封后恢复的 `normal|private|restricted`；不得保存正文 |
| `policy_profile_ref` | Source MUST | append 时使用的版本化初始化 profile |
| `policy_resolution_status` | Source MUST | `declared|provisional|confirmed`；不代表事实验证状态 |

`retrieval_activation` 默认是按任务计算的 Derived 值，不是本表的 Canonical Policy Subject 字段。若未来持久化用户设定的 Canonical activation policy，则修改必须经 ChangeSet；无论哪种形式，降权都不得改变真值、sensitivity 或 retention state。

### 6.2 AccessRequest

```yaml
privacy_lifecycle_action_values: [archive, unarchive, seal, unseal, soft_delete, restore, hard_delete]
```

```yaml
caller_ref: actor
purpose: declared purpose
action: read | search | summarize | propose | append | approve | mutate | revert | export_private | share_external | archive | unarchive | seal | unseal | soft_delete | restore | hard_delete
resource_refs: requested scope
field_paths: requested fields
valid_time_scope: optional
authorization_refs: owner_session, explicit grant, or capability refs
requested_at: timestamp
```

Policy action 与 S3 proposal operation MUST 一一对应：`archive`、`unarchive`、`seal`、`unseal`、`soft_delete`、`restore`、`hard_delete` 使用同名 operation。`revert` 只授权整包补偿 ChangeSet，不得代替 `unarchive|unseal|restore`；`restore` 只恢复 policy 允许窗口内的 soft delete，不得恢复 hard delete。

### 6.3 PolicyDecision

```yaml
decision: allow | deny | allow_with_redaction
allowed_fields: paths
denied_fields: paths
effective_until: timestamp | request_end
reason_code: non-leaking code
policy_revision: version
audit_ref: reference
```

### 6.4 Grant

Grant MUST 绑定 caller、purpose、actions、resource/field scope、开始/到期、grantor 和可撤销状态；不得使用永久“访问全部”隐式授权。

### 6.5 DeletionReceipt

必须逐层报告 `live_source`、`canonical_payload`、`ledger_payload`、`derived_index`、`cache`、`backup`、`export_copy`、`minimal_audit_proof` 的 `deleted|pending_expiry|not_present|not_applicable|out_of_control|failed`，并带 policy、时间和失败原因。`minimal_audit_proof` 只能为 `retained_content_free|not_present|failed`，不得把 proof 自身写成“正文已删除”的替代副本。

### 6.6 Source Policy Initialization Profile

Source Append 使用的版本化 profile MUST 至少声明：`policy_profile_ref`、`sensitivity_floor`、`default_compartments`、`retention_policy_ref`、direct-owner recorder fallback 和 unresolved subject 的 fail-closed 行为。profile 来自已授权 intake context，不得来自 Source 正文、parser、模型或 `sensitivity_hint`。

初始化规则是封闭的：

1. `owner_ref` 来自已授权 intake context。
2. `recorder_ref` 必须显式提供；仅 direct owner intake 可按 profile 回落为 `owner_ref`。
3. 完整、已校验的 `declared_subject_refs` 和 `declared_third_party_present` 写为 `policy_resolution_status=declared`。
4. 主体声明缺失时写 `subject_refs=[]`、`third_party_present=unknown`、`policy_resolution_status=provisional`；不得解析正文同步猜测。
5. compartment 声明缺失时使用 profile 的 `default_compartments`；Micro profile 固定为 `[personal]`。
6. effective sensitivity 取 profile floor 与合法 hint 中更严格者；hint 不能降低保护。
7. 初次成功 append 的 `retention_state=active`，`retention_policy_ref` 来自 profile。

provisional Source 仅允许已授权 owner/intake purpose 继续保存、查看或产生候选；任何外部/跨 purpose 读取 fail closed。后续主体、compartment 或 sensitivity 修订必须走受控操作，且不得因模型推断自动扩大访问或降低保护。该合同不要求 Micro 建设通用权限 runtime。

## 7. 状态机

```yaml
third_party_present_values: [true, false, unknown]
source_policy_resolution_status_values: [declared, provisional, confirmed]
```

Retention 与封存敏感度使用两个独立状态机：

```text
retention_state:
  active -> archived       (operation=archive)
  archived -> active       (operation=unarchive)
  active | archived -> soft_deleted
  soft_deleted -> active | archived  (operation=restore，仅在 policy 撤销窗口内)
  active | archived | soft_deleted -> hard_delete_pending
  hard_delete_pending -> hard_deleted | delete_partial_failure
  delete_partial_failure -> hard_delete_pending

sensitivity seal transition:
  normal | private | restricted -> sealed  (operation=seal)
  sealed -> pre_seal_sensitivity  (operation=unseal，仅 owner 主动)

source policy resolution:
  provisional -> declared | confirmed  (仅受控 metadata revision)
  declared -> confirmed                (仅 owner 明确确认)
```

`hard_deleted` 为正文不可恢复终态，此时正文 sensitivity 不再可恢复。在 hard delete 完成前，原有 sealed 限制继续生效。降权只改变 `retrieval_activation`，不属于上述状态机，也不改变真值。Source policy resolution 不回写 append receipt；新歧义需要纠正时创建新的 provisional metadata revision 并维持或提高保护，不能用原地倒退扩大访问。

## 8. 允许与禁止的状态转换

允许：owner 以 `unseal` 主动解封且不改变 retention；以 `unarchive` 恢复 archived；以 `restore` 在软删除窗口内恢复到删除前的 active/archived 状态；硬删除失败后重试未完成层；临时 Grant 到期自动失效；provisional Source 经受控修订补充声明或由 owner 确认。

禁止：Agent 自动解封；sealed 内容进入检索/摘要/候选；权限不足时用相关关系猜测；把 archive 当删除；把 unseal 当 restore；删除失败仍返回 completed；分享动作复用 owner 全量导出权限；parser/model 直接把 provisional 改为 declared/confirmed 或降低 Source 保护。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `PAP-INV-001` | 无明确允许即拒绝 |
| `PAP-INV-002` | 多舱室取所有适用策略的最严格交集 |
| `PAP-INV-003` | Derived View 不得降低输入限制 |
| `PAP-INV-004` | sealed 从检索、摘要、候选、训练/评测和外发全部排除 |
| `PAP-INV-005` | 权限拒绝不得通过计数、错误或摘要泄露 |
| `PAP-INV-006` | 临时授权有目的、范围和到期时间 |
| `PAP-INV-007` | 第三方分享默认脱敏 |
| `PAP-INV-008` | 私有导出与外部分享策略分离 |
| `PAP-INV-009` | 删除回执逐层诚实，不承诺控制范围外副本 |
| `PAP-INV-010` | 审计最小证明不保留已硬删除正文 |
| `PAP-INV-011` | 权限标签和 destructive 状态修改经 ChangeSet |
| `PAP-INV-012` | 频繁访问/降权不改变真值或 sensitivity |
| `PAP-INV-013` | sealed sensitivity、retention 与 retrieval activation 正交，任一轴转换不得隐式修改另两轴 |
| `PAP-INV-014` | 被硬删除 Source/正文不能继续支撑 verified 回答；依赖对象与 View 必须失效并重评估 |
| `PAP-INV-015` | Source policy 由获授权声明与 profile 确定性初始化；未解析主体使用 provisional/unknown 保守默认，hint 不得降低保护 |
| `PAP-INV-016` | archive/seal/soft delete 的逆向授权与 ChangeSet operation 分别为 unarchive/unseal/restore，且不得恢复 hard delete 或隐式修改其他状态轴 |

## 10. 时间语义

- Grant 必须有明确有效期或单请求生命周期。
- Policy evaluation 使用请求时刻和 policy revision。
- 删除回执分别记录请求、开始、各层完成和最终/部分完成时间。
- backup `pending_expiry` 必须给出适用 retention deadline；没有政策不得虚构日期。

## 11. 证据语义

- PolicyDecision、Grant 和授权日志不是个人事实证据。
- Source Evidence Ref 只有在字段级授权后可返回。
- 脱敏摘要不能反向成为更低敏感度的证据。
- 隐藏证据会使答案不安全时 fail closed，不透露隐藏证据数量或类型。

## 12. 权限要求

经 `IQ-013` 裁决，多舱室记录应用策略交集和最严格 sensitivity；冲突默认 deny。字段允许集合取交集，禁止集合取并集。Derived View 继承依赖的 compartments 合集和最严格 sensitivity。

owner 对本地 `normal` 数据的读取仍需有效 owner session 和匹配 purpose，不等于永久全库 Grant。`private/restricted` 继续要求相应明确授权，`sealed` 必须先由 owner 主动 unseal。

destructive action 必须 owner 明确授权并重新认证（具体机制后置 ADR）；外部 Agent 无默认 destructive 权限。

## 13. 冲突行为

- 普通 Grant 只能满足策略声明的“需要明确授权”，不能覆盖 absolute deny、sealed、字段禁止或 destructive re-auth 要求。Grant 与 caller/purpose/scope/time 任一不匹配即 deny。
- 多 policy 无法求交时 deny 并记录非泄露原因。
- 第三方与 owner 权益冲突时，外部分享默认裁剪第三方正文；法律例外后置。

## 14. 失败与降级

| 失败 | MUST 行为 |
|---|---|
| policy engine 不可用 | 所有受控 payload、mutate、destructive 和 external 请求 fail closed；不得用缓存 decision 猜测当前授权 |
| Grant 过期/不明 | deny |
| 字段裁剪失败 | 不返回 payload |
| seal 传播失败 | 标记不安全并停止检索/外发，不声称完成 |
| hard delete 部分失败 | `delete_partial_failure` + 分层 receipt |
| backup 不可即时清除 | `pending_expiry`，列政策期限，不称已删除 |
| 外部导出副本 | `out_of_control`，不得声称召回 |
| Source 主体/compartment 声明缺失 | 使用 profile 保守默认并标 provisional；非 owner/非 intake purpose fail closed，不为完成 append 解析正文 |
| hint/profile 冲突 | 采用更严格值；非法枚举或试图降低 floor 的声明不得生效 |

## 15. 撤销与审计

- archive、seal、soft delete 可按状态机撤销；hard delete 正文不可恢复。
- 每个授权与 destructive action 记录 actor、purpose、scope、policy revision 和结果。
- 硬删除审计只保留对象不可逆标识摘要、时间、scope 和结果，不保留正文/敏感字段。
- 删除 Source 或 evidence payload 后，所有依赖 Assertion/State/Answer/View 必须失效并按剩余可见证据重评估；不得保留旧 `verified` 结果或由 Derived 副本复原正文。

## 16. 兼容与迁移

- 未知 sensitivity/compartment/action 必须 fail closed 并保留扩展。
- 旧数据缺权限标签时默认 `private`，不得默认 normal。
- 旧 Source 缺主体解析状态时迁移为 `policy_resolution_status=provisional`、`third_party_present=unknown`，不得根据正文批量猜测。
- 迁移不得扩大 Grant 或解封 sealed。
- 导出/导入必须保留策略版本与未知扩展语义。

## 17. 正例

工作用途请求同时命中 `work` 与 `relationship`：只返回两域都允许的字段；受限第三方正文被裁剪，响应说明未使用隐藏内容但不泄露其细节。

## 18. 反例

- “本地运行”被当成读取所有 sealed 数据的授权。
- 工作 Agent 根据隐藏健康摘要猜测会议能力。
- hard delete 只清缓存就返回 completed。
- 对外分享直接使用 owner 私有全量 Context Pack。

## 19. 可执行验收测试

```yaml
suite_id: privacy_access_policy_v0_4
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `PAP-AT-001` | 无 Grant 外部 caller 读取 private | deny |
| `PAP-AT-002` | normal + 本地授权 purpose | 仅允许请求字段 |
| `PAP-AT-003` | work+relationship 策略合并 | 返回交集 |
| `PAP-AT-004` | 一个 policy deny | 整体 deny/裁剪 |
| `PAP-AT-005` | Derived View 汇总 restricted | 继承 restricted |
| `PAP-AT-006` | sealed 搜索 | 零 payload 且不泄露存在 |
| `PAP-AT-007` | sealed 摘要/候选/外发 | 全部拒绝 |
| `PAP-AT-008` | 临时 Grant 到期 | 自动 deny |
| `PAP-AT-009` | Grant purpose 不匹配 | deny |
| `PAP-AT-010` | 低权限错误响应 | 不含隐藏计数/字段 |
| `PAP-AT-011` | 私有完整导出 | owner 授权范围内完整、带清单 |
| `PAP-AT-012` | 外部分享导出 | 第三方默认脱敏、最小字段 |
| `PAP-AT-013` | archive | 默认工作集移除、仍可授权搜索；sensitivity 不变 |
| `PAP-AT-014` | seal/unseal | 仅 owner 主动切换；解封恢复 pre_seal_sensitivity，retention_state 不变 |
| `PAP-AT-015` | soft delete/restore | 窗口内恢复到删除前 retention；sensitivity 不变 |
| `PAP-AT-016` | hard delete 全层成功 | content-free proof + completed receipt |
| `PAP-AT-017` | backup 待到期 | pending_expiry，不称 completed |
| `PAP-AT-018` | 一层删除失败 | partial failure 明确列出 |
| `PAP-AT-019` | 用户自持外部副本 | out_of_control |
| `PAP-AT-020` | 绕过 ChangeSet 改 sensitivity | 拒绝 |
| `PAP-AT-021` | 降权 | truth/review status 不变 |
| `PAP-AT-022` | policy engine 失败 | fail closed |
| `PAP-AT-023` | 未知 policy enum 导入 | 保留但 deny |
| `PAP-AT-024` | 全部 fixture 扫描 | 仅合成数据 |
| `PAP-AT-025` | 无明确法律/产品 Grant 的继承请求 | 默认 deny，不返回第三方正文 |
| `PAP-AT-026` | archived 对象被 seal 后再 unseal | 仍为 archived，不因轴切换回 active |
| `PAP-AT-027` | 支撑 verified 回答的唯一 Source 被 hard delete | Source 正文不可恢复；依赖 Answer/View 失效并降级为剩余证据对应状态 |
| `PAP-AT-028` | policy engine 不可用且存在旧 allow decision | 不返回缓存 payload，明确 unavailable/deny 且不泄露资源 |
| `PAP-AT-029` | direct owner Intake 显式声明 subjects、third-party 和 compartments，并引用固定 profile | Source policy 字段由声明/profile 唯一产生，状态 declared；正文内容不参与初始化 |
| `PAP-AT-030` | Intake 缺少 subject/compartment 声明且给出 `normal` hint，profile floor 为 private/personal；parser 后来提出 subject | Source 先为 private/personal/provisional、subjects=[]、third-party=unknown；非 owner/非 intake purpose deny；parser 只产生 metadata proposal，owner 确认后新 revision 才为 confirmed |
| `PAP-AT-031` | caller 分别请求 unarchive/unseal/restore，并尝试 restore hard-deleted payload | 前三者只有同名授权与 S3 operation 都通过时生效且不改变其他轴；hard delete restore 永久拒绝，`revert/correct` 不得替代 |

不变量覆盖：001→AT001/022/025/028/030；002→003/004；003→005；004→006/007；005→010/028；006→008/009；007→012/025；008→011/012；009→016-019；010→016；011→020；012→021；013→013-015/026；014→027；015→029/030；016→AT031。

## 20. 未决问题

本 SPEC 无 blocking open question。已决定：

- `IQ-011`：硬删除按系统控制层逐项完成；备份可 pending expiry；无固定政策不承诺期限。
- `IQ-012`：owner 私有完整导出与外部分享导出是不同策略。
- `IQ-013`：多舱室取最严格交集，冲突 deny。
- `IQ-017`：Canonical 权限/封存/删除语义经 ChangeSet。

家庭授权、数字遗产、法律例外和密钥恢复保持 deferred，不进入 Micro/首年实现。

## 21. 完成定义

- 默认拒绝、字段裁剪、sealed、防旁路和 destructive action 可测试。
- 删除不作虚假承诺，私有/分享导出分离。
- 16 条不变量与 31 个测试有映射。
- FR-012/304/305 进入追踪，但后两者实现仍按路线图 deferred。
- 测试未执行、未选择安全技术栈。

当前结论：本 SPEC v0.4 于 2026-07-15 完成 PRD v0.5 兼容复审并保持 `Approved`。Source policy 保守初始化继续有效，隐私生命周期正向/逆向动作已与 S3 一一映射；测试仍未物化、执行或通过，不授权权限 runtime、家庭协作、数字遗产或外部 Agent 实现。
