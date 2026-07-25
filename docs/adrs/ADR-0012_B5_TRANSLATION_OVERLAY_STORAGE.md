# ADR-0012：B5 翻译对照记录存储位置与对照视图派生方式

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-25 |
| Slice | `SLICE-MVP-B-MULTILINGUAL-001` |
| Contract | `SPEC-B5-MULTILINGUAL-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

B5 切片需要两个同层技术裁决：TranslationRecord（派生对照记录）的存储位置与修订历史的表达方式；BilingualView（原文/翻译对照视图）的派生位置与覆盖拒绝面的具体形态。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §20.2 FR-108、§21.5；`DEC-MVP-B-MULTILINGUAL-001` |
| SPEC | `SPEC-B5-MULTILINGUAL-001` §2..§7 |
| Acceptance Test | `B5-001..008` |
| Traceability | 矩阵 §4.14 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；SQLite PRAGMA 沿用 ADR-0001。
- 翻译记录不得进入 Canonical 对象层、Source Vault 原文层或 Evidence Ref 解析链（`B5-INV-001/002`）。
- 对照视图查询时派生、不持久化、不作证据（`B5-INV-005`）。
- 不决定：真实翻译引擎、全语言覆盖、多翻译并存策略、导出合同扩展。

## 4. 候选方案

### Option A：ledger_records（record_type=`translation_record`）+ 独立 `bilingual.py` 查询模块

- 做法：翻译记录存 revision ledger（append 语义，`translation_id` 含 revision 标识，修订 = 新记录 + 旧记录置 `superseded`）；`bilingual.py` 提供对照视图派生、orphan 检测与覆盖拒绝面；原文复用既有 `append_source` 追加路径。
- 优点：零 schema 变更；ledger 天然 append-only 契合历史保留；翻译物理隔离于 canonical_objects/source_records 之外，结构性满足 `B5-INV-001/002`。
- 代价与风险：ledger 记录类型增加一种；修订语义由模块保证而非表约束。
- 可逆性：纯新增记录类型与模块，可整体回退。

### Option B：新增 `translation_records` 专用表（B2/B3 先例）

- 优点：表约束显式。
- 代价与风险：schema 变更面扩大；B5 是只读对照切片，专用表带来的约束价值低于其迁移成本；superseded 历史仍需应用层逻辑。

### Option C：翻译存 canonical_objects（object_type=source 变体）

违反 `B5-INV-002`（翻译进入 Canonical/Evidence 解析链风险），直接排除。

## 5. 决定

采纳 Option A，两项裁决如下。

**5.1 存储位置**：TranslationRecord 存 `ledger_records`，`record_type="translation_record"`，record_id 形态 `translation:{source_ref}:{translation_revision}`；payload 含 `translation_id`、`source_ref`、`target_language`、`translated_text`、`translation_revision`、`status`（`active|superseded`）、`recorded_at`、`record_kind="translation_overlay"`。修订 = 插入新 revision 记录 + `replace_ledger_record` 将旧记录 status 置 `superseded`；全部历史保留。原文只经既有 `append_source` 路径进入 Source Vault。

**5.2 对照视图与拒绝面**：`src/noetide_micro/bilingual.py` 提供三个只读/窄写入口——`read_bilingual_view(store, source_ref)`（查询时派生 BilingualView；未知 source_ref 显式拒绝；无翻译时 `pairing_status=translation_unavailable`）、`translation_anomalies(store)`（报告 source_ref 缺失的 orphan 翻译，不静默配对）、`revise_source_with_translation(...)`（覆盖拒绝面：任何以翻译文本改写 Source Vault 原文的请求返回 `failed/original_overwrite_rejected`，不写入）。翻译修订入口 `revise_translation(...)` 仅追加 ledger 并置旧 revision superseded，不触碰 Source Vault。

## 6. 后果

### 正向后果

- `B5-INV-001/002` 由存储位置结构性保证：Source Vault 与 Canonical 无任何翻译写入路径。
- 历史保留（`B5-INV-004`）由 ledger append + superseded 标记直接表达，可用 oracle 精确断言。
- 无 schema 变更，既有 14 个 verified suite 不受影响。

### 负向后果与债务

- 修订一致性（同时只有一条 active）由模块逻辑保证；未来 ChangeSet 化时应迁移到正式变更边界（后续切片 Decision）。
- 多翻译并存策略未定义，留待 FR-108 扩展切片。

## 7. 验证与回退

- 验证方式：`B5-001..008` 可执行场景；`tools/validate_b5_suite.py` preflight；覆盖拒绝与 orphan 检测正反证明。
- 失败信号：翻译出现在 canonical_objects/source_records/Evidence 解析链；旧 revision 被删除而非 superseded；原文 hash 变化。
- 回退步骤：删除 `bilingual.py` 与 B5 suite 工件、清理 `translation_record` 记录类型、回退本 ADR；不影响已 verified suite。
- 数据兼容：本 ADR 不引入 schema 变更。

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | 创建 `B5_MULTILINGUAL_ARCHITECTURE.md` |
| Suite Materialization | 物化 `b5_multilingual_v1` fixture/oracle/runner/validator/manifest；preflight 后业务测试保持 `not_executed` |
| Implementation Plan | 创建 B5 Implementation Plan 与 Task Cards |
| Traceability | 矩阵 §4.14 `adr_accepted` 更新为 `true` |

## 9. 未决项

- 翻译记录的正式 ChangeSet 化（修订纳入标准变更边界）：后续切片 Decision。
- 多翻译并存与语言扩展：FR-108 扩展切片。
- 以上均不影响本决定成立。
