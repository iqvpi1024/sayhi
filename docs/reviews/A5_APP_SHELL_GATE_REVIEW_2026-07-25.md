# A5 自然语言审查与最小可用应用壳 Gate Review

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-A-APP-SHELL-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前实现提交 | `0884526` |

## 结论

`P0=0`、`P1=0`，允许创建 A5 工程恢复点。

## 审计证据

- A5 official runner：`A5-001..008` 同一次 run 全部 `passed`，exit code `0`；当前 immutable result 为 `docs/testing/results/a5-20260725.json`（manifest 绑定 result SHA 与文件实测一致，`tools/validate_a5_suite.py` exit 0，输出 `materialized and current business runner result is bound`）。
- A5 manifest 已绑定 runner 所见 manifest SHA、result SHA、全部 artifact 和八个 required result；fixture/oracle 自物化以来未做任何修改（`git log` 可证），`app_shell.py`、`cli.py`、`a5_testing_adapter.py` 均为新增或任务卡允许的文件，未反向改动合同。
- 全量 configured-adapter semantic regression：211 passed、0 skipped，exit code `0`（含 A5 contract 8 项，无 skip）；A5 contract 的权威执行证据以官方 runner 为准。
- Micro、A1、B1、B2、B3、C1、A2、A3、A4、A5、Synthetic Ingestion、Context Pack 共 12 个 suite validator 均 exit code `0`；`git diff --check` exit code `0`。
- 七个 `A5-INV-001..007` 均有正/反证明：壳写操作全部经 ChangeSet 且 `record` 只 append Source + receipt、canonical/revisions 不变（A5-001 forbidden_mutations + `shell_write_scan` 静态扫描 `forbidden=[]` + A5-008 `zero_bypass=true`）；自然语言呈现为请求时 Derived、不持久化、不作证据（A5-002 呈现与 oracle 一致且呈现前后 canonical digest 不变）；影响预览与实际发布对象集/视图集一致（A5-008 `preview_matches_publish=true`，发布实际创建 `state_contact_002`、修改 `state_contact_001`、两视图前进 rev_011）；撤销后全部 Core View 恢复一致且历史保留（A5-007 rev_012 两视图 fresh、`contact_state=active`、history_count=1，历史同时保留 publish 与 revert 条目）；trust/closeness/人格判断不因壳操作被自动修改（A5-004..008 forbidden_mutations 覆盖两保护层 + A5-008 `trust_closeness_unchanged/personality_unchanged=true`）；普通路径不暴露 ChangeSet JSON 内部结构（A5-002 呈现形状仅 `candidate_ref/summary_text/evidence_citations/presentation_revision`，无 proposals 等内部字段，专家命令可显式查询）；壳默认离线（official runner 运行期间 socket 被封禁仍通过，adapter 使用内存库无任何网络调用）。

## 范围与风险

- A5 仅覆盖固定 `a5_app_shell_v1` 合成 profile，复用 Micro 演示旅程（rev_010 → rev_011 → rev_012）；不实现真实输入渠道、通用 NLP、Web/桌面 UI、云账户、多租户、连接器、多设备或真实个人数据。
- 呈现文本为请求时 Derived，不持久化、不作 Evidence Ref、Assertion input 或 ChangeSet trigger；预览/发布一致性以对象集与视图集比较为准，不以文本比较为准。
- 壳为 owner 本地单用户路径；A4 查询层权限语义不在本切片重判，壳不实现权限旁路；多用户、家庭授权、数字遗产、sealed 紧急恢复（DQ-003/004/009 deferred）、外部 Agent/MCP runtime、策略编辑器 UI 均不支持。
- 当前通过不表示完整 PRD 产品或 D2/D3 一键部署完成；D2/D3（签名、升级/卸载、真实数据安全合同）仍是最终目标，当前交付级别保持 D1 合成预览。
