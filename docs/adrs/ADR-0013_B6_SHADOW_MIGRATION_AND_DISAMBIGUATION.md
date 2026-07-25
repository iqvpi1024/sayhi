# ADR-0013：B6 影子迁移实现方式与消歧传播计数策略

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-25 |
| Slice | `SLICE-MVP-B-SHADOW-MIGRATION-001` |
| Contract | `SPEC-B6-SHADOW-MIGRATION-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

B6 切片需要两个同层技术裁决：影子迁移的实现方式（影子副本如何产生、v1->v2 模拟变换的形态、迁移后如何验证）；压测消歧与传播的计数策略（候选对如何确定性生成、已确认合并的传播如何计数、批次如何划分）。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §24.3、§10.5、§13.2；`DEC-MVP-B-SHADOW-MIGRATION-001` |
| SPEC | `SPEC-B6-SHADOW-MIGRATION-001` §2..§7；B4 对账语义（`SPEC-B4-RECONCILIATION-001`） |
| Acceptance Test | `B6-001..010` |
| Traceability | 矩阵 §4.15 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；SQLite PRAGMA 沿用 ADR-0001。
- 原始库在影子迁移中完全只读；失败无部分写入（`B6-INV-001/006`）。
- 计数断言为确定性计数（条数/批次数），不做 wall-clock SLO（`B6-INV-005`）。
- 不决定：真实历史迁移、真实 schema 演进合同、连接器、真实数据。

## 4. 候选方案

### Option A：文件级影子副本 + 确定性变换函数 + 复用 B4 深度对账；消歧/传播为纯函数计数模块

- 做法：`shadow_migration.py` 将原始库 SQLite 文件复制为影子副本，在影子上应用确定性 v1->v2 变换（合成字段重命名 + 变换日志计数），随后用 B4 的逐分区重建比较对影子做对账；故障注入在指定批次抛错并标记影子 discarded。`disambiguation.py` 以纯函数从实体 name_key 分组生成候选对（C(n,2) 计数）、对显式 merge 指令做引用传播计数、按固定 batch_size 确定性分批。
- 优点：原始库物理只读（文件复制，不打开原始库写事务）结构性满足 `B6-INV-001/006`；对账复用已 verified 的 B4 能力；计数全部为数据规模的确定性函数，oracle 直接断言。
- 代价与风险：文件级复制依赖 SQLite DELETE journal 模式下无活跃写事务（测试 profile 静态，成立）；变换是模拟而非真实 schema 演进。
- 可逆性：纯新增模块，可整体回退。

### Option B：SQL 层 INSERT INTO ... SELECT 在同库内建影子表

- 优点：无文件操作。
- 代价与风险：影子与原始同库，违反"影子可丢弃、原始零改动"的物理隔离倾向；原始库出现写事务，`B6-INV-001` 的证明变弱。

### Option C：逐对象导出/导入 JSON 重建影子

- 优点：格式无关。
- 代价与风险：绕开存储层直接验证对象，引入第二套序列化路径；文件级复制已可满足且更接近真实迁移形态。

## 5. 决定

采纳 Option A，两项裁决如下。

**5.1 影子迁移**：`src/noetide_micro/shadow_migration.py` 提供 `run_shadow_migration(source_path, shadow_path, transform, clock, fault_injection=None)`：复制 SQLite 文件到 shadow_path → 在影子副本上按批次应用确定性变换 `v1_to_v2`（合成字段重命名 `contact_frequency -> contact_frequency_v2` 与同义字段映射，逐条记录 transform_log 计数）→ 复用 B4 深度对账对影子做三分区 match/mismatch → 返回 `{state, transform_log, deep_result}`。fault_injection 指定批次时迁移显式 failed、影子标记 discarded、原始库未被打开写。验证侧 `verify_shadow(shadow_store, expected)` 比较影子与对 fixture 直接应用同一公开变换函数得到的期望快照。

**5.2 消歧/传播计数**：`src/noetide_micro/disambiguation.py` 提供三个纯函数入口——`scan_candidates(entities)`（按 name_key 分组，组内 C(n,2) 生成 `DisambiguationCandidate`，全部 `proposed`，`auto_merges=0`）、`propagate_merge(store, merge_instruction)`（对显式 merge 指令重定向引用并返回确定性传播计数，历史记录 append-only 保留）、`process_batches(items, batch_size)`（确定性分批，返回 `{batches, processed}` 计数）。所有函数不引入随机性与 wall-clock 依赖。

## 6. 后果

### 正向后果

- `B6-INV-001/006` 由文件级物理隔离结构性保证，oracle 可用原始库 digest 前后一致性直接断言。
- 消歧/传播计数为数据规模的解析函数，确定性可复现（`B6-INV-005`）。
- 对账验证复用 B4 verified 能力，不引入第二套比较逻辑。

### 负向后果与债务

- 文件级复制只适用于静态 profile；真实在线库的影子迁移需要备份/快照合同（后续切片）。
- 变换是模拟 v1->v2；真实 schema 演进合同与迁移版本登记仍是开放债务。

## 7. 验证与回退

- 验证方式：`B6-001..010` 可执行场景；`tools/validate_b6_suite.py` preflight；原始库 digest 前后一致性断言。
- 失败信号：原始库 digest 变化、候选自动合并、传播计数不可复现、失败影子转正。
- 回退步骤：删除两个新模块与 B6 suite 工件、回退本 ADR；不影响已 verified suite。
- 数据兼容：本 ADR 不引入 schema 变更。

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | 创建 `B6_SHADOW_MIGRATION_ARCHITECTURE.md` |
| Suite Materialization | 物化 `b6_shadow_migration_v1` fixture/oracle/runner/validator/manifest；preflight 后业务测试保持 `not_executed` |
| Implementation Plan | 创建 B6 Implementation Plan 与 Task Cards |
| Traceability | 矩阵 §4.15 `adr_accepted` 更新为 `true` |

## 9. 未决项

- 真实在线库快照/备份迁移合同与迁移版本登记：后续切片 Decision。
- 真实 schema 演进与索引迁移：C5/C6 前的独立 ADR。
- 以上均不影响本决定成立。
