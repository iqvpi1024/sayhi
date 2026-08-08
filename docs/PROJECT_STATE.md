# 项目状态

## 1. 恢复入口

每次任务按 `AGENTS.md` 的顺序恢复。当前产品语义以 `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的 `PRDv06.md` v0.6 为准；历史 PRD、SPEC、结果和 tag 保留审计价值，不得覆盖动态状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 sayhi（原名 Noetide；代码内部标识保留 `noetide_micro`） |
| 当前产品基线 | `PRDv06.md` v0.6 Approved，canonical LF SHA-256 `4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8` |
| 当前公开发布 | **`v0.3.4-beta` 已发布（2026-08-09，GitHub prerelease，首个 sayhi 品牌版：九项优化 + MCP 协议加固 + Windows setup P0 修复）；仓库已公开** |
| 当前工作切片 | 完整产品已实现（NoetideApp/product_server/webui）；本地安装、Web 管理、识灵分析、MCP/API、导出备份、远程访问全部可运行 |
| 当前阶段 | `v0.3.4-beta released + repo public`；cloud 提取评测 + 第二轮真人模拟已完成（§3 第 86 条），并行竞态/备份恢复两缺陷已修未发布（待 v0.3.5） |
| 当前公开版本 | `v0.3.4-beta` GitHub prerelease |
| tag / commit | annotated tag `v0.3.4-beta` -> `3b89df6`（九项优化 + 改名提交）；`v0.3.3-beta` -> `5c4ea0c`；`v0.3.2-beta` -> `2d9602e`；`v0.3.1-beta` -> `5f7c89d`；`v0.3.0-beta` -> `0dcc89d`；历史 `v0.2.0-beta` -> `08095cc4aca88adad6469ffe3bedc9f25bdabaf7` |
| product-complete recovery tag | annotated tag `product-complete-rp-20260803`（tag object `a64fb89`）-> `9e3875d0c32c7a1aab249a90d6b7cd84911f533d`，已创建并推送 origin |
| audit-remediation recovery tag | annotated tag `audit-remediation-rp-20260808` -> `8ea83d2`（整改提交，76 文件），已创建并推送 origin |
| GitHub Release | `https://github.com/iqvpi1024/sayhi/releases/tag/v0.3.4-beta`（仓库已公开） |
| v0.3.4 发布产物 | `sayhi-beta-v0.3.4-win64.zip` SHA-256 `d94b96cade4534aa2ba157e862df49505b007166ca231a223c2a57c431641c70`、`sayhi-0.3.4-src.tar.gz` SHA-256 `0c3b46fbb553833540946d5cd424d7490566317f62ef7238fb91c4eee9ed7f5d`（均从 tag `v0.3.4-beta` 构建；GitHub API 远端 digest 与本地一致）；smoke 14/14：setup exit 0（P0 修复实测）、/api/health 200、中文导入、异步分析 done、9 候选提议+确认、标准 MCP initialize（serverInfo sayhi 0.3.4）/tools/list 五工具/ask_memory、恶意 Origin 403、Web UI 200 |
| 历史发布产物 | v0.3.3 zip SHA-256 `2d1d2a30fbc2d9a86033c5c6c7d103c5ed12b0dfe7f6ef893e32ba68ca97d27c`（tag `v0.3.3-beta`）；v0.3.2 zip SHA-256 `c89165a6abc7ece2f4151919d569ae39582334bb8f3e7b578cdf7cbeb29048b1`（tag `v0.3.2-beta`）；v0.3.1 zip SHA-256 `236f88d12420e6aeb9bfe09ec8d45bf28aec085ca012c1b4c969e9c7945533e0`（tag `v0.3.1-beta`）；v0.3.0 zip SHA-256 `f702908b4256b46e7ab9e78b483cd5a6a38d58e81314ef44b7bffb9bc974f014`（tag `v0.3.0-beta`） |
| 交付级别 | D1/D2/D3 历史版本已发布；当前完整产品已具备一键安装、Web 管理、MCP/API、识灵大模型分析、导出备份与远程访问 |
| 分支 | `main`，已推送至 `origin/main` |

## 3. 已完成内容

### 完整产品（2026-08-03）

- 已实现 `NoetideApp`：空库初始化、文本/文件夹导入、离线识灵分析、本地/云端模型分析、候选确认/忽略、搜索/时间线、Context Pack 导出/导入、加密备份/恢复。
- 已实现 `product_server.py`：本地 Web UI、REST API、`/mcp` JSON-RPC、远程令牌鉴权、默认/自定义 Agent 授权。
- 已实现 `webui.html`：总览、导入、识灵分析、记忆、搜索、Agent 接入、导出备份、设置；桌面和移动端响应式。
- 已实现桌面启动器 `noetide_desktop.py`、CLI `noetide product` / `noetide product-init` 子命令（console script `noetide` / `noetide-product`）、portable 安装/启动脚本。
- 产品测试 5/5 OK；全量 configured-adapter regression 485 OK、0 skipped（2026-08-03）。
- `dist/Noetide-beta-v0.3.0-win64.zip` 构建成功，SHA-256 `55c26e39aca14ef3839978093d55856403ce19f6ca8e222e6543f0aecb3b80f2`；portable 空库初始化与 `/api/health` 启动检查通过。

