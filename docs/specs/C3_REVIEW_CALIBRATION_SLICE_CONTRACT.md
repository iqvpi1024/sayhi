# C3 Review & Calibration 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-C3-REVIEW-001` |
| 版本 | `0.1` |
| 状态 | `Approved for C3 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-C-REVIEW-001` |
| 上游 | S1 v0.6、S2 v0.5、S6 v0.5 |
| 适用范围 | `SLICE-MVP-C-REVIEW-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：在一个固定合成 profile 上证明两类 Derived 能力——周期性复盘报告（周/月/年度窗口的确定性计数，fresh/stale 随底层 Canonical 变化、历史版本保留、可删除可重建且重建等价）与跨阶段比较（同一指标集两个窗口的逐指标 signed delta，不合法比较 fail closed 且无写入）；两者永不成为 Canonical 证据、永不修改任何 Canonical 对象（含 Hypothesis 状态）。

非目标：复盘报告的自然语言生成、LLM 摘要、因果推断、趋势预测、人格判断、自动 Hypothesis 状态变化、决策室 UI、北极星看板、C1 单决策闭环重建、C4 情景推演、C5 Context Pack、真实数据、多设备、连接器。

## 2. 对象与字段

### 2.1 ReviewReport（Derived 对象，不为 Canonical 证据）

```yaml
review_id: stable ID（由 review_kind + window_start + window_end + view_revision 决定）
review_kind: weekly | monthly | yearly
window_start: 固定合成日期（含）
window_end: 固定合成日期（排他）   # 半开区间 [start, end)
metrics:
  days_recorded: int            # 窗口内至少有一条 Episode 的不同日期数
  episodes: int                 # 窗口内 Episode 总数
  commitments_completed: int    # status=completed 且 completed_at 落在窗口
  commitments_cancelled: int    # status=cancelled 且 cancelled_at 落在窗口
  commitments_closed_on_time: int  # completed 且 completed_at <= due_at
  decisions_reviewed: int       # 窗口内带复盘结论的 Decision 数
  hypothesis_status_counts: {active: int, challenged: int, weakened: int, retired: int}  # 生成时点快照
