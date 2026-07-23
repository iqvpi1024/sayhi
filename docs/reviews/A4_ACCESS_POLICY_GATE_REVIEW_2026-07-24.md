# A4 查询层权限与舱室强制执行 Gate Review

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-A-ACCESS-POLICY-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-24 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前实现提交 | `bfdbe84` |

## 结论

`P0=0`、`P1=0`，允许创建 A4 工程恢复点。

## 审计证据

- A4 official runner：`A4-001..008` 同一次 run 全部 `passed`，exit code `0`；当前 immutable result 为 `docs/testing/results/a4-20260724.json`（manifest 绑定 result SHA 与文件实测一致，`tools/validate_a4_suite.py` exit 0）。
- A4 manifest 已绑定 runner 所见 manifest SHA、result SHA、全部 artifact 和八个 required result；fixture/oracle 自物化以来未做任何修改（`git log` 可证），判决器与 adapter 均为新增文件，未反向改动合同。
- 全量 configured-adapter semantic regression：191 passed、0 skipped，exit code `0`（含 A4 contract 8 项，无 skip）；A4 contract 的权威执行证据以官方 runner 为准。
- Micro、A1、B1、B2、B3、C1、A2、A3、A4、Synthetic Ingestion、Context Pack 共 11 个 suite validator 均 exit code `0`；`git diff --check` exit code `0`。
- 七个 `A4-INV-001..007` 均有正/反证明：fail closed 全集 unknown_caller/unknown_purpose/unknown_compartment/policy_missing（A4-005）；多舱室最严格交集与无法求交 `policy_conflict`（A4-003）；拒绝响应只回显请求字段、不泄露内容或存在性（A4-008 `deny_shape_clean` 及全部 deny 场景形状）；判决零写入、revision/canonical/trust/人格判断不变（A4-007 replay 前后 digest 一致）；sealed 从 read/search/summarize 全部排除（A4-006）；Grant 过期与 caller/purpose/action/scope 不匹配即无效（A4-004）；Derived View 路径判决与直查一致、不成为权限证据（A4-008 `decision_consistent`）。

## 范围与风险

- A4 仅覆盖固定 `a4_access_policy_v1` 合成 profile 的单用户本地调用者；Grant 全部由 fixture 注入，不实现 Grant 生命周期管理。
- PolicyDecision 为请求时 Derived，不持久化、不作 Evidence Ref、Assertion input 或 ChangeSet trigger；判决器为纯函数，只读 S1 标注，不写任何表。
- 多策略求值封闭为：allow 字段交集、deny 字段并集、无法求交默认拒绝；时间求值只比较 `requested_at` 与 Grant 固定窗口，不读系统时钟。
- 不支持多用户、家庭授权、数字遗产、sealed 紧急恢复（DQ-003/004/009 deferred）、外部 Agent/MCP runtime、策略编辑器 UI、网络或真实数据。
- 当前通过不表示完整 S4 权限体系、真实查询接入或 D2/D3 交付完成；应用壳（A5）接入真实查询路径是后续切片。