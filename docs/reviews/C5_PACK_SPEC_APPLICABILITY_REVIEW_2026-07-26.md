# C5 Context Pack & Encrypted Backup SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `C5-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-26 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-C-PACK-001` |
| 切片 | `SLICE-MVP-C-PACK-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | C5 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Derived 不作证据（Markdown 为解释性副本）；删除/导出语义边界 | DeletionReceipt 八成分结构；RestoreReceipt 结构；S1 未定义备份/恢复回执对象 |
| S2 Bitemporal & Evidence v0.5 | `partial` | data_revision 语义；历史关系（current/historical） | 恢复后 revision 一致性证明；备份与源库字节一致性验收方式 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner/result 四态 | C5 exact scenario 集、篡改注入、错误密钥注入、确定性渲染 oracle |
| S7 Storage, Index & Portability v0.4 | `partial` | Context Pack JSON 导出/校验/导入机制（已 verified）；checksums/manifest 模式；_safe_relative 防护 | Markdown 渲染合同；本地加密备份语义（非生产构造标注）；删除诚实性八成分报告；S7 未覆盖加密备份与删除回执 |

S3 不进入 C5：导出/备份/校验均为 read-only，无 Canonical 写入；恢复写入全新目标库不经 ChangeSet（属存储层语义，S7 范围）。S4、S5、S8、S9 不进入 C5：不建设权限 runtime、候选生成策略、MCP 或导入迁移（真实导入属后续切片）。

## 发现与处理

1. S7 覆盖了 JSON Pack 导出/校验（已 verified 切片），但没有 Markdown 渲染合同；PRD §24.x 要求 Markdown+JSON Pack，路线图要求独立可读。
2. 没有任何 SPEC 覆盖本地加密备份；PRD §24.x 首年范围明确要求。stdlib 无 AEAD，切片用确定性构造并显式标注非生产（ADR 裁决），生产加密推迟到 D2/D3。
3. S1 给了删除语义边界，但八成分诚实回执（PRD §534）无对象级合同；`pending_expiry`/`out_of_control` 标记需要明确定义。
4. 恢复语义（字节一致、不覆盖源库、回执哈希）无现有合同。

处理：新增 C5 slice contract，闭合 Markdown 渲染、Pack 校验、加密备份、恢复、删除诚实性与 fail-closed 边界。不得修改基础 SPEC，不得引入生产加密宣称、自动备份、云端或真实数据。

## 下游影响

在 C5 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 C5 Context Pack & Encrypted Backup slice contract，绑定 Markdown 渲染、校验、加密备份、恢复、八成分删除回执与 fail-closed 边界后进入 Traceability。
