# ADR-0023：Y2-S4 云端模型可选后端的授权门与审计实现方案

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0023` |
| Date | 2026-08-03 |
| Status | `Accepted` |
| Slice | `SLICE-Y2-S4-CLOUD-MODEL-001` |
| Contract | `SPEC-Y2S4-CLOUD-MODEL-001` v0.1 |
| Decision | `DEC-Y2-S4-001` |

## 1. 决策

1. 新模块 `src/noetide_micro/cloud_model.py`：`CloudGate`（默认关闭、授权评估、红线 fail closed、脱敏预览、Ledger 审计）、`CloudFixtureBackend`（确定性、无 I/O）、`CloudHttpBackend`（stdlib `urllib`，默认要求 `https://`，测试可显式传 `allow_loopback=True`）、`CloudModelCurator`（批内授权原子、输出校验、候选构建、版本注册）。
2. 授权模型采用有界 Grant：绑定 `actor`、`purpose`、`compartments`、`source_scope.source_ids`、`expires_at`、`revoked`；默认 grants 为空，无授权即拒绝。
3. 批内授权原子：请求中任一 Source 未授权、授权不匹配或属红线舱室，整批拒绝且零后端调用；避免部分 Source 意外外发。
4. 外发预览：`CloudGate.build_preview` 只返回 `source_id/content_hash/byte_length/compartments/locator`，`raw_content_present=false`；`CloudModelCurator.propose` 必须引用匹配 preview，否则拒绝。
5. 审计写入 Ledger：使用 `store.put_ledger_record(record_type="cloud_audit")` 记录 `grant_created/grant_revoked/preview_built/send_allowed/send_denied/send_failed/send_succeeded`；不写 Canonical，不存正文/凭据。
6. 候选与版本：复用 Y2-S2 `_validate_output`、candidate envelope 语义与 `VersionRegistry`；`CloudModelCurator` 注册模型/prompt 版本，provenance 含 authorization/preview/版本，支持回滚。
7. `CloudHttpBackend` 请求体只在实际通过授权门和预览门后构造；请求上下文包含 purpose、grant_ref、preview_id、模型版本。测试 loopback override 仅允许本机 stub，official runner 全局阻断外部网络。

## 2. 备选方案与放弃理由

- 直接扩展现有 `ModelCurator` 接受 cloud：放弃。Y2-S2 的 `LOCAL_BACKEND_KINDS` 与 profile 是已 verified 边界；独立 `CloudModelCurator` 避免静默放宽旧切片并保持回退简单。
- 云端授权持久化为新 SQLite 表：放弃。Y2-S4 只需证明门禁与审计语义；`cloud_audit` Ledger 足以保留授权事件，后续真实权限 runtime 可另立 ADR。
- 使用第三方云 SDK/requests：放弃。引入第三方依赖违反 `Y2E-INV-005` 与零依赖红线；stdlib `urllib` 足够覆盖最小 chat completions HTTP 面。
- 允许部分 Source 通过授权：放弃。部分外发会让用户难以确认数据范围，且可能绕过批级 fail closed。
- 真实公网调用做 suite：放弃。仓库测试必须离线、确定、只含合成数据；authorized path 由 fixture 与 loopback stub 证明。

## 3. 代价与回退

- 代价：云端后端不能持久化授权表，审计事件必须按每次运行/ledger 记录解析；真实云调用不会在 official suite 中执行。
- 回退：删除 `cloud_model.py` 与 `y2s4_testing_adapter.py` 即可移除；无 Canonical 写入、无新表迁移。

## 4. 环境

Windows 11 10.0.26200；CPython 3.12.8；stdlib only；runner 阻断外部网络（loopback-only socket guard）；fixture clock；显式合成数据。
