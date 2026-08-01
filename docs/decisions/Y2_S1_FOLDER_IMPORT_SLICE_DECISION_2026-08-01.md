# Y2-S1 真实文件夹文本导入切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-Y2-S1-001` |
| Date | 2026-08-01 |
| Product Baseline | `PRDv06.md` v0.6 Approved |
| Upstream Decision | `DEC-Y2-ENTRY-001` §2.2/§2.6（首连接器 = 本地文件夹文本导入，Y2-S1） |
| Current Slice | `SLICE-Y2-S1-FOLDER-IMPORT-001` |

## 1. 决定内容

选择 Y2-S1 真实文件夹文本导入作为 Year 2 第一个切片。具体决定：

1. 切片只证明 FR-302 的第一个连接器切片：本地文件夹（`.txt`/`.md`）批量导入与可选轮询监视，全部进入 Source Vault；不做语义解释（Y2-S2）。
2. 每个文件产生独立 Source append + AppendReceipt：内容哈希、字节长度、来源时间（文件修改时间）、摄入时间、语言、CoverageWindow。
3. 幂等与去重：同一内容哈希重复出现（不同文件名或重复扫描）产生 `duplicate` receipt，不重复存储；重复扫描零新写入。
4. 路径安全：根目录外、符号链接逃逸、路径穿越一律 fail closed `rejected`，不产生任何写入。
5. 中断恢复：批量导入中途失败不产生半完成状态；失败文件显式报告；恢复重跑可完成剩余导入。
6. Canonical 不变：导入只写 Source Vault 与 receipt，不触发 ChangeSet，不改变任何 Canonical 对象、revision 或 Core View。
7. 真实数据生产合同（PRDv06 §21.6）的切片部分：本切片验证其中的"导入中断无半完成状态"与"不静默丢失"两条；其余四条（删除、备份恢复、导出、升级卸载）由已 verified 的 C5/D2 覆盖并在 Gate Review 中引用。
8. 本切片仍在固定合成 fixture 上验证；"真实数据模式开放"以本切片 + §21.6 全项通过为准，不由本切片单独宣告。

## 2. 产品依据

- PRDv06 §2.2/§24.5：Y2-S1 范围与排序。
- PRDv06 §7.2、§11.1：Source append 独立 receipt，语义写入才走 ChangeSet；本切片零语义写入。
- PRDv06 §9.2：CoverageWindow 记录覆盖起止与连续性。
- PRDv06 §19.4：Ingestion Contract 必备字段（来源系统、原始时间、时区、语言、哈希、解析器版本）。
- PRDv06 §21.6：真实数据生产合同前置项。
- PRDv06 §26 Case H：导入可续、无静默丢失、候选与确认后置 Y2-S2。

## 3. 切片范围

- `src/noetide_micro/folder_import.py`：确定性文件夹扫描、过滤（扩展名白名单）、UTF-8 校验、逐文件 Source append + receipt、批量报告、轮询监视（显式调用单次 poll，无后台线程）。
- 复用 `SemanticStore.append_source`；新增窄 store 辅助仅限 Source/receipt 查询，不动 Canonical 写路径。
- Suite：fixture（合成文件夹树）、oracle、scenarios、adapter protocol、contract 测试、offline runner、validator、manifest。

## 4. 非目标

- 语义解释、候选生成、实体对齐、NLP（Y2-S2）。
- 微信/日历/邮件等其余连接器（DQ-008 未裁决部分）。
- 二进制/图片/PDF、OCR、ASR、压缩包、递归符号链接跟随。
- 实时文件系统事件监听（OS-level watcher）、后台守护进程、调度器。
- 真实数据模式开放的单独宣告；任何隐私政策变更。

## 5. 不变量

- `Y2S1-INV-001`：导入只写 Source Vault 与 receipt；Canonical digest、data_revision、Core View 在导入前后不变。
- `Y2S1-INV-002`：同一内容哈希不重复存储；重复扫描零新 Source。
- `Y2S1-INV-003`：路径不安全（根目录外、穿越、逃逸）fail closed 且无写入。
- `Y2S1-INV-004`：批量导入无静默丢失；每个文件都有终态 receipt（stored/duplicate/rejected/skipped）；失败显式报告。
- `Y2S1-INV-005`：中断后无半完成状态；重跑可完成剩余导入且最终状态与无中断运行一致。
- `Y2S1-INV-006`：无 wall-clock；时间全部来自 fixture clock 与文件元数据；报告确定性（同输入同输出）。

## 6. 授权与下一步

本决定授权 S1/S7/S9 SPEC applicability review（其余 SPEC 不涉及），随后 slice contract、traceability、ADR、suite 物化、Implementation Plan。不授权业务编码。
