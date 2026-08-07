# A6 MVP-A 硬化与本地 Alpha 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-A6-HARDENING-001` |
| 版本 | `0.1` |
| 状态 | `Approved for A6 slice`（`A6-CONTRACT-REVIEW-001`，2026-07-25） |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-A-HARDENING-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5、S7 v0.3 |
| 适用范围 | `SLICE-MVP-A-HARDENING-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：

1. 在同一个版本化 Reference Profile `a6_mvp_a_reference_v1` 上顺序执行 12 个端到端集成验收场景（`A6-001..012`），证明 FR-001..012 在同一系统状态下协同成立（PRD §24.2 出口项，解释按 `DEC-MVP-A-HARDENING-001` §2 裁决）。
2. 固定壳层错误恢复表面的预期行为并以可执行场景演示：干净机器启动、启动失败（数据库损坏）、数据目录不可写、发布失败回滚、视图 unavailable。
3. 固定本地 Alpha 可解释性验收：用户数据路径可发现、备份与导出可验证、卸载默认不删用户数据、合成/真实数据路径分离可验证。
4. 在 `a6_mvp_a_reference_v1` 上执行固定 SLO 检查并记录实际结果；结果仅对该 profile 有效，不外推。

非目标：

- MVP-B 任何功能（B4 对账、B5 多语言、B6 影子迁移均不在本切片）。
- D2 安装包、签名、升级/卸载程序；D3 GitHub 正式发布与仓库可见性变更。
- 真实个人数据、真实导入渠道、连接器、多设备。
- UI 框架变更、Grant 管理 UI、性能调优（除固定 SLO 检查外）。
- Alpha 发布的版本号、工件内容与发布动作：在 A6 Gate Review 通过后的发布门禁单独决定。
- 新候选生成语义、新权限策略语义、MCP、新恢复语义、任何新产品规则。

### 1.1 已知限制（显式记录，非扩张）

FR-003 的候选生成侧：Entity/Assertion 候选生成没有已批准的 executable 语义。既有证据边界：Micro 证明 RelationshipState 候选链路；B1 仅有 state 类候选；合成导入 suite 只证明 SI-001..004 的存储持久性。本切片不为 Entity/Assertion 候选生成补写任何新产品规则。`A6-002` 只证明"候选不成为事实"的不变量：对 profile 内已存在的候选（RelationshipState 候选与固定合成候选），未经 ChangeSet 确认不得进入 Canonical、不得出现在 Core View。FR-003 生成侧的可执行闭合记录为 MVP-A 已知限制，移交后续切片决策，不阻塞本切片。

## 2. 对象与字段

```yaml
reference_profile (a6_mvp_a_reference_v1):
  profile_id: a6_mvp_a_reference_v1
  data_revision: 版本化固定合成数据集（fixture 物化时固定版本号与校验清单）
  environment_descriptor: 由 A6 ADR 记录的硬件/OS/Python/runner 描述（S6 IQ-014）
  seed_order: 固定
  execution_mode: sequential, single system state

integration_scenario:
  scenario_id: A6-001..A6-021
  fr_refs: [FR-xxx] | cross_cutting | hardening
  depends_on: 前序场景留下的系统状态（顺序执行、共享状态）
  expected: per-scenario fixed oracle assertions

slo_observation:
  slo_id: canonical_query_p95 | changeset_publish_p95 | core_view_read_after_publish | l3_stale_visibility
  profile_id: a6_mvp_a_reference_v1
  measured_value: 实际测量值（由 runner 记录）
  timing_boundary: 本地核心接受请求 -> 满足合同的响应可供调用者读取；后台工作单独计量
  extrapolation: forbidden

shell_error_surface:
  surface_id: clean_start | startup_db_corrupt | data_dir_unwritable | publish_failure | view_unavailable
  expected_exit: 非零（clean_start 为 0）
  expected_message_class: 非泄露（普通用户路径不暴露内部细节）
  expected_write_behavior: 不部分写入；不在声明目录以外写入
