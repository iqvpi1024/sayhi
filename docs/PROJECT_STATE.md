# 项目状态

## 1. 恢复入口

每次任务按 `AGENTS.md` 的顺序恢复。当前产品语义以 `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的 `PRDv06.md` v0.6 为准；历史 PRD、SPEC、结果和 tag 保留审计价值，不得覆盖动态状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 当前产品基线 | `PRDv06.md` v0.6 Approved，canonical LF SHA-256 `4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8` |
| 当前公开发布 | `v0.2.0-beta` GitHub prerelease 已发布（D3 完成） |
| 当前工作切片 | Y2-S4 已 verified；待 Y2-S5（MCP runtime）切片决策 |
| 当前阶段 | `recovery_point_published`（Y2-S4）；首年全部 `recovery_point_published` |
| 当前公开版本 | `v0.2.0-beta` GitHub prerelease |
| tag / commit | annotated tag `v0.2.0-beta` -> `08095cc4aca88adad6469ffe3bedc9f25bdabaf7` |
| GitHub Release | `https://github.com/iqvpi1024/sayhi/releases/tag/v0.2.0-beta` |
| 交付级别 | D1 合成预览（v0.1.3）与 D2/D3 Beta（v0.2.0 一键安装）均已发布；首年路线图切片全部 verified |
| 分支 | `main`，已推送至 `origin/main` |

## 3. 已完成内容

