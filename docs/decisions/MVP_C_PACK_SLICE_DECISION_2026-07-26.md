# MVP-C Context Pack & Encrypted Backup 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-PACK-001` |
| Date | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-C-SCENARIO-001`（已 verified，recovery tag `c4-scenario-action-rp-20260726`） |
| Current Slice | `SLICE-MVP-C-PACK-001` |

## 1. 决定内容

选择 MVP-C 的 C5 Context Pack & Encrypted Backup 作为下一条窄切片（FR-303 首年切片：Markdown+JSON Pack、本地加密备份；路线图 `C5-CONTEXT-PACK-BACKUP`），在一个固定合成 profile 上验证三类能力：

1. Markdown+JSON Pack：在已 verified 的 JSON Context Pack 基础上，增加确定性 Markdown 渲染（sources/canonical/ledger 每层一个 Markdown 文件，脱离软件可读）；Pack 校验（manifest + 逐文件 sha256 + 未知文件/篡改 fail closed）。
2. 本地加密备份：将合成 SQLite 备份为密文文件（stdlib 确定性构造，ADR 明确标注非生产加密）；正确密钥恢复字节一致、错误密钥 fail closed 零写入；备份/恢复回执记录哈希。
3. 删除与恢复诚实性：删除回执按 PRD §534 分别报告 `live_source`、`canonical_payload`、`ledger_payload`、`derived_index`、`cache`、`backup`、`export_copy`、`minimal_audit_proof` 八个成分；`backup` 可诚实标为 `pending_expiry`、`export_copy` 标为 `out_of_control`；恢复回执记录源哈希与恢复后 revision。

## 2. 产品依据

- PRD §20.4 FR-303（909 行）：Context Pack 导出与导入。
- PRD §24.x（1108 行）：首年范围含本地加密备份和 Markdown+JSON Context Pack。
- PRD §120、§237、§534：删除与封存语义必须诚实；回执八成分报告；`pending_expiry`/`out_of_control` 合法标记；partial failure 必须报告。
- PRD §758：owner 私有备份导出与对外分享是不同动作（本切片只做 owner 私有导出）。
- 路线图约束（135 行）：独立可读、校验、删除与恢复诚实性。

## 3. 切片范围

- 单一固定合成 profile `c5_pack_backup_v1`：固定合成 sources/canonical/ledger 数据（复用 store 种子能力），全部显式合成。
- MarkdownPack：`markdown/sources.md`、`markdown/canonical.md`、`markdown/ledger.md` 确定性渲染 + manifest 扩展 + checksums。
- EncryptedBackup：密文文件 + backup_receipt（hash、key_hint 不含密钥本体、created_at）；restore 字节一致校验。
- DeletionReceipt：八成分诚实报告；任一成分失败显式 partial failure。
- RestoreReceipt：源哈希、恢复后 data_revision、字节一致性声明。
- 全部操作为显式调用；无自动备份、无后台任务。

## 4. 非目标

- 已 verified 的 Context Pack JSON 导出/导入闭环重建（本切片只加 Markdown 渲染与加密备份增量）。
- 生产级加密算法选型（vetted AEAD、密钥管理、KDF 参数）：本切片使用 ADR 标注的 stdlib 确定性构造，仅证明语义合同；生产加密属 D2/D3 决策。
- 加密多设备同步（FR-301）、对外分享导出、真实数据、云端备份。
- 自动备份调度、增量备份、备份保留策略引擎。

## 5. 不变量

- `C5-INV-001`：Markdown 渲染确定性可复现（同 store 同结果，字节一致）；Markdown 为解释性副本，JSON 为权威（Derived 不作证据）。
- `C5-INV-002`：Pack 校验 fail closed：哈希不匹配、未知/缺失文件、不安全路径一律拒绝并报告原因，不写 SQLite。
- `C5-INV-003`：备份密文不等于明文；正确密钥恢复字节一致；错误密钥 fail closed 零写入。
- `C5-INV-004`：删除回执必须报告全部八成分；`backup=pending_expiry` 与 `export_copy=out_of_control` 为合法诚实标记；partial failure 显式报告，不谎称 deleted。
- `C5-INV-005`：导出/备份/校验不修改 store（read-only）；恢复只写入新目标库，不覆盖源库。
- `C5-INV-006`：Pack 只含合成数据；export_scope 恒 `owner_private_synthetic`；对外分享导出不在本切片。
- `C5-INV-007`：profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S6/S7 的 C5 applicability review、切片合同、追踪和测试合同设计。完成这些开发前产物前不得编写 C5 业务代码。
