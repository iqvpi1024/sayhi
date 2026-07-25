# A6 MVP-A 硬化与本地 Alpha SPEC 适用性复核

| 字段 | 值 |
|---|---|
| Review ID | `A6-SPEC-APPLICABILITY-001` |
| 日期 | 2026-07-25 |
| 产品基线 | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-HARDENING-001` |
| 切片 | `SLICE-MVP-A-HARDENING-001` |
| 结论 | `pass_with_slice_contract_required` |

## 逐份结论

| SPEC | 结论 | 可直接复用 | A6 必须补齐 |
|---|---|---|---|
| S1 Semantic Object Model v0.6 | `pass` | 12 类核心对象模型、schema_version、保护对象语义；A6 不引入新对象类型 | 无 |
| S2 Bitemporal & Evidence v0.5 | `pass` | 双时态语义完整：valid/recorded 分离、`recorded_at` 不可回填、纠正与时间演化区分、历史查询语义；A6-008 直接复用 | 无 |
| S3 ChangeSet & Consistency v0.4 | `partial` | ChangeSet 状态机、原子发布、stale base 拒绝、撤销补偿、审计回执、L2 失败 Canonical fallback/unavailable | 显式合同：壳层错误恢复表面（启动失败、数据目录不可写、数据库损坏、发布失败回滚、视图 unavailable）的固定预期行为；S3 证明原子语义，壳层呈现不新增恢复语义 |
| S6 Semantic Test Harness v0.5 | `pass` | fixture/oracle/manifest/runner 四态；Reference Profile 与 SLO 语义已闭合（`HTH-INV-009` SLO 仅对声明 profile 有效、`IQ-014` 计时边界、`HTH-AT-015` 记录边界与 profile） | 12 场景集成验收组的场景集、每步预期结果、Reference Profile `a6_mvp_a_reference_v1` 的具体版本化定义、SLO 实际结果记录、current result 绑定 |
| S7 Storage, Index & Portability v0.3 | `partial` | Context Pack 导出、删除与备份可验证、Round Trip、未知字段保留；数据目录由用户拥有 | 显式合同：卸载语义（默认不删用户数据、删除独立确认）、首次启动合成/真实路径分离可验证、干净机器启动路径；S7 覆盖数据侧删除/备份/导出，壳层卸载与首启路径不在其范围 |

S4、S5、S8、S9 不进入 A6：`A6-011` 复用 A4 已验证的查询层强制执行，不重判权限语义、不引入新策略；`A6-002` 复用 S5 Candidate Envelope 字段语义，不引入新候选生成语义；本切片无 MCP、无真实导入或迁移。

## 发现与处理

1. **集成证明缺口**：A1-A5 各自在独立 fixture 上证明单个 FR，没有任何既有工件证明 FR-001..012 在同一系统状态下协同成立。A6 的 12 场景必须在同一个版本化 Reference Profile 上顺序执行；合同必须声明集成执行不削弱、不替代任何已 verified suite 的独立证据。
2. **Reference Profile 具体化**：S6 已闭合 Reference Profile/SLO 的产品语义，但具体硬件、OS、runner 由 ADR 记录（S6 §IQ-014）；A6 的 ADR 步骤必须落地 `a6_mvp_a_reference_v1` 的版本化环境描述符与 SLO 计时边界，且结果不得跨 profile 外推。
3. **错误恢复壳层表面**：S3 证明发布原子回滚与 L2 fallback 语义，但启动失败、数据目录不可写、数据库损坏的壳层行为（非零退出、非泄露错误信息、不部分写入）需要切片合同固定预期；不得借恢复之名新增绕过写入路径。
4. **本地 Alpha 可解释性**：S7 覆盖 Pack/删除/导出/备份可验证，但卸载语义（默认不删用户数据、删除独立确认并说明备份/导出副本）、首次启动合成/真实数据路径分离、干净机器可启动属于壳层与发布边界，需要切片合同以文档 + 可执行 smoke 闭合。
5. **开发启动 ADR 到期**：按 `ONE_CLICK_DELIVERY_PLAN.md` §2，A6 前须建立开发启动与 evaluator package ADR；该决策进入 A6 的 ADR 步骤，不在本复核预选命令名或工具。

处理：新增 A6 slice contract，闭合 12 场景集成验收、Reference Profile 版本化与 SLO 记录、壳层错误恢复固定行为、本地 Alpha 可解释性验收。该合同不得修改基础 SPEC，不得引入 MVP-B 功能、真实数据、D2/D3 安装/发布动作或新产品规则。

## 下游影响

在 A6 slice contract Approved 前，Traceability 只能标为 `product_decided`，不得物化 fixture/oracle/runner、建立 ADR 或编写业务代码。

## 下一步

起草 A6 hardening slice contract，绑定 12 场景映射、Reference Profile 定义边界、错误恢复固定行为与 Alpha 可解释性验收后进入 Traceability。
