# PRD v0.6 与九份 SPEC 兼容复审

## 1. 审查结论

当前结论：`yes`（全部兼容，绑定同步 + 最小升版）。

九份 SPEC 已按 S1 至 S9 完成 v0.6 兼容复核。PRDv06 相对 v0.5 只新增内容（§2、§14.5、§17.4、§18.8、§19.5、§21.6、§24.5、§24.7、§25.1、§26 Case H、§27），未修改任何既有语义；因此本次复核无语义修订，只做产品基线绑定同步与最小升版。

Finding 计数：P0=0、P1=0、P2=0。

## 2. 审查基线

- 当前产品基线：`PRDv06.md` v0.6，Approved Product Baseline。
- canonical LF SHA-256：`4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8`。
- 历史只读基线：`PRDv05.md` v0.5（`34DA32FF...`）、`PRDv04.md` v0.4（`F2A4D795...`）。
- 批准决定：`DEC-PRD-V06-001`（2026-08-01），范围授权 `DEC-Y2-ENTRY-001` §2.7。
- 审查日期：2026-08-01。

## 3. 逐份结论

- S1 Semantic Object Model：v0.6 -> v0.7，`compatible_after_revision`。绑定同步；§8.1/§9.4/12 对象引用同步至 PRD v0.6；无语义修订。
- S2 Bitemporal & Evidence：v0.5 -> v0.6，`compatible_after_revision`。绑定同步；无语义修订。
- S3 ChangeSet & Consistency：v0.4 -> v0.5，`compatible_after_revision`。绑定同步；无语义修订。
- S4 Privacy & Access Policy：v0.4 -> v0.5，`compatible_after_revision`。绑定同步；§17.4 云端授权原则与既有舱室语义不冲突，细则属 Y2-S4 slice contract。
- S5 Shiling Policy：v0.4 -> v0.5，`compatible_after_revision`。绑定同步；§14.5 模型政策与 propose-only 边界一致，实现合同属 Y2-S2 slice contract。
- S6 Semantic Test Harness：v0.5 -> v0.6，`compatible_after_revision`。绑定同步；无语义修订。
- S7 Storage, Index & Portability：v0.3 -> v0.4，`compatible_after_revision`。绑定同步；§21.6 真实数据生产合同验收属 Y2-S1 slice contract。
- S8 MCP Contract：v0.3 -> v0.4，`compatible_after_revision`。绑定同步；§19.5 确认 runtime 后置，重开 DQ-013 前保持图纸状态。
- S9 Ingestion & Migration：v0.4 -> v0.5，`compatible_after_revision`。绑定同步；文件夹导入合同属 Y2-S1 slice contract。

## 4. 新增语义的覆盖缺口声明

PRDv06 新增的五块语义（§14.5 模型接入、§18.8 本地 Web UI、§19.5 MCP 时机、§21.6 真实数据生产合同、§24.5 Year 2 切片）目前没有任何 SPEC 或 slice contract 覆盖。按 §27.3 门禁，它们不得直接实现；每个 Year 2 切片必须先完成 slice decision、SPEC applicability review、slice contract、traceability、ADR、suite 物化后才可编码。本复审不授权任何业务编码。

## 5. 不变确认

- 32 条 FR、12 核心对象、assertion 八态、answer 六态、Micro/MVP 白名单、删除与导出语义在 v0.6 中与 v0.5 完全一致。
- 已 verified 的首年切片（Micro、A1-A6、B1-B6、C1-C6、D0-D3）结果继续有效；v0.6 不改变其 oracle、fixture 或结论。
- `DQ-001..013` 中仅 DQ-008 被 `DEC-Y2-ENTRY-001` 部分触及（首个连接器）；其余保持 deferred。
