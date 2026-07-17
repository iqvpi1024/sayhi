# MVP-A Answer Safety SPEC Applicability Review

## 0. 元数据

| 字段 | 值 |
|---|---|
| Review ID | `REVIEW-MVP-A-AS-SPEC-001` |
| Slice | `SLICE-MVP-A-ANSWER-SAFETY-001` |
| Product | `PRDv05.md` v0.5 Approved |
| Decision | `DEC-MVP-A-AS-001` |
| Date | 2026-07-17 |
| Review Target | S1-S9 current Approved baseline |

## 1. 结论

现有 SPEC 足以定义 A1 固定合成切片，不需要修改正式 SPEC 或发布新 PRD。

逐份结论：

| SPEC | Version | Applicability | 结论 |
|---|---:|---|---|
| S1 Semantic Object Model | v0.6 | `required` | `keep_current` |
| S2 Bitemporal & Evidence | v0.5 | `primary_required` | `keep_current` |
| S3 ChangeSet & Consistency | v0.4 | `boundary_required` | `keep_current` |
| S4 Privacy & Access | v0.4 | `not_applicable_runtime` | 不实现权限 runtime；只使用已授权固定合成 profile |
| S5 Shiling Policy | v0.4 | `not_applicable_runtime` | 不生成候选、不运行识灵；freshness policy 由查询 fixture 显式提供，不建立领域默认 |
| S6 Semantic Test Harness | v0.5 | `required` | `keep_current` |
| S7 Storage, Index & Portability | v0.3 | `boundary_required` | `keep_current` |
| S8 MCP Contract | v0.3 | `not_applicable` | 无 MCP/API runtime |
| S9 Ingestion & Migration | v0.4 | `not_applicable` | 无新摄取或迁移 |

Review Finding：P0=0、P1=0、P2=0、P3=1。P3 为现有 S6 `coverage_level` 名称仍使用 `micro_required_slice`；A1 通过同一 Matrix 内的独立 active-slice mapping 表达，不在本切片为命名整洁升版 S6。

## 2. S1 复核

适用内容：

- §6.4 Assertion 的 `assertion_kind`、perspective、review status。
- §5.3 Derived/Canonical 边界。
- `SOM-INV-002/003/004/010/013/015`。
- `SOM-AT-008/009/018/021`。

结论：S1 已明确 opinion/fictional 不因确认改变内容类型，Derived View 不能作证，不兼容 Assertion 并列保留。A1 不创建或修改 Canonical 对象，不触发对象状态机修订。

## 3. S2 复核

适用内容：

- §6.5 CoverageWindow、§6.6-§6.7 Evidence、§6.8 AnswerEnvelope、§6.9 六态。
- §7.3 Answer Status 为查询派生而非持久状态。
- §9 `BTE-INV-004/005/008/009/010/011/012/014/015`。
- §13 冲突检测与并列呈现；§14 失败降级。

A1 使用六个互相隔离的 fixture case，不声明所有复合条件的全局优先级。每个 case 的输入必须满足一个主状态的必要语义；若 materialized oracle 需要处理未由 S2 唯一决定的复合条件，必须停止并回 SPEC，不得由 evaluator 自定 precedence。

`stale` case 使用版本化、显式传入的 fixture policy，只证明“已声明 policy 下唯一证据超期”的 S2 行为，不建立产品默认阈值或领域 freshness 规则。

## 4. S3 复核

A1 查询路径为只读：

- 不产生 ChangeSet、proposal、revision、receipt 或 View 写入。
- 查询前后 `data_revision`、Canonical payload digest 和 Ledger count 必须不变。
- 若实现发现需要持久化评估结果，只能写 Derived cache，并且本切片默认不要求；不得借评估写 Canonical。

现有 S3 写入唯一入口和 Derived 边界足够，不需升版。

## 5. S6 复核

A1 独立建立 suite identity，不修改或复用 Micro 的 pass：

- `suite_defined=true` 只在验收合同完成后成立。
- materialized 前 executed/passed 必须 false。
- expected 与 actual 分离；固定 Clock、离线、合成、隐私扫描。
- required tests 必须同一次 A1 run 全部执行。
- A1 实现改变共享模块后，必须另行重跑 Micro regression；两个 suite 结果不能拼接。

S6 当前合同足够。`HTH-AT-027` 只针对 Micro 映射，不进入 A1 required。

## 6. S7 复核

S7 对 A1 只提供逻辑边界：

- Coverage declaration 属于 Source/Canonical 可追溯数据，不进入 Projection evidence。
- EvidenceAssessment 与 AnswerEnvelope 是 Derived、可重算结果。
- Derived 删除或失败不得改变 Source/Canonical/Ledger。
- 物理 SQLite 表和索引由 A1 ADR 决定，不写回 SPEC。

A1 不实现 Context Pack、导出、迁移、删除或长期容量目标。

## 7. Deferred 与旧结果

- `DQ-012` 保持 deferred；`BTE-AT-038` 不进入 A1 required。
- S4/S5/S8/S9 未被声明不重要，只是当前固定、已授权、离线查询不需要其 runtime。
- Micro result 继续作为上一实现提交的历史 current evidence；A1 修改共享实现后必须按 Change Control 重新判定并重跑，不得直接沿用 49/49。

## 8. Gate

SPEC Gate：`yes`。A1 达到 `spec_approved`，允许进入 Traceability、ADR 和 suite contract 定义；仍不允许业务编码。

## 9. 下一步唯一动作

固定 A1 人类可读验收合同和 exact required mapping，并回填 Requirements Matrix。
