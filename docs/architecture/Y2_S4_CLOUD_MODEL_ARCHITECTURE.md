# Y2-S4 云端模型可选后端架构视图

## 元信息

- Architecture ID: `ARCH-Y2S4-CLOUD-MODEL-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S4-CLOUD-MODEL-001`
- ADR: `ADR-0023`
- Contract: `SPEC-Y2S4-CLOUD-MODEL-001` v0.1

## 1. 组件

```text
Source（store.seeded_source）
  -> CloudModelCurator（cloud_model.py）
       preview_id 校验：必须匹配 source_ids/purpose/actor
       CloudGate.evaluate：default closed -> bounded grant -> red-line absolute deny
       -> send_allowed 审计
       -> CloudFixtureBackend（确定性无 I/O） | CloudHttpBackend（stdlib urllib，https）
       -> send_failed/send_succeeded 审计
       -> Y2-S2 输出校验 -> CandidateEnvelope（unconfirmed, provenance, authorization/preview）
       -> 不写 Canonical
CloudGate（cloud_model.py）
  -> grants（显式创建/撤销）
  -> build_preview（data_scope，raw_content_present=false）
  -> store.put_ledger_record(record_type="cloud_audit")
VersionRegistry（model_capability.py 复用）
  -> register / activate / rollback；未注册版本 fail closed
```

## 2. 边界

- 写面：仅 Ledger `cloud_audit` 审计记录；Source 已由 adapter 物化；无 Canonical 写、无新表。
- 读面：`seeded_source`、`current_revision`、`canonical_layer_digest`、`ledger_records_of_type("cloud_audit")`、`seed_snapshot`。
- 失败面：无授权、红线、purpose/scope/expiry/revoke/preview 不匹配、畸形输出、传输失败全部拒绝；拒绝原因不泄露正文。
- 时间面：全部使用 fixture clock，无 wall-clock。
- 网络面：CloudHttpBackend 默认要求 `https://` 外部端点；测试只使用显式 `allow_loopback=True` 的本机 stub；official runner 使用 loopback-only socket guard。

## 3. 数据流

用户显式创建 grant -> build_preview（仅范围元数据） -> propose（preview 匹配后逐 Source 授权检查） -> 全批允许才调用后端 -> 输出校验 -> 候选 Envelope（Derived） -> 审计记录。任何拒绝或失败保持 Canonical/revision 不变，候选零落库。

## 4. 测试面

`y2s4_testing_adapter.py` 在临时目录物化 fixture source，按 case 创建/撤销 grant、构建 preview、调用 `CloudModelCurator`；CloudHttpBackend 场景启动 127.0.0.1 stub；contract 10 场景覆盖 6 条不变量；审计、determinism、stdlib 与 loopback-only 由 adapter/runner 证明。
