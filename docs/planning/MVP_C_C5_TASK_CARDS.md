# C5 Context Pack & Encrypted Backup Task Cards

Plan：`PLAN-MVP-C-C5-IMPL-001`；Contract：`SPEC-C5-PACK-001` v0.1；ADR：`ADR-0017`。

## C5-TASK-001 pack_backup 模块

- 交付：`pack_backup.py` 六入口（render_markdown/export_markdown_pack/verify_pack/create_backup/restore_backup/build_deletion_receipt）。
- 合同：§2 字段、§3 状态机、§5 不变量、§6 失败语义；`stdlib_deterministic_v1` 标注。
- 验证：import/syntax、定向窄测试、`git diff --check`。

## C5-TASK-002 C5 testing adapter

- 交付：`c5_testing_adapter.py` 实现 `tests/runner/c5_pack_adapter_protocol.py`。
- 验证：`NOETIDE_C5_ADAPTER=noetide_micro.c5_testing_adapter python -m unittest tests.semantic.test_c5_pack_contract` 10/10。

## C5-TASK-003 official runner 与绑定

- 交付：`python -m tests.runner.run_c5_suite --adapter noetide_micro.c5_testing_adapter --output docs/testing/results/c5-20260726.json`；manifest 绑定；全量回归与 20 validators。

## C5-TASK-004 Gate Review 与 Recovery Point

- 交付：Gate Review（P0/P1=0）、矩阵 §4.19 状态、PROJECT_STATE、CURRENT_HANDOFF、PRD hash 校验、recovery tag。
