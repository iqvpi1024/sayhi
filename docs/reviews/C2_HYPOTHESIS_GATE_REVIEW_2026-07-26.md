# C2 Hypothesis Lifecycle Gate Review

| 字段 | 值 |
|---|---|
| Gate ID | `C2-HYPOTHESIS-GATE-2026-07-26` |
| Slice | `SLICE-MVP-C-HYPOTHESIS-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |

## 结论

`P0=0`、`P1=0`，允许创建 C2 工程恢复点。MVP-C 第二个切片（C2 Hypothesis Lifecycle，FR-201）至此 verified。

## 审计证据

- C2 official runner：`C2-001..010` 同一次 run 全部 `passed`，exit code `0`；immutable result `docs/testing/results/c2-20260726.json`（`tools/validate_c2_suite.py` exit 0，输出 `materialized and current business runner result is bound`）。
- C2 manifest 已绑定 runner 所见 manifest SHA、result SHA 与全部 artifact；fixture/oracle/scenarios 自物化以来未做任何修改；`hypotheses.py`、`c2_testing_adapter.py` 为任务卡允许文件，未反向改动合同、fixture 或 oracle。
- 全量 configured-adapter semantic regression：347 passed、0 skipped，exit code `0`（含 C2 contract 10 项真实执行与 C2-TASK-001 定向 9 项）。
- 17 个 suite validator 全部 exit code `0`；`git diff --check` exit code `0`。
- 七个 `C2-INV-001..007` 均有正/反证明：
  - `C2-INV-001`（永不升级为 Fact/Assertion）：`C2-007` `upgrade_outcome=rejected`、`writes_during_upgrade=0`、status/revision 不变；`C2-001` `in_assertion_layer=false`；`C2-006` `in_fact_evidence_set=false`、`is_fact=false`。
  - `C2-INV-002`（全部写入必须用户确认）：`C2-009` 未确认 attach 与 transition 均 `rejected`、revision 不变、`auto_transitions=0`；模块内不存在自动迁移代码路径（ADR-0014 §5.2），`C2-003/010` `auto_transitions=0`。
  - `C2-INV-003`（迁移产生新 revision、历史永不删除、retired 可 restore）：`C2-008` 五次迁移 rev1..9、`history_statuses=[active,active,challenged,challenged,challenged,weakened,active,retired]`、`no_deletions=true`；`C2-010` `revision_chain_complete=true`。
  - `C2-INV-004`（tentative 呈现、确定性文案禁令）：`C2-004/005` `display_tone=tentative`；`C2-006` `certain_tone_used=false`、`is_fact=false`。
  - `C2-INV-005`（证据必须真实 Source、Derived 非证据）：`C2-010` `illegal_missing_source_outcome=rejected`、`illegal_derived_ref_outcome=rejected`、`all_evidence_sources_exist=true`；C2-TASK-001 定向测试同证零写入。
  - `C2-INV-006`（反例只进 evidence_against 不自动改状态）：`C2-003` `evidence_against=1`、`status=active`、`auto_transitions=0`。
  - `C2-INV-007`（profile 外 fail closed、无关层不变）：`C2-010` `out_of_profile_outcome=rejected`、`unrelated_canonical_unchanged=true`；全场景 forbidden_mutations（source/entity/assertion/derived 四层）前后 digest 一致。

## 范围与风险

- C2 仅覆盖固定合成 profile `c2_hypothesis_v1` 上的 10 个场景；不实现识灵自动生成 Hypothesis、自动状态迁移、自动反例检测、置信度评分、人格推断或外部验证规则引擎（均为合同非目标）。
- `display_tone` 是由 status 决定的纯函数；真实首页/仪表盘呈现层的接入属后续呈现切片范围。
- revision 历史内嵌于对象 payload（ADR-0014 Option A）；大规模历史下的专用历史表为开放债务，当前规模无实际需求。
- 当前通过不表示完整 PRD 产品或 D2/D3 一键部署完成；交付级别保持 D1 合成预览。

## 下一步唯一建议动作

创建并推送 C2 recovery tag `c2-hypothesis-lifecycle-rp-20260726`，然后按 `MASTER_DELIVERY_ROADMAP` 进入 `C3-REVIEW-CALIBRATION`（FR-203/205），从 C3 Decision 门禁开始。
