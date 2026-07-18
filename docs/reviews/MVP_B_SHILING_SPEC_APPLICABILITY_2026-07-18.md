# MVP-B Shiling SPEC Applicability Review

## 审查信息

| 字段 | 值 |
|---|---|
| Review ID | `REVIEW-MVP-B-SHILING-SPEC-001` |
| Date | 2026-07-18 |
| Product Baseline | `PRDv05.md` v0.5 |
| Decision | `DEC-MVP-B-SHILING-001` |
| Slice | `SLICE-MVP-B-SHILING-001` |

## 1. 审查范围

复核九份已批准 SPEC 对 B1 Candidate Review 的适用性：

- SPEC-SOM-001 (Semantic Object Model)
- SPEC-BTE-001 (Bitemporal & Evidence)
- SPEC-CS-001 (ChangeSet & Consistency)
- SPEC-PAP-001 (Privacy & Access Policy)
- SPEC-SHP-001 (Shiling Policy)
- SPEC-HTH-001 (Semantic Test Harness)
- SPEC-SIP-001 (Storage, Index & Portability)
- SPEC-MCP-001 (MCP Contract)
- SPEC-ING-001 (Ingestion & Migration)

## 2. 适用性结论

| SPEC | 适用性 | 说明 |
|---|---|---|
| SOM-001 | current | 12 对象模型继续有效；Candidate 作为 Ledger 记录类型已覆盖 |
| BTE-001 | current | 双时态、CoverageWindow 继续适用；B1 不新增时间语义 |
| CS-001 | current | ChangeSet 生命周期继续适用；B1 使用现有状态机 |
| PAP-001 | current-compatible | 字段级权限保持兼容；B1 不新增权限 runtime |
| SHP-001 | **需要升版** | Shiling Policy 是 B1 核心依赖，需增加 Review Budget 和候选聚合语义 |
| HTH-001 | current | 测试框架继续适用；B1 需新增验收场景 |
| SIP-001 | current | 存储层继续适用；B1 不新增存储需求 |
| MCP-001 | not-applicable | B1 不实现 MCP 接口 |
| ING-001 | current-compatible | 输入合同保持兼容；B1 不新增导入器 |

## 3. 需要升版的 SPEC

SPEC-SHP-001 (Shiling Policy) 需要升版以包含：

1. Candidate 聚合规则（去重、合并、价值评分）
2. Review Budget 定义（时间预算、数量预算、频率控制）
3. 审查分级策略（Critical/High/Normal/Low）
4. 事后可撤销策略的触发条件和降级路径
5. 候选生命周期（proposed -> aggregated -> reviewed -> accepted/rejected/deferred）

## 4. 不修改的 SPEC

SOM-001、BTE-001、CS-001、PAP-001、HTH-001、SIP-001 保持当前版本，不做升版。
MCP-001、ING-001 标记为 not-applicable。

## 5. 结论

- P0=0、P1=0
- SPEC-SHP-001 需要升版到 v0.2
- 其他 SPEC 保持 current-compatible
- 可以进入 B1 Traceability 和 ADR 规划

---
