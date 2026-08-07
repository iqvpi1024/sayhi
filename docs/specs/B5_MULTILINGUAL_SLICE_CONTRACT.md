# B5 Multilingual 原文与翻译对照切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-B5-MULTILINGUAL-001` |
| 版本 | `0.1` |
| 状态 | `Approved for B5 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-B-MULTILINGUAL-001` |
| 上游 | S1 v0.6、S2 v0.5、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-B-MULTILINGUAL-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：在一个固定合成 profile 上证明多语言 Source 的三类能力——原文与翻译分离存储（原文进 Source Vault 带 content hash，翻译为独立派生对照记录）、原文/翻译对照读取（并排 Derived 视图，缺失翻译显式降级）、证据完整性（Evidence Ref 永远解析到原文；以翻译覆盖原文的写入被拒绝；翻译修订保留历史）。

非目标：真实翻译引擎/机器翻译/语言检测/LLM、全语言覆盖、多翻译并存策略、翻译质量评分、真实数据、连接器、多设备同步、导出合同扩展。

## 2. 对象与字段

### 2.1 TranslationRecord（派生对照记录，不进入 Canonical、不进入 Evidence 解析链）

```yaml
translation_id: stable ID
source_ref: Source Vault 中的 source_id
target_language: synthetic_lang_b   # 固定合成语言标识
translated_text: fixed synthetic text
translation_revision: tr_001 | tr_002
recorded_at: fixed synthetic clock
record_kind: translation_overlay    # 显式非证据
```

### 2.2 BilingualView（Derived 只读对照视图，不持久化为事实）

```yaml
view_id: stable ID within the run
source_ref: source_id
original: {text, content_hash, source_kind}
translation: {translation_id, target_language, translated_text, translation_revision} | null
pairing_status: paired | translation_unavailable
derived_only: true
```

`TranslationRecord` 与 `BilingualView` 都不是 Canonical 对象，不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。原文只经既有 Source Vault 追加路径存储（append receipt + content hash）。

## 3. 状态机

翻译对照记录：`draft -> active -> superseded`（修订时旧 revision 转 superseded，全部保留）。BilingualView 无状态机：每次查询即时派生，不缓存为事实。

## 4. 时间、证据与权限

- 原文与翻译记录使用固定 synthetic clock；翻译修订不回填或修改原文的任何字段。
- Evidence Ref 解析目标永远是 Source Vault 原文（source_id + content hash）；翻译记录永远不是解析目标。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 5. 系统不变量

- `B5-INV-001`：原文与 content hash 不因任何翻译操作改变。
- `B5-INV-002`：Evidence Ref 永远解析到原文；翻译不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。
- `B5-INV-003`：以翻译覆盖原文的写入被拒绝（fail closed），原文与 hash 不变。
- `B5-INV-004`：翻译修订保留全部历史；Current 不覆盖 Historical（旧 revision 转 superseded 而非删除）。
- `B5-INV-005`：对照视图是 Derived；缺失翻译显式 `translation_unavailable`，不得把原文冒充翻译。
- `B5-INV-006`：profile 外输入 fail closed 且无写入。

## 6. 失败、撤销与审计

- 读取未知 source_ref 的对照视图：显式拒绝，不猜测。
- 原文缺失但存在翻译记录：报告 `orphan_translation`，不得静默配对到其他 Source。
- 审计：对照读取结果只在测试 oracle 与 verification result 中绑定；不新增 Canonical 审计对象。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `B5-001` | 干净 profile / 追加合成双语 Source（原文 + 翻译对照记录） | 原文入 Vault 带 receipt + content hash；翻译独立存储、source_ref 关联；原文不被翻译覆盖 |
| `B5-002` | 已存双语 Source / 读取原文与 Evidence Ref 解析 | 返回原文 text + hash；Evidence Ref 解析到原文 source_id；不解析到翻译 |
| `B5-003` | 已存双语 Source / 查询对照视图 | `pairing_status=paired`；原文 + 翻译并排；翻译标记 `record_kind=translation_overlay`；`derived_only=true` |
| `B5-004` | 已存原文 / 尝试以翻译文本覆盖原文 | 拒绝（`original_overwrite_rejected`）；原文 text 与 content hash 不变；receipt 历史不变 |
| `B5-005` | 只有原文无翻译 / 查询对照视图 | `pairing_status=translation_unavailable`；translation 为 null；原文不冒充翻译 |
| `B5-006` | 已有 tr_001 翻译 / 修订为 tr_002 | tr_002 active、tr_001 superseded 且保留；原文与 hash 不变；对照视图显示 tr_002 |
| `B5-007` | 存在指向不存在 Source 的翻译记录 / 查询对照视图 | 报告 `orphan_translation`；不静默配对；原文不受影响 |
| `B5-008` | 全旅程后 / 横切检查 + profile 外输入 | 原文/hash/receipt 全不变；翻译历史完整；对照视图不作证据；profile 外输入 fail closed 无写入 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `B5-001..008` passed result 存在，且所有 `B5-INV-*` 有正/反证明时，B5 才能标记 `verified`。未执行时必须保持 `not_executed`。
