# C5 Context Pack & Encrypted Backup 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-C5-PACK-001` |
| 版本 | `0.1` |
| 状态 | `Approved for C5 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-C-PACK-001` |
| 上游 | S1 v0.6、S2 v0.5、S6 v0.5、S7 v0.4 |
| 适用范围 | `SLICE-MVP-C-PACK-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：在一个固定合成 profile 上证明——Markdown+JSON Pack（确定性 Markdown 渲染 + 严格校验 fail closed）、本地加密备份（密文非明文、正确密钥字节一致恢复、错误密钥 fail closed 零写入）、删除与恢复诚实性（八成分回执、`pending_expiry`/`out_of_control` 合法标记、partial failure 显式报告）。

非目标：已 verified 的 JSON Pack 闭环重建、生产级加密选型与密钥管理、FR-301 多设备同步、对外分享导出、自动备份调度、增量备份、真实数据。

## 2. 对象与字段

### 2.1 MarkdownPack（在既有 JSON Pack 上扩展，Derived 解释性副本）

```yaml
markdown/sources.md: 每条 source 一个确定性小节（标题 + 字段表）
markdown/canonical.md: 每个 canonical object 一个确定性小节
markdown/ledger.md: 每条 ledger record 一个确定性小节
manifest.json: 既有 entries 之外追加 markdown 条目（content_ref/media_type=text/markdown/hash）
checksums.sha256: 全部条目（含 markdown）逐行 sha256
```

渲染规则：字段按 key 字典序；记录按主键字典序；空值渲染为 `(empty)`；无 wall-clock（时间取 fixture clock）；同 store 快照渲染字节一致。JSON 为权威；Markdown 不作证据。

### 2.2 EncryptedBackup（本地加密备份，非生产构造）

```yaml
backup_file: <name>.nobak          # 密文：nonce(16B) + XOR(plaintext, sha256 密钥流)
backup_receipt:
  backup_id / source_db_sha256 / backup_sha256 / created_at（fixture clock）
  encryption: stdlib_deterministic_v1   # 明确标注非生产；禁止宣称生产安全
  key_hint: 不含密钥本体的固定合成标签
```

### 2.3 RestoreReceipt

```yaml
restore_id / backup_sha256 / restored_db_sha256 / data_revision
byte_identical: true                 # 恢复后 DB 与源 DB 字节一致才可为 true
```

### 2.4 DeletionReceipt（八成分诚实报告，PRD §534）

```yaml
target_ref / requested_at（fixture clock）
components:
  live_source: deleted | failed
  canonical_payload: deleted | failed
  ledger_payload: deleted | failed
  derived_index: deleted | failed
  cache: deleted | failed
  backup: deleted | pending_expiry | failed
  export_copy: out_of_control | deleted | failed
  minimal_audit_proof: retained
overall: deleted | partial_failure   # 任一 failed -> partial_failure，绝不谎称 deleted
```

## 3. 状态机

```text
Pack:    （无） --导出--> files on disk --校验--> validated | rejected_*（fail closed，无写入）
Backup:  （无） --显式创建--> ciphertext+receipt --恢复(正确密钥)--> restored（字节一致）
                                               --恢复(错误密钥)--> rejected 零写入
Deletion: 请求 -> 逐成分执行 -> overall=deleted | partial_failure（报告失败成分）
```

- 全部操作为显式调用；无自动备份、无后台任务、无 wall-clock。
- 恢复只写新目标库，绝不覆盖源库；目标已存在则 fail closed。

## 4. 时间、证据与权限

- 全部使用 fixture clock；渲染、回执时间均取固定值。
- Markdown 为解释性副本，不作证据；Pack/备份内容只含合成数据；`export_scope=owner_private_synthetic` 恒定。
- 密钥只以测试输入存在；回执不记录密钥本体。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 5. 系统不变量

- `C5-INV-001`：Markdown 渲染确定性（同快照字节一致）；Markdown 不作证据。
- `C5-INV-002`：Pack 校验 fail closed（篡改/缺失/未知文件/不安全路径均拒绝并报告，不写 SQLite）。
- `C5-INV-003`：密文≠明文；正确密钥恢复字节一致；错误密钥 fail closed 零写入。
- `C5-INV-004`：删除回执报告全部八成分；partial failure 显式；不谎称 deleted。
- `C5-INV-005`：导出/备份/校验 read-only（store digest 不变）；恢复只写新目标库。
- `C5-INV-006`：Pack/备份只含合成数据；export_scope 恒定；无对外分享路径。
- `C5-INV-007`：profile 外输入 fail closed 且无写入。

## 6. 失败、撤销与审计

- 校验失败：`rejected_hash_mismatch`/`rejected_path`/`rejected_unknown_file`/`rejected_schema`，零写入。
- 错误密钥/损坏密文：`rejected`，零写入，不产出部分恢复。
- 目标库已存在：`rejected`，零写入。
- 删除成分失败：该成分标 `failed`，overall=`partial_failure`，报告具体成分。
- 审计：backup_receipt/restore_receipt/deletion_receipt 为返回值与文件回执；验收结果只在测试 oracle 与 verification result 中绑定。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `C5-001` | 固定合成 store / 导出 Markdown+JSON Pack | 三层 JSON + 三个 Markdown + manifest + checksums 全部存在；manifest 含 markdown 条目且哈希正确 |
| `C5-002` | 同 store / 连续两次导出到不同目录 | 两次 Markdown 字节一致；含预期记录标题；Markdown 独立可读（无需软件解析即可读字段表） |
| `C5-003` | 已导出 Pack / 校验；随后篡改一个文件再校验 | 首次 `validated`；篡改后 `rejected_hash_mismatch`；SQLite 无写入 |
| `C5-004` | 已导出 Pack / 注入未知文件与缺失文件变体 | 均 fail closed（`rejected_unknown_file`/`rejected_hash_mismatch`）并报告，零写入 |
| `C5-005` | 固定合成 store / 创建加密备份 | 密文 ≠ 明文；receipt 含 source_db_sha256 与 backup_sha256；store digest 不变 |
| `C5-006` | 已有备份 / 正确密钥恢复到新目标 | 恢复 DB 与源 DB 字节一致；`byte_identical=true`；data_revision 一致；源库不变 |
| `C5-007` | 已有备份 / 错误密钥恢复 | `rejected`、零写入、无部分恢复文件 |
| `C5-008` | 固定合成对象 / 执行删除（备份保留策略=pending_expiry） | 回执报告全部八成分；`backup=pending_expiry`、`export_copy=out_of_control`、`overall=deleted` |
| `C5-009` | 同上 / 注入一个成分失败 | 该成分 `failed`、`overall=partial_failure`、不谎称 deleted |
| `C5-010` | 全旅程后 / 横切 | 导出/备份/校验后 store digest 不变；恢复不覆盖源库；profile 外输入 rejected 零写入；Pack 只含合成数据 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `C5-001..010` passed result 存在，且所有 `C5-INV-*` 有正/反证明时，C5 才能标记 `verified`。未执行时必须保持 `not_executed`。