1. PRD v0.5、S1-S9 Approved 语义基线、Micro 关系链路、Answer Safety、Candidate Review、Decision/Outcome、合成导入和私有合成 Context Pack 均保留为当前实现范围内的合成能力。
2. A1 suite 完整性绑定已修复，官方 runner 在 `8556eea` 实际通过 35/35；C1 runner 场景映射已修复，官方 runner 在同一提交实际通过 7/7。
3. `v0.1.3-synthetic-preview` 已发布源码 ZIP、Windows portable ZIP 及各自 SHA-256 校验文件。portable 包自带 Python runtime，解压后可初始化合成 SQLite 并读取 `rev_010`。
4. GitHub Actions 对 `main` 和 tag 的两个 run 均通过，包含 Linux 合同/语义回归与 Windows portable smoke。
5. B2 Episode/summary 已完成合同、ADR、suite、实现、官方 runner、Gate Review 与 recovery point；它只证明 FR-103 的固定合成切片。
6. B2 official suite 的 `B2-001..008` 为 8/8 passed/current；recovery tag `b2-episode-summary-rp-20260719` 已推送。

> 编者注（2026-08-07）：编号 7-13 为历史重编号遗留的断档；为保持既有文档对条目标号的引用稳定，此处不重排编号。

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
74. Y2-S5（MCP runtime 最小子集）全门禁链完成并 verified（2026-08-03）：`DEC-Y2-S5-001`、applicability（pass_with_slice_contract_required）、`SPEC-Y2S5-MCP-RUNTIME-001` v0.1 + 合同复核、矩阵 §4.25、`ADR-0024`、`ARCH-Y2S5-MCP-RUNTIME-001`、suite 物化（10 场景）、`PLAN-Y2-S5-IMPL-001`；TASK-001/002 实现（`mcp_runtime.py`、`y2s5_testing_adapter.py`）unit 8/8；adapter contract 10/10；official runner `y2s5-20260803.json` 同一次 run 10/10 passed/current 并绑定 manifest；全量回归 480 OK 0 skip；26 个 suite validator 全过；Gate Review P0=0/P1=0；recovery tag `y2s5-mcp-runtime-rp-20260803` 已创建并推送。切片只证明 MCP runtime 最小子集的只读接入，不宣告 controlled mutate、A2A、多 Agent、真实数据模式或云端调用。
75. 2026-08-07 全面审核整改（2026-08-07/08 执行）：双份独立审核（`项目全面审核报告-2026-08-07.md`、`Review-report/FULL_AUDIT_REPORT_2026-08-07.md`）后实施四包整改。安全闭环：`product_server.py` 去除 `ACAO: *`、Host/Origin 回环校验、非回环绑定无 token 拒绝启动、`hmac.compare_digest` 令牌比较、请求体 1 MiB 上限、错误信息不外泄；`pack_backup.py` 备份格式升级 NOBAK2（PBKDF2 20 万轮 + HMAC-SHA256，去除明文哈希爆破 oracle，旧格式明确拒绝）；`local_web.py` 移除硬编码备份密钥（改环境变量/随机持久化）；`webui.html` 增加非生产级加密风险提示；`SECURITY.md` 重写覆盖 v0.3.0 真实攻击面；`.gitignore` `/devdata/` 行尾 `\r` 失效修复。
76. 整改（核心工程加固，2026-08-08）：产品云通路接入 `CloudGate` 授权/红线/预览三门并全审计落账（`product.py:459-592`）；source 红线舱室确定性启发式标注；local 模型模式强制 loopback；`SemanticStore.next_revision()` 统一 revision 分配消除跨模块碰撞；`confirm_candidate`/`import_pack` 写入事务化并修正 base_revision 语义；`hypotheses.py` 补 changeset 账本；`access_policy.py` 畸形输入 fail-closed deny；时间戳比较统一 UTC epoch；receipt id 改库内计数分配；`store.py` 全连接 RLock 序列化 + 嵌套事务 SAVEPOINT；其余 P2（answers freshness、b1 幂等、candidate_aggregator fail-closed、shadow_migration 半成品清理等）一并修复。oracle 锁定项（scenarios revision 账本、changesets/episodes 硬编码 rev 命名、decision 持久化、C5 encryption 标签更名）仅做 docstring 标注，待 Change Control。
77. 整改（测试与工具链，2026-08-08）：`b3_testing_adapter.py` B3-002 自问自答修复为真实业务判定；micro/answer_safety contract 改 `skipUnless`（裸跑 errors 2→0）；micro validator 补 `bound_artifacts` 复核、y2s1..y2s5 validator 修正成功措辞（6 个 validator 与其余 20 个对齐）；`validate_pre_development_gate.ps1` 加一次性门禁标注并修复 `$PSHOME` 调用；新增 `pytest.ini`（`pythonpath = src`）；`docs/testing/README.md` 固化 canonical 回归命令。按 Change Control 对 8 个 suite 重跑 official runner 并 rebind manifest：`b3-20260807.json`(8/8)、`micro-20260807.json`(49/49)、`a1-20260807.json`(35/35)、`y2s1..y2s5-20260807.json`（各 10/10)，旧结果以 superseded 入 historical_verification_results。
78. 整改（文档收尾，2026-08-08）：`PROJECT_STATE.md` §2/§3/§6 收尾（product-complete tag 补记、Y2-S5 补登、编号断档编者注）；`CURRENT_HANDOFF.md` 三字段同步；`docs/process/README.md` §10 与 `docs/adrs/README.md` §5 过期快照改为指向 PROJECT_STATE 的指针；`LATEST_*` 加时效声明；矩阵 FR-302 与 §5 补切片级进展；新建合并 Recovery Record `docs/releases/Y2_AND_PRODUCT_COMPLETE_RECOVERY_RECORDS_2026-08-03.md`；基线索引补路径解析基准说明；15 份首年切片合同补 v0.6 适用性注记；CLI 表述修订为 `noetide product`/`noetide product-init` 子命令。
79. Change Control 尾巴清理（2026-08-08，实现修复层 + 测试物化层，触发来源：第 76 条遗留的四项 oracle 锁定标注之三）：(a) `scenarios.py` 三处 Canonical 写入（`create_scenario_set`/`create_follow_ups`/`complete_follow_up`）补齐 canonical_revisions revision 行 + changeset 账本行（noetide.changeset.v1，风格同 `hypotheses.py`，同事务提交）；c4 oracle 由 `forbidden_mutations` 禁止 revision_ledger 变化改为 `revisions_added` 精确锁定新增 revision id（断言加强而非弱化，fixture 未动），official runner `c4-20260808.json` 同一次 run 10/10 passed/current，manifest 已 rebind，`c4-20260726.json` 以 superseded 入 historical_verification_results。(b) `pack_backup.py` `ENCRYPTION_LABEL` 由 `stdlib_deterministic_v1` 更名为 `nobak2_pbkdf2_hmac_v1`，与实际 NOBAK2 构造（PBKDF2-HMAC-SHA256 20 万轮 + HMAC-SHA256）一致；`SPEC-C5-PACK-001` 升 v0.2（仅标签更名注记，构造/状态机/不变量未变）、`SECURITY.md` 现行描述同步；c5 oracle C5-005 同步，runner `c5-20260808.json` 10/10 passed/current，manifest 已 rebind，`c5-20260726.json` 转 superseded；ADR-0017、C5/Beta Gate Review、C5 计划文档与 Y2S3 SPEC 中的旧标签为历史记录，保留不改。(c) `c1.py` 新增 `C1ChangeSetService.publish_revision`（add-only：只追加新 revision + changeset 账本行，payload 内 revision_history 保留旧快照，不改写历史），`decision.py` 新增 `decide_persisted`/`close_persisted`/`set_predicted_outcome_persisted`（复用内存版校验后经 publish_revision 落库）；`test_c1_changesets.py` 新增 3 个持久化测试，runner `c1-20260808.json` 7/7 passed/current，manifest 已 rebind，`c1-release-8556eea-20260719.json` 转 superseded；c1 fixture/oracle 未动。三个 validator 全部 exit 0；26 个 suite validator 复扫全部 exit 0。第 76 条遗留的第四项（changesets/episodes 硬编码 rev 命名）仍未处理。
80. LLM 提供商层 + 识灵提取质量 + docx 导入（2026-08-08）：新增 `llm_providers.py`——统一 `chat_completion` 适配器（openai_compatible / anthropic / gemini），`PROVIDER_PRESETS` 预置 OpenAI、Anthropic Claude、Google Gemini、DeepSeek、Moonshot(Kimi)、智谱、通义千问、Ollama 远程、custom；云端发送仍全过 CloudGate 三门 + 审计，api_key 三层防泄（只进请求头、适配层脱敏、public_settings 只回 `*_set`）。结构化提取：模型输出强制 JSON + 逐字 evidence_quote，编造证据的候选自动丢弃并计数（`extraction_stats` 诚实透出）；解析失败 fail-closed。离线规则新增人物-项目关系与裸年份事件两个确定性模式。docx 导入：stdlib zipfile+XML 提取，损坏文件 fail-closed 计数。webui 设置页加提供商下拉与模型名。新增 `tests/semantic/test_product_providers.py` 17 个用例全过（三种 provider 请求形状、红线拒绝、解析器四类输入、docx 正常/损坏）。
81. 问识海 Q&A（2026-08-08）：`NoetideApp.ask()`（product.py:868）——只读零写入，只对已确认断言作答且逐条过 `AnswerEvaluator` 核对；无证据固定回答"我不知道……识海不会编造回答"并给出覆盖度声明（`no_coverage` + reason_codes）；Derived-only 证据被拒（AS-008 保持）；`POST /api/ask` 走既有 Host/Origin/令牌防护；webui 新增"问识海"版块（回答+覆盖度醒目声明+证据跳转来源）。answers.py 本体零改动，产品侧适配层把产品断言映射为 `statement_occurrence` 查询（语义="资料中确实这样记录"，不声称世界事实）。新增 `tests/semantic/test_product_ask.py` 6 个用例全过（含零写入三重快照对比、Derived-only 拒绝、路由冒烟）。
82. 真人模拟测试与测试驱动修复（2026-08-08，测试环境 `ces/` 已 gitignore、不入库）：以真实 Kimi API（会员 key，测试后用户已吊销）+ 用户自有的 10 份雷军语料在独立数据目录完成 7 轮端到端真人模拟（导入→云端分析→确认/拒绝→问识海→备份恢复→3 个并发 MCP Agent），发现并修复两类真实缺陷：(a) 推理模型兼容性——`llm_providers.py` 硬编码 `temperature: 0` 导致 Kimi 推理模型全 400，改为缺省不发送；`max_tokens` 默认 1024→4096（推理 token 占额度）；anthropic/gemini 适配器同步支持；`product.py` 调用点 timeout 15s→120s，新增可选设置 `model_temperature`/`model_max_tokens`（SETTINGS_KEYS 已登记）。(b) ask 诚实漏洞——`_ask_terms` 重写为按停用词切段+长段 2-gram 并返回 `(terms, primary_count)`，相关性门槛 `min(2, primary_count)`（修复"只命中主题词即判相关"）；`_ask_adapt_assertion` 从只接 assertion 扩展到 entity/episode/commitment（按类型拼 text，扁平结构字段在顶层，payload 兜底），适配结果带 `product_object_type` 供 evidence 使用。测试中发现并实证的正面行为：红线门拦截心理咨询记录（不出网+对 MCP Agent 不可见）、反编造门丢弃 2 条模型编的假证据、备份错密钥拒绝且恢复 42/42 保真、3 个并发 Agent 零冲突。遗留改进点（未修）：MCP propose_changeset 提议只进账本不落产品候选队列（网页不可见无法确认）、MCP 合同可发现性差、提取摘要丢实质内容、10 分钟分析无进度提示。完整记录见 `ces/测试报告-2026-08-08.md`（含 key 的环境，未入库）。新增 2 个回归测试后全量回归 513 OK 0 skipped。
83. Agent 记忆中枢表面（2026-08-08，第 82 条遗留改进的落地）：(a) **标准 MCP 协议层**——`product_server.py` `/mcp` 在遗留 `params.request` 合同之外新增主流标准方法：`initialize`（serverInfo+instructions）、`ping`、`tools/list`（`mcp_runtime.TOOL_DESCRIPTORS`：name+description+inputSchema，解决可发现性）、`tools/call`、`resources/list`、`resources/read`（`noetide://source/<id>`）；能力令牌经 `X-Noetide-Capability` 请求头指定，缺省回落本地默认令牌；幂等键缺省按内容哈希派生；主流 Agent（Claude Code、Codex 等）可直接把 `/mcp` 配为 HTTP MCP server。(b) **ask_memory 只读工具**——`READ_TOOLS` 新增 `ask_memory`，`McpRuntime` 新增 `ask_handler` 注入（`NoetideApp._mcp_ask`）；`ask()` 新增 `source_scope` 参数：MCP 路径只看能力令牌授权资料，红线舱室在 ask 层过滤（诚实 no_coverage 而非整请求拒绝，与 list_resources 同策略）；零写入，复用同一套诚实语义。(c) **propose_changeset 落产品候选队列**——`NoetideApp.mcp_handle` 在 accepted 后把候选写入 `product_candidate` 账本（`model_or_rule_version=mcp-agent:<caller>`、`mcp_changeset_id` 溯源、material 哈希幂等去重），网页可确认/拒绝；确认走既有 `confirm_candidate` 不变。(d) **提取摘要保实质**——`build_extraction_prompt` 明确要求 summary 保留具体人名/数字/清单/口诀，禁止笼统概括（第 82 条"七字诀"问题）。(e) **长任务进度**——`NoetideApp.start_analysis` 后台线程 + `analysis_status()`，服务端 `POST /api/analyze` 改异步、`GET /api/analyze/status` 透出进度；webui 分析页 2s 轮询显示"分析中 i/n:当前资料"，切页回来恢复轮询；重复启动拒绝 `already_running`。(f) webui Agent 页新增"Agent 可用工具"面板（GET /api/mcp 现返回工具描述表）。新增 `tests/semantic/test_product_mcp_agent.py` 11 用例（标准协议握手/工具发现/资源读写/legacy 兼容/ask_memory 回答+诚实拒绝+红线过滤+限定令牌/提议落队列幂等确认/进度与重复启动拒绝）+ providers 提示词回归 1 用例；全量回归 525 OK 0 skipped。README 新增"把识海接进你的 Agent"一节（含 Claude Code 配置示例）。
84. Change Control 尾巴清零（2026-08-08，第 76 条遗留第四项的评估结论）：(a) `changesets.py` 发布/补偿 revision 由硬编码 `rev_011`/`rev_012` 改为事务内 `next_revision()` 统一分配；fixture 基线 rev_010 下分配结果数值不变，C1 official runner `c1-revalloc-20260808.json` 同一次 run 7/7 passed/current，manifest 已 rebind，`c1-20260808.json` 转 superseded，fixture/oracle/测试模块未动。(b) `episodes.py` **评估后保留硬编码 `rev_021`/`rev_022`**：B2 合同把这两个 id 作为固定 fixture 编号（语义上继承 B1 末端 rev_020），其直接单测路径的 store 只推进到 rev_010，动态分配会产生 rev_011 与合同固定值冲突；修正需改动 b2 套件绑定的测试模块与 oracle（manifest 锁哈希），属合同变更而非实现修复，收益不足以抵消——评估结论在此留痕，如未来 B2 合同修订再一并处理。(c) 版本号单一来源：`__init__.py.__version__` 0.1.3（陈旧）→ 0.3.3，`product_server.MCP_SERVER_VERSION` 改为引用包 `__version__`，消除手工同步遗留。26 个 suite validator 全 exit 0；全量回归 525 OK 0 skipped。
85. 九项优化 + 品牌改名 sayhi（2026-08-08）：(a) **Agent 授权 UI**:webui Agent 页改为勾选资料一键创建限定范围能力令牌（原手填 source_id 输入移除），创建后给出含 `X-Noetide-Capability` 请求头的配置说明；工具面板展示描述表。(b) **真实 MCP 客户端验证**：官方 TypeScript SDK 1.30.0（StreamableHTTPClientTransport）7/7 PASS + Python mcp 2.0.0 6/6 PASS（initialize/tools/list/ask_memory/resources/ping/未知工具 -32601）；按验证报告修三处规范偏差——notification 回 202 无 body、initialize 版本协商（`MCP_PROTOCOL_VERSIONS` 清单内回显，否则回最高支持版）、GET/DELETE `/mcp` 回 405 JSON（原 404/501 HTML)。(c) **设置页补齐** `model_temperature`/`model_max_tokens`/`ask_retrieval`/`model_embed_name`。(d) **本地向量召回**：`llm_providers.embed_texts`(OpenAI 兼容 /embeddings，端点推导，异常脱敏）+ `ask(source_scope)` 同级新增 `_ask_relevant_embedding`——仅 local 模式 + loopback 端点（cloud 模式永不走向量，记忆文本不出网）；向量只决定送核对器的候选集，作答仍由 AnswerEvaluator 逐条核对，诚实性不依赖相似度；不可用如实回落 `embedding_unavailable_fallback_lexical` 并透出在 coverage.retrieval。(e) **分析并行化**：外部模型模式 ThreadPoolExecutor 3 路并行（pool.map 保序、候选按来源顺序串行落库、store RLock 序列化），离线规则保持串行。(f) **候选合并**:webui 按 kind+label 分组成组确认/忽略。(g) **macOS/Linux 源码启动包**:`scripts/portable/setup-noetide.sh`/`start-noetide.sh`（版本检查、NOETIDE_HOME、与 Windows 同构 privacy.json)+ `scripts/build-unix-source.sh`(git archive + SHA256SUMS,Git Bash 实测打包+解包+setup+start+curl 200)。(h) **P0 修复**:`setup-noetide.ps1` 安装末步健康检查由 `status`（对 product-init 库误报 SeedConflictError，实测复现）改为 NoetideApp 健康检查——此前 Windows 安装流程最后一步必失败。(i) **提取质量评测**:`tests/fixtures/extraction_eval_v1/`（6 份显式合成语料 + expected.json 26 期望事实/15 实质片段）+ `tools/eval_extraction.py`(offline/cloud 两模式，api_key 三道脱敏防线）;offline 基线 `docs/testing/results/extraction-eval-offline-20260808.json`:fact_recall 0.7692、verbatim_retention 0.6667、编造丢弃 0;cloud 模式无凭据记 not_executed。(j) **品牌改名**：用户面 Noetide → sayhi（谐音"识海");README 重写（名字的故事、mac/linux 启动、英文完整版）；构建产物名 `sayhi-beta-vX.Y.Z-win64.zip` / `sayhi-X.Y.Z-src.tar.gz`;portable .cmd 改名 `sayhi *.cmd`;webui 标题、MCP serverInfo name、initialize instructions 同步；代码标识符（包名 `noetide_micro`、CLI、schema id、`noetide://` URI、`X-Noetide-Capability` 头、数据目录 `~/.noetide`）保持不变，避免测试资产哈希绑定连锁 rebind。新增测试 4（embedding 3 + 并行 1)，全量回归 529 OK 0 skipped,26 validator 全 exit 0。
86. cloud 提取评测 + 第二轮真人模拟 + 两个测试驱动修复 + 雷军语料入库（2026-08-09）：(a) **cloud 提取评测**:`tools/eval_extraction.py --mode cloud`(Kimi `kimi-for-coding` 真实 API,`NOETIDE_EVAL_API_KEY` 环境变量传入，报告三道脱敏）——`docs/testing/results/extraction-eval-cloud-kimi-20260809.json`:fact_recall 0.8462(22/26， offline 基线 0.7692)、verbatim_retention 0.6667(10/15)、6/6 语料 parse 成功、编造证据丢弃符合预期。(b) **第二轮 ces 真人模拟**（新 Kimi key，环境 gitignore 不入库）：设置云端模型（key 不明文回显）→ 10/10 语料导入 → 云端并行分析 10/10 完成、36 候选、3 份红线语料被红线门拒发（设计行为）→ 人工审候选确认 31/拒绝 5 → 问识海：命中已确认记忆作答（8 条证据），"星座/血型"类无证据问题诚实 no_coverage → 备份加密创建 + 正确 key 恢复 byte_identical、19 表行数全一致，错误 key fail-closed。(c) **修复 1：并行分析 sqlite 竞态**（本轮实测复现：cloud 并行 3 路同时 `_audit` 读改序号撞主键 IntegrityError / 懒游标迭代与他线程写入交错读 None 行 TypeError，首轮 10 份全灭）——`store.py` `_LockedConnection.execute` 改为锁内物化 `_LockedCursor`（fetchone/fetchall/迭代/rowcount/description 语义不变）;`cloud_model.py` `_audit` 序号分配+写入包进 `store.transaction()` 原子化；新增 `test_cloud_mode_parallel_authorize_and_audit_are_race_free` 回归。(d) **修复 2：备份恢复必失败**（实测复现：`restored/` 父目录不存在 → `write_bytes` OSError 被兜底误报 "key mismatch or corrupted backup"，正确 key 首次恢复必失败）——`pack_backup.py restore_backup` 预建目标父目录；`test_product_app` 增加恢复成功 + 错误 key 拒绝断言。(e) **雷军语料入库**:`tests/fixtures/leijun-corpus/`（全 10 文件，公众人物公开事实 + 3 份显著标注虚构文件；经项目所有者明确决定，不绑定任何 suite/oracle),`tests/fixtures/README.md` 新增"演示/评测语料"类目规则，hash 绑定 fixture 的合成数据规则不变。修复后全量回归 530 OK 0 skipped(529 + 竞态回归 1),26 validator 全 exit 0。**注意：已发布的 v0.3.4-beta 包含上述两个缺陷（cloud 并行分析必崩、首次恢复必败），建议尽快发 v0.3.5-beta 修复版。**

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
| Y2-S5 定向测试 | TASK-001/002：unit 8/8 passed（`mcp_runtime` + `y2s5_testing_adapter`） |
| Y2-S5 contract（adapter） | 10/10 passed |
| Y2-S5 官方 suite | `docs/testing/results/y2s5-20260803.json`：同一次 run 10/10 passed/current，网络阻断、stdlib only；manifest 已绑定；全量回归 480 OK 0 skip；26 个 suite validator 全 PASSED |
| Y2-S5 Gate Review | `Y2_S5_MCP_RUNTIME_GATE_REVIEW_2026-08-03.md`：P0=0、P1=0 |
| 审核整改 rebind（2026-08-08） | 8 个 suite 重跑 official runner 并 rebind manifest：`b3-20260807.json` 8/8、`micro-20260807.json` 49/49、`a1-20260807.json` 35/35、`y2s1..y2s5-20260807.json` 各 10/10，均同一次 run passed/current；旧结果以 superseded 留痕 |
| 整改后裸跑回归（2026-08-08） | 无 adapter `unittest discover`：Ran 485，OK，skipped=209，errors=0（修复前 errors=2） |
| 整改后全量回归（2026-08-08，最终树） | `PYTHONPATH=src` + 21 adapter 环境变量 + `python -m unittest discover -s tests -t .`：exit 0，Ran 485 tests，OK，0 skipped |
| 整改后 validator 复扫（2026-08-08） | 26 个 suite validator 全部 exit 0；`validate_product_baseline.ps1` / `validate_spec_baseline.ps1` 均 exit 0 |
| 整改安全定点实测（2026-08-07） | 无 ACAO 头、恶意 Origin 403、非回环 Host 403、OPTIONS 501、非法 Content-Length 400、超大 body 413、`0.0.0.0` 无 token 拒绝启动 rc=2、NOBAK2 往返/错密钥/篡改/旧格式四项拒绝、remote_access token 组合、4 线程并发写无错误：全部符合预期（代理手写端到端脚本实测） |
| 提供商层定向测试（2026-08-08） | `test_product_providers.py` 17/17 OK：三种 provider 请求形状、api_key 防泄、红线拒绝无 grant 落账、解析器四类输入、docx 正常/损坏 |
| 问识海定向测试（2026-08-08） | `test_product_ask.py` 6/6 OK：带证据回答、无证据诚实拒绝、零写入三重快照对比、Derived-only 拒绝、路由冒烟 |
| 第二波后全量回归（2026-08-08，最终树） | `PYTHONPATH=src` + 21 adapter 环境变量 + `python -m unittest discover -s tests -t .`：exit 0，**Ran 511 tests，OK，0 skipped**（485 + providers 17 + ask 6 + c1 持久化 3） |
| 第二波后 validator 复扫（2026-08-08） | 26 个 suite validator 全部 exit 0；`validate_product_baseline.ps1` / `validate_spec_baseline.ps1` 均 exit 0 |
| C4 官方 suite（Change Control，2026-08-08） | `docs/testing/results/c4-20260808.json`：同一次 run 10/10 passed/current，网络阻断、stdlib only；oracle 改 `revisions_added` 精确锁定（fixture 未动）；manifest 已 rebind；`c4-20260726.json` 转 superseded；`validate_c4_suite.py` exit 0 |
| C5 官方 suite（Change Control，2026-08-08） | `docs/testing/results/c5-20260808.json`：同一次 run 10/10 passed/current；oracle C5-005 encryption_label 同步 `nobak2_pbkdf2_hmac_v1`（fixture 未动）；manifest 已 rebind；`c5-20260726.json` 转 superseded；`validate_c5_suite.py` exit 0 |
| C1 官方 suite（Change Control，2026-08-08） | `docs/testing/results/c1-20260808.json`：同一次 run 7/7 passed/current；`test_c1_changesets.py` 新增 3 个 decision 持久化测试；fixture/oracle 未动；manifest 已 rebind；`c1-release-8556eea-20260719.json` 转 superseded；`validate_c1_suite.py` exit 0 |
| Change Control 后回归（2026-08-08） | `PYTHONPATH=src` + 21 adapter 环境变量 + `python -m unittest discover -s tests -t .`：exit 0，Ran 505 tests，OK，0 skipped（505 含并行任务新增的产品 provider 测试；首跑 exit=1 发生在并行任务编辑 product.py 中间态，其树稳定后复跑通过，非本次 c1/c4/c5 变更引起） |
| Change Control 后 validator 复扫（2026-08-08） | 26 个 suite validator 全部 exit 0 |
| 真人模拟测试（2026-08-08） | 7 轮端到端实测（真实 Kimi API + 10 份用户语料，`ces/` 独立数据目录）：10/10 导入、54 候选、确认 48/拒绝 6、红线门拦截敏感记录、反编造门丢弃 2 条假证据、备份恢复 42/42 保真、3 并发 MCP Agent 零冲突；报告 `ces/测试报告-2026-08-08.md`（未入库） |
| 模拟测试修复后全量回归（2026-08-08，最终树） | `PYTHONPATH=src` + 21 adapter 环境变量 + `python -m unittest discover -s tests -t .`：exit 0，**Ran 513 tests，OK，0 skipped**（511 + ask 新增 2 回归用例）；`test_product_ask.py` 8/8、`test_product_providers.py` 17/17、`test_product_app.py` 5/5 |
| v0.3.2-beta 发布核验（2026-08-08） | GitHub API 附件 digest：zip = `sha256:c89165a6abc7ece2f4151919d569ae39582334bb8f3e7b578cdf7cbeb29048b1`、SHA256SUMS = `sha256:47a602ad11b69fd05686b8014fc4ba57787650338d563fc3e600b8b820859ad8`，与本地 `dist/` 复核一致；发布包从 tag `v0.3.2-beta` 构建；smoke 实测：product-init exit 0、/api/health 200、/api/ask 空库诚实 no_coverage、Web UI 200、恶意 Origin 403；prerelease 已发布，tag 已推送远端 |
| Agent 记忆中枢定向测试（2026-08-08） | `test_product_mcp_agent.py` 11/11 OK：initialize/tools/list/unknown method、resources list+read、legacy 形状兼容、ask_memory 回答+no_coverage+红线过滤+限定令牌+空问题、propose 落队列+幂等+确认成正式记忆、后台分析进度+already_running；`test_product_providers.py` 提示词保实质回归 1/1 |
| Agent 记忆中枢后全量回归（2026-08-08，最终树） | `PYTHONPATH=src` + 21 adapter 环境变量 + `python -m unittest discover -s tests -t .`：exit 0，**Ran 525 tests，OK，0 skipped**（513 + mcp_agent 11 + 提示词 1） |
| v0.3.3-beta 发布核验（2026-08-08） | GitHub API 附件 digest：zip = `sha256:2d1d2a30fbc2d9a86033c5c6c7d103c5ed12b0dfe7f6ef893e32ba68ca97d27c`、SHA256SUMS = `sha256:ee4d492121f45d968e7bdec8e98e4e363e87aa844c7a8ded4ab057c31798b89c`，与本地 `dist/` 复核一致；发布包从 tag `v0.3.3-beta` 构建；smoke 实测：product-init exit 0、/api/health 200、异步分析 started/done 1/1/候选 1、候选确认 confirmed、标准 MCP initialize（serverInfo noetide 0.3.3）/tools/list 五工具/tools/call ask_memory 正常应答、恶意 Origin 403、Web UI 200；prerelease 已发布，tag 已推送远端 |
| C1 官方 suite（Change Control，2026-08-08） | `docs/testing/results/c1-revalloc-20260808.json`：同一次 run 7/7 passed/current；`changesets.py` revision 改事务内动态分配（fixture 下数值不变）；fixture/oracle/测试模块未动；manifest 已 rebind；`c1-20260808.json` 转 superseded；`validate_c1_suite.py` exit 0 |
| Change Control 清零后复扫（2026-08-08） | 26 个 suite validator 全部 exit 0；`PYTHONPATH=src` + 21 adapter 全量回归 exit 0，Ran 525 tests，OK，0 skipped |
| 真实 MCP 客户端验证（2026-08-08） | 官方 TS SDK 1.30.0 StreamableHTTP 7/7 PASS、Python mcp 2.0.0 6/6 PASS（ initialize/tools/list/ask_memory 命中已确认记忆/resources list+read/未知工具 -32601/ping）；三处规范偏差（notification 202、版本协商、GET/DELETE 405）已修复；验证脚本与 venv 在 gitignore 的 tmp/ 下 |
| Windows setup P0 复现与修复（2026-08-08） | 实测复现：`product-init` 后 `python -m noetide_micro status` 对产库报 SeedConflictError exit 1 → `setup-noetide.ps1` 末步必失败；修复为 NoetideApp 健康检查 |
| 提取评测 offline 基线（2026-08-08） | `tools/eval_extraction.py --mode offline` exit 0，`docs/testing/results/extraction-eval-offline-20260808.json`:fact_recall 0.7692(20/26)、verbatim_retention 0.6667(10/15)、fabricated_dropped 0;cloud 模式无凭据 not_executed |
| 九项优化后全量回归（2026-08-08，最终树） | `PYTHONPATH=src` + 21 adapter 环境变量 + `python -m unittest discover -s tests -t .`：exit 0，**Ran 529 tests，OK，0 skipped**（525 + embedding 3 + 并行 1）；26 个 suite validator 全部 exit 0 |
| v0.3.4-beta 发布核验（2026-08-09） | GitHub API 附件 digest：zip = `sha256:d94b96cade4534aa2ba157e862df49505b007166ca231a223c2a57c431641c70`、src tar = `sha256:0c3b46fbb553833540946d5cd424d7490566317f62ef7238fb91c4eee9ed7f5d`，与本地 `dist/` 复核一致；发布包从 tag `v0.3.4-beta` 构建；smoke 14/14 通过：`setup-noetide.ps1 -Yes` exit 0（P0 修复实测确认）、/api/health 200、中文文本导入、异步分析 started→done 无错误、9 候选提议 + 确认 confirmed、标准 MCP initialize（serverInfo sayhi 0.3.4）/tools/list 五工具/tools/call ask_memory 正常、恶意 Origin 403、Web UI 200；prerelease 已发布，tag 已推送远端 |
| cloud 提取评测（2026-08-09） | `tools/eval_extraction.py --mode cloud`（Kimi `kimi-for-coding` 真实 API，key 经 `NOETIDE_EVAL_API_KEY` 环境变量、报告三道脱敏）exit 0：`docs/testing/results/extraction-eval-cloud-kimi-20260809.json`，fact_recall **0.8462**（22/26）、verbatim_retention 0.6667（10/15）、6/6 parse 成功、编造证据丢弃符合预期 |
| 第二轮真人模拟测试（2026-08-09） | 新 Kimi key + 10 份雷军语料（`ces/` gitignore）：云端设置 key 不明文回显、10/10 导入、并行分析 10/10 完成 36 候选 3 红线拒发、确认 31/拒绝 5、问识海带证据作答 + 无证据诚实 no_coverage、备份恢复 byte_identical 19 表一致、错误 key 拒绝；实测发现并修复并行竞态与恢复父目录两个缺陷（§3 第 86 条） |
| 二轮模拟修复后全量回归（2026-08-09，最终树） | `PYTHONPATH=src` + 21 adapter 环境变量（模块名形式）+ `python -m unittest discover -s tests -t .`：exit 0，**Ran 530 tests，OK，0 skipped**（529 + 并行竞态回归 1；备份恢复断言并入既有用例）；26 个 suite validator 全部 exit 0 |


