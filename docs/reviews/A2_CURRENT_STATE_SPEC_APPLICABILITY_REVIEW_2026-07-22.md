# A2 current_state Core View SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `A2-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-22 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-CURRENT-STATE-001` |
| 切片 | `SLICE-MVP-A-CURRENT-STATE-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | A2 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Entity/Relationship/State/Assertion 的 Canonical 边界；State 的 subject_ref 配置 | `current_state` 视图选取哪些对象、字段与有效区间规则 |
| S2 Bitemporal & Evidence v0.5 | `partial` | valid_time/recorded 双时态；Current 不覆盖 Historical；直接 Source locator | 视图如何判定"当前有效"与历史区间排除 |
| S3 ChangeSet & Consistency v0.4 | `partial` | 发布后 revision 递增、Core View stale 义务、原子发布 | `current_state` 在每次 Canonical 变更后的失效/重建合同 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | A2 exact scenario 集、failure injection、current result 绑定 |
| S7 Storage, Index & Portability v0.3 | `partial` | Canonical/Derived 分层、projection 删除/重建、revision 语义 | `current_state` projection 的最小持久表示与依赖声明 |

S4、S5、S8、S9 不进入 A2：本切片不建设权限/舱室 runtime（属 A4）、新的识灵候选生成、MCP、真实导入或迁移。

## 发现与处理

1. S1/S2 定义对象与双时态，但没有第三个 Core View 的对象集合、字段子集与"当前有效"的可执行定义。
2. S3 只要求 Core View 确认后保持一致或显式 stale，未定义 `current_state` 的依赖集合与重建等价证明方式。
3. A1 的 AnswerEnvelope/freshness 已验证；A2 复用其 freshness 语义，不重复实现六态回答。

处理：新增 A2 slice contract，闭合视图对象集合、字段子集、有效区间判定、stale/重建、Derived 不作证与可执行验收。该合同不得修改基础 SPEC 或引入查询语言、UI、权限 runtime、真实数据。

## 下游影响

在 A2 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 A2 current_state slice contract，并将视图边界、freshness、失效/重建与验收场景绑定后再进入 Traceability。
