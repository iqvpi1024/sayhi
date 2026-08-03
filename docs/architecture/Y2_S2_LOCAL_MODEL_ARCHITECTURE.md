# Y2-S2 本地模型提议式整理架构视图

## 元信息

- Architecture ID: `ARCH-Y2S2-LOCAL-MODEL-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S2-LOCAL-MODEL-001`
- ADR: `ADR-0021`
- Contract: `SPEC-Y2S2-LOCAL-MODEL-001` v0.1

## 1. 组件

```text
Source（store.seeded_source）
  -> ModelCurator（model_capability.py）
       backend 入口检查：kind 仅 fixture | local_http；red-line local-only
       -> FixtureModelBackend：按 content_hash 返回 fixture raw output
       -> LocalHttpBackend：stdlib urllib，仅 http://127.0.0.1/::1 回环
       -> 整批输出校验：invalid_json / missing_field / unknown_kind / escalation_field
       -> CandidateEnvelope（Derived，review_status=unconfirmed，provenance）
       -> CandidateRegistry（run 内内存字典，不新增 SQLite 表）
  -> confirm_candidate（用户显式动作）
       -> proposed ChangeSet ledger 记录（Derived，不发布、不写 Canonical）
VersionRegistry（model_capability.py）
  -> register / activate / rollback；历史保留，未注册版本 fail closed
```

## 2. 边界

- 写面：仅 source_records + append_receipts（adapter 物化合成 source）与 ledger_records 的 proposed 提案记录；无 Canonical 写路径、无新表。
- 读面：`seeded_source`、`current_revision`、`canonical_layer_digest`、`seed_snapshot`。
- 失败面：畸形输出整批拒绝；非回环 URL 构造即拒绝且不连接；未注册版本不得激活；profile 外 fail closed。
- 时间面：全部使用 fixture clock，无 wall-clock。
- 网络面：只允许本机回环；official runner 使用 loopback-only socket guard。

## 3. 数据流

Source 文本 -> content_hash -> backend raw output -> 整批校验 -> 候选 Envelope（含 evidence_refs/provenance）-> 用户确认 -> ChangeSet proposed（status=proposed, published_revision=None）。Canonical digest、data_revision 和 Core View 不在此切片数据流上变化。

## 4. 测试面

`y2s2_testing_adapter.py` 在临时目录物化 fixture source，按 case 选择 fixture/local_http/cloud 探针，注入 fixture clock 与 profile；local_http 场景启动 127.0.0.1 stub 服务并在结束后关闭。contract 10 场景覆盖 6 条不变量。