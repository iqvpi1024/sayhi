# MVP-C MVP Release Gate 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-C-RELEASE-001` |
| Date | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-C-PACK-001`（已 verified，recovery tag `c5-context-pack-backup-rp-20260726`） |
| Current Slice | `SLICE-MVP-C-RELEASE-001` |

## 1. 决定内容

选择 MVP-C 的 C6 MVP Release 作为下一条窄切片（路线图 `C6-MVP-RELEASE`：首年完整回归、安全审计、数据恢复和公开 Beta 门禁），不新增任何业务语义能力，而是把发布就绪性做成可执行审计：

1. 首年完整回归：全部 16 个 configured-adapter suite 在同一次全量 regression 中通过且零 skip；全部 suite validator 通过。
2. 安全审计（可执行）：隐私边界扫描（fixture/源码只含合成数据标记）、依赖审计（src 只含 stdlib 导入）、网络隔离证明（src 无 socket/urllib/http 调用面）、manifest 绑定审计（全部 suite executed+passed 且 result 绑定）。
3. 数据恢复演练：对已 verified 的 C5 加密备份做端到端恢复演练（建库 -> 备份 -> 恢复 -> 字节一致 + revision 一致）。
4. 公开 Beta 门禁：全部首年切片 verified、recovery tag 齐全、PROJECT_STATE/CURRENT_HANDOFF 当前、全部首年非目标保持关闭的逐项确认。

## 2. 产品依据

- 路线图（136 行）：C6 范围与"全部首年非目标保持关闭"约束。
- PRD §23、§24：价值指标与首年范围的发布前核验。
- PRD §534、§758：删除/导出诚实性已被 C5 覆盖，C6 只复核其验证状态，不重建。
- 项目铁律：未执行的测试不得描述为通过——发布门禁必须由可执行审计支撑，不得用文档声明代替。

## 3. 切片范围

- `c6_release_audit` 可执行审计套件：8 个审计场景（C6-001..008），产出 immutable audit result。
- 安全审计报告（由可执行结果支撑）：隐私、依赖、网络隔离、manifest 绑定。
- 数据恢复演练记录：复用 `pack_backup`（ADR-0017），在固定合成 demo 库上执行。
- 公开 Beta 门禁复核文档：逐项确认 + 非目标关闭清单。
- 无新业务代码、无 schema 变更、无新对象类型。

## 4. 非目标

- 新业务能力、新 suite 业务场景、真实数据、生产加密、D2 安装包、D3 发布动作。
- 修改任何已 verified 切片的 fixture/oracle/结果。
- 公开 Beta 的实际发布（D3 发布动作需用户确认，不在本切片）。
- 首年非目标的任何形式开启（多设备、连接器、真实导入、多用户、A2A 等全部保持关闭）。

## 5. 不变量

- `C6-INV-001`：全量回归真实执行且零 skip；任何 suite 失败或 skip 即门禁失败。
- `C6-INV-002`：src/noetide_micro 只含 stdlib 导入；无 socket/urllib/http/client 网络调用面。
- `C6-INV-003`：全部 fixture 显式合成（synthetic=true、external_data_used=false）；源码与 fixture 无真实个人数据标记。
- `C6-INV-004`：全部 suite manifest flags=executed+passed 且 latest result 哈希绑定；任何未绑定即门禁失败。
- `C6-INV-005`：数据恢复演练字节一致且 revision 一致；源库不被修改。
- `C6-INV-006`：首年非目标保持关闭：审计产物不得宣称多设备/连接器/真实导入/生产加密/多用户已就绪。
- `C6-INV-007`：审计只读：不修改任何已 verified artifact、不移动 tag、不写业务库。

## 6. 授权与下一步

本决定只授权 S6/S7 的 C6 applicability review、发布门禁合同、追踪和审计套件设计。完成这些产物前不得编写 C6 审计代码。
