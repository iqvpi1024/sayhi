# C2 Hypothesis Lifecycle 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-C2-HYPOTHESIS-001` |
| 版本 | `0.1` |
| 状态 | `Approved for C2 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-C-HYPOTHESIS-001` |
| 上游 | S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5 |
| 适用范围 | `SLICE-MVP-C-HYPOTHESIS-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：在一个固定合成 profile 上证明 Hypothesis 生命周期的完整管理能力——用户确认创建（active，带 valid_scope 与初始支持证据）、用户确认的支持证据/反例追加、用户确认的状态迁移（`active -> challenged -> weakened`，含纠正性回退与 retired/restore）、反例只进 evidence_against 不自动改状态、状态迁移产生新 revision 且历史永不删除、challenged/weakened 呈现 tentative、Hypothesis 永不升级为 Fact/Assertion 且不进入事实证据集。

非目标：识灵自动生成 Hypothesis、自动状态迁移、自动反例检测、置信度评分或阈值算法、人格推断能力本身、外部验证规则引擎、C3 复盘、C4 情景、C5 Context Pack、真实数据、多设备、连接器。

## 2. 对象与字段

### 2.1 Hypothesis（Canonical 对象，object_type=hypothesis，与 Assertion/Fact 隔离）

```yaml
hypothesis_id: stable ID
statement: 可反驳的模式/因果/人格/未来解释（固定合成文案）
hypothesis_kind: pattern | causal | personality | future   # 本切片仅合成实例
valid_scope: 显式有效范围（固定合成条件文案）
status: active | challenged | weakened | retired
evidence_for: list[EvidenceRef]      # stance=supports
evidence_against: list[EvidenceRef]  # stance=contradicts
object_revision: 单调递增；每次确认的迁移/证据追加产生新 revision
```

### 2.2 EvidenceRef（复用 S2 语义与 canonical_evidence_refs 存储）

```yaml
source_id: 必须指向真实存在的 Source 记录
locator: Source 内稳定定位
stance: supports | contradicts | contextual
claim_ref: 指向该 Hypothesis
```

### 2.3 HypothesisView（Derived 呈现，不是证据）

```yaml
hypothesis_id: ref
status: 当前状态
display_tone: exploratory | tentative | archived   # 由 status 纯函数决定
is_fact: false        # 恒 false；Hypothesis 永远不是事实
derived_only: true
```

display_tone 映射：`active -> exploratory`，`challenged -> tentative`，`weakened -> tentative`，`retired -> archived`。HypothesisView 不进入事实型回答的证据集，不产生确定性文案。

## 3. 状态机

```text
active -> challenged -> weakened
active -> weakened                 # 允许跨级（用户确认）
active|challenged|weakened -> retired   # 用户确认退休
weakened|challenged -> active      # 用户确认纠正性回退
retired -> active                  # 用户确认 restore（可纠正；retired 不是删除）
```

- 所有状态迁移与证据追加都必须经用户确认的 ChangeSet；未确认操作一律拒绝且无写入。
- 反例追加只扩充 evidence_against，不自动触发状态迁移；自动状态迁移计数恒为 0。
- retired 为语义终态（不再参与呈现与后续自动流程），但用户可通过确认的 restore 迁回 active；任何迁移都不删除历史 revision。

## 4. 时间、证据与权限

- 全部使用固定 synthetic clock；迁移与证据追加使用各自确认时间，不回填 recorded_at。
- Evidence Ref 必须指向真实存在的 Source 记录；指向不存在 Source、Derived View 或 profile 外数据的引用 fail closed 且无写入。
- 固定 synthetic profile 外输入 fail closed 且无写入。
- 本切片不建设权限 runtime；仅复用既有单用户本地调用者语义。

## 5. 系统不变量

- `C2-INV-001`：Hypothesis 永不升级为 Fact/Assertion；任何 upgrade_to_fact 尝试 fail closed 且无写入。
- `C2-INV-002`：所有状态迁移与证据追加必须经用户确认的 ChangeSet；自动迁移计数恒为 0。
- `C2-INV-003`：状态迁移产生新 revision；历史 revision、证据与审计永不删除；retired 可经用户确认 restore。
- `C2-INV-004`：challenged/weakened 呈现 tentative；任何状态下 Hypothesis 不以确定性文案或事实身份展示，不进入事实证据集（is_fact 恒 false）。
- `C2-INV-005`：证据只能引用真实存在的 Source Evidence Ref；Derived View 不得成为证据；非法引用 fail closed。
- `C2-INV-006`：反例只进入 evidence_against，不自动改变 status。
- `C2-INV-007`：profile 外输入 fail closed 且无写入；无关 Canonical 层 digest 在 C2 操作前后不变。

## 6. 失败、撤销与审计

- 未确认操作（证据追加/状态迁移/restore）：显式 `rejected`，无写入，对象 digest 不变。
- 非法状态迁移目标（未知状态值）：显式 `rejected`，无写入。
- 非法证据引用（Source 不存在、Derived 引用、profile 外）：显式 `rejected`，无写入。
- upgrade_to_fact 尝试：显式 `rejected`，无写入。
- 审计：每次确认的迁移/追加产生新 revision 并进入修订账本；验收结果只在测试 oracle 与 verification result 中绑定。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `C2-001` | 固定合成 profile / 用户确认创建 Hypothesis（scope + 2 条支持证据） | `status=active`、`object_revision=1`、`evidence_for=2`、`evidence_against=0`、valid_scope 保留、对象类型 hypothesis 且不在 Assertion 层 |
| `C2-002` | 已有 active Hypothesis / 用户确认追加 1 条支持证据 | `evidence_for=3`、status 保持 active、revision 递增、历史保留 |
| `C2-003` | 同上 / 用户确认追加 1 条反例 | `evidence_against=1`、status 仍为 active、`auto_transitions=0`、无自动迁移 |
| `C2-004` | 同上 / 用户确认迁移 active->challenged（Case G 路径） | `status=challenged`、新 revision、旧 revision 可读、`display_tone=tentative` |
| `C2-005` | challenged / 追加 2 条反例并确认迁移 challenged->weakened | `status=weakened`、`evidence_against=3`、tone tentative、全部历史可读 |
| `C2-006` | weakened Hypothesis / 呈现与事实隔离检查 | `display_tone=tentative`、`is_fact=false`、事实证据集不含该 Hypothesis、Assertion 层 digest 不变 |
| `C2-007` | 任意状态 / 尝试 upgrade_to_fact | 显式 `rejected`、无写入、Hypothesis 保持原状态原 revision |
| `C2-008` | weakened / 用户确认回退 weakened->active，随后确认 retire，再确认 restore retired->active | 三次迁移各产生新 revision、终态 active、历史 revision 全链可读、无删除 |
| `C2-009` | 任意状态 / 未确认的证据追加与未确认的状态迁移 | 均显式 `rejected`、无写入、digest 不变、全旅程 `auto_transitions=0` |
| `C2-010` | 全旅程后 / 横切检查 + 非法证据引用 + profile 外输入 | revision 链完整、证据全部指向真实 Source、非法引用 rejected 无写入、profile 外输入 fail closed、无关层 digest 不变 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `C2-001..010` passed result 存在，且所有 `C2-INV-*` 有正/反证明时，C2 才能标记 `verified`。未执行时必须保持 `not_executed`。
