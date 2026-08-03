# Y2-S2 本地模型提议式整理切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-Y2-S2-001` |
| Date | 2026-08-01 |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| Upstream Decision | `DEC-Y2-ENTRY-001` §2.1/§2.6（模型接入政策，Y2-S2） |
| Current Slice | `SLICE-Y2-S2-LOCAL-MODEL-001` |

## 1. 决定内容

选择 Y2-S2 模型能力接口 + 本地模型提议式整理作为 Year 2 第二个切片。具体决定：

1. 切片只证明：模型能力接口（propose-only）、本地后端（本机回环 OpenAI 兼容端点，stdlib HTTP）、确定性 fixture 后端（测试/演示）、红线舱室 local-only enforcement、畸形输出 fail closed、注入免疫、模型/prompt 版本审计与回滚。
2. 模型输出只能是 Candidate Envelope（复用 S5 候选语义与 B1 候选基础设施）：全部 `review_status=unconfirmed`，永不直接写 Canonical；确认后仍必须走既有 ChangeSet 链路。
3. 候选必须携带 provenance：model_id、model_version、prompt_version、source 证据定位。
4. 畸形模型输出（非法 JSON、缺必填字段、未知候选类型）fail closed：零候选、错误回执、不部分采用。
5. Source 中的指令性文本（提示注入）只是数据；模型输出中的"确认/自动发布"标志被忽略，候选状态不受影响。
6. 红线舱室（health、finance、relationship、sealed）内容只允许本地后端；任何非回环地址的后端配置 fail closed 且不发起连接。
7. 不捆绑任何模型权重；不调用云端；真实本地模型（Ollama 等）不在测试范围，测试只使用确定性 fixture 后端与本机 stub HTTP 服务。

## 2. 产品依据

- PRDv06 §14.5：模型接入政策（propose-only、本地优先、红线 local-only、版本审计、诚实降级）。
- PRDv06 §14.4：提示注入边界。
- PRDv06 §6.1/§11.4：用户裁决权与自动处理边界；候选不等于事实。
- PRDv06 §22.4：模型升级门禁（版本记录、隔离评测、可回滚）。
- PRDv06 §26 Case H：候选全部 unconfirmed，确认一条走 ChangeSet。

## 3. 切片范围

- `src/noetide_micro/model_capability.py`：后端接口、FixtureModelBackend、LocalHttpBackend（stdlib urllib，仅回环）、ModelCurator（编排 + 输出校验 + 候选生成 + provenance + 版本注册与回滚）。
- 复用 `store.append_source` 读取 Source；候选存放于 Derived 层（不落 Canonical）；确认流复用既有 changesets 提案路径。
- Suite：10 场景，覆盖 6 条不变量。

## 4. 非目标

- 云端模型后端（Y2-S4）、真实模型权重评估、微调、embedding/reranker。
- 通用 NLP 质量保证；候选质量评分属于产品校准，不在本切片验收。
- MCP runtime、多 Agent、自动发布、真实数据模式开放的单独宣告。

## 5. 不变量

- `Y2S2-INV-001`：propose-only——候选永不自动进入 Canonical；确认后仍必须走 ChangeSet。
- `Y2S2-INV-002`：候选完整——envelope 字段、证据定位、provenance（model_id/model_version/prompt_version）齐全。
- `Y2S2-INV-003`：畸形输出 fail closed——零候选、错误回执、不部分采用。
- `Y2S2-INV-004`：注入免疫——Source 内指令文本无效果；模型输出中的确认/发布标志被忽略。
- `Y2S2-INV-005`：红线 local-only——红线舱室拒绝非本地后端；非回环地址 fail closed 且不连接。
- `Y2S2-INV-006`：版本审计与确定性——版本记录、可回滚；同输入同输出。

## 6. 授权与下一步

本决定授权 S1/S2/S5 SPEC applicability review，随后 slice contract、traceability、ADR、suite 物化、Implementation Plan。不授权业务编码。
