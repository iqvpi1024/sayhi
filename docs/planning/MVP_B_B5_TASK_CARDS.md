# B5 Task Cards

| Card | Plan Task | 范围红线 |
|---|---|---|
| `B5-TASK-001` | bilingual.py 实现 | 只写 `bilingual.py`；不动 store/schema；原文只走 append_source；翻译只进 ledger |
| `B5-TASK-002` | Testing Adapter | 只写 `b5_testing_adapter.py`；fixture/oracle/scenarios 一律不改 |
| `B5-TASK-003` | Official Runner + 回归 | 不改实现迎合测试；失败必须回修实现或走 Change Control |
| `B5-TASK-004` | Gate Review + Recovery | 只在 P0/P1=0 后创建 tag `b5-multilingual-rp-20260725` |