1. PRD v0.5、S1-S9 Approved 语义基线、Micro 关系链路、Answer Safety、Candidate Review、Decision/Outcome、合成导入和私有合成 Context Pack 均保留为当前实现范围内的合成能力。
2. A1 suite 完整性绑定已修复，官方 runner 在 `8556eea` 实际通过 35/35；C1 runner 场景映射已修复，官方 runner 在同一提交实际通过 7/7。
3. `v0.1.3-synthetic-preview` 已发布源码 ZIP、Windows portable ZIP 及各自 SHA-256 校验文件。portable 包自带 Python runtime，解压后可初始化合成 SQLite 并读取 `rev_010`。
4. GitHub Actions 对 `main` 和 tag 的两个 run 均通过，包含 Linux 合同/语义回归与 Windows portable smoke。
5. B2 Episode/summary 已完成合同、ADR、suite、实现、官方 runner、Gate Review 与 recovery point；它只证明 FR-103 的固定合成切片。
6. B2 official suite 的 `B2-001..008` 为 8/8 passed/current；recovery tag `b2-episode-summary-rp-20260719` 已推送。
14. `DEC-MVP-B-COMMITMENT-001` 已选择 B3 的固定合成 Commitment 生命周期切片；尚未开始 B3 代码或 suite 物化。
15. B3 applicability review 结论为 `pass_with_slice_contract_required`；基础 SPEC 不足以直接授权 Commitment 业务实现。
16. `SPEC-B3-COMMITMENT-001` 与合同复核已完成；尚未建立 B3 traceability、ADR、suite 或代码。
17. B3 FR-104 traceability 已建立；尚未物化 B3 suite 或实现。
18. `ADR-0005` 与 `ARCH-B3-COMMITMENT-001` 已接受；未创建 B3 fixture、oracle、runner 或代码。
19. B3 executable suite 已物化：`tests/fixtures/b3_commitment_v1/`、`tests/integration/b3_commitment_scenarios.json`、`tests/runner/b3_commitment_adapter_protocol.py`、`tests/semantic/test_b3_commitment_contract.py`、`tests/runner/run_b3_suite.py`、`tools/validate_b3_suite.py`、`tests/b3_suite_manifest.json`；无 adapter，业务测试保持 `not_executed`。
20. `PLAN-MVP-B-B3-IMPL-001` 与 B3 任务卡已建立（B3-TASK-001..006）。
21. B3-TASK-001 已完成：schema/store 增加 commitments、due_status_projections、due_rebuild_receipts 及窄 store 方法；定向 5/5 passed，configured-adapter regression 120 tests OK（8 B3 contract skipped）；B3 official suite 仍 `not_executed`。
22. B3-TASK-002 已完成：`commitments.py` 实现 propose/approve/publish/complete/cancel/revert 全经 ChangeSet；定向 8/8 passed，regression 128 OK；B3 official suite 仍 `not_executed`。
23. B3-TASK-003 已完成：`due_status.py` 实现固定 clock 确定性投影、delete/rebuild 等价、失败降级 unavailable 与 Derived 不作证；定向 4/4 passed，regression 132 OK；B3 official suite 仍 `not_executed`。
24. B3-TASK-004 已完成：`b3_testing_adapter.py` 完整实现 adapter protocol，contract 8/8 passed；fixture/oracle 未修改；official runner 属 B3-TASK-005。
25. B3-TASK-005 已完成：official runner `b3-20260722.json` 同一次 run 8/8 passed/current；configured-adapter regression 132 OK 无 skip；8 个 suite validator 全 PASSED；manifest 已绑定 current result。
26. B3-TASK-006 已完成：Gate Review `B3_COMMITMENT_GATE_REVIEW_2026-07-22.md` 结论 P0=0/P1=0；B3 切片 verified，recovery tag `b3-commitment-rp-20260722` 已推送。
27. `DEC-MVP-A-CURRENT-STATE-001` 已选择 A2 current_state Core View 切片；只授权 applicability review，未授权业务代码。
28. A2 applicability review `A2-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`。
29. `SPEC-A2-CURRENT-STATE-001` 与合同复核 `A2-CONTRACT-REVIEW-001`（approved_for_traceability）已完成。
30. A2 traceability（矩阵 §4.8）已建立。
31. `ADR-0006` 与 `ARCH-A2-CURRENT-STATE-001` 已接受。
32. A2 executable suite 已物化（fixture/oracle/scenarios/protocol/contract module/runner/validator/manifest）；preflight validator exit 0，contract 8 skipped（无 adapter），业务测试保持 `not_executed`。
33. `PLAN-MVP-A-A2-IMPL-001` 与 A2 任务卡已建立（A2-TASK-001..005）。
34. A2-TASK-001 已完成：a2_view_rebuild_receipts 表与 upsert/stale/delete 辅助；定向 5/5 passed，regression 145 OK（8 A2 contract skipped）；A2 official suite 仍 `not_executed`。
35. A2-TASK-002 已完成：`current_state.py` 实现当前有效纯函数、build/read/stale/rebuild/失败降级/不作证；定向 6/6 passed，regression 151 OK；A2 official suite 仍 `not_executed`。
36. A2-TASK-003 已完成：`a2_testing_adapter.py` 完整实现 adapter protocol，contract 8/8 passed；fixture/oracle 未修改；official runner 属 A2-TASK-004。
37. A2-TASK-004 已完成：official runner `a2-20260722.json` 同一次 run 8/8 passed/current；configured-adapter regression 151 OK 无 skip；9 个 suite validator 全 PASSED；manifest 已绑定 current result。
38. A2-TASK-005 已完成：Gate Review `A2_CURRENT_STATE_GATE_REVIEW_2026-07-22.md` 结论 P0=0/P1=0；A2 切片 verified，recovery tag `a2-current-state-rp-20260722` 已推送。
39. `DEC-MVP-A-ENTITY-MERGE-001` 已选择 A3 实体合并/拆分切片；只授权 applicability review，未授权业务代码。
40. A3 executable suite、Implementation Plan、TASK-001..005 与 Gate Review 均已完成；A3 切片 verified，recovery tag `a3-entity-merge-rp-20260724` 已推送。
41. `DEC-MVP-A-ACCESS-POLICY-001` 已选择 A4 查询层权限切片；applicability review `A4-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`。
42. `SPEC-A4-ACCESS-POLICY-001` 已批准；A4 traceability、`ADR-0008`、`ARCH-A4-ACCESS-POLICY-001`、suite 物化与 `PLAN-MVP-A-A4-IMPL-001`（A4-TASK-001..005）已完成。
43. A4-TASK-001 已完成：store 新增只读策略标注辅助（`object_policy_labels`/`policy_labeled_objects`）与 canonical digest 辅助（`canonical_object_digest`/`canonical_layer_digest`）；定向 6/6 passed，configured-adapter regression 175 OK、8 A4 contract skipped；A4 official suite 仍 `not_executed`。
44. A4-TASK-002 已完成：`access_policy.py` 纯函数判决器（Grant 有效性、最严格交集、sealed 排除、fail closed、零写入）；定向 8/8 passed，regression 183 OK、8 A4 contract skipped；A4 official suite 仍 `not_executed`。
45. A4-TASK-003 已完成：`a4_testing_adapter.py` 完整实现 adapter protocol，contract 8/8 passed；fixture/oracle/contract module 未修改；official runner 属 A4-TASK-004。
46. A4-TASK-004 已完成：official runner `a4-20260724.json` 同一次 run 8/8 passed/current；manifest 已绑定 current result；全量 regression 191 OK 无 skip；11 个 suite validator 全 PASSED。
47. A4-TASK-005 已完成：Gate Review `A4_ACCESS_POLICY_GATE_REVIEW_2026-07-24.md` 结论 P0=0/P1=0；A4 切片 verified；recovery tag `a4-access-policy-rp-20260724` 已创建并推送。
48. `DEC-MVP-A-APP-SHELL-001` 已选择 A5 应用壳切片；applicability review `pass_with_slice_contract_required`；`SPEC-A5-APP-SHELL-001` v0.2 已批准（含 Change Control：read_view 视图集合修订为 person_card+relationship_timeline）；traceability、`ADR-0009`、`ARCH-A5-APP-SHELL-001`、suite 物化与 `PLAN-MVP-A-A5-IMPL-001`（A5-TASK-001..005）已完成；preflight validator exit 0，业务测试 `not_executed`。
49. A5-TASK-001 已完成：`app_shell.py` 呈现层纯函数（NL review、impact preview、零绕过静态扫描辅助）；定向 6/6 passed，configured-adapter regression 205 OK（8 A5 contract skipped）；A5 official suite 仍 `not_executed`。
50. A5-TASK-002 已完成：`cli.py` 增加 guide/receipts/history 命令，`a5_testing_adapter.py` 完整实现 adapter protocol；定向 6/6 passed，contract 8/8 passed（adapter），全量 regression 211 OK 无 skip；fixture/oracle 未修改；official runner 属 A5-TASK-004。
51. A5-TASK-003 已完成：contract 集成验证 8/8 passed（commit a45a8bd），全量 regression 211 OK 无 skip 无退化；无实现变更；A5 official suite 仍 `not_executed`。
52. A5-TASK-004 已完成：official runner `a5-20260725.json` 同一次 run 8/8 passed/current；manifest 已绑定 current result；12 个 suite validator 全 PASSED；全量 regression 211 OK 无 skip。
53. A5-TASK-005 已完成：Gate Review `A5_APP_SHELL_GATE_REVIEW_2026-07-25.md` 结论 P0=0/P1=0；A5 切片 verified；矩阵 §4.11 已同步；recovery tag `a5-app-shell-rp-20260725` 已创建并推送。
54. `DEC-MVP-A-HARDENING-001` 已选择 A6 硬化与本地 Alpha 切片，并显式裁决"12 个可执行语义变更测试"= FR-001..012 各一个端到端场景在同一 Reference Profile 执行；只授权 S1/S2/S3/S6/S7 applicability review，未授权业务代码。
55. A6 applicability review `A6-SPEC-APPLICABILITY-001` 结论 `pass_with_slice_contract_required`（2026-07-25）：S1/S2/S6 pass，S3/S7 partial；4 个缺口（集成证明、Reference Profile 具体化、错误恢复壳层、Alpha 可解释性）由 A6 slice contract 闭合；尚未建立 A6 合同、traceability、ADR、suite 或代码。
56. `SPEC-A6-HARDENING-001` v0.1 已起草并 Approved（`A6-CONTRACT-REVIEW-001`，2026-07-25，结论 `approved_for_traceability`）：21 场景在同一 Reference Profile `a6_mvp_a_reference_v1` 顺序执行共享状态；FR-003 生成侧为显式已知限制（合同 §1.1）；错误恢复五表面与 Alpha 可解释性验收已固定；Traceability 矩阵 §4.12 已建立；尚未建立 A6 ADR、suite 或代码。
57. `ADR-0010` 已 Accepted（2026-07-25）：根目录 `start.py` 为 D0 唯一入口（runtime 检查、合成 devdata 根、init/migrate、preflight+smoke、`--clean` 路径前缀校验）；evaluator package 复用版本化 runner/validator 模式；`a6_mvp_a_reference_v1` 环境描述符已记录（Windows 11 10.0.26200 / Ryzen 5 5600H / CPython 3.12.8 / SQLite ADR-0001 PRAGMA），runner 须戳记实际环境，SLO 不外推；`ARCH-A6-HARDENING-001` 已建立；`.gitignore` 已加 `/devdata/`；尚未物化 A6 suite 或代码。
58. A6 executable suite 已物化（2026-07-25）：fixture/oracles（21 场景固定预期）、scenarios（固定顺序、共享状态执行模式）、adapter protocol、contract module、offline runner（环境戳记 wall time/monotonic/timezone + reference profile 绑定）、preflight validator、manifest；`tools/validate_a6_suite.py` exit 0；contract 21 skipped（无 adapter，不代表业务通过）；全量 regression 232 tests = 211 OK + 21 skipped，无退化；尚未建立 A6 Implementation Plan 或业务代码。
59. `PLAN-MVP-A-A6-IMPL-001` 与 A6 任务卡已建立（2026-07-25）：6 个任务（start.py 壳面 -> Alpha 可解释性 -> 旅程编排 -> adapter -> official runner -> Gate Review）；明确 FR-003 生成侧不得静默补写；尚未开始 A6 业务代码。
60. A6-TASK-001 已完成（2026-07-25）：`start.py` D0 入口与错误恢复壳面（clean_start exit 0；db corrupt 非零退出、非泄露错误、原文件不动；unwritable 非零退出不越界写；`--clean` 仅删默认合成根）；store.py 窄修复（init 失败关闭连接，防文件锁泄漏）；定向 6/6 passed，全量 regression 238 OK（21 A6 contract skipped）；A6 official suite 仍 `not_executed`。
61. A6-TASK-002 已完成（2026-07-25，commit 3fc39db）：`alpha_explainability.py` 数据路径发现（合成/真实路径分离可验证）、备份产物+SHA-256 校验清单、导出 Round Trip（委托已验证 CP 能力，无新导出格式）、卸载语义（默认保留数据目录、删除需独立确认+已验证备份副本）；cli 窄接线 paths/backup/export/uninstall-info；定向 8/8 passed，全量 regression 259 OK（21 A6 contract skipped）；A6 official suite 仍 `not_executed`。注：该任务首个工作树曾因会话中断丢失，本轮按已批准任务卡重做。
62. A6-TASK-003 已完成（2026-07-25，commit 08173d8）：`a6_journey.py` 集成旅程编排辅助（seed 固定合成数据、journey 步骤、conflict/bitemporal/merge-split/restricted-query/stale-base 探针、cross-cutting 审计、SLO 计时收集绑定 `a6_mvp_a_reference_v1`），全部只调用已验证核心能力，零新恢复/权限/候选生成语义；定向 13/13 passed，全量 regression 259 OK（21 A6 contract skipped）；A6 official suite 仍 `not_executed`。
63. A6-TASK-004 已完成（2026-07-25，commit 77066da）：`a6_testing_adapter.py` 完整实现 adapter protocol；contract 21/21 passed；沙箱场景经 start.py 子进程、A6-007/009/016/017 用隔离内存探针库不动共享状态；A6-019 导出真实共享 store；定向 5/5 passed；全量 regression 264 OK 0 skip。
64. A6-TASK-005 已完成（2026-07-25，commit 00d146a）：official runner `a6-20260725.json` 同一次 run 21/21 passed/current；环境戳记与 `a6_mvp_a_reference_v1` 绑定完整；manifest 绑定 current result（flags 全 true）；13 个 suite validator + product baseline 校验全部 PASSED；regression 264 OK 0 skip。
65. A6-TASK-006 已完成（2026-07-25）：Gate Review `A6_HARDENING_GATE_REVIEW_2026-07-25.md` 结论 P0=0/P1=0，八个 A6-INV 均有正/反证明；矩阵 §4.12 状态更新为 verified；recovery tag `a6-hardening-rp-20260725` 已创建并推送。FR-003 生成侧保持合同 §1.1 显式已知限制；Alpha 发布动作须独立发布门禁决定。
66. D3 发布已执行（2026-07-26）：annotated tag `v0.2.0-beta` 已创建并推送。计划偏差如实记录：tag 实际打在 `08095cc`（含 D3 发布说明文档），而非 `D3_RELEASE_PLAN.md` §3.1 字面指定的 `d2-installer-rp-20260726`（`db2f0cc`）。从 tag 重建产物并复核 SHA-256 一致（commit `963e6e7`，smoke 通过）；GitHub prerelease 已创建并上传 ZIP + SHA256SUMS 两个附件；经 GitHub API 复核远端附件 digest 与本地一致；README 双语化（`fd8a023`）为发布收尾提交，main 已推送至 origin。
67. `DEC-Y2-ENTRY-001` 已裁决（2026-07-26，产品负责人委托代理定案）：模型接入本地优先 + 云端显式授权 + 红线舱室 local-only；首个连接器为本地文件夹文本导入；真实数据红线与真实数据生产合同前置；本地 Web UI（stdlib、127.0.0.1、离线）；MCP runtime 后置；Y2-S1..S5 排序；授权起草 PRDv06。仅文档与决策，无业务编码。
68. `PRDv06.md` 草案已完成（2026-07-27）：以 v0.5 全文为底，仅并入 §2.2 五块新语义（§14.5 模型接入政策、§21.6 真实数据生产合同、§24.5 Year 2 切片、§18.8 本地 Web UI、§19.5 MCP 门禁时机）+ Case H + 风险/DQ 同步；结构自查 27 章、32 FR、围栏配对正常；文档状态 Draft，产品基线索引仍指向 v0.5，待 `DEC-PRD-V06-001` 批准后切换并做 S1-S9 兼容复核。
69. `DEC-PRD-V06-001` 已批准（2026-08-01）：`PRDv06.md` v0.6 成为当前产品基线（hash `4513B268...CAD8`），v0.5 转只读；`CURRENT_PRODUCT_BASELINE.md` 索引已切换；九份 SPEC 完成 v0.6 兼容复核（`PRD_V06_SPEC_COMPATIBILITY_REVIEW.md`，绑定同步 + 最小升版：S1 v0.7、S2 v0.6、S3 v0.5、S4 v0.5、S5 v0.5、S6 v0.6、S7 v0.4、S8 v0.4、S9 v0.5，无语义修订）；两个 baseline validator 已同步 v05/v06 版本对并实际通过；业务编码仍未开始。
70. Y2-S1（真实文件夹文本导入）全门禁链完成并 verified（2026-08-01）：`DEC-Y2-S1-001`、applicability（pass_with_slice_contract_required）、`SPEC-Y2S1-FOLDER-IMPORT-001` v0.1 + 合同复核、矩阵 §4.21、`ADR-0020`、`ARCH-Y2S1-FOLDER-IMPORT-001`、suite 物化（10 场景）、`PLAN-Y2-S1-IMPL-001`；TASK-001/002 实现（`folder_import.py` importer+watcher、store 窄辅助）定向 10/10；TASK-003 adapter contract 10/10（3 次复跑稳定）；TASK-004 official runner `y2s1-20260801.json` 同一次 run 10/10 passed/current 并绑定 manifest；全量回归 412 OK 0 skip；22 个 suite validator 全过；Gate Review P0=0/P1=0。切片只证明合成文件夹树的 Source Vault 导入与单次 poll 监视，不宣告真实数据模式开放。
71. Y2-S2（本地模型提议式整理）全门禁链完成并 verified（2026-08-03）：`DEC-Y2-S2-001`、applicability（pass_with_slice_contract_required）、`SPEC-Y2S2-LOCAL-MODEL-001` v0.1 + 合同复核、矩阵 §4.22、`ADR-0021`、`ARCH-Y2S2-LOCAL-MODEL-001`、suite 物化（10 场景）、`PLAN-Y2-S2-IMPL-001`；TASK-001/002 实现（`model_capability.py`、`y2s2_testing_adapter.py`）unit 8/8；adapter contract 10/10；official runner `y2s2-20260803.json` 同一次 run 10/10 passed/current 并绑定 manifest；全量回归 430 OK 0 skip；23 个 suite validator 全过；Gate Review P0=0/P1=0。切片只证明本地模型候选 propose-only 与版本审计，不宣告云端后端、真实模型评估或自动发布。
72. Y2-S3（本地 Web UI 呈现层）全门禁链完成并 verified（2026-08-03）：`DEC-Y2-S3-001`、applicability（pass_with_slice_contract_required）、`SPEC-Y2S3-LOCAL-WEB-UI-001` v0.1 + 合同复核、矩阵 §4.23、`ADR-0022`、`ARCH-Y2S3-LOCAL-WEB-UI-001`、suite 物化（10 场景）、`PLAN-Y2-S3-IMPL-001`；TASK-001/002 实现（`local_web.py`、`y2s3_testing_adapter.py`）unit 7/7；adapter contract 10/10；official runner `y2s3-20260803.json` 同一次 run 10/10 passed/current 并绑定 manifest；全量回归 447 OK 0 skip；24 个 suite validator 全过；Gate Review P0=0/P1=0。切片只证明本地回环 Web 呈现链，不宣告云端后端、MCP、真实数据模式或生产级加密密钥管理。
73. Y2-S4（云端模型可选后端）全门禁链完成并 verified（2026-08-03）：`DEC-Y2-S4-001`、applicability（pass_with_slice_contract_required）、`SPEC-Y2S4-CLOUD-MODEL-001` v0.1 + 合同复核、矩阵 §4.24、`ADR-0023`、`ARCH-Y2S4-CLOUD-MODEL-001`、suite 物化（10 场景）、`PLAN-Y2-S4-IMPL-001`；TASK-001/002 实现（`cloud_model.py`、`y2s4_testing_adapter.py`）unit 5/5；adapter contract 10/10；official runner `y2s4-20260803.json` 同一次 run 10/10 passed/current 并绑定 manifest；全量回归 462 OK 0 skip；25 个 suite validator 全过；Gate Review P0=0/P1=0。切片只证明云端可选后端的授权门、红线门、预览门、审计与诚实降级，不宣告 MCP runtime、真实数据模式或自动上传。

