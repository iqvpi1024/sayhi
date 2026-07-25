# B5 Multilingual 原文与翻译对照 Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-B5-MULTILINGUAL-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-B-MULTILINGUAL-001` |
| ADR | `ADR-0012` |

```text
synthetic original text
  -> Source Vault (append_source: receipt + content hash)   [原文唯一入口]
synthetic translation text
  -> ledger_records (record_type=translation_record)        [独立对照记录]
        |  revise_translation: new revision active, old -> superseded (all retained)
        v
bilingual.read_bilingual_view (query-time derived, never persisted)
  -> BilingualView { original + translation | translation_unavailable }
bilingual.translation_anomalies -> orphan_translation report (no silent pairing)
bilingual.revise_source_with_translation -> always failed/original_overwrite_rejected
```

- Source Vault 与 Canonical 无任何翻译写入路径；Evidence Ref 永远解析到原文。
- BilingualView 是 Derived：不得成为 Evidence Ref、Assertion input 或 ChangeSet trigger。
- 翻译修订只动 ledger；旧 revision 转 superseded 保留，Current 不覆盖 Historical。
- profile 外输入 fail closed 且无写入。
