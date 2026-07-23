# A3 实体合并/拆分切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `A3-CONTRACT-REVIEW-001` |
| Contract | `SPEC-A3-ENTITY-MERGE-001` v0.1 |
| 结论 | `approved_for_traceability` |

## 结论依据

- `identity_status` 状态机与 `merged_into` 字段遵守 S1 §（Entity 状态机：`active -> merged`、`merged -> active` 仅经已确认 split/revert ChangeSet）；未新增核心对象，`merge_record` 被限定为 ChangeSet 发布的审计组成部分。
- merge/split 仅经用户确认的 ChangeSet 原子发布，遵守 PRD §10-§12、S3（`merge`/`split` 为合法 proposal operation）；无直接写入路径。
- 历史永不删除、原 Source identity 保留，符合 S1 不变量“Entity merge/split MUST 可审计并保持原 Source identity”与 PRD §12。
- 引用重定向集合闭合为 `relationship_party/state_subject/assertion_subject` 三类；split 以 `merge_record.pre_merge_references` 为唯一恢复依据，恢复等价可逐字段证明。
- trust、closeness、人格判断不被自动修改，延续 Micro 既有不变量；三个 Core View 显式 stale 或重建一致，复用 A2 已验证语义。
- 自动合并、模糊身份匹配、真实联系人导入、权限 runtime、UI、真实数据均明确为非目标；非 profile 输入 fail closed。

## 发现

无 A3 blocking 产品歧义。合并候选自动评分、非 Person 实体合并与批量合并不进入本切片，保持后置。

## 下一步

建立 FR-011 的 A3 Traceability，随后才可选择 ADR 和物化 executable suite。
