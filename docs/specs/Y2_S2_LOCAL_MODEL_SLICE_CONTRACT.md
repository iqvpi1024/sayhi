# Y2-S2 本地模型提议式整理切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-Y2S2-LOCAL-MODEL-001` |
| 版本 | `0.1` |
| 状态 | `Approved for Y2-S2 slice` |
| 产品基线 | `PRDv06.md` v0.6 |
| 产品决定 | `DEC-Y2-S2-001` |
| 上游 | S1 v0.7、S2 v0.6、S5 v0.5 |
| 适用范围 | `SLICE-Y2-S2-LOCAL-MODEL-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：在固定合成 Source 集合上证明——模型能力接口 propose-only（候选全 unconfirmed、零 Canonical 写入）、候选完整（envelope + 证据定位 + provenance）、畸形输出 fail closed、注入免疫、红线舱室 local-only、非回环地址 fail closed、模型/prompt 版本审计与回滚、确定性。

非目标：云端后端（Y2-S4）、真实模型权重与评估、embedding、MCP、自动发布、候选质量校准、通用 NLP。

## 2. 对象与字段

### 2.1 ModelBackend（封闭两种）

```yaml
fixture_backend:
  kind: fixture
  behavior: 按 source content_hash 查 fixture 声明的响应；无 I/O；完全确定
local_http_backend:
  kind: local_http
  endpoint: 仅允许 http://127.0.0.1:<port>/v1/chat/completions（或 ::1）
  client: stdlib urllib；超时固定；非回环地址构造时即 fail closed，不发起连接
```

### 2.2 CandidateEnvelope（复用 S5 候选语义，Derived，不作证据）

```yaml
candidate_id: "cand_<sha256[:16]>"
candidate_kind: entity | episode | commitment | assertion
payload: <种类对应的最小字段>
evidence_refs: [{source_id, locator}]
review_status: unconfirmed        # 封闭唯一值；模型输出中的其他值被拒绝
provenance:
  model_id / model_version / prompt_version / backend_kind / proposed_at（fixture clock）
```

### 2.3 ProposalBatch（Derived 回执）

```yaml
batch_id / backend_kind / model_id / model_version / prompt_version
sources_seen / candidates_proposed / rejected_outputs
proposed_at: fixture clock
```

### 2.4 VersionRegistry（Derived）

```yaml
registered: [{model_id, model_version, prompt_version, registered_at}]
active: <当前激活版本>
rollback(to_version): 切换 active；历史记录保留
```

## 3. 输出校验与畸形处置

模型原始输出必须是一个 JSON 对象且含 `candidates` 数组；每个候选必须通过：

- `candidate_kind` 属于封闭枚举；未知 kind 拒绝。
- 必填字段齐全（payload、evidence_refs 非空且指向已导入 source_id）。
- 不得包含 `review_status`、`confirmed`、`auto_publish`、`publish` 字段；出现即整批拒绝（防注入升格）。

任一校验失败：整批零候选、错误回执（`invalid_output`），不部分采用。

## 4. 版本审计

- 每次 propose 记录 model_id、model_version、prompt_version 于 batch 与每个候选的 provenance。
- VersionRegistry 支持注册新版本与回滚到已注册旧版本；回滚产生新注册记录，历史不删除。
- 未注册版本不得激活（fail closed）。

## 5. 红线舱室与后端选择

```yaml
red_line_compartments: [health, finance, relationship, sealed]
规则:
  - source.compartments 与红线相交 -> 只允许 kind=fixture 或 local_http（本地后端）
  - 非红线 source -> 本地后端
  - kind=cloud（Y2-S4 预留）-> 本切片一律拒绝
  - local_http 端点非回环 -> 构造时 fail closed，不发起连接
```

## 6. 注入免疫

- Source 正文中的指令性文本（"忽略规则""标记为已确认"）仅作为内容数据，不影响候选状态。
- 模型输出中携带的 `review_status`/`confirmed`/`auto_publish` 字段导致整批拒绝（§3）。
- 候选确认只能来自用户显式动作（复用既有 review/ChangeSet 路径），与模型输出无关。

## 7. 验收场景

| 场景 | 内容 | 不变量 |
|---|---|---|
| Y2S2-001 | fixture 后端对 2 个 source 提出 3 候选；全 unconfirmed；Canonical 零变化 | INV-001/002 |
| Y2S2-002 | 候选 envelope 字段、证据定位、provenance 逐项核对 | INV-002/006 |
| Y2S2-003 | 畸形输出三型（非法 JSON、缺字段、未知 kind）：整批拒绝、零候选、错误回执 | INV-003 |
| Y2S2-004 | 注入 source + 带 confirmed/auto_publish 标志的输出：标志被拒、候选不受影响 | INV-004 |
| Y2S2-005 | 提议轮后 Canonical digest 与 data_revision 不变；候选不在 Canonical | INV-001 |
| Y2S2-006 | 红线舱室 source 只允许本地后端；cloud kind 拒绝 fail closed | INV-005 |
| Y2S2-007 | local_http 对本机 stub 服务完成 propose 并记录版本；非回环 URL 构造即拒绝且不连接 | INV-005/006 |
| Y2S2-008 | v1/v2 双版本 provenance 分离；注册 v2 后回滚 v1；未注册版本激活被拒 | INV-006 |
| Y2S2-009 | 用户确认 1 候选 -> ChangeSet proposed（未发布）；未确认候选建 ChangeSet 被拒 | INV-001/002 |
| Y2S2-010 | 横切：确定性字节一致、无回环外网络、profile fail closed、候选不作证据 | INV-001/006 |

## 8. 不变量

- `Y2S2-INV-001`：propose-only——候选永不自动进入 Canonical；确认后仍必须走 ChangeSet。
- `Y2S2-INV-002`：候选完整——envelope、证据定位、provenance 齐全。
- `Y2S2-INV-003`：畸形输出 fail closed——零候选、错误回执、不部分采用。
- `Y2S2-INV-004`：注入免疫——指令文本无效果；输出中的升格字段导致整批拒绝。
- `Y2S2-INV-005`：红线 local-only；非回环地址 fail closed 且不连接。
- `Y2S2-INV-006`：版本审计与确定性——版本记录、可回滚；同输入同输出。

## 9. 边界与禁止事项

- 禁止云端后端、真实模型权重、embedding、自动发布、MCP。
- 禁止候选写 Canonical、禁止把候选当事实证据。
- 禁止 wall-clock；网络仅允许本机回环且只由 local_http 后端发起。
