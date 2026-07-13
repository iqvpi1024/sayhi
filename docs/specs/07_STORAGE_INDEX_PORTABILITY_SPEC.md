# Storage, Index & Portability SPEC

## 0. 文档信息

| 字段 | 值 |
|---|---|
| 文档 ID | `SPEC-SIP-001` |
| 版本 | `0.2` |
| 状态 | `Approved` |
| 产品基线 | `PRDv04.md` v0.4 |
| 上游 | S1-S6 `Approved` |
| 产品裁决 | `IQ-006`、`IQ-011`、`IQ-012`、`IQ-015`，2026-07-13 已决定 |
| 实现状态 | 未开始 |
| 测试状态 | `suite_defined=true`、`suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 独立审计 | 2026-07-14；补齐 Pack 快照、路径安全与策略感知重建合同 |

本文定义逻辑持久与可移植合同，不选择数据库、对象存储、向量库、图数据库、文件系统布局或云服务。

## 1. 目标

1. 分离 Source Vault、Canonical Context、Revision Ledger 与 Derived Index。
2. 确保 Source/Canonical 可脱离当前软件读取和迁移。
3. 定义 Markdown + structured JSON Context Pack、清单、校验和导入前验证。
4. 保证未知扩展字段语义往返，Derived 可删除重建。
5. 让删除、备份、容量和重建结果可验证且不夸大。

依据：PRD §1、§7-§8、§16、§20 FR-002/301/303、§21、§25。

## 2. 非目标

- 不选择最终数据库、图模型、向量库、事件溯源或云供应商。
- 不实现多设备同步、连接器或真实历史迁移。
- 不把 Markdown 用作事务协调器。
- 不要求 JSON-LD/RDF 作为 MVP 依赖。
- 不承诺删除用户已带走的外部副本。

## 3. 术语

| 术语 | 定义 |
|---|---|
| Source Vault | 原始内容、manifest、hash、locator 与覆盖声明的持久层 |
| Canonical Store | 当前与历史规范对象的逻辑持久层 |
| Revision Ledger | ChangeSet、确认、发布、撤销和 revision 的审计层 |
| Derived Index | 搜索、Embedding、图索引、缓存、统计、摘要等可重建层 |
| Context Pack | 独立可读、版本化、带清单和校验的导出包 |
| Manifest | 文件/对象、类型、大小、hash、schema、依赖和策略的清单 |
| Round Trip | export→import→export 后语义等价 |
| Rebuild | 只从授权 Source/Canonical/Ledger 重新生成 Derived 数据 |
| Orphan | 引用目标缺失或不可解析的记录 |

## 4. 适用范围

逻辑层适用于单用户本地实例。容量目标是设计/测试 profile，不是 Micro 验收：百万 Assertion/State、千万 Source 片段、1 TB 原始媒体、十年以上跨度。

## 5. 对象与边界

- Source Vault、Canonical Store、Ledger 是规范持久层；Derived Index 不是事实源。
- Source 原始内容尽量不可变；更正以新 Source/受控元数据修订表达，删除按 S4。
- Canonical 对象必须有 `schema_version`、`object_revision` 和稳定 ID。
- Ledger 可保留审计，但硬删除后只留不含正文的最小证明。
- Context Pack 是传输/备份表示，不是运行时唯一真相源。

## 6. 字段语义

### 6.1 Storage Manifest Entry

```yaml
entry_id: stable ID
logical_layer: source | canonical | ledger | derived
media_type: declared type
schema_version: version
content_ref: relative portable path or object ref
byte_length: integer
hash_algorithm: named algorithm
content_hash: digest
owner_ref: owner
sensitivity: policy label
pre_seal_sensitivity: normal | private | restricted | not_applicable
compartments: [policy domain]
retention_state: policy lifecycle state
policy_revision: version
dependencies: [entry_id]
created_at: timestamp
```

`content_ref` MUST 是以 Pack 根目录为边界的规范化相对引用；绝对路径、盘符、UNC、`..` 越界、符号链接/重解析点逃逸或解包后指向 Pack 外的引用均不得进入 validated。Manifest 中的 policy 字段不得低于实际内容限制。

### 6.2 Context Pack

必须包含：pack manifest、Source 原始文件/清单、Canonical structured JSON、human-readable Markdown、Ledger 可共享范围、schema/policy 版本、hash 清单、未知扩展和导入说明。JSON-LD MAY 作为附加表示。

### 6.3 Narrative Context

经 `IQ-006` 裁决，Canonical `narrative_context` 默认保存 Source locator 和可选最小用户自写 note，不复制原始敏感正文。Context Pack 可在 owner 私有完整导出中按 policy 内联相应 Source；分享导出仍按 S4 裁剪。

### 6.4 Unknown Extensions

经 `IQ-015` 裁决，结构化未知字段必须保留字段名、命名空间、类型、嵌套和值语义；不保证 JSON 对象键顺序、空白或原始字节。需要字节保真的未知格式必须作为 opaque Source blob + media type/hash 保存，不能假称已理解。

### 6.5 Rebuild Receipt

记录输入 revision/policy、目标 index、开始/结束、成功/失败/跳过计数、orphan、hash 和 `view_revision`。

## 7. 状态机

### 7.1 Pack

```text
requested -> assembling -> validated -> exported
assembling | validated -> failed
```

`exported` Pack 是某个 `data_revision` 的不可变快照，不因后续导出而 supersede 或失效。与当前 Canonical 的关系由查询时 `pack_relation=current|historical|unknown` 派生；不得改写旧 Pack。

### 7.2 Import Validation

```text
received -> quarantined -> validated -> eligible_for_import
quarantined | validated -> rejected
```

eligible 不等于已写入；Canonical 导入仍经 S9/S3 ChangeSet。

### 7.3 Derived Rebuild

```text
absent | stale -> rebuilding -> fresh | failed
fresh -> stale
failed -> rebuilding
```

## 8. 允许与禁止的状态转换

允许：删除 Derived 后重建；验证 Pack 后提出导入 ChangeSet；schema 升级生成新表示；owner 导出完整包。

禁止：Derived 回写 Canonical；未校验 Pack 直接导入；未知字段静默丢弃；hash mismatch 标 validated；把 Markdown 当原子事务；用备份 pending 伪称 hard delete complete。

## 9. 系统不变量

| ID | 不变量 |
|---|---|
| `SIP-INV-001` | Source/Canonical/Ledger/Derived 逻辑边界不可混用 |
| `SIP-INV-002` | Derived 可完全删除并从规范层重建 |
| `SIP-INV-003` | Derived 永远不是直接事实证据 |
| `SIP-INV-004` | Context Pack 有 manifest、版本、hash 和独立可读表示 |
| `SIP-INV-005` | 未知结构字段语义往返保留 |
| `SIP-INV-006` | 不理解的 opaque 内容按 Source blob 保存，不猜测 Schema |
| `SIP-INV-007` | hash mismatch 不得进入 validated/imported |
| `SIP-INV-008` | narrative_context 默认 locator，不复制敏感正文 |
| `SIP-INV-009` | 删除状态逐层诚实并服从 S4 |
| `SIP-INV-010` | 原文与翻译分离，翻译不覆盖 Source |
| `SIP-INV-011` | Pack 权限不低于所含最敏感内容 |
| `SIP-INV-012` | 容量/SLO 结果只适用于声明 workload/profile |
| `SIP-INV-013` | Pack 引用和解包结果不能逃逸 Pack 根目录或触发主动内容执行 |
| `SIP-INV-014` | Derived rebuild 只读取当前获授权且未 sealed/删除的输入，并对排除项诚实记账 |

## 10. 时间语义

- Manifest `created_at` 不替代 Source/valid/recorded time。
- Pack 记录 `exported_at` 与 included `data_revision`。
- Derived freshness 绑定 data/view revision 和生成时间。
- Backup retention、delete pending expiry 使用 S4 policy，不虚构期限。

## 11. 证据语义

- Pack hash 证明内容完整性，不证明个人事实真伪。
- Markdown 是人类可读投影，不能替代 structured Canonical 或 Source locator。
- Derived search hit/Embedding 不能成为 Evidence Ref。
- Source 原文与转换/翻译保留 provenance。

## 12. 权限要求

- owner 私有完整导出与外部分享导出分开。
- sealed 默认不进入任何导出，除非 owner 对该次私有导出明确解封/包含。
- Pack manifest 本身也需裁剪，不能泄露隐藏条目名称/计数。
- 导入 Pack 不能扩大原 policy/Grant。
- 导入内容一律视为 inert data；manifest、Markdown、扩展字段或文件名不能触发命令、脚本、网络访问或权限变更。

## 13. 冲突行为

- 相同 stable ID 不同 payload/hash 进入 import conflict，不覆盖。
- schema version 不兼容时 quarantine/reject，不猜映射。
- Round-trip semantic diff 必须列未知字段、枚举和 policy 差异。
- Derived 重建差异不能反向修改 Canonical。

## 14. 失败与降级

| 失败 | 行为 |
|---|---|
| Source 写失败 | 明确失败，不返回 stored |
| Canonical/Ledger 原子失败 | 由 S3 保持旧安全 revision |
| Derived 写失败 | 退化为 Canonical/全文/时间查询并标状态 |
| Pack 某条 hash mismatch | 整包不 eligible，列失败条目 |
| Markdown 生成失败 | structured pack 可失败/部分结果，但不得称完整导出 |
| unknown extension 不可解析 | opaque 保留或拒绝，不丢弃 |
| rebuild 失败 | 旧 View stale 或 unavailable，不影响 Canonical |
| content_ref 越界/主动内容 | 整包 quarantine/reject，不解析或执行目标内容 |

## 15. 撤销与审计

- 导出不改变 Canonical，无需撤销，但记录范围、policy、revision 和 receipt。
- 导入/迁移通过 ChangeSet 可撤销。
- 新 Pack 不删除、覆盖或使用户已有 Pack 失效；每个 Pack 保持其 snapshot revision 与 hash。
- 删除 receipt 按层记录；hard-deleted 正文不留在审计。

## 16. 兼容与迁移

- 每层和 Pack 都有 schema version。
- 读取器必须忽略但保留未知 namespaced 字段。
- 重大 schema 升级先导出/验证/迁移/回归，不原地静默重写。
- 最低可读合同是公开说明的文件、Markdown 与 structured JSON；具体 Schema 随 SPEC 版本发布。

## 17. 正例

停止当前应用后，用户仍可用普通文件工具看到 Source 清单和 Markdown，用通用 JSON 解析器读取 Canonical；删除 Derived 后按 manifest/revision 重建相同语义 View。

## 18. 反例

- 只有专有数据库文件、无导出 Schema。
- 只有 Markdown 摘要，丢失 Canonical 类型/证据。
- 未知扩展导入后消失。
- Embedding 被列为 fact evidence。
- 删除缓存后称“所有备份已硬删除”。

## 19. 可执行验收测试

```yaml
suite_id: storage_portability_v0_2
suite_defined: true
suite_materialized: false
suite_executed: false
suite_passed: false
```

| Test ID | Given/When | Then |
|---|---|---|
| `SIP-AT-001` | 导出 pack | manifest/JSON/Markdown/Source 清单存在 |
| `SIP-AT-002` | 停止应用读取 | 普通工具可读 |
| `SIP-AT-003` | 校验全部 entry hash | 一致 |
| `SIP-AT-004` | 一条 hash mismatch | pack 不 eligible |
| `SIP-AT-005` | 删除 Derived 后重建 | 语义 View 等价 |
| `SIP-AT-006` | Derived 作为 evidence | 拒绝 |
| `SIP-AT-007` | unknown namespaced object 往返 | 名称/类型/值保留 |
| `SIP-AT-008` | JSON 键顺序变化 | 仍语义等价 |
| `SIP-AT-009` | opaque unknown media | blob/hash/media type 保留 |
| `SIP-AT-010` | narrative context | Canonical 只含 locator/最小 note |
| `SIP-AT-011` | 原文与翻译 | 两者分离且 provenance 存在 |
| `SIP-AT-012` | ID 相同 payload 不同 | import conflict |
| `SIP-AT-013` | unknown core type | quarantine/reject |
| `SIP-AT-014` | owner private export | policy 允许内容完整 |
| `SIP-AT-015` | external share export | 裁剪第三方/受限字段 |
| `SIP-AT-016` | sealed 默认导出 | 排除且不泄露 manifest |
| `SIP-AT-017` | live/index/cache delete | 分层 receipt |
| `SIP-AT-018` | backup pending expiry | 不称 complete |
| `SIP-AT-019` | rebuild failure | Canonical 安全、View stale/unavailable |
| `SIP-AT-020` | Markdown 失败 | 不称完整 pack |
| `SIP-AT-021` | schema 升级 | 旧 Source/确认历史不变 |
| `SIP-AT-022` | 容量 workload | 结果绑定 profile |
| `SIP-AT-023` | Pack manifest 隐私扫描 | 不泄露 excluded entries |
| `SIP-AT-024` | fixture 扫描 | 仅合成数据 |
| `SIP-AT-025` | manifest 含绝对路径、`..`、UNC 或解包逃逸链接 | pack quarantine/reject，Pack 外文件零读取/零写入 |
| `SIP-AT-026` | 新导出完成后读取旧 Pack | 旧 Pack hash/revision/内容不变，关系只显示 historical |
| `SIP-AT-027` | Derived rebuild 输入含 sealed、soft/hard deleted 或无权限条目 | 不读取/不重建这些条目，receipt 只给非泄露 skip 结果，Derived 不残留旧 payload |

不变量覆盖：001→AT001/005；002→005/019；003→006；004→001-004/026；005→007/008；006→009/013；007→003/004；008→010；009→017/018/027；010→011；011→014-016/023；012→022；013→025；014→027。

## 20. 未决问题

本 SPEC 无 blocking open question。已决定：

- `IQ-006`：narrative_context 默认 Source locator + 最小 user note。
- `IQ-011`：删除按控制层分项，备份可 pending expiry。
- `IQ-012`：私有完整导出与外部分享策略分离。
- `IQ-015`：未知结构保语义，不承诺键顺序/字节；opaque blob 保字节。

数据库、文件布局、hash 默认算法、压缩、备份介质与多设备同步进入实现 ADR/Year 2。

## 21. 完成定义

- 四逻辑层、Pack、round-trip、rebuild、删除和权限合同可测试。
- 14 条不变量、27 个测试有映射。
- FR-002/301/303 进入追踪；FR-301 实现仍 deferred。
- 未选择存储技术；测试未执行。

当前结论：本 SPEC v0.2 于 2026-07-14 完成独立基线审计并保持 `Approved`。Pack 快照不可变、引用不越界、导入内容惰性和策略感知重建已闭合；测试尚未物化、执行或通过，不授权多设备同步或物理存储选型。
