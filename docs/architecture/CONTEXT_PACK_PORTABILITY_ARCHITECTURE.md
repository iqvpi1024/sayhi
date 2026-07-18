# Context Pack Portability Architecture

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-CONTEXT-PACK-001` |
| Status | `Accepted Design Baseline` |
| ADR | `ADR-0003` |
| Scope | `WS-07` private synthetic Context Pack |

```text
SemanticStore (Source / Canonical / Ledger)
        | read-only snapshot
        v
ContextPackExporter -> pack root: JSON + Markdown + manifest + checksums
        |
        v
ContextPackVerifier -> dry-run validation / quarantine receipt
```

- `ContextPackExporter` 只读取规范层；不读取 Projection，且不创建 revision、receipt 或 ChangeSet。
- `ContextPackVerifier` 只接受 Pack root 内受控相对引用，先验证 manifest/schema/hash，再返回解析后的 inert snapshot；不写 SQLite。
- 人类可读 `README.md` 是 Projection，不替代 `canonical.json`、`ledger.json` 或 Source 内容。
- 任何未知 namespaced 字段作为 JSON 值原样通过导出与校验；未知核心对象类型、路径越界、缺文件和 hash 不匹配均拒绝。