view_revision: 同窗口单调递增（首次为 1，每次重建 +1）
freshness: fresh | stale
source_digest: 生成时点的 Canonical digest（stale 判定依据）
derived_only: true
```

### 2.2 PhaseComparison（Derived 对象，不为 Canonical 证据）

```yaml
comparison_id: stable ID
window_a / window_b: 两个 ReviewReport 窗口（同 review_kind、同长度、半开区间）
metric_set_id: 指标集标识；两窗口必须使用同一指标集，否则 fail closed
deltas: 逐指标 signed delta（window_b - window_a），不含 hypothesis_status_counts 以外推断
derived_only: true
```

比较只输出计数 delta：不输出因果解释、趋势判断、人格或行为评价，不产生任何 Canonical 写入。

### 2.3 窗口语义

- 半开区间 `[window_start, window_end)`；weekly=7 天、monthly=固定合成月、yearly=固定合成年。
- 全部使用固定 synthetic clock；报告只经显式生成调用产生，无自动生成路径。

## 3. 状态机

```text
（不存在） --显式生成--> fresh
fresh --底层 Canonical digest 变化--> stale   # 判定动作，不改写历史报告内容
fresh|stale --显式重建--> 新版本 fresh（view_revision +1，旧版本保留不覆盖）
fresh|stale --显式删除--> 不存在（可重建，重建后 metrics 与同 Canonical 时点等价）
```

- PhaseComparison 无 freshness 状态机：生成即固定快照；它是 Derived，可删除可重建。
- ReviewReport 与 PhaseComparison 均不进入事实证据集；Canonical 对象不引用报告或比较。

## 4. 时间、证据与权限

- 全部使用固定 synthetic clock；窗口日期全部来自 fixture，无 wall-clock 依赖。
- 报告/比较的指标只从 Canonical 层（Episode、Commitment、Decision、Hypothesis）确定性计算；不读取 Derived 层作为输入。
- 固定 synthetic profile 外输入 fail closed 且无写入。
- 本切片不建设权限 runtime；仅复用既有单用户本地调用者语义。

## 5. 系统不变量

- `C3-INV-001`：ReviewReport 与 PhaseComparison 为 Derived，永不成为 Canonical 证据；Canonical 不引用报告或比较；生成与比较前后 Canonical digest 不变。
- `C3-INV-002`：所有指标与 delta 确定性可复现（同 fixture、同窗口、同 Canonical 时点，同结果）。
- `C3-INV-003`：底层 Canonical 变化后相关窗口报告判为 stale；旧报告版本历史保留不覆盖，重建产生新 view_revision。
- `C3-INV-004`：报告可删除可重建；同窗口同 Canonical 时点重建的 metrics 与删除前等价；删除 Derived 不影响 Canonical digest。
- `C3-INV-005`：跨阶段比较只允许同一指标集、同 review_kind、同长度窗口；不合法比较 fail closed 且无写入。
- `C3-INV-006`：比较只输出计数 delta；不修改任何 Canonical 对象（含 Hypothesis 状态、Decision、Commitment）。
- `C3-INV-007`：profile 外输入 fail closed 且无写入；无关 Canonical 层 digest 在 C3 操作前后不变。

## 6. 失败、撤销与审计

- 指标集不一致的比较请求：显式 `rejected`，无写入。
- 窗口不合法（kind 不同、长度不同、空窗口、日期倒置）：显式 `rejected`，无写入。
- profile 外输入：显式 `rejected`，无写入。
- 删除为 Derived 层操作：删除后可重建；删除动作不产生 Canonical 变化。
- 审计：报告版本（view_revision 链）与比较快照保留在 Derived 层可读；验收结果只在测试 oracle 与 verification result 中绑定。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `C3-001` | 固定合成 profile（带日期 Episode、带状态 Commitment、带复盘 Decision、带状态 Hypothesis）/ 显式生成周复盘 | metrics 精确匹配 oracle、`freshness=fresh`、`view_revision=1`、`derived_only=true`、Canonical digest 不变 |
| `C3-002` | 同 profile / 显式生成月度与年度复盘 | 两窗口 metrics 各自精确匹配 oracle、半开窗口边界 Episode 归属正确（起始含、结束排他） |
| `C3-003` | 已有 fresh 周报 / 窗口内新增一条确认的 Episode（Canonical 变化） | 该周报判为 `stale`；报告内容本身不被改写 |
| `C3-004` | stale 周报 / 显式重建同窗口 | 新版本 `fresh`、`view_revision=2`、metrics 反映新 Canonical、v1 旧版本保留可读不覆盖 |
| `C3-005` | 某窗口报告 / 显式删除后在同一 Canonical 时点重建 | 重建 metrics 与删除前等价；删除与重建前后 Canonical digest 不变 |
| `C3-006` | 两个同 kind 同长度窗口（同指标集）/ 显式生成 PhaseComparison | 逐指标 signed delta 精确匹配 oracle（含负值）、`derived_only=true` |
| `C3-007` | 两窗口指标集不一致 / 请求比较 | 显式 `rejected`、无写入、无 comparison 记录 |
| `C3-008` | 窗口 kind 不同或长度不同或日期倒置 / 请求比较 | 显式 `rejected`、无写入 |
| `C3-009` | 全旅程后 / 证据边界检查 | 报告与比较不在事实证据集；Canonical 对象无对报告/比较的引用；Hypothesis 状态分布快照与生成时点一致 |
| `C3-010` | 全旅程后 / 横切检查 + profile 外输入 | 版本链完整、比较前后 Canonical 各层 digest 不变、profile 外输入 fail closed 且无写入、无关层 digest 不变 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `C3-001..010` passed result 存在，且所有 `C3-INV-*` 有正/反证明时，C3 才能标记 `verified`。未执行时必须保持 `not_executed`。