## 4. 真实验证结果

| 范围 | 真实结果 |
|---|---|
| Product / SPEC baseline validator | exit code `0` |
| Micro、A1、B1、C1、Synthetic Ingestion、Context Pack suite validator | 全部 exit code `0` |
| 全量 semantic regression | B2 current verification 时 107/107 passed |
| D1 source demo | exit code `0`，初始化后 `Current revision: rev_010` |
| tag 构建 portable smoke | exit code `0`，初始化后 `Current revision: rev_010` |
| GitHub Actions | `29654926812`、`29654930604` 均为 `success` |
| Release 附件 digest | GitHub API 与本地构建 SHA-256 一致 |
| 独立公开发布终审 | `PUBLIC_PREVIEW_V0.1.3_INDEPENDENT_AUDIT.md`：P0=0、P1=0 |
| B2-TASK-002 | `b2-task002-6944b22-20260719.json`：定向 5/5 passed；全量 semantic regression 103 passed、B2 contract 8 skipped；B2 official suite `not_executed` |
| B2-TASK-003 | `b2-task003-c2fba31-20260719.json`：定向 4/4 passed；全量 semantic regression 107 passed、B2 contract 8 skipped；B2 official suite `not_executed` |
| B2 官方 suite | `b2-a810513-20260719.json`：8/8 passed/current；全量 semantic regression 107 passed |
| B3 suite preflight validator | `python tools/validate_b3_suite.py` exit code `0`（materialized，未执行业务测试） |
| B3 contract module（无 adapter） | 8 skipped，不代表业务通过 |
| B3-TASK-001 | `b3-task001-20260722.json`：定向 5/5 passed；configured-adapter regression 120 OK；B3 official suite `not_executed` |
| B3-TASK-002 | `b3-task002-20260722.json`：定向 8/8 passed；configured-adapter regression 128 OK；B3 official suite `not_executed` |
| B3-TASK-003 | `b3-task003-20260722.json`：定向 4/4 passed；configured-adapter regression 132 OK；B3 official suite `not_executed` |
| B3-TASK-004 | `b3-task004-20260722.json`：contract 8/8 passed（adapter）；official runner 未执行 |
| B3 官方 suite | `b3-20260722.json`：8/8 passed/current；全量 regression 132 OK；manifest 已绑定 |
| A2-TASK-001 | `a2-task001-20260722.json`：定向 5/5 passed；configured-adapter regression 145 OK；A2 official suite `not_executed` |
| A2-TASK-002 | `a2-task002-20260722.json`：定向 6/6 passed；configured-adapter regression 151 OK；A2 official suite `not_executed` |
| A2-TASK-003 | `a2-task003-20260722.json`：contract 8/8 passed（adapter）；official runner 未执行 |
| A2 官方 suite | `a2-20260722.json`：8/8 passed/current；全量 regression 151 OK；manifest 已绑定 |
| A2 可复现性重跑 | `a2-20260722-r2.json`：同 commit/同 manifest 8/8 passed |
| A2 Gate Review | `A2_CURRENT_STATE_GATE_REVIEW_2026-07-22.md`：P0=0、P1=0 |
| A3-TASK-001 | 定向 5/5 passed（test_a3_task_001_store）；configured-adapter regression 156 OK、8 A3 contract skipped；A3 official suite `not_executed` |
| A3-TASK-002 | 定向 5/5 passed（test_a3_task_002_entity_merge）；configured-adapter regression 161 OK、8 A3 contract skipped；A3 official suite `not_executed` |
| A3-TASK-003 | contract 8/8 passed（adapter）；全量 regression 169 OK 无 skip；official runner 未执行 |
| A3 官方 suite | `a3-20260724.json`：8/8 passed/current；全量 regression 169 OK；manifest 已绑定 |
| A3 Gate Review | `A3_ENTITY_MERGE_GATE_REVIEW_2026-07-24.md`：P0=0、P1=0 |
| A4-TASK-001 | 定向 6/6 passed（test_a4_task_001_store）；configured-adapter regression 175 OK、8 A4 contract skipped；A4 official suite `not_executed` |
| A4-TASK-002 | 定向 8/8 passed（test_a4_task_002_access_policy，判决器与 oracle 全场景一致）；configured-adapter regression 183 OK、8 A4 contract skipped；A4 official suite `not_executed` |
| A4-TASK-003 | contract 8/8 passed（adapter）；全量 regression 191 OK 无 skip；official runner 未执行 |
| A4 官方 suite | `a4-20260724.json`：同一次 run 8/8 passed/current；全量 regression 191 OK；11 个 suite validator 全 PASSED；manifest 已绑定 |
| A4 Gate Review | `A4_ACCESS_POLICY_GATE_REVIEW_2026-07-24.md`：P0=0、P1=0 |
| A5-TASK-001 | `a5-task001-2320515-20260724.json`：定向 6/6 passed；configured-adapter regression 205 OK、8 A5 contract skipped；A5 official suite `not_executed` |
| A5-TASK-002 | `a5-task002-310bcf2-20260725.json`：定向 6/6 passed；contract 8/8 passed（adapter）；全量 regression 211 OK 无 skip；A5 official suite `not_executed` |
| A5-TASK-003 | `a5-task003-a45a8bd-20260725.json`：contract 8/8 passed；全量 regression 211 OK 无 skip 无退化；A5 official suite `not_executed` |
| A5 官方 suite | `a5-20260725.json`：同一次 run 8/8 passed/current；全量 regression 211 OK 无 skip；12 个 suite validator 全 PASSED；manifest 已绑定 |
| A5 Gate Review | `A5_APP_SHELL_GATE_REVIEW_2026-07-25.md`：P0=0、P1=0 |
| A6 官方 suite | `a6-20260725.json`：同一次 run 21/21 passed/current；全量 regression 264 OK 无 skip；13 个 suite validator 全 PASSED；manifest 已绑定 |
| A6 Gate Review | `A6_HARDENING_GATE_REVIEW_2026-07-25.md`：P0=0、P1=0 |
| B4-TASK-001 | `b4-task001-20260725.json`：增量对账四类发现定向 7/7 passed；B4 official suite `not_executed` |
| B4-TASK-002 | `b4-task002-20260725.json`：深度对账三分区重建比较定向 11/11 passed；B4 official suite `not_executed` |
| B4-TASK-003 | `b4-task003-20260725.json`：semantic_diff 定向 7/7 passed；B4 official suite `not_executed` |
| B4-TASK-004 | `b4-task004-20260725.json`：contract 10/10 passed（adapter）；B4 official suite `not_executed` |
| B4 官方 suite | `b4-20260725.json`：同一次 run 10/10 passed/current；全量 regression 292 OK 无 skip；14 个 suite validator 全 PASSED；manifest 已绑定 |
| B4 Gate Review | `B4_RECONCILIATION_GATE_REVIEW_2026-07-25.md`：P0=0、P1=0 |
| B5-TASK-001 | `b5-task001-20260725.json`：bilingual overlay 定向 9/9 passed；B5 official suite `not_executed` |
| B5-TASK-002 | `b5-task002-20260725.json`：contract 8/8 passed（adapter）；B5 official suite `not_executed` |
| B5 官方 suite | `b5-20260725.json`：同一次 run 8/8 passed/current；全量 regression 309 OK 无 skip；15 个 suite validator 全 PASSED；manifest 已绑定 |
| B5 Gate Review | `B5_MULTILINGUAL_GATE_REVIEW_2026-07-25.md`：P0=0、P1=0 |
| B6-TASK-001/002 | `b6-task001/task002-20260725.json`：shadow migration + disambiguation 定向 9/9 passed；B6 official suite `not_executed` |
| B6-TASK-003 | `b6-task003-20260725.json`：contract 10/10 passed（adapter）；B6 official suite `not_executed` |
| B6 官方 suite | `b6-20260725.json`：同一次 run 10/10 passed/current；全量 regression 328 OK 无 skip；16 个 suite validator 全 PASSED；manifest 已绑定 |
| B6 Gate Review | `B6_SHADOW_MIGRATION_GATE_REVIEW_2026-07-25.md`：P0=0、P1=0；MVP-B（B1-B6）全部 verified |
| C2-TASK-001 | `c2-task001-20260726.json`：hypotheses 生命周期模块定向 9/9 passed；回归 347 OK（C2 contract skipped）；C2 official suite `not_executed` |
| C2-TASK-002 | `c2-task002-20260726.json`：contract 10/10 passed（adapter）；回归 347 OK 0 skip；C2 official suite `not_executed` |
| C2 官方 suite | `c2-20260726.json`：同一次 run 10/10 passed/current；全量 regression 347 OK 0 skip；17 个 suite validator 全 PASSED；manifest 已绑定 |
| C2 Gate Review | `C2_HYPOTHESIS_GATE_REVIEW_2026-07-26.md`：P0=0、P1=0；C2 Hypothesis Lifecycle（FR-201）verified |
| C3-TASK-001 | `c3-task001-20260726.json`：reviews 模块 + `store.delete_ledger_record` 定向 5/5 passed；回归 362 OK（C3 contract skipped）；C3 official suite `not_executed` |
| C3-TASK-002 | `c3-task002-20260726.json`：contract 10/10 passed（adapter）；oracle 一处人工计数修正（月/年度 completed 3->4、on_time 2->3，fixture 未动，manifest hash 已同步）；C3 official suite `not_executed` |
| C3 官方 suite | `c3-20260726.json`：同一次 run 10/10 passed/current；全量 regression 362 OK 0 skip；18 个 suite validator 全 PASSED；manifest 已绑定 |
| C3 Gate Review | `C3_REVIEW_GATE_REVIEW_2026-07-26.md`：P0=0、P1=0；C3 Review & Calibration（FR-203/FR-205）verified |
| C4-TASK-001 | `c4-task001-20260726.json`：scenarios 七入口模块定向 5/5 passed；C4 official suite `not_executed` |
| C4-TASK-002 | `c4-task002-20260726.json`：contract 10/10 passed（adapter）；oracle 两处 forbidden_mutations 设计修正（fixture 未动，manifest hash 已同步）；C4 official suite `not_executed` |
| C4 官方 suite | `c4-20260726.json`：同一次 run 10/10 passed/current；全量 regression 377 OK 0 skip；19 个 suite validator 全 PASSED；manifest 已绑定 |
| C4 Gate Review | `C4_SCENARIO_GATE_REVIEW_2026-07-26.md`：P0=0、P1=0；C4 Scenario & Action（FR-204/FR-206）verified |
| C5-TASK-001 | `c5-task001-20260726.json`：pack_backup 六入口模块定向 5/5 passed；C5 official suite `not_executed` |
| C5-TASK-002 | `c5-task002-20260726.json`：contract 10/10 passed（adapter）；oracle 两处呈现修正（fixture 未动，manifest hash 已同步）；C5 official suite `not_executed` |
| C5 官方 suite | `c5-20260726.json`：同一次 run 10/10 passed/current；全量 regression 392 OK 0 skip；20 个 suite validator 全 PASSED；manifest 已绑定 |
| C5 Gate Review | `C5_PACK_GATE_REVIEW_2026-07-26.md`：P0=0、P1=0；C5 Context Pack & Encrypted Backup（FR-303 首年切片）verified |
| C6 审计 | `c6-20260726.json`：审计 runner 同一次 run 8/8 passed（21 validators、回归 392 OK 0 skip、隐私/依赖/网络/manifest 审计、恢复演练、门禁核验）；run1 失败留痕 `c6-audit-run1-failed-20260726.json`；manifest 已绑定 |
| C6 Gate Review | `C6_RELEASE_GATE_REVIEW_2026-07-26.md`：P0=0、P1=0；Beta 门禁 `BETA_GATE_REVIEW_2026-07-26.md` beta_ready=true；MVP-C 全部切片 verified |
| D2 一键安装 | `D2_BETA_V0.2.0_VERIFICATION.md`：构建 exit 0（产物 SHA-256 `3798971cb5471043bf3b0bf79e32b668bb85c6fdd9807ad70dd120bc47264147`）；clean-install、真实状态、升级（自动数据备份+回滚点）、卸载（保留数据/显式删除+强制校验备份）、三项失败行为全部真实验证通过；回归 392 OK 0 skip；21 个 suite validator 全 PASSED；未发布 GitHub Release |
| D3 发布核验 | GitHub API 附件 digest：`Noetide-beta-v0.2.0-win64.zip` = `sha256:3456b2b67d8788a006c7906629b25556af5d42ba02a84a892542d7f3f0f4b8a8`、`SHA256SUMS-0.2.0-win64.txt` = `sha256:7cd7fae68d662d0e55a534ed30014a8d02645dec6a1044bdc4716a3495f3f29a`，与 `D3_RELEASE_PLAN.md` 记录及本地 `dist/` 复核哈希逐项一致；prerelease published at 2026-07-26T06:59:35Z；tag 已推送远端 |
| DEC-Y2-ENTRY-001 文档变更 | `validate_product_baseline.ps1` exit 0；`validate_spec_baseline.ps1` exit 0；`git diff --check` exit 0（2026-07-26，静态校验，非业务测试） |
| DEC-PRD-V06-001 基线切换 | `validate_product_baseline.ps1` exit 0（v04/v05 immutable、v06 approved、27 章、32 FR、12 对象、DQ-001..013、隐私与围栏通过）；`validate_spec_baseline.ps1` exit 0（275 测试 ID、133 不变量、32 FR 行、185 引用、9 SPEC 绑定 v0.6、197 文件隐私扫描、643 文件围栏通过）（2026-08-01，静态校验，非业务测试） |
| Y2-S1 定向测试 | TASK-001/002：10/10 passed（importer 四终态、确定性、profile fail closed、watcher、中断收敛） |
| Y2-S1 contract（adapter） | 10/10 passed，连续 3 次复跑结果一致 |
| Y2-S1 官方 suite | `docs/testing/results/y2s1-20260801.json`：同一次 run 10/10 passed/current，网络阻断、stdlib only；manifest 已绑定；全量回归 412 OK 0 skip；22 个 suite validator 全 PASSED |
| Y2-S1 Gate Review | `Y2_S1_FOLDER_IMPORT_GATE_REVIEW_2026-08-01.md`：P0=0、P1=0 |
| Y2-S2 定向测试 | TASK-001/002：unit 8/8 passed（`model_capability` + `y2s2_testing_adapter`） |
| Y2-S2 contract（adapter） | 10/10 passed |
| Y2-S2 官方 suite | `docs/testing/results/y2s2-20260803.json`：同一次 run 10/10 passed/current，网络阻断、stdlib only；manifest 已绑定；全量回归 430 OK 0 skip；23 个 suite validator 全 PASSED |
| Y2-S2 Gate Review | `Y2_S2_LOCAL_MODEL_GATE_REVIEW_2026-08-03.md`：P0=0、P1=0 |
| Y2-S3 定向测试 | TASK-001/002：unit 7/7 passed（`local_web` + `y2s3_testing_adapter`） |
| Y2-S3 contract（adapter） | 10/10 passed |
| Y2-S3 官方 suite | `docs/testing/results/y2s3-20260803.json`：同一次 run 10/10 passed/current，网络阻断、stdlib only；manifest 已绑定；全量回归 447 OK 0 skip；24 个 suite validator 全 PASSED |
| Y2-S3 Gate Review | `Y2_S3_LOCAL_WEB_UI_GATE_REVIEW_2026-08-03.md`：P0=0、P1=0 |
| Y2-S4 定向测试 | TASK-001/002：unit 5/5 passed（`cloud_model` + `y2s4_testing_adapter`） |
| Y2-S4 contract（adapter） | 10/10 passed |
| Y2-S4 官方 suite | `docs/testing/results/y2s4-20260803.json`：同一次 run 10/10 passed/current，网络阻断、stdlib only；manifest 已绑定；全量回归 462 OK 0 skip；25 个 suite validator 全 PASSED |
| Y2-S4 Gate Review | `Y2_S4_CLOUD_MODEL_GATE_REVIEW_2026-08-03.md`：P0=0、P1=0 |


完整命令、环境、哈希和限制见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。静态校验不被表述为业务测试通过；历史失败运行结果仍保留在 `docs/testing/results/`。

## 5. 风险与边界

- 当前发布只允许固定合成 demo 数据。不得输入、导入、提交或推断真实个人资料、凭据或工作区外数据。
- 该版本不是完整 PRD 产品，不实现真实导入、通用 NLP、权限/MCP runtime、同步、连接器、分享、签名安装包、升级或真实数据生产合同。
- v0.2.0-beta 已发布，但未代码签名、Windows-only、无自动更新；真实数据生产合同仍未完成；不得宣称“完整一键部署”或生产可用。

## 6. 下一步唯一建议动作

**Y2-S4 已 verified（recovery tag `y2s4-cloud-model-rp-20260803`）。下一步唯一动作：重开 `DQ-013` 并形成 Y2-S5（MCP runtime 最小子集）切片决策 `DEC-Y2-S5-001`，保持本地优先、最小工具、显式授权、只读优先与 fail closed，按同一门禁链推进。**
