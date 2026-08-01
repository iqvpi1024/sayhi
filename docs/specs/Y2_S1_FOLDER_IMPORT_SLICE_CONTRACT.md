# Y2-S1 真实文件夹文本导入切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-Y2S1-FOLDER-IMPORT-001` |
| 版本 | `0.1` |
| 状态 | `Approved for Y2-S1 slice` |
| 产品基线 | `PRDv06.md` v0.6 |
| 产品决定 | `DEC-Y2-S1-001` |
| 上游 | S1 v0.7、S7 v0.4、S9 v0.5 |
| 适用范围 | `SLICE-Y2-S1-FOLDER-IMPORT-001`，仅固定合成数据 |

## 1. 目标与非目标

目标：在一个固定合成文件夹树上证明——`.txt`/`.md` 批量导入全部进入 Source Vault（哈希、字节长度、来源时间、CoverageWindow、语言齐全）、幂等去重、路径安全 fail closed、批量中断无半完成状态且重跑收敛、单次 poll 轮询监视只导入新增文件、Canonical 零变化、报告确定性。

非目标：语义解释与候选生成（Y2-S2）、其余连接器、二进制/图片/PDF、OCR、递归符号链接跟随、OS 级文件事件、后台线程/守护进程、真实数据模式开放的单独宣告、多设备同步。

## 2. 对象与字段

### 2.1 FolderSource（导入产生的 Source，复用 S1 Source 对象）

```yaml
source_id: "src_folder_<sha256[:16]>"        # 由内容哈希派生，天然幂等
source_kind: folder_text_import
source_system: folder_importer_v1
inline_content: <UTF-8 文本>
content_hash: sha256(utf8 bytes)
byte_length: <字节数>
source_created_at: <文件修改时间，UTC ISO8601>
ingested_at: <fixture clock>
language: <fixture 声明，未声明则 "unknown">
source_timezone: "unknown"
locator_scheme: file_path_v1
locator: {root_ref: "<逻辑根>", relative_path: "<POSIX 风格相对路径>"}
coverage_window: {start: source_created_at, end: source_created_at, continuous: true, gaps: []}
policy_profile_ref: owner_intake_private_v1
sensitivity: private
compartments: [personal]
retention_state: active
```

### 2.2 ImportReceipt（终态 receipt，终态集合封闭）

```yaml
status_values: [stored, duplicate, rejected, skipped]
receipt_id: "receipt_<source_id 或 file_ref>"
failure: null | invalid_utf8 | path_outside_root | path_traversal | symlink_escape | unsupported_extension | storage_failure
actor: folder_importer_v1
```

- `stored`：新 Source 已写入。
- `duplicate`：内容哈希已存在；不写新 Source，receipt 指向既有 source_id。
- `rejected`：安全或编码失败；零写入。
- `skipped`：扩展名不在白名单；不视为错误，计入报告。

### 2.3 ImportReport（批量报告，Derived 运行产物，不作证据、不落 Canonical）

```yaml
report_id: "report_<run_seq>"
files_seen / stored / duplicate / rejected / skipped: <确定性计数>
receipts: [按 relative_path 字典序排列的 receipt 摘要]
started_at / finished_at: <fixture clock>
```

### 2.4 WatchCursor（轮询监视游标）

```yaml
cursor_id: watch_folder_v1
seen_hashes: [已导入内容哈希集合]
last_poll_at: <fixture clock>
```

单次 `poll()` 为显式调用：扫描 -> 与 seen_hashes 求差 -> 只导入新增 -> 更新游标。无后台线程、无定时器、无 OS 事件订阅。

## 3. 状态机

```text
文件枚举: scan -> filtered（扩展名白名单） -> validated（UTF-8） -> stored | duplicate
              \-> skipped（非白名单）     \-> rejected（编码失败）
路径检查: resolve -> in_root -> 继续
              \-> outside_root | traversal | symlink_escape -> rejected（零写入）
批量: run -> 部分完成（中断） -> 终态 receipts 仅覆盖已处理文件 -> rerun -> 收敛至与无中断一致
```

## 4. 时间、证据与权限

- 全部时间来自 fixture clock 与文件元数据；无 wall-clock。
- Source append 不产生事实证据；FolderSource 的 `review_status` 为 `unreviewed`。
- 权限字段保守初始化（`private`、`personal`），不实现权限 runtime。

## 5. 路径安全与失败降级

- 逻辑根之外的绝对路径、`..` 穿越、符号链接逃逸：fail closed `rejected`，零写入，继续处理其余文件。
- 存储层失败（sqlite 异常）：当前文件 `rejected(storage_failure)`，已写入文件不回滚（append-only 语义），报告如实区分。

## 6. 中断恢复语义

- 中断后：已处理文件各有终态 receipt，未处理文件无残留；不存在"半个 Source"。
- 重跑同一根目录：已导入内容哈希命中 duplicate，未导入的继续 stored；最终 Source 集合与一次无中断运行完全一致（INV-005）。

## 7. 验收场景

| 场景 | 内容 | 不变量 |
|---|---|---|
| Y2S1-001 | 批量导入 3 个有效文件：3 stored、source 字段齐全、报告计数正确 | INV-001/004/006 |
| Y2S1-002 | 每文件哈希、字节长度、来源时间、CoverageWindow、语言逐项核对 | INV-004 |
| Y2S1-003 | 重复内容不同文件名：duplicate receipt 指向既有 source_id，不重复存储 | INV-002 |
| Y2S1-004 | 重复扫描同一根：零新 Source、全部 duplicate | INV-002 |
| Y2S1-005 | 混入非白名单扩展名：skipped 计数正确，其余正常导入 | INV-004 |
| Y2S1-006 | 根外路径、`..` 穿越、符号链接逃逸：rejected 且零写入 | INV-003 |
| Y2S1-007 | 无效 UTF-8 文件：rejected(invalid_utf8)，其余正常 | INV-004 |
| Y2S1-008 | 注入中断后重跑：终态与无中断运行一致 | INV-005 |
| Y2S1-009 | 两次 poll：第一次导入新增，第二次零新增，游标只前进 | INV-002/004 |
| Y2S1-010 | 横切：Canonical digest、data_revision、Core View 不变；两次运行报告字节一致；profile 外 fail closed | INV-001/006 |

## 8. 不变量

- `Y2S1-INV-001`：导入只写 Source Vault 与 receipt；Canonical digest、data_revision、Core View 导入前后不变。
- `Y2S1-INV-002`：同一内容哈希不重复存储；重复扫描/重复 poll 零新 Source。
- `Y2S1-INV-003`：路径不安全 fail closed 且无写入。
- `Y2S1-INV-004`：每个枚举文件都有终态 receipt；无静默丢失；失败显式报告。
- `Y2S1-INV-005`：中断后无半完成状态；重跑收敛至与无中断一致。
- `Y2S1-INV-006`：无 wall-clock；同输入报告字节一致。

## 9. 边界与禁止事项

- 禁止语义解释、候选生成、实体对齐、任何 Canonical 写入。
- 禁止读取逻辑根之外路径；禁止跟随逃逸符号链接。
- 禁止后台线程、定时器、OS 文件事件、网络访问。
- 禁止把 ImportReport 当作事实证据或写入 Canonical。
