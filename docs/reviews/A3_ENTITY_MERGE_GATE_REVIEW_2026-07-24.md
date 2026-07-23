# A3 实体合并候选与拆分回滚 Gate Review

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-A-ENTITY-MERGE-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-24 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前实现提交 | `e066883` |

## 结论

`P0=0`、`P1=0`，允许创建 A3 工程恢复点。

## 审计证据

- A3 official runner：`A3-001..008` 全部 `passed`，exit code `0`；当前 immutable result 为 `docs/testing/results/a3-20260724.json`（manifest 绑定 SHA 与文件实测一致，validator exit 0）。
- A3 manifest 已绑定 runner 所见 manifest SHA、result SHA、全部 artifact 和八个 required result；fixture/oracle 自物化以来仅经一次施工前 Change Control（A3-006/008 改 `pre_published` 播种，oracle 语义不变），此后未修改。
- 全量 configured-adapter semantic regression：169 passed、0 skipped，exit code `0`；A3 contract 的权威执行证据以官方 runner 为准。
- Micro、A1、B1、B2、B3、C1、A2、A3、Synthetic Ingestion、Context Pack 共 10 个 suite validator 均 exit code `0`；`git diff --check` exit code `0`。
- 七个 `A3-INV-001..007` 均有正/反证明：ChangeSet 边界与 candidate 非 Canonical（001/002）、历史保留（003/006）、split 逐字段恢复等价（005）、trust/closeness/人格判断不变（007）、视图 stale 不伪装 fresh（003）、fail closed 全集（002/008）、原子回滚（004）。

## 范围与风险

- A3 仅覆盖固定 `a3_entity_merge_v1` 合成 profile；不支持真实输入、自动合并、模糊身份匹配、合并候选评分、非 Person 合并、批量合并、权限 runtime、UI、网络或真实数据。
- 引用重定向集合闭合为 `relationship_party/state_subject/assertion_subject` 三类；trust/closeness 状态与 hypothesis 人格判断被显式排除在重定向之外。
- `merge_records` 严格只增不改；split 记录独立 `split_records` 表 append-only；split 恢复等价以 `pre_merge_references` 逐字段断言为准。
- 当前通过不表示完整 FR-011 的自动候选生成、通用实体消歧或 D2/D3 交付完成。
