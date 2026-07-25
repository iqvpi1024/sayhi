# ADR-0017：C5 Markdown 渲染与本地加密备份的实现方式

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-26 |
| Slice | `SLICE-MVP-C-PACK-001` |
| Contract | `SPEC-C5-PACK-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

C5 切片需要三个同层技术裁决：Markdown 渲染形态（是否扩展既有 Exporter）；加密备份的密码学构造（stdlib 无 AEAD 的约束下如何既诚实又可用）；删除回执八成分在 micro 存储上的映射。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §20.4 FR-303、§24.x、§534、§758；`DEC-MVP-C-PACK-001` |
| SPEC | `SPEC-C5-PACK-001` §2..§7；S1 v0.6、S2 v0.5、S6 v0.5、S7 v0.4 |
| Acceptance Test | `C5-001..010` |
| Traceability | 矩阵 §4.19 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；零 schema 变更；不安装依赖。
- Markdown 为解释性副本不作证据；渲染确定性（`C5-INV-001`）。
- 密文≠明文、正确密钥字节一致、错误密钥 fail closed（`C5-INV-003`）。
- 删除回执八成分诚实报告（`C5-INV-004`）。
- 不决定：生产加密算法/KDF/密钥管理（D2/D3）、自动备份、云端。

## 4. 候选方案

### Option A：新模块复用 Exporter 快照 + sha256 密钥流 XOR + 成分映射表

- 做法：`src/noetide_micro/pack_backup.py` 复用 `store.portability_snapshot()` 与 `ContextPackExporter` 的文件/manifest 机制，追加 `markdown/*.md` 渲染与条目；加密用 `keystream = sha256(key || nonce || counter)` 的 XOR 构造（文件头 16 字节随机 nonce）；删除回执把八成分映射为：live_source=source_records、canonical_payload=canonical_objects、ledger_payload=ledger_records+canonical_revisions、derived_index=projection 表、cache=临时文件、backup=.nobak 文件、export_copy=Pack 目录、minimal_audit_proof=保留的删除回执本体。
- 优点：零 schema 变更；复用已 verified 的快照/manifest/校验机制；XOR 构造完全确定性可测试且满足本切片语义合同（密文≠明文、密钥敏感、字节一致恢复）。
- 代价与风险：XOR+sha256 密钥流不是认证加密、不抗篡改检测以外的密码学攻击；必须在 receipt 与文档中显式标注 `stdlib_deterministic_v1` 非生产。密钥无 KDF 加固。
- 可逆性：纯新增模块，可整体回退。

### Option B：引入第三方加密库（cryptography/PyNaCl）

- 优点：真正的 AEAD。
- 代价与风险：违反 stdlib-only 约束与"不安装依赖"施工原则；生产加密选型属 D2/D3 决策，不应在本切片偷渡。

### Option C：不加密，只做诚实标记的明文备份

- 优点：最简单。
- 代价与风险：不满足 FR-303 首年切片"本地加密备份"的语义要求；密文≠明文无法证明。

## 5. 决定

采纳 Option A。

**5.1 Markdown 渲染**：`render_markdown_pack(snapshot)` 生成 `sources.md/canonical.md/ledger.md`；记录按主键字典序、字段按 key 字典序、空值 `(empty)`、每记录一个二级标题小节；导出时追加进 manifest entries（`media_type=text/markdown`）与 checksums；校验器扩展为检查未知文件（不在 manifest 的文件即 `rejected_unknown_file`）。

**5.2 加密备份**：`create_backup(db_path, key, clock)` 读取 DB 字节 -> `nonce=os.urandom(16)` -> `ciphertext = nonce + xor(plaintext, sha256_stream(key, nonce))` 写 `<name>.nobak`；receipt 记录 `source_db_sha256`、`backup_sha256`、`encryption=stdlib_deterministic_v1`、`key_hint`（固定合成标签，不含密钥）。`restore_backup(backup_path, key, target_path)`：目标已存在则 `rejected`；解密后用 `sha256(plaintext)` 与 receipt 的 `source_db_sha256` 比对，不一致（错误密钥/损坏）则 `rejected` 且删除部分文件；一致则写目标库并出 RestoreReceipt（`byte_identical` 由恢复后再 hash 目标文件验证）。

**5.3 删除回执**：`build_deletion_receipt(store, target_ref, policy, clock)` 逐成分执行并记录 `deleted|pending_expiry|out_of_control|retained|failed`；任一 `failed` -> `overall=partial_failure`。本切片 profile 中 `backup` 策略固定 `pending_expiry`（备份文件保留待过期）、`export_copy` 固定 `out_of_control`、`minimal_audit_proof` 固定 `retained`。

## 6. 后果

- 正面：零依赖零 schema 变更落地三类能力；语义合同（fail closed、诚实报告、字节一致）全部可执行证明。
- 代价：加密构造非生产级，必须在所有对外文档保持 `stdlib_deterministic_v1` 标注；生产迁移时需替换为 vetted AEAD + KDF（D2/D3 决策项）。
- 回退：删除 `pack_backup.py`、`c5_testing_adapter.py` 与对应 suite；不影响既有 Pack 切片。
