# B2 Episode 与分层摘要 Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-B2-EPISODE-SUMMARY-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| Decision | `DEC-MVP-B-EPISODE-SUMMARY-001` |
| Contract | `SPEC-B2-EPISODE-SUMMARY-001` v0.1 |
| ADR | `ADR-0004` |
| Verification | `not_executed` |

## 1. 组件责任

| Component | 责任 | 禁止责任 |
|---|---|---|
| `EpisodeFixtureLoader` | 加载版本化合成 candidate、Clock 与 failure plan | 不读取工作区外内容，不生成 expected |
| `EpisodeService` | 校验 profile、direct Source/Entity/time refs，构造 B2 ChangeSet input | 不直接写 Canonical，不做 NLP/LLM |
| `ChangeSetService` | 在既有 L1 边界发布 Episode、revision 与 receipt | 不把 summary 写回 Canonical |
| `SemanticStore` | 保存 Episode Canonical 行、Source refs 和 Derived summary 行 | 不用 trigger 裁决语义 |
| `SummaryProjector` | 从允许 dependency 确定性生成 day/phase summary，标记 stale/rebuild result | 不生成 Evidence Ref、Fact 或 Assertion |
| `SummaryReader` | 返回 fresh summary、显式 stale 或 unavailable | 不把旧 payload 标 current |
| `B2SuiteRunner` | 执行 B2-001..008，保存 immutable result | 不从实现生成 oracle 或跨 run 拼接通过 |

## 2. 数据与信任边界

```text
fixed synthetic fixture + Clock
        |
        v
EpisodeService -> proposed Episode ChangeSet
        |
        v
ChangeSetService -> Canonical Episode + Revision + Receipt
        |
        +-> SummaryProjector -> Derived summary_projections
                                      |
                                      v
                                SummaryReader
```

- `episodes`、Source、Ledger 是规范层；`summary_projections` 是 Derived 层。
- `SummaryProjector` 的输入只能是 `Episode`、直接 Source locator 和允许 Canonical metadata；不得读取 summary/receipt 当作事实。
- Canonical revision 改变时，summary 先 stale，后 rebuild；rebuild 失败不得回滚已成功的 L1 Episode 发布。

## 3. 写入与读取路径

1. FixtureLoader 提供固定 `EpisodeCandidate`，EpisodeService 先验证 synthetic profile、direct refs 和时间。
2. 用户确认后，ChangeSetService 原子写 Episode、全局 revision、ChangeSet outcome 和 receipt summary。
3. SummaryProjector 读取该 revision 的 dependency set，生成 deterministic day/phase projection，并记录 `view_revision`/`freshness_status`。
4. SummaryReader 只在 `freshness_status=fresh` 且 revision 对齐时返回 current；否则返回 stale 标记或 unavailable，不返回伪装的最新文本。

## 4. 失败与恢复

| Failure | 安全结果 |
|---|---|
| invalid Source/Entity/time/profile | ChangeSet failed，无 Episode/revision |
| L1 Episode write failure | transaction rollback，无半完成 Canonical |
| summary generation failure | Canonical/Episode 可读；summary stale/unavailable，记录 Derived receipt |
| Derived evidence attempt | 拒绝 `derived_evidence_forbidden`，Canonical 不变 |
| delete Derived then rebuild | 只由 Canonical/Episode/Source 恢复等价 summary |

## 5. 排除范围

不包含真实 Source、通用文本解析/摘要、模型调用、Embedding、权限/MCP runtime、连接器、同步、UI、Commitment、Semantic Diff、Hypothesis 或专业建议。
