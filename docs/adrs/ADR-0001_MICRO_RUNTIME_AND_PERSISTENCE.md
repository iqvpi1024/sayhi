# ADR-0001：Micro 单进程运行时与事务持久化

## 0. 元数据

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0001` |
| Status | `Accepted` |
| Date | `2026-07-16` |
| Slice | `SLICE-MICRO-RELATIONSHIP-001` |
| Decision Owner | Noetide Technical Lead（用户授权的当前技术负责人） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

当前 Micro 切片使用什么最小本地运行时与持久化边界，才能在零外部服务、零新增依赖下证明 Source receipt、ChangeSet L1 原子发布、revision、幂等 receipt、两个 L2 Core View、失败降级和补偿撤销？

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | PRD v0.5 §6-§12、§21-§22、§24.1、§25.2、§26 Case A；`DEC-MICRO-GATE-001` |
| SPEC | S1 v0.6；S2 v0.5；S3-S5 v0.4；S6 v0.5；S7-S8 v0.3；S9 v0.4 |
| Acceptance Test | `MM-001..010` 与 `MICRO_MVP_ACCEPTANCE.md` §6 的 39 个 exact required upstream Test Ref |
| Traceability | FR-001..FR-007、FR-009、FR-105 的 `micro_required_slice` |
| Gate Review | `MICRO_PRE_ADR_SPEC_CONSISTENCY_REVIEW_2026-07-16.md`，P0=0、P1=0、结论 yes |

## 3. 约束与非目标

必须满足：

- 完全本地、离线、单用户；测试不得访问网络或工作区外个人数据。
- Source、Canonical、Revision Ledger、Derived Projection 在逻辑层分离。
- Source Append 不经 ChangeSet；Canonical 写入只经 ChangeSet。
- L1 proposal、`data_revision`、ChangeSet outcome 与 receipt summary 使用同一事务恢复边界。
- publish attempt 与 idempotency binding 必须在语义发布前可恢复。
- L2 失败时只能读 current Canonical fallback 或无旧 payload 的 updating/unavailable。
- 固定时钟、固定合成 fixture、确定性 candidate builder 和可注入失败。
- Derived 表不得被证据读取路径使用；protected semantics 必须逐对象 digest 比较。
- 无新增第三方依赖；运行时、Schema 与工件格式必须在仓库中可复现。

本 ADR 不决定：

- 长期最终数据库、通用图数据库、向量库、云服务、同步、备份或密钥管理。
- MCP runtime、连接器、真实迁移、权限 runtime、多 Agent 或 A2A。
- 通用 NLP/LLM、模糊时间、实体消歧或 Micro 以外对象工作流。
- S7 完整 Context Pack、容量目标和长期物理分层。

## 4. 候选方案

### Option A：Python 标准库 + SQLite 单进程事务存储

- 做法：使用 Python 3.12 标准库 `sqlite3/json/hashlib/unittest`；一个 SQLite 文件承载逻辑分层表，使用显式事务、外键、`journal_mode=DELETE` 与 `synchronous=FULL`。JSON 只用于版本化 suite/fixture/oracle/result 工件。
- 优点：当前机器已具备 Python 3.12.8 与 SQLite 3.45.3；无需安装；SQLite 事务可直接证明 L1 原子性和单调 revision；失败注入和临时数据库隔离简单。
- 代价与风险：SQLite 是当前切片实现依赖；单进程策略不证明多设备/多进程并发；Source 与其他逻辑层共享物理文件；未来更换存储需保持 SPEC 行为和导出合同。
- 可逆性：高。Micro 表和 repository boundary 很窄，且没有真实数据迁移；若验证失败，可在新 ADR 中替换。

### Option B：Node 24 + 内置 SQLite 接口

- 做法：使用现有 Node 24 和内置 SQLite API，测试使用 Node 标准测试模块。
- 优点：同样可零安装并使用事务；JSON 工件处理自然。
- 代价与风险：当前仓库没有既有 JavaScript/TypeScript 基线；需要额外验证内置 SQLite API 的稳定性和跨版本行为；对本切片没有相对 Python 的语义收益。
- 可逆性：高，但会改变运行时与测试工件加载器。

### Option C：文件原生 JSON + 自建 journal

- 做法：Source、Canonical、Ledger 和 View 使用独立 JSON/JSONL 文件，通过临时文件、rename、锁和恢复日志实现事务。
- 优点：普通文件工具直接可读，物理层与可移植愿景接近。
- 代价与风险：必须自行实现原子多对象写入、revision CAS、幂等、崩溃恢复和部分失败清理；会在 Micro 阶段重造事务系统，显著增加错误面。
- 可逆性：中；一旦 journal 格式成为隐式事实源，迁移成本上升。

### Option D：暂不决定

推迟会阻止 suite 的数据库事务故障注入、实施模块边界和原子发布 oracle 物化，因此不是当前可行门禁结果。

## 5. 决定

接受 Option A。

当前切片使用 Python 3.12 标准库与 SQLite 单进程事务存储。实现只使用 SQLite 的基础事务、约束和普通表，不依赖 JSON1、FTS、扩展模块、触发器生成业务语义或供应商专有能力。

SQLite 文件内按逻辑职责分表：

- Source/Append Receipt。
- Canonical objects 与 bitemporal State。
- ChangeSet/Proposal/Publish Attempt/Revision Ledger。
- `person_card` 与 `relationship_timeline` Projection 及其 freshness/revision。

所有业务时间来自注入的 `Clock`。Candidate builder 只接受固定合成 fixture 并产生一条 allowlisted contact proposal，不调用在线模型。View Projector 只消费已提交 Canonical revision；测试可在两个投影点分别注入失败。

当前参考环境是 Python 3.12.8 / SQLite 3.45.3 / Windows。实现不得把精确补丁版本写成产品承诺；真实验证结果必须记录实际版本。

## 6. 后果

### 正向后果

- L1 原子性、revision、CAS、幂等 attempt/receipt 和补偿可以用单个本地事务直接测试。
- 不需要安装依赖或运行外部服务，符合离线合成测试边界。
- JSON suite 工件与 SQLite 实际状态分离，expected oracle 不会被实现反向读取。
- 单进程同步边界使 Publish Barrier 与 L2 失败状态可观察。

### 负向后果与债务

- 只证明单进程本地语义，不证明多进程、多设备或同步行为。
- 当前物理存储未证明 S7 完整 portability/Context Pack；该能力仍 deferred。
- SQLite 事务不能自动证明业务不变量，仍需字段级 oracle 和故障注入。
- Python/SQLite 是本切片技术选择，不是长期不可替换平台承诺。

## 7. 验证与回退

- 验证方式：物化并校验 exact Micro manifest；实现后同一次 current run 执行 `MM-001..010` 与 39 个 required upstream refs；加入 transaction failure、stale base、单 View failure 和 compensation 场景。
- 失败信号：出现半发布 L1、重复 revision、丢失 attempt/receipt、旧 L2 冒充 current、protected digest 改变、非确定时间/网络访问或运行需要第三方包。
- 回退步骤：停止实现；保留失败 run；将 ADR 标为 Superseded；从当前 Git Recovery Point 建新分支并以新 ADR 替换 runtime/store；不得转换失败结果为 passed。
- 数据兼容：Micro 仅使用合成 fixture 和临时数据库。替换方案必须能从权威 fixture 重建，不迁移或导入真实数据。

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | 创建 `MICRO_RELATIONSHIP_ARCHITECTURE.md`，固定组件和失败边界 |
| Suite Materialization | 使用 JSON manifest/fixtures/oracles；增加标准库预检器，仍不执行业务场景 |
| Implementation Plan | 模块绑定 Source intake、semantic store、candidate builder、ChangeSet service、projector、read model 与 runner |
| Portability / Privacy | 临时数据根限定在测试目录；禁止网络和工作区外读取；S7 完整 Pack 不进入 Micro |

## 9. 未决项

- SQLite Schema 细节属于 Implementation Plan，不得新增业务语义。
- 长期存储、Context Pack、真实备份和同步在对应切片重开新 ADR。
- 若实现需要第三方包，必须先新 ADR；本 ADR 不授权安装依赖。
