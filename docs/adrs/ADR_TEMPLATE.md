# ADR-XXXX：<一个具体技术决定>

## 0. 元数据

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-XXXX` |
| Status | `Proposed` |
| Date | `YYYY-MM-DD` |
| Slice | `<slice_id>` |
| Decision Owner | `<role>` |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

用一句可比较、可裁决的话描述当前切片必须解决的技术问题。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `<reference>` |
| SPEC | `<versioned section>` |
| Acceptance Test | `<test refs>` |
| Traceability | `<matrix rows>` |

## 3. 约束与非目标

列出必须满足的语义、隐私、可移植性、失败和恢复约束；明确本 ADR 不决定的事项。若约束无法从已批准基线推导，停止并转入产品裁决。

## 4. 候选方案

### Option A：<名称>

- 做法：
- 优点：
- 代价与风险：
- 可逆性：

### Option B：<名称>

- 做法：
- 优点：
- 代价与风险：
- 可逆性：

### Option C：暂不决定

说明推迟决定是否会阻止 suite 物化或实现。

## 5. 决定

在状态变为 `Accepted` 前保持为空。记录选择及其直接理由，不重复宣传产品愿景。

## 6. 后果

### 正向后果

- `<consequence>`

### 负向后果与债务

- `<tradeoff>`

## 7. 验证与回退

- 验证方式：`<tests/measurements>`
- 失败信号：`<observable failure>`
- 回退步骤：`<reversible steps>`
- 数据兼容：`<preservation/migration requirement>`

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | `<none/update/create>` |
| Suite Materialization | `<impact>` |
| Implementation Plan | `<impact>` |
| Portability / Privacy | `<impact>` |

## 9. 未决项

只记录不影响本决定成立的后续问题。会改变用户可见行为的问题必须回到 OPEN_QUESTIONS。
