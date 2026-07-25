# ADR-0011：B4 对账检测实现位置、投影重建比较策略与 Semantic Diff 实现

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-25 |
| Slice | `SLICE-MVP-B-RECONCILIATION-001` |
| Contract | `SPEC-B4-RECONCILIATION-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

B4 切片需要三个相互独立但同层的技术裁决：对账检测器（incremental/deep）在代码结构中的实现位置与访问方式；深度对账逐投影分区重建与比较的具体策略（digest 形态与重建入口）；Semantic Diff 的实现形态（派生时机、比较算法与不持久化保证）。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §16/§20（FR-105/FR-106）；`DEC-MVP-B-RECONCILIATION-001` |
| SPEC | `SPEC-B4-RECONCILIATION-001` §2..§7；S2 v0.5；S3 v0.4；S6 v0.5 |
| Acceptance Test | `B4-001..010` |
| Traceability | 矩阵 §4.13 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；SQLite PRAGMA 沿用 ADR-0001（`foreign_keys=ON`、`journal_mode=DELETE`、`synchronous=FULL`）。
- 检测器只读 Canonical、L2 投影与 revision ledger；本切片不实现任何修复性写入；对账发现唯一终态 `quarantined_reported`。
- 深度对账逐分区（person_card / relationship_timeline / current_state）重建比较，不要求整图重算（`B4-INV-003`）。
- Semantic Diff 不持久化、不作证据、不触发写入；diff 查询前后 Canonical digest 不变（`B4-INV-002`）。
- 不决定：多设备同步、自动修复执行器、后台调度器、性能 SLO、通用图 diff、真实数据。

## 4. 候选方案

### Option A：独立只读模块 `reconciliation.py` + 独立查询模块 `semantic_diff.py` + 复用既有 projector 重建比较

- 做法：新建 `src/noetide_micro/reconciliation.py` 实现对账运行状态机（`requested -> scanning -> report_issued`）与四类增量发现检测 + 三分区深度对账；新建 `src/noetide_micro/semantic_diff.py` 实现查询时字段级派生 diff。两者经 `SemanticStore` 只读访问；深度对账在隔离的临时 store 上复用既有 projector（`CoreViewProjector`、timeline reader、`CurrentStateService`）从 Canonical 快照逐分区重建，以规范化 digest 比较；diff 从 revision ledger 读取两个 revision 的规范化快照做字段级递归比较，仅在内存返回。
- 优点：只读职责与写入职责物理隔离，天然满足 `B4-INV-001/002`；重建比较复用已 verified 的 projector，不引入第二套投影逻辑；digest 规范化复用 `store._canonical_json/_canonical_digest`，比较可重放。
- 代价与风险：新增两个模块与适配器，行数增加；需保证重建入口与生产投影入口完全一致（同一函数、同一 clock 注入方式）。
- 可逆性：纯新增模块，可整体回退，不触碰既有 verified 切片。

### Option B：对账逻辑并入 `views.py`/`current_state.py`，diff 并入 `queries.py`

- 优点：模块数不增加。
- 代价与风险：把只读诊断职责混入投影/查询生产路径，扩大既有 verified 模块的变更面，破坏 A6 硬化后的冻结面；diff 并入查询层容易滑向缓存，违反 `B4-INV-002` 的倾向难静态阻断。

### Option C：深度对账用 SQL 层整库快照比较

- 优点：实现最短。
- 代价与风险：绕过投影语义层，digest 无法对齐"从 Canonical 重建"的合同语义；整库比较违反 `B4-INV-003`（逐分区、不整图重算）。

## 5. 决定

采纳 Option A，三项裁决如下。

**5.1 对账检测位置**：`src/noetide_micro/reconciliation.py`。对外仅暴露 `run_reconciliation(store, mode, clock, ...)` 形态的只读入口，返回 `ReconciliationReport`（dict，含 `mode`、`findings`、`deep_result`/`summary`）；内部实现四类增量发现（failure_queue、stale_view、orphan_reference、unconsumed_changeset）与三分区深度对账；运行状态机 `requested -> scanning -> report_issued`，自身失败时返回显式 unavailable 报告壳而非空报告。fixture 中的异常注入（投影失败条目、stale 视图、孤儿引用、未消费 ChangeSet、投影偏差）由测试 adapter 完成，检测器本身无写入 API。

**5.2 投影重建比较策略**：深度对账按 `person_card`、`relationship_timeline`、`current_state` 三分区独立执行。每个分区在隔离临时 store 中以固定 synthetic clock 复用生产 projector 从 Canonical 快照重建期望投影，与磁盘上的实际投影做规范化 JSON digest 比较（复用 `store._canonical_json/_canonical_digest`）；输出逐分区 `match | mismatch`，mismatch 时报告期望/实际 digest；绝不回写实际投影。

**5.3 Semantic Diff 实现**：`src/noetide_micro/semantic_diff.py` 提供 `compute_diff(store, object_ref, base_revision, target_revision)`，从 revision ledger 取两个 revision 的规范化对象快照，做字段级递归比较，产出 `{change_type: create|modify|no_change, field_diffs: [{field_path, before, after}]}`；结果仅存在于调用方内存，不写入任何表、不缓存；目标 revision 不存在时显式拒绝。

## 6. 后果

### 正向后果

- `B4-INV-001/002` 由结构保证：检测器与 diff 模块没有任何 Canonical/投影写入依赖，suite 可用 digest 前后对比直接证明。
- 深度对账的比较正确性继承已 verified projector 的正确性，oracle 只需绑定 digest 与分区结果。
- `B4-001..010` 每个场景可映射到单一模块的确定性输出，runner/oracle 绑定简单。

### 负向后果与债务

- 两个新模块与 b4 testing adapter 增加维护面；重建比较依赖固定 clock 与规范化序列化的稳定性，序列化规则变化会使历史 oracle digest 失效（届时需新 oracle 版本而非静默更新）。
- 性能 SLO 不在本切片，深度对账在真实大 profile 上的成本未知，留待 C 系列切片。

## 7. 验证与回退

- 验证方式：`B4-001..010` 可执行场景；`tools/validate_b4_suite.py` preflight；diff 查询前后 Canonical digest 一致性断言（`B4-INV-002` 正反证明）。
- 失败信号：检测器或 diff 产生任何写入、mismatch 被静默修复、diff 被持久化或引用为证据、重建比较未逐分区执行。
- 回退步骤：删除两个新模块与 B4 suite 工件、回退本 ADR 状态；不影响任何已 verified suite。
- 数据兼容：本 ADR 不引入 schema 变更。

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | 创建 `B4_RECONCILIATION_ARCHITECTURE.md` |
| Suite Materialization | 物化 `b4_reconciliation_v1` fixture/oracle/runner/validator/manifest；preflight 后业务测试保持 `not_executed` |
| Implementation Plan | 创建 B4 Implementation Plan 与 Task Cards |
| Traceability | 矩阵 §4.13 状态行 `adr_accepted` 更新为 `true` |

## 9. 未决项

- 自动修复执行器与修复 ChangeSet 的合同：明确排除在本切片外，后续切片需要时另行 Decision + ADR。
- 深度对账调度形态（手动命令 vs 周期任务）：本切片只提供手动只读入口，调度留待 C5/C6。
- 以上均不影响本决定成立。
