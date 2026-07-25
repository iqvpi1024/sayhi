# MVP-C Hypothesis Lifecycle 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-HYPOTHESIS-001` |
| Date | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-B-SHADOW-MIGRATION-001`（已 verified，recovery tag `b6-shadow-migration-rp-20260725`）；MVP-C 已 verified 切片：`mvp-c-c1-v0.1` |
| Current Slice | `SLICE-MVP-C-HYPOTHESIS-001` |

## 1. 决定内容

选择 MVP-C 的 C2 Hypothesis Lifecycle 作为下一条窄切片（FR-201；路线图 `C2-HYPOTHESIS-LIFECYCLE`），在一个固定合成 profile 上验证 Hypothesis 的完整生命周期管理能力：

1. Hypothesis 创建：用户确认后以 `active` 状态建立可反驳的模式/因果/人格/未来解释，携带显式有效范围（valid scope）与初始支持证据。
2. 支持证据与反例：用户确认后把 Evidence Ref 追加进 `evidence_for` 或 `evidence_against`；反例进入后用户确认状态迁移 `active -> challenged -> weakened`（PRD §26 Case G 黄金路径）。
3. 生命周期与纠正：用户确认的状态迁移（含纠正性回退，如 `weakened -> active`）与 `retired` 终态；全部迁移产生新 revision，历史永不删除。
4. 隔离与呈现：Hypothesis 永不自动升级为 Fact/Assertion；challenged/weakened 的 Hypothesis 呈现语气必须为 tentative，不得以确定性文案展示，不得进入事实型回答的证据集。

## 2. 产品依据

- PRD §20.2 FR-201（898 行）：Hypothesis 的支持证据、反例、范围和生命周期。
- PRD §5.2 第 7 条（231 行）：Hypothesis 不得自动升级为 Fact；必须经过用户确认或明确的外部验证规则。
- PRD §8（290 行）：Hypothesis 是对模式、因果、人格或未来的可反驳解释；规范数据，但与事实隔离。
- PRD §26 Case G（1251 行）：新反例进入 evidence_against；状态从 active 转为 challenged 或 weakened；不删除历史；不再用确定性文案展示。
- PRD §22.1 第 9 条（994 行）：成长回路要求 Hypothesis 被反例削弱。
- PRD §23（1147 行）：自我强化防御——认知隔离、反例、禁止自动升格。
- S1 SPEC §3：Hypothesis 与 Assertion 隔离；完整生命周期流程是 S1 的显式非目标，由本切片合同授权。

## 3. 切片范围

- 单一固定合成 profile `c2_hypothesis_v1`：固定合成 Source 集合、一个合成 Entity（`ENT-SYN-SELF` 类自我实体）与若干合成 Episode/Assertion 上下文；全部显式合成。
- Hypothesis 对象：`hypothesis_id`、`statement`、`hypothesis_kind`（`pattern`/`causal`/`personality`/`future` 合成实例）、`valid_scope`、`status`、`evidence_for`、`evidence_against`、revision 历史。
- 状态机：`active | challenged | weakened | retired`；所有状态迁移与证据追加都必须经用户确认的 ChangeSet；`retired` 为终态，但用户可通过确认的 `restore` 新建迁移回 `active`（可纠正性）。
- 反例流程：反例只是 Evidence Ref（stance=`contradicts`）；追加反例不自动改状态；状态迁移是独立且必须用户确认的操作；自动迁移计数恒为 0。
- 呈现合同：`display_tone` 由状态决定——`active -> exploratory`，`challenged -> tentative`，`weakened -> tentative`，`retired -> archived`；Hypothesis 永远不以 fact 身份出现在事实型回答或确定性文案中。
- 事实隔离断言：Hypothesis 不写入 Assertion/Fact 层；`upgrade_to_fact` 类操作 fail closed；答案层不引用 Hypothesis 作为事实证据。
- 确定性计数断言：证据条数、迁移次数、revision 数为固定 oracle 值。

## 4. 非目标

- 识灵自动生成 Hypothesis（LLM 生成、模式挖掘、因果推断）。
- 自动状态迁移、自动反例检测、置信度评分或阈值算法。
- 人格推断能力本身；本切片只用合成 personality-kind Hypothesis 验证生命周期，不做推断。
- Hypothesis 的外部验证规则引擎（PRD §5.2 提到的明确外部验证规则后置）。
- C3 复盘校准、C4 情景推演、C5 Context Pack、真实数据、多设备、连接器。

## 5. 不变量

- Hypothesis 永不自动升级为 Fact/Assertion；任何 `upgrade_to_fact` 尝试 fail closed。
- 所有 Hypothesis 状态迁移与证据追加必须经用户确认的 ChangeSet；自动迁移计数恒为 0。
- 状态迁移产生新 revision；历史 revision、证据与审计记录永不删除（retired 不是删除）。
- challenged/weakened 的 Hypothesis 呈现语气为 tentative；任何状态下 Hypothesis 不得以确定性文案或事实身份展示。
- evidence_for/evidence_against 只能引用真实存在的 Source Evidence Ref；Derived View 不得成为证据。
- 用户确认一次后的 Core View 保持一致或显式标记 stale；无关层 digest 在 C2 操作前后不变。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6 的 C2 applicability review、切片合同、追踪和测试合同设计。完成这些开发前产物前不得编写 C2 业务代码。
