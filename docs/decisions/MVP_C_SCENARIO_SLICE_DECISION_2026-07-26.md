# MVP-C Scenario & Action 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-SCENARIO-001` |
| Date | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-C-REVIEW-001`（已 verified，recovery tag `c3-review-calibration-rp-20260726`） |
| Current Slice | `SLICE-MVP-C-SCENARIO-001` |

## 1. 决定内容

选择 MVP-C 的 C4 Scenario & Action 作为下一条窄切片（FR-204 基准/乐观/悲观情景推演、FR-206 可执行性约束和行动跟进；路线图 `C4-SCENARIO-ACTION`），在一个固定合成 profile 上验证四类能力：

1. 情景三元组：用户确认创建 baseline/optimistic/pessimistic 情景，持久化为 Canonical assertion 对象且 `assertion_kind=predicted` 恒定；每个情景携带显式假设、预测结果与可执行性约束（hard_blockers / soft_constraints）。
2. 可执行性评估：`feasibility_status` 为声明约束的确定性纯函数（存在 hard blocker -> `infeasible`；否则存在 soft constraint -> `constrained`；否则 `feasible`），同输入恒同结果，不生成任何建议文案。
3. 情景选择：用户确认选择一个情景；选择只产生选择收据，不修改 Decision/Outcome 与情景历史。
4. 行动跟进：从已选情景经用户确认创建跟进动作（object_type=commitment 的 follow_up 记录，status=open）；用户确认完成；过期未完成在 Derived 视图中确定性标记 `missed`（固定 synthetic clock），不产生任何 Canonical 自动写入。

## 2. 产品依据

- PRD §20.3 FR-204（901 行）：基准、乐观、悲观情景推演。
- PRD §20.3 FR-206（903 行）：可执行性约束和行动跟进。
- PRD §8.1（315 行）：`predicted` 覆盖预测、计划、情景推演，与 observed 等事实型严格分离。
- 路线图约束（134 行）：情景不是预测事实；不替代专业意见。
- C1 先例：情景以 `assertion_kind=predicted` 持久化、不写入 observed（runtime.py `ensure_scenario`）；C4 不重建 C1 已验证的单情景创建/比较子集，扩展完整生命周期与行动跟进。

## 3. 切片范围

- 单一固定合成 profile `c4_scenario_action_v1`：固定合成 Decision（已存在）、情景三元组定义（假设、预测结果、约束清单）、跟进动作清单（带 due date），全部显式合成。
- Scenario（Canonical assertion，`assertion_kind=predicted`）：`scenario_kind`、`assumptions`、`projected_result`、`feasibility_constraints`、`feasibility_status`、`object_revision`。
- SelectionReceipt（ledger 收据）：用户确认选择，只追加。
- FollowUp（Canonical commitment 对象，payload 内嵌 revision_history）：`status=open|done`、`due_date`、scenario_ref、decision_ref。
- FollowUpView（Derived）：固定 clock 下 `open|done|missed` 的确定性呈现；`missed` 只在视图层计算。
- ScenarioView（Derived 呈现）：`is_fact=false`、`not_professional_advice=true`、无建议文案。

## 4. 非目标

- C1 已验证的单情景创建与比较闭环重建。
- 情景自动生成、概率/置信度评分、蒙特卡洛或任何推演算法。
- 专业建议文案生成（医疗/法律/财务建议）、LLM 参与。
- 跟进的自动创建、自动完成、自动延期；真实提醒/通知系统。
- C5 Context Pack、真实数据、多设备、连接器。

## 5. 不变量

- `C4-INV-001`：情景 `assertion_kind` 恒为 `predicted`（或 `fictional`），永不变为 observed/事实；不进入事实证据集；任何升级尝试 fail closed 且无写入。
- `C4-INV-002`：所有写入（创建情景、选择、创建跟进、完成跟进）必须用户确认；未确认一律 rejected 零写入；自动状态迁移计数恒为 0。
- `C4-INV-003`：`feasibility_status` 为声明约束的确定性纯函数；同约束输入恒同结果；不含任何评分或推断算法。
- `C4-INV-004`：不生成专业建议；ScenarioView 恒 `not_professional_advice=true` 且无建议文案字段。
- `C4-INV-005`：选择与跟进不修改 Decision/Outcome/情景历史；跟进状态变化产生新 revision 且历史保留不覆盖。
- `C4-INV-006`：`missed` 为 Derived 视图确定性计算（固定 clock + due date + status），无 Canonical 自动写入。
- `C4-INV-007`：profile 外输入 fail closed 且无写入；无关 Canonical 层 digest 在 C4 操作前后不变。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6 的 C4 applicability review、切片合同、追踪和测试合同设计。完成这些开发前产物前不得编写 C4 业务代码。
