# MVP-B Episode 与分层摘要切片产品决定

## 1. 决定信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-B-EPISODE-SUMMARY-001` |
| 状态 | `decided` |
| 日期 | 2026-07-19 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| 前置能力 | Micro、A1 Answer Safety、B1 Candidate Review 已有合成验证 |
| 选择切片 | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| 交付阶段 | `product_decided` |

用户已指示继续推进项目。本决定只选择 PRD 已定义的窄切片，不修改 PRD、SPEC 或既有事实语义。

## 2. 决定

选择 MVP-B 的 B2 `Episode` 与分层摘要作为下一条切片，主需求为 PRD FR-103。

目标是在固定合成 Source 与既有 Canonical Context 上，形成可追溯的 `Episode`，并生成可失效、可重建、严格标识为 Derived 的分层摘要。摘要只能帮助浏览，不得成为 Assertion、Fact、ChangeSet proposal 或后续摘要的证据。

## 3. 范围

包含：

- 固定合成 Episode 的最小字段、时间边界、Source locator 和 Canonical 引用。
- 固定、可审计的 Episode 聚类边界；不使用模糊 NLP、LLM 或外部网络。
- 由 Episode 和 Canonical evidence 生成的日/阶段两级 Derived summary。
- summary dependency、`data_revision`、`view_revision`、`freshness_status` 与失效/重建。
- 用户读取时的 Source/Episode 回溯定位，以及 summary 不能作为证据的拒绝行为。
- 专属 synthetic fixture、oracle、offline runner 和 immutable verification result。

不包含：

- 真实日记、聊天、照片、语音、OCR、ASR 或任何工作区外输入。
- 通用自然语言摘要、模型调用、Embedding、RAG、人格推断或自动事实升级。
- Commitment、提醒、Semantic Diff、实体合并、权限 runtime、MCP、连接器、同步、财务、健康或专业建议。
- B1 预算策略、自动发布范围或 `DQ-002`/`DQ-011` 的重新裁决。

## 4. 不变量

1. `Episode` 是 Canonical 对象；其 Canonical 写入必须遵守 Source append 或 ChangeSet 合同。
2. summary 是 Derived Projection，不得反向成为任何事实型回答或 ChangeSet 的 Evidence Ref。
3. Source、Episode、Assertion、Summary 的引用方向必须可追溯；summary 不得覆盖原始时间、证据或历史状态。
4. Canonical revision 变化后，依赖 summary 必须重建或显式标记 `stale`；旧 payload 不得冒充 current。
5. 固定合成输入外的内容一律拒绝，拒绝不得创建 Canonical revision 或伪造 Source receipt。
6. Episode 聚类或摘要失败时，既有 Canonical 与已验证安全版本保持可读，且失败结果可审计。

## 5. 适用 SPEC 与前置证据

必须复核 S1（Episode/Projection 边界）、S2（时间与证据）、S3（ChangeSet/失效）、S5（识灵策略）、S6（可执行 harness）及 S7（存储/可移植性）。S4/S8/S9 默认不进入实现；若复核发现不可避免的依赖，必须缩小切片或回到 Product Decision。

前置通过证据：Micro 49/49、A1 35/35、B1 5/5。它们不能替代本切片的 suite。

## 6. 开放问题

本切片不重开 `DQ-002`、`DQ-011` 或任何 deferred 产品问题，因为不改变自动处理范围、Review Budget 或用户授权。未发现 B2 当前 blocking 产品问题。

## 7. 授权边界与下一步

本决定只授权 B2 的 SPEC applicability review、Traceability、ADR、suite 物化和 Implementation Plan。业务代码必须在 suite 物化和计划批准后开始。

下一步唯一动作：对 S1/S2/S3/S5/S6/S7 完成 `SLICE-MVP-B-EPISODE-SUMMARY-001` applicability review。
