# Implementation Plan：B5 Multilingual 原文与翻译对照

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-B-B5-IMPL-001` |
| Status | `Approved` |
| Slice | `SLICE-MVP-B-MULTILINGUAL-001` |
| Decision | `DEC-MVP-B-MULTILINGUAL-001` |
| Contract | `SPEC-B5-MULTILINGUAL-001` v0.1 |
| ADR / Architecture | `ADR-0012` / `ARCH-B5-MULTILINGUAL-001` |
| Suite | `tests/b5_suite_manifest.json`，materialized，not executed |

## 1. 施工原则

- 只使用 Python 3.12 标准库与现有 SQLite store；不安装依赖、不引入 ORM/trigger/网络/模型/翻译引擎。
- 原文只经既有 `append_source` 路径；翻译记录只存 ledger（record_type=`translation_record`）；Source Vault 与 Canonical 无任何翻译写入路径。
- 对照视图查询时派生、不持久化、不作证据；覆盖原文的任何请求 fail closed。
- 每个 Task 结束运行定向检查；只有 `B5-TASK-004` 可以运行 B5 official runner。
- 固定 synthetic profile `b5_multilingual_v1` 外的所有输入 fail closed；不触碰真实数据和用户未跟踪目录。

## 2. 任务与追踪

| Task | 交付物 | Contract / Test | 完成条件 | 状态 |
|---|---|---|---|---|
| `B5-TASK-001` | `bilingual.py`：对照记录追加/修订、对照视图、orphan 检测、覆盖拒绝面 | §2..§6、`B5-001..007` | 分离存储；paired/unavailable/orphan 正确；覆盖拒绝；修订历史保留 | `completed`；定向 9/9 passed，见 `b5-task001-20260725.json` |
| `B5-TASK-002` | `b5_testing_adapter.py` 与 B5 contract 集成 | §7/§8、`B5-001..008` | adapter 完整实现 protocol；fixture/oracle 不被修改；B5-008 横切通过 | `pending` |
| `B5-TASK-003` | B5 official runner、existing regression 与 immutable result | §7/§8 | B5 8/8 同一次 run passed；既有 suite 无回归；manifest 正确绑定 result | `pending` |
| `B5-TASK-004` | Gate Review、状态/追踪、Recovery Point | Process 流程 | P0/P1=0、验证记录完整、tag 仅在审查通过后创建 | `pending` |

## 3. 允许文件边界

| Task | 允许主要实现文件 |
|---|---|
| `B5-TASK-001` | `src/noetide_micro/bilingual.py`、窄范围 tests |
| `B5-TASK-002` | `src/noetide_micro/b5_testing_adapter.py` |
| `B5-TASK-003` | B5 manifest/result、验证记录；不修改 oracle 迎合 implementation |
| `B5-TASK-004` | review、状态、trace、release/recovery record |

## 4. 固定顺序

```text
B5-TASK-001 -> B5-TASK-002 -> B5-TASK-003 -> B5-TASK-004
```

任何 Task 若需要改变 B5 contract、fixture/oracle 的产品语义，停止并回到 Change Control；不得继续下一个 Task。

## 5. 验证与完成定义

每个 Task 至少执行：Python import/syntax、定向测试、受影响 validator、`git diff --check`。`B5-TASK-003` 另外执行 B5 official runner、既有 suite validator、全量 semantic regression、privacy boundary scan。未执行 B5 runner 前，B5 只能保持 `not_executed`。
