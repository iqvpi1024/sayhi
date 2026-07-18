# 架构文档说明

## 1. 职责

本目录只描述当前交付切片的组件边界、数据流、信任边界和运行时责任。它回答“系统各部分如何协作”，不回答产品为什么需要某种行为，也不代替技术选择的 ADR。

依据：PRD §7、§10-§12、§19、§21、§24-§25；`docs/process/README.md`。

## 2. 与其他产物的边界

| 产物 | 负责内容 | 本目录不得替代 |
|---|---|---|
| PRD / Decision | 产品价值、范围和产品裁决 | 不得由组件图补业务规则 |
| SPEC | 字段、状态机、不变量、失败和验收 | 不得改变语义合同 |
| ADR | 技术选择及取舍理由 | 架构图不等于选择依据 |
| Architecture View | 已接受决定下的组件、接口和数据流 | 不得声称未经验证的运行行为 |
| Implementation Plan | 实施顺序和模块任务 | 不得在架构文档内夹带 TODO |

## 3. 何时创建

只有当前切片已达到 `traceable`，并且确有两个以上运行时责任需要澄清时才创建 Architecture View。一个切片可以只需要 ADR，不强制为了目录完整而绘制架构图。

每份 Architecture View 至少记录：

- `slice_id`、适用 PRD/Decision/SPEC/ADR 版本。
- 组件职责和明确非职责。
- Canonical、Derived、Source、receipt 等数据边界。
- 写入、读取、失败、恢复和审计路径。
- 外部系统、网络和权限边界。
- 已知风险、待验证假设和被排除范围。

## 4. 当前状态

`SLICE-MICRO-RELATIONSHIP-001` 的 `MICRO_RELATIONSHIP_ARCHITECTURE.md` 已被实现和验证。

当前 A1 已有固定合成 Answer Safety 架构和已验证 runner。B2 的 `B2_EPISODE_SUMMARY_ARCHITECTURE.md` 是 Accepted Design Baseline：固定 synthetic Episode 经 ChangeSet 发布，day/phase summary 位于 Derived 层并按 revision stale/rebuild；B2 suite 仍未物化，业务行为为 `not_executed`。
