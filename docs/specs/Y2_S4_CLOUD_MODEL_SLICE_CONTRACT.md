# Y2-S4 云端模型可选后端切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-Y2S4-CLOUD-MODEL-001` |
| 版本 | `0.1` |
| 状态 | `Approved for Y2-S4 slice` |
| 产品基线 | `PRDv06.md` v0.6 |
| 产品决定 | `DEC-Y2-S4-001` |
| 上游 | S1 v0.7、S2 v0.6、S3 v0.5、S4 v0.5、S5 v0.5、S6 v0.6、S7 v0.4、S8 v0.4、S9 v0.5 |
| 适用范围 | `SLICE-Y2-S4-CLOUD-MODEL-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：证明固定合成用户只有在显式、有界、可撤销的云端授权下，才能让非红线 Source 经云端模型后端生成 propose-only 候选；默认关闭、红线舱室 fail closed、外发前有脱敏预览、全部授权/调用/失败可审计，且 Canonical 与 revision 不变化。

非目标：MCP runtime（Y2-S5）、真实云端凭据入库、账户体系、自动上传、真实数据模式、第三方 SDK、生产级密钥管理、模型质量评测。

## 2. 对象与字段

```yaml
cloud_grant:
  grant_id: grant_y2s4_<short_hash>
  actor: person_alpha
  purpose: summarize | organize | clarify
  compartments: [general, work]     # 非红线舱室；health/finance/relationship/sealed 永远不可授权外发
  source_scope:
    source_ids: [src_...]
  expires_at: ISO-8601 fixture time
  revoked: false
  created_at: ISO-8601 fixture time
  policy_revision: y2s4_cloud_policy_v1

outbound_preview:
  preview_id: preview_y2s4_<short_hash>
  status: preview_ready
  actor: person_alpha
  purpose: summarize
  built_at: ISO-8601 fixture time
  data_scope:
    - source_id: src_...
      content_hash: sha256
      byte_length: int
      compartments: [general]
      locator: {scheme, root_ref, relative_path}
      raw_content_present: false
      redacted: true

cloud_backend:
  cloud_fixture_backend:
    kind: cloud_fixture
    behavior: 按 source content_hash 查 fixture 声明；无 I/O；完全确定
  cloud_http_backend:
    kind: cloud_http
    endpoint: https://<configured host>/v1/chat/completions
    test_only_override: allow_loopback=True（仅显式合成测试可用）
    client: stdlib urllib；超时固定；不存储凭据

cloud_call_context:
  actor / purpose / grant_ref / preview_id
  model_id / model_version / prompt_version / requested_at

cloud_batch:
  batch_id / status: accepted | rejected
  backend_kind / purpose / preview_id / authorization_refs
  sources_seen / candidates_proposed / rejected_outputs
  requested_at / proposed_at
