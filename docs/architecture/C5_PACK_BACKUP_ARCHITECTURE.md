# C5 Context Pack & Encrypted Backup 架构说明

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-C-PACK-001` |
| Contract | `SPEC-C5-PACK-001` v0.1 |
| ADR | `ADR-0017` |
| 日期 | 2026-07-26 |

## 1. 模块边界

```text
tests/fixtures/c5_pack_backup_v1/fixture.json   固定合成 profile（store 种子 + 密钥 + 删除策略）
tests/fixtures/c5_pack_backup_v1/oracles.json   C5-001..010 精确期望
src/noetide_micro/c5_testing_adapter.py         fixture 播种 + scenario 分发 + 快照
src/noetide_micro/pack_backup.py                render/export/verify/backup/restore/delete-receipt 六入口
```

- 复用 `store.portability_snapshot()` 与 `portability.py` 的 manifest/checksum/_safe_relative 机制。
- 所有导出/备份/校验 read-only；恢复只写新目标库；删除回执为纯函数 + 成分执行器。

## 2. 数据流

```text
store --snapshot--> render markdown/*.md + json + manifest + checksums（read-only）
pack --verify--> validated | rejected_*（fail closed，零写入）
db --create_backup(key)--> .nobak 密文 + backup_receipt（read-only on store）
.nobak --restore_backup(key)--> 新目标库 + restore_receipt（byte_identical 校验）
store --build_deletion_receipt--> 八成分回执（deleted|pending_expiry|out_of_control|retained|failed）
```

## 3. 不变量落点

| 不变量 | 落点 |
|---|---|
| C5-INV-001 渲染确定性 | 排序渲染 + 字节比对 oracle |
| C5-INV-002 校验 fail closed | manifest 全集校验 + 未知文件检测 + _safe_relative |
| C5-INV-003 加密语义 | 密文比对 + 正确/错误密钥正反测试 |
| C5-INV-004 删除诚实性 | 八成分回执 + 注入失败成分 |
| C5-INV-005 read-only/不覆盖 | store digest 断言 + 目标存在拒绝 |
| C5-INV-006 只含合成数据 | fixture 固定 + export_scope 恒定 |
| C5-INV-007 fail closed | profile 外输入 rejected |

## 4. 与其他切片关系

- 复用已 verified 的 Context Pack Portability（portability.py）机制；不重建其闭环。
- 与 C3 Derived 语义一致：Markdown 是解释性副本，不作证据。
- 生产加密替换为 D2/D3 决策项；本切片 receipt 恒定标注 `stdlib_deterministic_v1`。
