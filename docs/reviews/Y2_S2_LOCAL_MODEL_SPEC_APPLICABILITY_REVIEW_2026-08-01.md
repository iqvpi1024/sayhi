# Y2-S2 SPEC Applicability Review

| 字段 | 值 |
|---|---|
| Review ID | `Y2S2-SPEC-APPLICABILITY-001` |
| Date | 2026-08-01 |
| Slice | `SLICE-Y2-S2-LOCAL-MODEL-001` |
| Decision | `DEC-Y2-S2-001` |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| 结论 | `pass_with_slice_contract_required` |

## 1. 审查范围

按 `DEC-Y2-S2-001` §6 授权，只复核 S1（Semantic Object Model v0.7）、S2（Bitemporal & Evidence v0.6）、S5（Shiling Policy v0.5）。其余 SPEC 无直接语义交集。

## 2. 逐份结论

### S5 Shiling Policy v0.5：`pass_with_slice_contract_required`

- Candidate Envelope、propose-only、protected semantics、DQ-011 最保守 automatic 边界与切片一致。
- 缺口 1：模型后端的接入形态（fixture/local-http）、后端选择的红线舱室规则 S5 未定义——由 slice contract §2/§5 闭合。
- 缺口 2：模型输出的 schema 校验、畸形输出处置、注入免疫的可执行判据 S5 未定义——由 slice contract §3/§6 闭合。
- 缺口 3：模型/prompt 版本注册与回滚的运行语义 S5 未定义——由 slice contract §4 闭合。

### S1 Semantic Object Model v0.7：`pass`

- 候选不产生新核心对象；Candidate 作为 propose-only 派生语义与 12 对象封闭集一致；Assertion 八态不被模型输出触碰。

### S2 Bitemporal & Evidence v0.6：`pass`

- 候选的 evidence_refs 必须指向 Source locator（file_path_v1 或 text_utf8_byte_range_v1），不得指向模型生成文本；证据维度不因模型重复而增加。

## 3. 结论与条件

`pass_with_slice_contract_required`：基础 SPEC 不阻碍切片，但三个缺口必须由 `SPEC-Y2S2-LOCAL-MODEL-001` 显式闭合后才可物化 suite 或编码。禁止 slice contract 扩张到云端后端、真实模型评估或自动发布。