```

## 3. 判定规则

1. 默认全关：没有匹配且未到期、未撤销的显式授权时，云端后端不得被调用。
2. 批内授权原子：同一批 `source_ids` 中任一 Source 缺少授权、授权不匹配或属于红线舱室，整批拒绝，零后端调用。
3. 红线舱室 `health`、`finance`、`relationship`、`sealed` 绝对 fail closed；授权文本中出现这些舱室不产生例外。
4. 授权必须匹配 `actor`、`purpose`、`compartments` 与 `source_scope.source_ids`，且 `expires_at > requested_at`、`revoked=false`。
5. 外发前必须先生成匹配的 `outbound_preview`；预览与请求的 `source_ids`、`purpose`、`actor` 任一不匹配，或未提供预览，均拒绝且不发送。
6. 预览只包含数据范围元数据（source_id、content_hash、byte_length、compartments、locator），不包含原始正文；`raw_content_present=false`。
7. 云端候选继续执行 Y2-S2 输出校验：非法 JSON、缺字段、未知 kind、升格字段整批拒绝，不部分采用。
8. 候选 `review_status=unconfirmed`，不写 Canonical，不自动发布；确认仍走既有 ChangeSet 路径。
9. 模型、prompt 版本进入 `VersionRegistry`、候选 provenance 与审计；未注册版本不得激活，回滚历史保留。
10. 所有授权创建/撤销、预览、允许、拒绝、调用成功/失败写入 Ledger `cloud_audit` 记录。

## 4. 时间、证据与权限

- 全部产品时间来自 fixture clock；不读 wall-clock。
- 授权到期比较使用 fixture `requested_at`。
- 授权、预览与审计记录是 Derived/审计数据，不是个人事实证据；不进入 Canonical。
- 本切片不开放真实数据；Source 全部为显式合成 fixture。
- 云端调用只发生在 `send_allowed` 审计之后；拒绝原因使用非泄露枚举，不包含正文。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `Y2S4-INV-001` | default closed——无有效显式授权即无云端调用、无云端候选。 |
| `Y2S4-INV-002` | red line fail closed——红线舱室内容即使有授权也不外发，拒绝记录不泄露正文。 |
| `Y2S4-INV-003` | bounded grant——授权绑定 actor/purpose/compartments/source scope/expires_at，可撤销；任一不匹配、到期或撤销即拒绝。 |
| `Y2S4-INV-004` | preview before send——每次外发前必须存在匹配的脱敏数据范围预览；无预览不发送，预览不含原始正文。 |
| `Y2S4-INV-005` | audit & rollback——授权、预览、允许、拒绝、成功、失败全部可审计；候选 propose-only；Canonical 与 revision 不变；版本可回滚。 |
| `Y2S4-INV-006` | deterministic/stdlib/synthetic/offline——fixture clock、stdlib only、显式合成数据、测试只走 loopback stub；失败时诚实降级。 |

## 6. 失败、撤销与审计

- `rejected_outputs[].reason` 使用封闭枚举：`default_disabled`、`red_line_denied`、`purpose_mismatch`、`scope_mismatch`、`grant_expired`、`grant_revoked`、`preview_missing`、`preview_mismatch`、`invalid_output`、`transport_failed`。
- 任一拒绝或失败：零云端候选，Canonical/revision 不变；已发生的后端调用在审计中如实记录。
- 撤销授权后，后续请求立即拒绝；已生成候选不得自动进入 Canonical。
- 后端不可用/畸形输出：批状态 `rejected`，诚实报告，不伪装成功。
- `cloud_audit` 事件类型：`grant_created`、`grant_revoked`、`preview_built`、`send_allowed`、`send_denied`、`send_failed`、`send_succeeded`。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `Y2S4-001` | 无授权 / 请求云端 propose | 整批 `default_disabled` 拒绝；零后端调用；零候选；审计含预览与拒绝；Canonical/revision 不变 |
| `Y2S4-002` | 有效 grant + preview / 云端 fixture propose | 候选 3 条全 unconfirmed；批 `accepted`；审计含 grant/preview/allow/success；Canonical/revision 不变 |
| `Y2S4-003` | grant 含 health + preview / 请求 health Source | 整批 `red_line_denied`；零后端调用；零候选；拒绝不泄露正文 |
| `Y2S4-004` | grant purpose=summarize / 请求 purpose=organize | 整批 `purpose_mismatch`；零后端调用 |
| `Y2S4-005` | grant scope=[src1] / 请求 [src2] | 整批 `scope_mismatch`；零后端调用 |
| `Y2S4-006` | 过期 grant + 撤销 grant / 分别请求 | `grant_expired` 与 `grant_revoked` 均拒绝；零后端调用 |
| `Y2S4-007` | 无 preview 或 preview mismatch / 请求 propose | `preview_missing` 或 `preview_mismatch` 拒绝；零后端调用 |
| `Y2S4-008` | 有效授权 + fixture 畸形输出 / loopback stub 返回 500 | `invalid_output` 或 `transport_failed`；零候选；失败审计存在 |
| `Y2S4-009` | 成功 propose 后检查审计/版本 | Ledger 含授权、预览、允许、成功事件；候选 provenance 含 authorization/preview/版本；注册 v2 后回滚 v1 历史保留 |
| `Y2S4-010` | 横切 / 两个独立系统 | 同输入同输出；CloudHttpBackend 默认拒绝不安全 endpoint，测试 override 只走 loopback；stdlib only；fixture 显式合成；profile fail closed |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `Y2S4-001..010` passed result 存在，且所有 `Y2S4-INV-*` 有正/反证明时，Y2-S4 才能标记 `verified`。未执行时必须保持 `not_executed`。
