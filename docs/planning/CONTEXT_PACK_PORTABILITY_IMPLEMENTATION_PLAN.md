# Context Pack Portability Implementation Plan

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-CONTEXT-PACK-001` |
| Status | `Approved for WS-07` |
| Prerequisites | `ADR-0003`、`ARCH-CONTEXT-PACK-001`、`ACCEPT-CONTEXT-PACK-001` |

1. 在 `store.py` 增加仅供 exporter 使用的规范层只读 snapshot，按 Source/Canonical/Ledger 分层返回 payload，禁止 Projection 进入 snapshot。
2. 创建 `portability.py`：目录导出、canonical JSON、Markdown、SHA-256 manifest/checksums 与 fail-closed dry-run verifier。
3. 创建固定合成 fixture、oracle、semantic tests、manifest、validator 和离线 runner；required 集只能是 `CP-001..006`。
4. 仅当同一 commit 的所有 CP 场景通过并绑定 artifact/result 后，更新 RC 状态与追踪。不得实现真实导入、分享导出、sealed runtime 或 ChangeSet 写入。

