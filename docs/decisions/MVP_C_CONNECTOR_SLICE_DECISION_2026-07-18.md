# MVP-C 连接器切片产品决定

## 文档信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-CONNECTOR-001` |
| Date | 2026-07-18 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-C-DECISION-001` (completed) |
| Current Slice | `SLICE-MVP-C-CONNECTOR-001` |

## 1. 决定内容

选择连接器为下一切片，但范围极度收缩：

- 只实现一个合成数据导入器（Synthetic Data Importer）
- 证明外部数据可以通过 Ingestion Contract 进入 Source Vault
- 不实现任何真实第三方连接器（微信、日历、邮件等）

## 2. 目标

1. 证明外部数据可以通过标准 Ingestion Contract 进入系统
2. 验证 Source Vault 可以接收非 fixture 来源的数据
3. 保持所有现有不变量（证据边界、隐私、合成数据）

## 3. 非目标（明确后置）

- 微信聊天记录导入
- 日历导入
- 邮件导入
- 文件系统监控
- 真实个人数据导入
- OCR/ASR/视频处理
- 多设备同步

## 4. 必须重开的 Deferred 问题

- `DQ-008`：连接器范围（进入前必须裁决）

## 5. 依赖

- Micro-MVP 核心完成（49/49 passed）
- MVP-A Answer Safety 完成（35/35 passed）
- Phase 4 CLI 完成
- Phase 5 B1 Candidate Review 完成（8/8 passed）
- Phase 6 C1 Decision-Outcome 完成（11/11 passed）

## 6. 授权边界

本决定只授权：
1. SPEC applicability review
2. 合成数据导入器实现
3. 不开始真实第三方连接器开发

## 7. 完成定义

- 合成数据导入器实现完成
- Ingestion Contract 验证通过
- 所有现有测试继续通过

---

> 本决定由产品负责人授权，技术代理不得自行扩大范围。
