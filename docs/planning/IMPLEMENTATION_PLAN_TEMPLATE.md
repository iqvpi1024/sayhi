# Implementation Plan：<slice_id>

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `<plan_id>` |
| Status | `Draft` |
| Slice | `<slice_id>` |
| Baseline Commit | `<commit>` |
| Accepted ADR | `<adr refs>` |
| Suite Manifest | `<path + digest>` |
| Scope Owner | `<role>` |

## 1. 目标与非目标

只描述本切片要交付的可观察结果，并列出明确后置能力。

## 2. 输入合同

| PRD Requirement | SPEC Section | Acceptance Test | ADR |
|---|---|---|---|
| `<FR>` | `<section>` | `<required test refs>` | `<ADR>` |

## 3. 模块边界

列出拟新增/修改模块的职责、输入、输出和禁止责任。`TBD` 必须在计划批准前关闭。

## 4. 施工任务

| Task ID | 修改范围 | SPEC/Test 依据 | 完成条件 | 状态 |
|---|---|---|---|---|
| `TASK-001` | `<files/modules>` | `<refs>` | `<observable definition of done>` | `pending` |

任务状态只用于施工跟踪：`pending | in_progress | blocked | completed`。`completed` 不等于业务验证通过。

## 5. 实施顺序与检查点

说明依赖顺序、每个小步要运行的检查，以及何时停止并回到 Change Control。

## 6. 数据、隐私与恢复

- Fixture 只使用合成数据：`<yes/no>`
- 外部网络：`<disabled/justification>`
- 数据变更：`<none/details>`
- 回滚方式：`<steps>`
- PRD 保护：`<check>`

## 7. 验证计划

记录唯一 required set、运行命令入口、结果产物目录和通过标准。不得在执行前填写 `passed`。

## 8. 风险与未决项

会改变产品行为的问题必须写回 OPEN_QUESTIONS；会改变技术决定的问题必须回到 ADR。

## 9. 完成定义

- [ ] 所有计划任务完成。
- [ ] 追踪矩阵的 Implementation Module 已更新。
- [ ] required suite 在同一次 current run 中实际执行。
- [ ] Verification Result 已保存，未执行项没有被描述为通过。
- [ ] Gate Review 已排期，但尚未以计划本身视为通过。
