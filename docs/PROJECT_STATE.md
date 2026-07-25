# 项目状态

## 1. 恢复入口

每次任务按 `AGENTS.md` 的顺序恢复。当前产品语义以 `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的 `PRDv05.md` v0.5 为准；历史 PRD、SPEC、结果和 tag 保留审计价值，不得覆盖动态状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 当前产品基线 | `PRDv05.md` v0.5 Approved，canonical LF SHA-256 `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前公开发布 | `PUBLIC-PREVIEW-D1-001` 已发布 |
| 当前工作切片 | `SLICE-MVP-A-APP-SHELL-001` |
| 当前阶段 | `implementation_planned` |
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


完整命令、环境、哈希和限制见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。静态校验不被表述为业务测试通过；历史失败运行结果仍保留在 `docs/testing/results/`。

## 5. 风险与边界

- 当前发布只允许固定合成 demo 数据。不得输入、导入、提交或推断真实个人资料、凭据或工作区外数据。
- 该版本不是完整 PRD 产品，不实现真实导入、通用 NLP、权限/MCP runtime、同步、连接器、分享、签名安装包、升级或真实数据生产合同。
- D2/D3 所需签名、升级/卸载、真实数据安全合同和普通用户生产支持仍未完成；不得因 portable ZIP 存在而宣称已完成。

## 6. 下一步唯一建议动作

**执行 A5-TASK-005（Gate Review、状态/追踪同步、recovery tag `a5-app-shell-rp-20260725` 创建并推送）。**