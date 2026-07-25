# 项目状态

## 1. 恢复入口

每次任务按 `AGENTS.md` 的顺序恢复。当前产品语义以 `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的 `PRDv05.md` v0.5 为准；历史 PRD、SPEC、结果和 tag 保留审计价值，不得覆盖动态状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 当前产品基线 | `PRDv05.md` v0.5 Approved，canonical LF SHA-256 `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前公开发布 | `PUBLIC-PREVIEW-D1-001` 已发布 |
| 当前工作切片 | `SLICE-MVP-A-HARDENING-001` |
| 当前阶段 | `task_003_completed` |
| 当前公开版本 | `v0.1.3-synthetic-preview` GitHub prerelease |
| tag / commit | annotated tag `v0.1.3-synthetic-preview` -> `c340eac939cdbc094d6ec8da7f4e710d879cf1c1` |
| GitHub Release | `https://github.com/iqvpi1024/sayhi/releases/tag/v0.1.3-synthetic-preview` |
| 交付级别 | 已发布 D1 Windows-first 合成预览；D2/D3 未完成 |
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


完整命令、环境、哈希和限制见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。静态校验不被表述为业务测试通过；历史失败运行结果仍保留在 `docs/testing/results/`。

## 5. 风险与边界

- 当前发布只允许固定合成 demo 数据。不得输入、导入、提交或推断真实个人资料、凭据或工作区外数据。
- 该版本不是完整 PRD 产品，不实现真实导入、通用 NLP、权限/MCP runtime、同步、连接器、分享、签名安装包、升级或真实数据生产合同。
- D2/D3 所需签名、升级/卸载、真实数据安全合同和普通用户生产支持仍未完成；不得因 portable ZIP 存在而宣称已完成。

## 6. 下一步唯一建议动作

**执行 A6-TASK-004：`a6_testing_adapter.py` 完整实现 adapter protocol，`NOETIDE_A6_ADAPTER=noetide_micro.a6_testing_adapter` 下 contract 21/21 passed。***