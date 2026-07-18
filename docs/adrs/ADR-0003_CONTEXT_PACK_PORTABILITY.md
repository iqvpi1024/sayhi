# ADR-0003：最小 Context Pack 与离线校验

## 元数据

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0003` |
| Status | `Accepted` |
| Date | `2026-07-18` |
| Slice | `SLICE-NOETIDE-E2E-RC-001` / `WS-07` |
| 基线 | PRDv05.md v0.5；S7 v0.3；S9 v0.4 |

## 决策

使用 Python 3.12 标准库生成目录式 Context Pack v1。每个 Pack 是一次不可变快照，包含：

- `manifest.json`：schema、included `data_revision`、条目相对路径、字节数和 SHA-256；
- `canonical.json`、`ledger.json` 和 `sources.json`：结构化规范层；
- `README.md`：可脱离软件阅读的对象、时间、证据和限制说明；
- `checksums.sha256`：人类可复核的条目清单。

所有 `content_ref` 仅接受 Pack 根下的 POSIX 相对路径；绝对路径、盘符、UNC、空路径、`.`、`..` 和根外解析均 fail closed。校验器只 dry-run，读取 JSON/文本为 inert data，不执行文件名、Markdown 或内容。

当前实现仅授权 owner 私有的**合成**运行时导出。Derived Projection 不导出为 Canonical evidence；外部分享、sealed 运行时、真实数据导入和 ChangeSet 写入不在此切片。

## 备选方案

- 单一 SQLite 文件：不能满足普通文件独立读取和 hash manifest 合同。
- ZIP/第三方归档库：增加依赖、路径逃逸复杂度，且对当前最小目录 Pack 没有收益。
- JSON-LD/RDF：超出当前合同，不提供必要验收价值。

## 后果与验证

导出不得改变数据库。验证必须证明：文件完整性、未知 namespaced 字段往返、篡改/越界拒绝、旧 Pack 不被新导出改写，以及验证过程零 Canonical 写入。若 hash 或路径检查失败，返回 quarantine/rejected，不执行导入。
