# B4 Task Cards

| Card | Plan Task | 范围红线 |
|---|---|---|
| `B4-TASK-001` | 增量对账检测 | 只写 `reconciliation.py` 增量部分；不动 store/schema；不实现深度对账与 diff |
| `B4-TASK-002` | 深度对账重建比较 | 只扩展 `reconciliation.py` 深度部分；重建必须走生产 projector + 隔离临时 store |
| `B4-TASK-003` | Semantic Diff | 只写 `semantic_diff.py`；不缓存、不持久化、不触发任何写入 |
| `B4-TASK-004` | Testing Adapter | 只写 `b4_testing_adapter.py`；fixture/oracle/scenarios 一律不改 |
| `B4-TASK-005` | Official Runner + 回归 | 不改实现迎合测试；失败必须回修实现或走 Change Control |
| `B4-TASK-006` | Gate Review + Recovery | 只在 P0/P1=0 后创建 tag `b4-reconciliation-rp-20260725` |
