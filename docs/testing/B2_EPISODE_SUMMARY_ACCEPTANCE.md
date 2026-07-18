# B2 Episode 与分层摘要验收合同

## 1. 适用范围

本合同只适用于 `SLICE-MVP-B-EPISODE-SUMMARY-001` 与 `SPEC-B2-EPISODE-SUMMARY-001`。所有 case 使用固定合成数据、固定 UTC clock、离线执行；不读取工作区外数据。

## 2. Required 场景

| ID | Given | When | Then |
|---|---|---|---|
| `B2-001` | 有直接合成 Source/Entity/time refs 的 Episode candidate | 用户确认并发布 | ChangeSet 原子发布 Episode，revision 增加且 direct locator 保留 |
| `B2-002` | candidate 缺 Source/Entity/time ref | 尝试确认发布 | failed，无 Episode、无新 revision |
| `B2-003` | 已发布 Episode | 生成 day/phase summary | 两个 Derived projection fresh，dependency/revision 对齐 |
| `B2-004` | summary 依赖已发布 Episode | 补偿撤销 Episode | 旧 summary stale，重建不包含已撤销 Episode |
| `B2-005` | 已生成 Derived summary | 删除 Derived 后 rebuild | 只从 Canonical/Episode/Source 恢复等价 summary |
| `B2-006` | summary/projection id | 用作 evidence 或 ChangeSet trigger | 拒绝 `derived_evidence_forbidden`，Canonical 不变 |
| `B2-007` | 已发布 Episode | 注入 summary rebuild 写入失败 | Canonical 可读，summary stale/unavailable，失败审计可读 |
| `B2-008` | 非合成输入或错误 profile | 尝试创建 candidate | 拒绝，且无 Source/Episode/summary/revision 写入 |

## 3. 结果状态

```yaml
suite_id: b2_episode_summary_v1
suite_defined: true
suite_materialized: true
suite_executed: false
suite_passed: false
```

在实现与实际 runner 同时通过前，任何文档不得将以上场景称为业务测试通过。

## 4. 官方执行入口

```powershell
$env:PYTHONPATH = "$PWD/src"
python -m tests.runner.run_b2_suite --adapter noetide_micro.b2_testing_adapter --output docs/testing/results/b2-run.json
```

该命令只在 adapter 实现完成后执行；输出路径必须为新文件，result 不可覆盖。
