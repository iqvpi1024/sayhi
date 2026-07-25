# Implementation Plan：C5 Context Pack & Encrypted Backup

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-C-C5-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-C-PACK-001` |
| Decision | `DEC-MVP-C-PACK-001` |
| Contract | `SPEC-C5-PACK-001` v0.1 |
| ADR / Architecture | `ADR-0017` / `ARCH-C5-PACK-001`（`C5_PACK_BACKUP_ARCHITECTURE.md`） |
| Suite | `tests/c5_suite_manifest.json`，materialized |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型；零 schema 变更（ADR-0017）。
- 导出/备份/校验 read-only；恢复只写新目标库；删除回执纯函数。
- 加密构造恒定标注 `stdlib_deterministic_v1`，禁止宣称生产安全。
- 每个 Task 结束运行定向检查；只有 `C5-TASK-003` 可以运行 C5 official runner。
- 固定 synthetic profile `c5_pack_backup_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `C5-TASK-001` | `pack_backup.py` 六入口（render/export/verify/backup/restore/delete-receipt） | §2/§3/§5/§6、`C5-001..009` | 六入口语义与合同一致；定向窄测试通过 | `completed`；定向 5/5 passed，见 `c5-task001-20260726.json` |
| `C5-TASK-002` | `c5_testing_adapter.py` 与 C5 contract 集成 | §7/§8、`C5-001..010` | adapter 完整实现 protocol；fixture/oracle 不被修改；C5-010 横切通过 | `completed`；contract 10/10 passed（adapter），oracle 两处呈现修正（见 `c5-task002-20260726.json` notes） |
| `C5-TASK-003` | C5 official runner、existing regression 与 immutable result | §7/§8 | C5 10/10 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `completed`；`c5-20260726.json` 10/10 current/passed，20 validators PASSED，回归 392 OK 0 skip，见 `c5-task003-20260726.json` |
| `C5-TASK-004` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `completed`；Gate Review `C5_PACK_GATE_REVIEW_2026-07-26.md` P0=0/P1=0，recovery tag `c5-context-pack-backup-rp-20260726` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `C5-TASK-001` | `src/noetide_micro/pack_backup.py`、窄范围 tests |
| `C5-TASK-002` | `src/noetide_micro/c5_testing_adapter.py` |
| `C5-TASK-003` | C5 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `C5-TASK-004` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
C5-TASK-001 -> C5-TASK-002 -> C5-TASK-003 -> C5-TASK-004
```

任何 Task 若需要改变 C5 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`C5-TASK-003` 另外执行 C5 official runner、既有 suite validator、全量 semantic regression、privacy boundary scan。未执行 C5 runner 前，C5 只能保持 `not_executed`。
