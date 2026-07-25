# C3 Review & Calibration 架构说明

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-C-REVIEW-001` |
| Contract | `SPEC-C3-REVIEW-001` v0.1 |
| ADR | `ADR-0015` |
| 日期 | 2026-07-26 |

## 1. 模块边界

```text
tests/fixtures/c3_review_calibration_v1/fixture.json   固定合成 profile（Episode/Commitment/Decision/Hypothesis 定义 + 窗口定义）
tests/fixtures/c3_review_calibration_v1/oracles.json   C3-001..010 精确期望（计数、delta、rejected、freshness）
src/noetide_micro/c3_testing_adapter.py                fixture 播种（Canonical 层）+ scenario 分发 + layer 快照
src/noetide_micro/reviews.py                           generate_review / present_review / rebuild_review /
                                                        delete_review / compare_phases 五个入口
src/noetide_micro/store.py                             + delete_ledger_record(record_id)（ADR-0015 唯一 store 扩展）
```

- `reviews.py` 不写 Canonical 层；唯一写入是 `ledger_records`（record_type=`review_report` / `phase_comparison`）。
- 指标计算只读 `canonical_object_summaries()`；不读任何 Derived 行作为输入。
- 比较入口的合法性校验（同 kind、同长度、同 metric_set_id、日期合法）在写入前完成，失败显式 `rejected` 零写入。

## 2. 数据流

```text
fixture --adapter seed--> Canonical 层（episode/commitment/decision/hypothesis 对象）
generate_review(kind, window) --读 Canonical--> 确定性 metrics --append--> ledger(review_report, view_revision=n)
present_review(window) --重算窗口输入 digest--> freshness(fresh|stale)（只读，不回写）
rebuild_review(window) --读 Canonical--> 新 metrics --append--> ledger(view_revision=n+1)（旧版本保留）
delete_review(review_id) --DELETE ledger 行--> 可重建（同 Canonical 时点 metrics 等价）
compare_phases(window_a, window_b, metric_set_id) --读 Canonical 两次--> signed deltas --append--> ledger(phase_comparison)
```

## 3. 不变量落点

| 不变量 | 落点 |
|---|---|
| C3-INV-001 Derived 非证据 | 只写 ledger；Canonical 无引用；生成/比较前后 canonical digest 断言 |
| C3-INV-002 确定性 | metrics 为 Canonical payload 纯函数；oracle 精确匹配 |
| C3-INV-003 stale + 历史保留 | 窗口输入 digest 判定；append-only 版本链 |
| C3-INV-004 删除重建等价 | `delete_ledger_record` + 同点重建 metrics 相等断言 |
| C3-INV-005 可比性 | compare 前置校验，非法 rejected 零写入 |
| C3-INV-006 只输出 delta | deltas 纯计数差；Canonical digest 不变断言 |
| C3-INV-007 fail closed | profile 外输入 rejected；无关层 digest 断言 |

## 4. 与其他切片关系

- 复用 C2 的 Hypothesis Canonical 对象（status 快照计数）；不调用 C2 迁移入口。
- 不依赖 B2 projection 机制；freshness 用窗口输入 digest（见 ADR-0015 §5.2）。
- 与 C1 Decision/Outcome 只共享 Canonical 对象类型语义；不重建 C1 闭环。
