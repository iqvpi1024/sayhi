# B6 Shadow Migration 与压测消歧传播 Gate Review

| 字段 | 值 |
|---|---|
| Gate ID | `B6-SHADOW-MIGRATION-GATE-2026-07-25` |
| Slice | `SLICE-MVP-B-SHADOW-MIGRATION-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |

## 结论

`P0=0`、`P1=0`，允许创建 B6 工程恢复点。MVP-B 全部切片（B1-B6）至此 verified。

## 审计证据

- B6 official runner：`B6-001..010` 同一次 run 全部 `passed`，exit code `0`；immutable result `docs/testing/results/b6-20260725.json`（`tools/validate_b6_suite.py` exit 0，输出 `materialized and current business runner result is bound`）。
- B6 manifest 已绑定 runner 所见 manifest SHA、result SHA 与全部 artifact；fixture/oracle/scenarios 自物化（`4ea6d9c`）以来未做任何修改；`shadow_migration.py`、`disambiguation.py`、`b6_testing_adapter.py` 为任务卡允许文件，未反向改动合同、fixture 或 oracle。
- 全量 configured-adapter semantic regression：328 passed、0 skipped，exit code `0`（含 B6 contract 10 项真实执行）。
- 16 个 suite validator 全部 exit code `0`；product baseline 静态校验 PASSED；`git diff --check` exit code `0`。
- 七个 `B6-INV-001..007` 均有正/反证明：
  - `B6-INV-001`（原始库不变）：`B6-001/003/004/008/010` `original_unchanged=true`，adapter 以三层 digest（Canonical/Source/Ledger）前后对比直接证明；影子为文件级副本（ADR-0013 §5.1）。
  - `B6-INV-002`（不绕过 ChangeSet、影子非证据）：`B6-009` `shadow_derived_only=true`、`canonical_references_shadow=false`、`report_is_evidence=false`；迁移对原始库只读。
  - `B6-INV-003`（无自动合并）：`B6-005` `auto_merges=0`、`all_candidates_proposed=true`；`B6-010` `no_auto_merge=true`。
  - `B6-INV-004`（bitemporal 历史随迁移完整）：`B6-008` revisions/snapshots/translations carried、undo_history_intact=true；`B6-006` `history_preserved=true`。
  - `B6-INV-005`（计数确定可复现）：`B6-002` `transform_log_counts={fields_renamed: 2}`、`transform_correct=true`；`B6-005` 12 对；`B6-006` 传播 2；`B6-007` batches=3 processed=12。
  - `B6-INV-006`（失败零部分写入、影子可丢弃）：`B6-003` `migration_fault_injected`、fault_batch=2、`partial_write_to_original=false`、`shadow_state=discarded`（影子文件已删除）。
  - `B6-INV-007`（profile 外 fail closed）：`B6-010` `out_of_profile_attempt` 返回 `failed/out_of_profile_input`、`write_attempted=false`。

## 范围与风险

- B6 仅覆盖固定合成复杂 profile `b6_shadow_migration_v1` 上的 10 个场景；不实现真实历史迁移、真实连接器、真实数据、wall-clock 性能 SLO、并发迁移或真实 schema 演进合同。
- 文件级影子复制只适用于静态 profile；真实在线库的快照/备份迁移合同与迁移版本登记为开放债务（ADR-0013 §9），留待 C5/C6 前决策。
- 当前通过不表示完整 PRD 产品或 D2/D3 一键部署完成；交付级别保持 D1 合成预览。

## 下一步唯一建议动作

创建并推送 B6 recovery tag `b6-shadow-migration-rp-20260725`，然后按 `MASTER_DELIVERY_ROADMAP` 进入 MVP-C（C2-C6），从 C2 Decision 门禁开始。
