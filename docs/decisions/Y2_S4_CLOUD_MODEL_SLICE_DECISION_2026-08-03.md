# Y2-S4 云端模型可选后端切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-Y2-S4-001` |
| Date | 2026-08-03 |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| Upstream Decision | `DEC-Y2-ENTRY-001` §2.1.3/§2.6（云端模型可选后端，Y2-S4） |
| Current Slice | `SLICE-Y2-S4-CLOUD-MODEL-001` |

## 1. 决定内容

选择云端模型可选后端作为 Year 2 第四个切片。具体决定：

1. 云端模型后端是可插拔 ModelCapability 的显式可选后端，默认禁用；没有用户显式授权时，任何云端后端不得被调用，任何云端候选不得产生。
2. 授权按舱室与目的分别授予，必须绑定 `actor`、`purpose`、`compartments`、`source scope`、`expires_at` 和可撤销状态；授权与请求任一维度不匹配即拒绝，到期或撤销后立即失效。
3. `health`、`finance`、`relationship`、`sealed` 红线舱室内容永远只许本地处理；即使授权文本包含这些舱室，云端后端也必须 fail closed 拒绝，且不发起外发。
4. 外发前必须生成并确认脱敏数据范围预览；预览只展示将离开本机的 `source_id`、内容哈希、字节长度、舱室与定位，不包含原始正文。没有有效预览时不得外发。
5. 所有授权创建/撤销、预览、允许、拒绝、调用成功与失败均写入可审计 Ledger 记录；候选继续 propose-only，不写 Canonical，不自动确认。模型、prompt 版本进入版本注册与候选 provenance，支持回滚。
6. 云端后端使用 Python 标准库 HTTP 客户端或确定性 fixture 后端；本切片不引入第三方依赖、不创建账户、不存储真实云端凭据、不自动上传。测试只使用显式合成 fixture 与本机 loopback stub，禁止真实公网调用。
7. 本切片只证明云端模型后端的授权门、红线门、预览门、审计与诚实降级；不开放真实数据模式，不实现 MCP，不改变本地模型或本地 Web UI 语义。

## 2. 产品依据

- PRDv06 §14.5.3：云端为显式例外，默认禁用，按舱室与目的显式授权，授权有范围和到期；红线舱室永远只许本地处理，云端后端必须 fail closed。
- PRDv06 §17.4：默认最小披露；临时授权有范围和自动到期；外发前提供脱敏预览；真实个人数据默认永不出本机；云端授权按舱室与目的分别授予。
- PRDv06 §22.4：模型、prompt 版本记录；升级先隔离评测；支持回滚；不改变 Source 和用户确认历史。
- PRDv06 §24.5：Y2-S4 关键约束为默认禁用、显式授权、红线 fail closed。
- PRDv06 §25.1：云端授权误配风险由默认全关、按舱室授权、红线 fail closed、外发前预览缓解。
- PRDv06 §26 Case H：健康舱室日记即使存在，也不被送往任何云端后端。

## 3. 切片范围

- `src/noetide_micro/cloud_model.py`：云端授权门、脱敏预览、审计记录、fixture/HTTP 云端后端与编排器；候选复用 Y2-S2 的 envelope/provenance/版本语义。
- `src/noetide_micro/y2s4_testing_adapter.py`：临时目录 + 显式合成 fixture + loopback stub 的 contract adapter。
- Suite：10 场景，覆盖 6 条不变量；全部使用固定合成 profile `y2s4_cloud_model_v1`。

## 4. 非目标

- MCP runtime（Y2-S5）、多设备同步、账户体系、真实云端凭据入库、自动上传、真实数据模式。
- 扩大预授权自动处理范围（`DQ-011` deferred）；云端模型输出仍只 propose。
- 修改任何已 verified 切片（含 Y2-S2 local model）的 fixture/oracle/result 或业务代码语义。
- 真实公网云端调用、第三方 SDK、真实模型评测或生产密钥管理。

## 5. 不变量

- `Y2S4-INV-001`：default closed——无有效显式授权即无云端调用、无云端候选。
- `Y2S4-INV-002`：red line fail closed——红线舱室内容即使有授权也不外发，且拒绝记录不泄露正文。
- `Y2S4-INV-003`：bounded grant——授权绑定 actor/purpose/compartments/source scope/expires_at，可撤销；任一不匹配、到期或撤销即拒绝。
- `Y2S4-INV-004`：preview before send——每次外发前必须存在匹配的脱敏数据范围预览；无预览不发送，预览不含原始正文。
- `Y2S4-INV-005`：audit & rollback——授权、预览、允许、拒绝、成功、失败全部可审计；候选 propose-only；Canonical 与 revision 不变；版本可回滚。
- `Y2S4-INV-006`：deterministic/stdlib/synthetic/offline——fixture clock、stdlib only、显式合成数据、测试只走 loopback stub；失败时诚实降级，不得用陪伴话术掩盖模型缺席。

## 6. 授权与下一步

本决定授权 S1/S2/S3/S4/S5/S6/S7/S8/S9 SPEC applicability review，随后 slice contract、traceability、ADR、suite 物化、Implementation Plan。不授权业务编码。