```

固定 SLO 检查项限定为 MVP-A 已存在能力面对应的四项；PRD §21.2 的冷来源搜索 SLO 因 MVP-A 不含搜索能力面而不适用，撤销可用性已由 `A6-006` 的能力证明覆盖。

关键区别：A1-A5 的 suite 各自在独立 fixture 上证明单个 FR；本切片的 21 个场景在同一个 Reference Profile 上顺序执行、共享同一系统状态。三个 Core View 固定为 `person_card`、`relationship_timeline`、`current_state`。

## 3. 判定规则

1. `A6-001..012` 与 FR 的映射固定按 `DEC-MVP-A-HARDENING-001` §2 表格，不得增删改语义。
2. 21 个场景在 `a6_mvp_a_reference_v1` 上按 `A6-001 -> A6-021` 固定顺序执行，共享同一系统状态；任一场景失败即整个验收组失败。
3. 集成执行不削弱、不替代任何已 verified suite 的独立证据；A6 结果与既有 suite 结果相互独立记录。
4. 错误恢复表面固定预期见 §6；恢复路径不得新增绕过 ChangeSet 的写入。
5. SLO 检查只记录实际结果并绑定 profile；未过不得通过返回旧值规避（PRD §21.2：5 秒 Core View SLO 不是返回旧值的许可）；结果不得跨 profile 外推。
6. 本地 Alpha 可解释性以文档 + 可执行 smoke 闭合；卸载默认不删除用户数据目录，删除需独立确认操作并提示备份/导出副本。
7. 合成 profile 数据路径与默认真实数据路径必须不同且可验证分离；错误恢复演示不得写入用户真实目录。

## 4. 时间、证据与权限

- 固定 A6 clock 只出现在 fixture；SLO 计时边界按 PRD §21.2 与 S6：从本地核心接受请求到响应可供读取。
- 所有规范写入经 ChangeSet；呈现层 Derived 不持久化、不反向成为证据（复用 `A5-INV-002`）。
- 权限：`A6-011` 复用 A4 已验证的查询层强制执行；本切片不重判权限语义、不引入新策略。
- 双时态：`A6-008` 复用 S2 已验证语义，valid/recorded 严格分离，`recorded_at` 不可回填。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `A6-INV-001` | 集成执行不削弱或替代任何已 verified suite 的独立证据。 |
| `A6-INV-002` | SLO 结果仅对声明 profile 有效，不外推；SLO 未过不得返回旧值规避。 |
| `A6-INV-003` | 错误恢复演示不写入用户真实目录；合成与真实数据路径不混。 |
| `A6-INV-004` | 所有规范写入经 ChangeSet；恢复路径不新增绕过写入。 |
| `A6-INV-005` | 卸载默认不删用户数据；删除需独立确认并说明备份/导出副本。 |
| `A6-INV-006` | 12 个集成场景只重述已 Approved 的 SPEC 行为，不补写新产品规则。 |
| `A6-INV-007` | 全旅程后 trust、closeness、人格判断与历史不被自动修改。 |
| `A6-INV-008` | 视图不可用时必须 Canonical fallback 或显式 unavailable，不得返回旧值冒充 fresh。 |

## 6. 失败、撤销与审计（错误恢复表面固定预期）

| surface | 固定预期 |
|---|---|
| `clean_start`（`A6-013`） | 干净环境首次初始化成功；合成 profile 可载入；exit 0 |
| `startup_db_corrupt`（`A6-014`） | 检测到损坏；拒绝启动；非零退出；非泄露错误；不尝试静默修复或覆盖原文件 |
| `data_dir_unwritable`（`A6-015`） | 写操作失败；非零退出；明确错误；不在声明目录以外写入 |
| `publish_failure`（`A6-016`） | 注入发布失败则原子回滚（复用 S3 已验证语义）；Canonical revision 不变；壳报告失败 |
| `view_unavailable`（`A6-017`） | L2 失败则 Canonical fallback 或显式 unavailable（复用 S3/A1 已验证语义）；不返回旧值冒充 fresh |

撤销：复用 Micro/S3 已验证的补偿语义，本切片不新增撤销语义。审计：复用 ChangeSet receipt 与 Source append receipt，本切片不新增审计对象。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `A6-001`（FR-001/002） | 干净 `a6_mvp_a_reference_v1` 状态 / append 固定合成 Source | Source appended + 独立 receipt；Canonical revision 不变 |
| `A6-002`（FR-003，范围按 §1.1） | profile 内已存在候选 / 未经确认直接读 Canonical 与 Core View | 候选不出现在 Canonical 与任何 Core View；候选不成事实 |
| `A6-003`（FR-004） | 合成输入产生规范语义 / 执行写入 | 规范写入全部经 ChangeSet；Source append 独立、不直接写 Canonical |
| `A6-004`（FR-005） | 已生成候选 / 自然语言审查 + 影响预览后确认发布 | 预览声明的对象集与受影响视图集 == 实际发布改变的对象集与视图集 |
| `A6-005`（FR-006） | 发布完成 / 读取三个 Core View | `person_card`、`relationship_timeline`、`current_state` 更新到新 revision 或显式失效；不返回旧值冒充 fresh |
| `A6-006`（FR-007） | 发布与撤销均完成 / 查询回执与历史 | 回执可查；ChangeSet 历史含发布与撤销补偿条目；链路完整可审计 |
| `A6-007`（FR-008） | 固定查询集 / 逐项提问 | 六态回答严格分离（复用 A1 已验证语义），未知不少答、不跨舱室猜测 |
| `A6-008`（FR-009） | 双时态数据 / 历史查询 | valid/recorded 严格区分；`recorded_at` 不可回填；纠正与时间演化区分 |
| `A6-009`（FR-010） | 存在冲突证据 / 查询相关事实 | 冲突被检测并并列呈现；不自动裁决 |
| `A6-010`（FR-011） | 实体合并候选 / 确认合并后执行拆分 | 合并经候选确认执行；拆分回滚恢复合并前状态（复用 A3 已验证语义） |
| `A6-011`（FR-012） | 受限调用者 / 跨舱室或权限不足查询 | 查询层 fail closed（复用 A4 已验证语义）；少回答、不猜测 |
| `A6-012`（横切） | `A6-001..011` 全部完成 / 终态检查 | trust/closeness/人格判断与历史未被自动修改；stale base 拒绝成立；L2 失败 fallback 成立 |
| `A6-013` | 干净环境 / 首次初始化并载入合成 profile | 启动成功 exit 0；数据目录创建于声明路径 |
| `A6-014` | 数据库文件损坏 / 启动 | 检测到损坏；非零退出；非泄露错误；不静默修复或覆盖原文件 |
| `A6-015` | 数据目录不可写 / 执行写操作 | 非零退出；明确错误；不在声明目录以外写入 |
| `A6-016` | 发布中途注入失败 / confirm | 原子回滚；Canonical revision 不变；壳报告失败 |
| `A6-017` | L2 视图投影失败 / 读 Core View | Canonical fallback 或显式 unavailable；不返回旧值冒充 fresh |
| `A6-018` | 已初始化环境 / 查询数据路径与路径分离 | 数据路径可发现；合成 profile 路径与默认真实路径不同且分离可验证 |
| `A6-019` | 已有数据 / 执行备份与导出 | 备份产物存在且校验清单可验证；导出 Round Trip 成立（复用 CP 已验证语义） |
| `A6-020` | 已安装环境 / 卸载（默认与显式删除两路径） | 默认卸载不删用户数据目录；删除需独立确认并提示备份/导出副本 |
| `A6-021` | Reference Profile 全程 / 执行固定 SLO 检查 | 各 `slo_observation` 实际结果被记录并绑定 `a6_mvp_a_reference_v1`；记录不外推 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `A6-001..021` passed result 存在，且所有 `A6-INV-*` 有正/反证明时，A6 才能标记 `verified`。未执行时必须保持 `not_executed`。Alpha 发布的版本号、工件内容与发布动作不在本完成定义内，由 A6 Gate Review 后的发布门禁单独决定。

## 9. 未决问题

1. Reference Profile `a6_mvp_a_reference_v1` 的环境描述符具体值（硬件/OS/Python/runner）：由 A6 的 ADR 步骤记录（S6 IQ-014），本合同不预选。
2. 开发启动与 evaluator package ADR（`ONE_CLICK_DELIVERY_PLAN.md` §2 到期项）：并入 A6 的 ADR 步骤，本合同不预选命令名或工具。
3. FR-003 生成侧（Entity/Assertion 候选生成）的可执行闭合：移交后续切片决策（见 §1.1）。

## 10. Change Control 记录

- v0.1（2026-07-25）：初版。按 `DEC-MVP-A-HARDENING-001` §2 裁决固定 12 场景映射；按 `A6-SPEC-APPLICABILITY-001` 四项发现闭合：集成证明缺口（§2/§3 顺序共享状态 + `A6-INV-001`）、Reference Profile 具体化边界（§2 `environment_descriptor` + `A6-021` + §9.1）、错误恢复壳层表面（§6 + `A6-013..017`）、本地 Alpha 可解释性（`A6-018..020` + `A6-INV-005`）；FR-003 生成侧已知限制显式记录于 §1.1。
