# Y2-S1 文件夹导入架构视图

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-Y2S1-FOLDER-IMPORT-001` |
| Date | 2026-08-01 |
| Slice | `SLICE-Y2-S1-FOLDER-IMPORT-001` |
| ADR | `ADR-0020` |

## 1. 组件

```text
虚拟/真实文件夹树
  -> FolderImporter（folder_import.py）
       枚举（扩展名白名单）-> 路径安全 resolve 复检 -> UTF-8 校验
       -> 内容寻址 source_id -> SemanticStore.append_source（唯一写入口）
  -> ImportReport（Derived 返回值，不落库）
FolderWatcher（folder_import.py）
  -> 单次显式 poll：从 store 重建 seen 哈希集 -> 只导入新增 -> 报告
```

## 2. 边界

- 写面：仅 `source_records` + `append_receipts`（经既有 `append_source`）；无新表、无 Canonical 写路径。
- 读面：`seeded_source`（按 source_id 查重）、按 source_system 列出哈希（watcher）。
- 失败面：路径不安全/编码失败零写入；存储失败仅当前文件 rejected；中断按文件原子。
- 测试面：`y2s1_testing_adapter.py` 在临时目录物化虚拟文件夹树，注入 fixture clock 与 fail_at_index。

## 3. 数据流

文件字节 -> sha256 -> source_id/receipt -> SQLite；报告只读回流。Canonical、revision、Core View 不在数据流上。
