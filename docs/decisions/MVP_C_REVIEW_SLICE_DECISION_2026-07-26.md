# MVP-C Review & Calibration 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-REVIEW-001` |
| Date | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-C-HYPOTHESIS-001`（已 verified，recovery tag `c2-hypothesis-lifecycle-rp-20260726`） |
| Current Slice | `SLICE-MVP-C-REVIEW-001` |

## 1. 决定内容

选择 MVP-C 的 C3 Review & Calibration 作为下一条窄切片（FR-203 周/月/年度复盘、FR-205 跨阶段行为和结果比较；路线图 `C3-REVIEW-CALIBRATION`），在一个固定合成 profile 上验证两类 Derived 能力：

1. 周期性复盘报告：基于固定合成 Canonical 数据（Episode、Commitment、Decision/Outcome、Hypothesis），生成周/月/年度复盘报告，报告内容为确定性计数（记录天数、Episode 数、Commitment 完成/取消/按期闭环计数、决策复盘完成计数、Hypothesis 状态分布）。报告可删除、可重建、重建等价；底层 Canonical 变化后报告必须标记 stale；同一窗口的历史报告版本保留不覆盖。
2. 跨阶段比较：对两个固定合成阶段的同一组确定性指标输出 signed delta 计数比较；比较只描述计数差异，不做因果、人格或趋势推断，不修改任何 Canonical 对象（尤其不自动改变 Hypothesis 状态）。

## 2. 产品依据

- PRD §20.3 FR-203（900 行）：周/月/年度复盘。
- PRD §20.3 FR-205（902 行）：跨阶段行为和结果比较。
- PRD §16.2（680-687 行）：摘要层级与失效——每一级摘要必须能回到更低一级证据；底层变化后上层摘要必须失效。
- PRD §12（412 行）：L3 最终一致——长摘要、统计、趋势为 Derived，旧版本立即标记 stale。
- PRD §23.5（1056 行）：决策复盘完成率、Commitment 按期闭环率为价值指标。
- PRD §24.4（1107 行）：决策室、复盘、校准和阶段比较。
- 路线图约束：历史版本、阶段可比性（同一指标集才可比）。

## 3. 切片范围

- 单一固定合成 profile `c3_review_calibration_v1`：固定合成 Episode（带日期）、Commitment（带 status/due/completed）、Decision/Outcome（带复盘结论有无）、Hypothesis（带 C2 状态机状态），全部显式合成。
- ReviewReport（Derived）：`review_kind`（weekly/monthly/yearly）、固定窗口、确定性指标计数、`view_revision`、freshness（fresh/stale）、`derived_only=true`。
- PhaseComparison（Derived）：两个同指标集窗口的逐指标 signed delta、`derived_only=true`；指标集不一致或窗口不合法 fail closed。
- 窗口语义固定：起始含、结束排他（半开区间），全部使用固定 synthetic clock，无 wall-clock 依赖。
- 报告/比较只经显式生成调用产生；不存在自动生成路径。
- 确定性计数断言：所有指标与 delta 为固定 oracle 值。

## 4. 非目标

- 决策室 UI、复盘报告的自然语言生成、LLM 摘要。
- 因果推断、趋势预测、人格判断、自动 Hypothesis 状态变化。
- C1 已验证的单决策 Decision/Outcome/Calibration 闭环重建。
- C4 情景推演、C5 Context Pack、真实数据、多设备、连接器。
- 复盘完成率的长期统计存储与北极星指标看板。

## 5. 不变量

- 复盘报告与阶段比较为 Derived，永不成为 Canonical 证据；Canonical 不引用报告或比较。
- 计数与 delta 确定性可复现（同 fixture 同窗口同结果）。
- 底层 Canonical 变化后相关报告立即 stale；旧报告版本历史保留不覆盖。
- 跨阶段比较只输出计数 delta；Canonical 层（含 Hypothesis 状态、Decision、Commitment）在比较前后逐字节不变。
- 报告可删除可重建且重建等价；删除 Derived 不影响 Canonical digest。
- 阶段可比性：只允许同一指标集的窗口比较；不合法比较 fail closed 无写入。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S6 的 C3 applicability review、切片合同、追踪和测试合同设计。完成这些开发前产物前不得编写 C3 业务代码。
