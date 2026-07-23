# A2 current_state Core View Gate Review

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-A-CURRENT-STATE-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-22 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前实现提交 | `5dd8bea` |

## 结论

`P0=0`、`P1=0`，允许创建 A2 工程恢复点。

## 审计证据

- A2 official runner：`A2-001..008` 全部 `passed`，exit code `0`；当前 immutable result 为 `docs/testing/results/a2-20260722.json`（manifest 绑定 SHA 与文件实测一致）。`a2-20260722-r2.json` 为同 commit、同 manifest 的可复现性重跑，同样 8/8 passed。
- A2 manifest 已绑定 runner 所见 manifest SHA、result SHA、全部 artifact 和八个 required result；fixture/oracle 自物化以来未被修改。
- 全量 configured-adapter semantic regression：151 passed、0 skipped，exit code `0`（2026-07-22 复审时重跑确认）；A2 contract 的权威执行证据以官方 runner 为准。
- Micro、A1、B1、B2、B3、C1、Synthetic Ingestion、Context Pack、A2 共 9 个 suite validator 均 exit code `0`；product baseline 与 spec baseline 静态校验 PASSED；`git diff --check` exit code `0`。
- 七个 `A2-INV-001..007` 均有正/反证明：Derived 不写回 Canonical（001/007）、Historical 不被 Current 覆盖（002）、stale 不伪装 fresh（003）、删除后等价重建（004）、Derived 不作证（005）、fail closed（006）。

## 范围与风险

- A2 仅覆盖固定 `a2_current_state_v1` 合成 profile 与固定 clock `2032-04-10T09:00:00Z`；不支持真实输入、LLM、网络、权限/MCP runtime、同步或 UI。
- `current_state` 是 Derived Core View：只收录 entity/relationship/state/assertion 四类当前有效对象；stale 判定严格依赖 `data_revision == view_revision == 当前全局 revision`；projection 删除后可从 Canonical 与 Source 等价重建。
- 当前通过不表示完整 FR-102、实时刷新调度、权限控制或 D2/D3 交付完成。
