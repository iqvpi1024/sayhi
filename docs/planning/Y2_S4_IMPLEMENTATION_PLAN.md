# Y2-S4 云端模型可选后端 Implementation Plan

## 元信息

- Plan ID: `PLAN-Y2-S4-IMPL-001`
- Date: 2026-08-03
- Slice: `SLICE-Y2-S4-CLOUD-MODEL-001`
- Contract: `SPEC-Y2S4-CLOUD-MODEL-001` v0.1
- ADR: `ADR-0023`
- Suite: `y2s4_cloud_model_v1`（materialized，未执行）

## 1. 任务

1. Y2S4-TASK-001：`src/noetide_micro/cloud_model.py`（CloudGate、CloudFixtureBackend、CloudHttpBackend、CloudModelCurator、stdlib 静态扫描）；定向 unit 测试。
2. Y2S4-TASK-002：`src/noetide_micro/y2s4_testing_adapter.py`，完整 adapter protocol，contract 10/10 passed；fixture/oracle 不修改。
3. Y2S4-TASK-003：official runner 同一次 run 10/10 passed/current；manifest 绑定；全量 regression 0 skip；全部 suite validator PASSED。
4. Y2S4-TASK-004：Gate Review（P0=0/P1=0）+ recovery tag `y2s4-cloud-model-rp-20260803` 推送，PROJECT_STATE/HANDOFF/矩阵状态同步。

## 2. 规则

- 每轮只执行一张任务卡；不得修改 fixture/oracle 迎合实现；oracle 修正必须单独说明并同步 manifest hash。
- 任何 `not_executed` 不得记为通过；official runner 属 TASK-003，提前执行不算数。
- 网络仅允许本机回环测试 stub；云端 HTTP 后端默认要求 https，`allow_loopback=True` 只能由合成测试传入。
- 云端模块只写 Ledger `cloud_audit`；不得写 Canonical、不得新增表、不得使用 wall-clock。
