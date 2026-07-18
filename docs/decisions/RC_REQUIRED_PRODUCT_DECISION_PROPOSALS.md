# Release Candidate 必需产品裁决提案

> 状态：`decided`。产品负责人于 2026-07-18 明确授权“不要门禁，直接继续任务”；本文件记录按最保守推荐方案作出的执行裁决。它不修改 PRD 或 Approved SPEC。

## DQ-002 / DQ-011：B1 审查预算与预授权自动处理

PRD 与 B1 Decision 在两个 DQ 编号的描述上存在互换：PRD 将 `DQ-002` 描述为默认 Review Budget，`DQ-011` 描述为预授权自动处理范围；B1 Decision 的文字次序相反。无论编号，B1 必须同时裁决下列两个语义。

### 提案 B1-A：审查预算

- 默认 profile 不按用户模式变化；不存在隐藏的模式推断。
- 仅允许显式、持久化且可审计的用户配置改变预算。
- critical Candidate 永不因预算被 suppress；预算只影响打扰频率，不删除候选、证据或风险。
- 初始固定数值建议：`session=3`、`weekly=12`；达到预算时返回 `suppressed_by_budget`，保留可手动查看的队列。

### 提案 B1-B：预授权自动处理

- MVP-B 默认禁止自动写入 Canonical。
- 即使用户预授权，唯一可自动完成的动作限于确定性 Source append receipt metadata 的机械补全，且必须可撤销、可审计、不可改变 owner/subject/compartment/sensitivity/retention、不可产生 Fact/verified/RelationshipState/Decision/Outcome。
- 所有个人语义 Canonical ChangeSet 仍要求显式用户确认。

### 已裁决文本

`接受 B1-A 与 B1-B；DQ-002/DQ-011 的编号按 PRD v0.5 的定义保留，B1 Decision 中的互换文字作为 superseded erratum 记录。`

## DQ-006：Decision 与专业建议边界

### 提案 C1-A

- C1 只处理用户记录的通用个人决策结构，不提供或排名医疗、法律、投资、债务、保险、税务或其他受监管专业建议。
- 对被标识为上述领域的输入，C1 仅允许保存为 `Source`/`reported`/`opinion` 或用户自己的 Decision 记录；不得生成推荐、风险评级、预测、自动选择或专业结论。
- 用户仍可记录“已咨询专业人士”的事实或观点，但系统必须保留 perspective/source，且不得把该记录扩展为专业建议或 verified world claim。
- C1 的 Scenario 只允许 `predicted|fictional` Assertion，永不自动升级为 `observed`、Fact 或 Outcome。

### 已裁决文本

`接受 C1-A；C1 在 MVP 仅提供非专业、用户主导的通用 Decision/Outcome 记录与回顾，不提供受监管领域建议或自动推荐。`

## DQ-005：许可证与公开发布

该项不阻塞当前 D0/D1 本地合成演示，但阻塞 D2/D3、正式 LICENSE、公开 tag 和 GitHub Release。建议在完成 B1/C1 前保持 `deferred`，并继续不声明开源许可证或公开发布可用性。

## 影响与确认后动作

| 确认项 | 影响 |
|---|---|
| B1-A/B | 更正 B1 Decision 编号歧义，建立 B1 applicability、ADR、Acceptance、suite、Plan 并实施 WS-04 |
| C1-A | 建立 C1 applicability、ADR、Acceptance、Approved Plan/suite 并实施 WS-05 |
| DQ-005 | 仅在 D2/D3 前选择 LICENSE、签名和公开发布合同；当前不执行 |
