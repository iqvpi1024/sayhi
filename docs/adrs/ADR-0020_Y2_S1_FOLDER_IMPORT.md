# ADR-0020：Y2-S1 文件夹导入实现方案

| 字段 | 值 |
|---|---|
| ADR ID | `ADR-0020` |
| Date | 2026-08-01 |
| Status | `Accepted` |
| Slice | `SLICE-Y2-S1-FOLDER-IMPORT-001` |
| Contract | `SPEC-Y2S1-FOLDER-IMPORT-001` v0.1 |

## 1. 决策

1. 新模块 `src/noetide_micro/folder_import.py`：`FolderImporter`（批量导入）与 `FolderWatcher`（单次 poll 游标监视），纯 stdlib（`pathlib`/`hashlib`/`json`/`sqlite3`），无第三方依赖。
2. 复用 `SemanticStore.append_source` 作为唯一写入口；不新增 Canonical 写路径；批量报告 `ImportReport` 只作为返回值与 Derived 运行产物，不落库。
3. `source_id = "src_folder_" + sha256(content)[:16]`：内容寻址，天然幂等；重复内容命中既有 source_id 时只写 duplicate receipt 引用，不写新 Source（receipt 也不重复写：duplicate 不产生新行，由报告引用既有 receipt_id）。
4. 路径安全：逻辑根用 `Path.resolve()` 后做 `relative_to` 检查；符号链接一律 `resolve()` 后复检；逃逸即 rejected，不读取内容。
5. 中断恢复：逐文件事务（`append_source` 自身事务）；中断时已处理文件保持 stored，未处理文件无残留；重跑靠内容哈希幂等收敛。不引入导入日志表。
6. 游标：`FolderWatcher` 的 seen 集合直接从 store 中 `folder_importer_v1` 来源的 Source 哈希重建，不新增游标表；`last_poll_at` 只出现在报告里。
7. 时间：全部来自显式注入的 `now`（fixture clock）与文件 `stat().st_mtime`；代码内禁止 `datetime.now()`。

## 2. 备选方案与放弃理由

- 导入日志/游标表持久化：放弃。本切片可用内容哈希幂等收敛，新增表会扩大 schema 与对账面；后续若需要增量游标再立 ADR。
- OS 级 watcher（watchdog 类库）：放弃。引入第三方依赖且违反零依赖红线；显式 poll 已满足合同。
- 递归跟随符号链接：放弃。逃逸风险大于便利；一律 resolve 后复检。
- 每批一个总事务：放弃。中断会产生大批量回滚语义，与 append-only 语义冲突；逐文件事务更符合"无半完成状态"的 per-file 定义。

## 3. 代价与回退

- 代价：重复内容不产生独立 receipt 行，报告需自行记录 duplicate 指向；大文件夹全量哈希有 IO 成本（本切片固定合成规模，不构成问题）。
- 回退：删除 `folder_import.py` 即可完全移除本切片；不写 Canonical 使回退无数据迁移负担。

## 4. 环境

Windows 11 10.0.26200；CPython 3.12.8；SQLite（ADR-0001 PRAGMA 不变）；stdlib only；网络由 runner 阻断。
