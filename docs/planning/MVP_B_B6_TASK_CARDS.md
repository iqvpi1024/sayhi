# B6 Task Cards

| Card | Plan Task | 范围红线 |
|---|---|---|
| `B6-TASK-001` | shadow_migration.py | 原始库只读；影子文件级副本；变换只改影子；不动 store/schema |
| `B6-TASK-002` | disambiguation.py | 纯函数计数；候选不自动合并；传播历史 append-only |
| `B6-TASK-003` | Testing Adapter | 只写 `b6_testing_adapter.py`；fixture/oracle/scenarios 一律不改 |
| `B6-TASK-004` | Official Runner + 回归 | 不改实现迎合测试；失败必须回修实现或走 Change Control |
| `B6-TASK-005` | Gate Review + Recovery | 只在 P0/P1=0 后创建 tag `b6-shadow-migration-rp-20260725` |
