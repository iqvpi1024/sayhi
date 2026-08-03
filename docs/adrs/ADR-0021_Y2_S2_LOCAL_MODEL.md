# ADR-0021：Y2-S2 本地模型提议式整理实现方案

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0021` |
| Date | 2026-08-01 |
| Status | `Accepted` |
| Slice | `SLICE-Y2-S2-LOCAL-MODEL-001` |
| Contract | `SPEC-Y2S2-LOCAL-MODEL-001` v0.1 |

## 1. 决策

1. 新模块 `src/noetide_micro/model_capability.py`：`FixtureModelBackend`、`LocalHttpBackend`（stdlib `urllib`，构造时回环校验）、`ModelCurator`（编排、整批校验、候选生成、provenance）、`VersionRegistry`；纯 stdlib，零第三方依赖。
2. 候选只存 Derived：run 内 `CandidateRegistry`（内存字典），不新增 SQLite 表、不落 Canonical；切片结束后候选可整体丢弃。候选持久化后置到后续切片另立 ADR。
3. 输出校验整批原子：任一候选非法（JSON 非法、缺字段、未知 kind、携带升格字段 `review_status`/`confirmed`/`auto_publish`/`publish`）则整批拒绝，不部分采用。
4. `LocalHttpBackend`：只允许 `127.0.0.0/8` 与 `::1`；非回环在构造时抛 `EndpointRejectedError`（不发起连接）；固定超时；请求/响应遵循 OpenAI chat completions 最小子集。
5. 红线 enforcement 在 `ModelCurator.propose` 入口：后端 `kind` 不在 `{fixture, local_http}` 一律拒绝；红线舱室 source 只传给本地后端（本切片全部后端均本地，规则在未来 cloud 后端加入时自然生效）。
6. 确认流边界：`confirm_candidate` 只产生 `status=proposed` 的 ChangeSet 提案记录（Derived），未确认候选确认即拒绝；完整发布集成（approve/publish/receipt）属于后续产品接线，不在本切片声明。
7. 时间：全部来自注入的 fixture clock；版本注册时间同样使用 fixture clock。

## 2. 备选方案与放弃理由

- 候选 SQLite 持久化：放弃。本切片只需 run 内语义；新增表扩大 schema 与对账面，持久化需求留给真实使用切片。
- 部分采用合法候选：放弃。部分采用会让畸形输出与合法输出同批通过，削弱 fail closed 的可证明性。
- 直接调用 Ollama Python SDK：放弃。引入第三方依赖违反零依赖红线；stdlib urllib 足够覆盖 OpenAI 兼容最小子集。
- 完整 ChangeSet 发布集成：放弃。本切片只证明 propose-only 边界，发布路径已由既有切片证明，重复集成无新信息且扩大爆炸半径。

## 3. 代价与回退

- 代价：候选不落库意味着跨进程不可恢复（本切片可接受）；整批拒绝可能丢弃合法候选（fail closed 的有意代价）。
- 回退：删除 `model_capability.py` 与 adapter 即可完全移除；无 Canonical 写入，无迁移负担。

## 4. 环境

Windows 11 10.0.26200；CPython 3.12.8；SQLite（ADR-0001 PRAGMA 不变）；stdlib only；runner 阻断外部网络（local_http 仅回环）。
