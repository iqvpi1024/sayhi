# A3 实体合并候选与拆分回滚 SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `A3-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-24 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-ENTITY-MERGE-001` |
| 切片 | `SLICE-MVP-A-ENTITY-MERGE-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | A3 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Entity `identity_status` 状态机（`provisional/active/merged/retired`，`merged -> active` 仅经已确认 split/revert ChangeSet）；`merged_into` 字段；名称相同禁止自动合并；merge/split 必须可审计并保留原 Source identity；`SOM-AT-017` | 合并发布时哪些 Canonical 引用（Relationship 参与方、State/Assertion `subject_ref`）必须重定向、重定向是否产生各对象新 `object_revision` |
| S2 Bitemporal & Evidence v0.5 | `partial` | 双时态、Historical 不覆盖、Source provenance 保留 | 合并/拆分如何记录 recorded 时间链；被合并实体的历史区间保持可见的具体合同 |
| S3 ChangeSet & Consistency v0.4 | `partial` | `merge`/`split` proposal_operation 枚举、原子发布、revision 递增、Core View stale 义务 | 一次 merge ChangeSet 内多对象引用重定向的原子性合同；split compensation 如何精确恢复合并前引用（需要可审计的合并记录）；合并后三个 Core View 的 stale/重建行为 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | A3 exact scenario 集、failure injection（部分重定向失败不得部分应用）、current result 绑定 |

S4、S5、S7、S8、S9 不进入 A3：本切片不建设权限/舱室 runtime（A4）、新的识灵候选生成（只用固定合成 proposal 输入）、新存储格式、MCP、真实导入或迁移。

## 发现与处理

1. S1 定义了 `identity_status` 状态机与 `merged_into`，但未定义合并发布时引用重定向的对象集合与 per-object revision 语义。
2. S3 把 `merge`/`split` 列为合法 proposal operation，但未定义一次 ChangeSet 内跨多对象的引用重定向原子性，也未定义 split 恢复合并前引用所需的合并记录（pre-merge reference snapshot）。
3. 既有 Micro 不变量“trust、closeness、人格判断不被自动修改”需要显式绑定到 merge/split 场景。
4. 合并后 current_state（A2 已验证）必须显式 stale 或重建一致，不得伪装 fresh。

处理：新增 A3 slice contract，闭合引用重定向集合、原子性、合并记录与 split 恢复等价、视图失效、不作证边界与可执行验收。该合同不得修改基础 SPEC，不得引入自动合并、模糊身份匹配、权限 runtime、UI 或真实数据。

## 下游影响

在 A3 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 A3 entity merge/split slice contract，并将引用重定向、原子性、split 等价恢复、视图失效与验收场景绑定后再进入 Traceability。
