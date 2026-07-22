# A2 current_state Core View 切片合同复核

| 字段 | 值 |
|---|---|
| Review ID | `A2-CONTRACT-REVIEW-001` |
| Contract | `SPEC-A2-CURRENT-STATE-001` v0.1 |
| 结论 | `approved_for_traceability` |

## 结论依据

- `current_state` 被限定为 Derived Core View，不新增核心对象，符合 PRD §8、S1；Derived 不反向成为事实证据，符合 PRD §6、§10。
- "当前有效"判定只使用对象 `valid_time` 与 fixture clock，Current 不覆盖 Historical，符合 PRD §9、S2。
- 发布后 stale 义务、原子发布与 revision 语义符合 PRD §11-§12、S3；视图构建不产生 Canonical revision。
- 权限/舱室 runtime 明确留给 A4，本切片 fail closed，符合 S4 边界且不提前建设。
- 真实数据、查询语言、UI、连接器、同步均明确为非目标。

## 发现

无 A2 blocking 产品歧义。通用查询、Core View 白名单扩展（属 MVP-B）、权限模板保持后置。

## 下一步

建立 FR-006/FR-008/FR-105（MVP-A 切片）的 A2 Traceability，随后才可选择 ADR 和物化 executable suite。
