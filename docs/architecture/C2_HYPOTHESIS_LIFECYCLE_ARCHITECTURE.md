# C2 Hypothesis Lifecycle Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-C2-HYPOTHESIS-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-C-HYPOTHESIS-001` |
| ADR | `ADR-0014` |

```text
fixed synthetic profile c2_hypothesis_v1 (Source Vault + Entity + Episode context)
  -> hypotheses.create_hypothesis (confirmed)        # canonical_objects(object_type=hypothesis), rev=1, active
  -> hypotheses.attach_evidence (confirmed)          # canonical_evidence_refs stance=supports|contradicts
       # 反例只进 evidence_against；不触发任何状态迁移；auto_transitions 恒 0
  -> hypotheses.transition_status (confirmed)        # object_revision+1, revision_history 追加旧态快照,
                                                     # canonical_revisions(changeset) + ledger hypothesis_transition 收据
  -> hypotheses.present_hypothesis                   # Derived view: display_tone 纯函数, is_fact=false
  -> hypotheses.attempt_upgrade_to_fact              # 无条件 rejected, 零写入
```

- 写入边界：模块全部入口要求显式 `confirmed=True`；未确认/非法引用/非法状态目标一律显式 `rejected` 且零写入。
- 证据边界：Evidence Ref 必须指向真实存在的 Source；Derived View（含 HypothesisView）不作证据。
- 隔离边界：Hypothesis 不写入 Assertion/Fact 层；事实证据集不含 Hypothesis；无关层 digest 在 C2 操作前后不变。
- 历史边界：状态迁移只追加（revision_history + ledger 收据），永不删除；retired 非删除，可经确认 restore。
