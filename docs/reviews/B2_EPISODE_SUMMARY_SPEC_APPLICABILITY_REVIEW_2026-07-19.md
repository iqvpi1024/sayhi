# B2 Episode 与分层摘要 SPEC 适用性复核

## 1. 复核信息

| 字段 | 值 |
|---|---|
| Review ID | `B2-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-19 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-B-EPISODE-SUMMARY-001` |
| 切片 | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| 结论 | `pass_with_slice_contract_required` |

## 2. 逐份结论

| SPEC | 结论 | B2 可直接复用的合同 | 必须补齐的切片合同 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `partial` | Episode 是核心对象；Projection/summary 是 Derived；Derived 不得作证 | Episode 最小字段、引用边界、B2 candidate/publish 形态 |
| S2 Bitemporal & Evidence v0.5 | `pass` | valid/recorded/source/ingested time、Source locator、Derived evidence 禁止 | Episode 时间聚类输入与摘要展示的时间选择 |
| S3 ChangeSet & Consistency v0.4 | `partial` | Canonical 写入经 ChangeSet；L3 stale/rebuild/失败降级 | Episode 发布 impact 与 summary 失效/重建 receipt |
| S5 Shiling Policy v0.4 | `partial` | Episode 聚类/分层摘要只能是可回源 Derived，不得生成稳定 Fact | 固定合成聚类规则、禁止自动升格与失败结果 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner 四态和 immutable result | B2 exact required 集、oracle 与失败注入 |
| S7 Storage, Index & Portability v0.3 | `partial` | Derived 可删除重建、revision/freshness、独立可读边界 | Episode/summary 的最小持久表示与 rebuild equivalence |

S4、S8、S9 不进入本切片：B2 不建立权限 runtime、MCP runtime、真实导入或迁移。若后续实现需要上述能力，必须重新审查切片范围。

## 3. 发现与处理

1. S1 §5/§6 只保留 Episode 的最小边界，S5 §6.5/§11 明确完整 Episode 流程后置；直接编码会让字段、状态与失败语义由实现猜测。
2. 现有 S3 的 L3 规则可约束摘要 stale，但没有 B2 的 dependency set 或 summary rebuild receipt 结构。
3. 现有 S6/S7 能支持离线、确定性 suite 和 Derived 重建，不需要选择数据库、模型、框架或新依赖。

处理决定：新增 `B2_EPISODE_SUMMARY_SLICE_CONTRACT.md` 作为对 S1/S2/S3/S5/S6/S7 的窄范围组合合同。它只定义本切片，不改写基础 SPEC 的全局版本或其他切片。

## 4. 下游影响

在 B2 slice contract Approved 前：

- Traceability 只能标为 `product_decided`，不得将 FR-103 写为 implemented。
- 不得创建 B2 fixture/oracle/runner、ADR、Implementation Plan 或业务代码。
- Micro、A1、B1、C1、Synthetic Ingestion、Context Pack 的 current result 不因本复核而 superseded。

## 5. 下一步

起草并审查 B2 slice contract，补齐对象、状态机、不变量、失败与可执行验收测试后，再进入 Traceability。
