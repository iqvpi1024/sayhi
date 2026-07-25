# ADR-0014：C2 Hypothesis 生命周期存储与状态迁移实现方式

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-26 |
| Slice | `SLICE-MVP-C-HYPOTHESIS-001` |
| Contract | `SPEC-C2-HYPOTHESIS-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

C2 切片需要两个同层技术裁决：Hypothesis 对象与其证据双清单的存储形态（是否新增表、revision 历史如何保留）；状态迁移与证据追加的执行形态（如何强制"必须用户确认的 ChangeSet"、如何保证自动迁移恒为 0、如何呈现 display_tone）。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §5.2、§8、§20.2 FR-201、§22.1、§23、§26 Case G；`DEC-MVP-C-HYPOTHESIS-001` |
| SPEC | `SPEC-C2-HYPOTHESIS-001` §2..§7；S1 v0.6、S2 v0.5、S3 v0.4、S6 v0.5 |
| Acceptance Test | `C2-001..010` |
| Traceability | 矩阵 §4.16 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；SQLite PRAGMA 沿用 ADR-0001。
- 所有规范写入必须经用户确认的 ChangeSet；自动状态迁移计数恒为 0（`C2-INV-002`）。
- 状态迁移产生新 revision；历史 revision、证据与审计永不删除（`C2-INV-003`）。
- Hypothesis 永不升级为 Fact/Assertion；Derived 不作证据（`C2-INV-001/005`）。
- 不决定：自动生成/自动迁移/评分算法、外部验证规则引擎、呈现层改版、真实数据。

## 4. 候选方案

### Option A：复用 canonical_objects(object_type=hypothesis) + canonical_evidence_refs，payload 内嵌 revision_history，迁移收据进修订账本

- 做法：Hypothesis 存为既有 `canonical_objects` 行（schema 已允许 `hypothesis` 类型，无需改表）；`evidence_for/evidence_against` 映射为 `canonical_evidence_refs` 的 `stance=supports/contradicts` 行；每次确认的迁移/追加把旧状态快照追加进 payload 的 `revision_history` 数组并递增 `object_revision`，同时写一条 `ledger_records`（record_type=`hypothesis_transition`）收据与 `canonical_revisions` 全局 revision。呈现 `display_tone` 为 status 的纯函数。
- 优点：零 schema 变更；复用已验证的对象/证据/revision 存储与 digest 能力；历史保留在 payload 内自包含可读（脱离软件可用 JSON 直接审计）；证据 FK 约束由既有表保证。
- 代价与风险：revision_history 内嵌使单对象 payload 增长；本切片规模固定合成（个位数迁移），无实际风险。
- 可逆性：纯新增模块，可整体回退。

### Option B：新增 hypothesis_records / hypothesis_history 专用表

- 优点：历史行级独立，查询直接。
- 代价与风险：引入 schema 迁移与新表的 digest/对账/导出适配面；与既有 canonical 对象模型重复建设同一语义；本切片规模下收益不抵成本。

### Option C：纯事件溯源（迁移事件进 ledger，当前态由事件折叠）

- 优点：审计性最强。
- 代价与风险：当前态需要折叠计算，引入重建正确性负担；与全仓"当前行 + revision 历史"的既有模式不一致。

## 5. 决定

采纳 Option A。

**5.1 存储**：`src/noetide_micro/hypotheses.py` 以 `SemanticStore.add_canonical_object` 创建 Hypothesis（payload：`object_type=hypothesis`、`object_revision=1`、`statement`、`hypothesis_kind`、`valid_scope`、`status=active`、`revision_history=[]`），证据经 `replace_evidence_refs` 全量替换（读取-追加-替换，事务内完成）。每次确认的变更：`object_revision += 1`、旧状态快照（status、object_revision、at、reason）追加进 `revision_history`、`add_revision` 记录全局 revision（`revision_kind=changeset`）、`put_ledger_record` 写 `hypothesis_transition` 收据（hypothesis_id、from_status、to_status、reason、confirmed_by、at）。

**5.2 执行形态**：模块公开 `create_hypothesis`、`attach_evidence`、`transition_status`、`present_hypothesis`、`attempt_upgrade_to_fact` 五个入口，全部要求显式 `confirmed` 参数（`True` 才执行，否则返回 `rejected` 且零写入）。模块内不存在任何自动迁移代码路径；`auto_transitions` 由 contract adapter 统计并恒为 0。`attach_evidence` 校验 source_id 必须存在于 Source Vault（`seeded_source`）、stance 合法、claim_ref 指向本 Hypothesis，否则 rejected 零写入。`attempt_upgrade_to_fact` 无条件 rejected 零写入。`present_hypothesis` 返回 `{hypothesis_id, status, display_tone, is_fact=False, derived_only=True}`，`display_tone` 映射 `active->exploratory、challenged->tentative、weakened->tentative、retired->archived`。

## 6. 后果

- 正面：零 schema 变更落地完整生命周期；证据复用既有 FK 约束天然满足"非法引用 fail closed"；payload 自包含历史满足独立可读；与 A/B 系列切片的 digest、对账、回放能力兼容。
- 代价：revision_history 内嵌使历史查询需解析 payload JSON；专用历史表查询更直接但当前不需要。
- 回退：删除 `hypotheses.py` 与对应 suite；canonical_objects 中合成 Hypothesis 行随 fixture 消失，无迁移负担。