完整命令、环境、哈希和限制见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。静态校验不被表述为业务测试通过；历史失败运行结果仍保留在 `docs/testing/results/`。

## 5. 风险与边界

- 当前完整产品已支持用户自己的真实资料；仓库仍不得新增真实个人姓名、地址、组织、电话、邮箱、凭据、债务、健康或亲密关系资料，demo/测试只使用显式合成数据。
- 完整产品当前以本地 Web/HTTP 服务形态交付：支持 REST API、MCP、本地/云端模型、导出备份和远程令牌访问；不含 A2A、多租户账户体系、连接器、自动同步或托管云控制台。
- portable 包未代码签名、Windows-only、无自动更新；用户部署到云时需自行负责 HTTPS 网关、域名、防火墙和多用户安全。

## 6. 下一步唯一建议动作

**v0.3.4-beta 已发布；cloud 提取评测（recall 0.8462）与第二轮真人模拟已完成，实测修复并行分析 sqlite 竞态与备份恢复父目录两个真实缺陷（全量回归 530 OK）。注意：v0.3.4-beta 发布包含这两个缺陷，下一步唯一建议动作：发 v0.3.5-beta 修复版（版本号升 0.3.5、构建、smoke 重点复测 cloud 并行分析与备份恢复、发布核验）；mac/linux 真机实测待补；持续关注公开后的外部反馈。**
