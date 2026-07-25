# MVP-A 硬化与本地 Alpha 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-A-HARDENING-001` |
| Date | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-A-APP-SHELL-001`（已发布 recovery point `a5-app-shell-rp-20260725`） |
| Current Slice | `SLICE-MVP-A-HARDENING-001`（A6） |

## 1. 决定内容

选择 MVP-A 的 A6 作为下一条切片：MVP-A 硬化与本地 Alpha。A1-A5 已分别 verified 并有 recovery point；A6 不再引入新产品能力，而是把 FR-001..012 的既有证明组装为 MVP-A 的发布级验收，并补齐硬化缺口。

顺序理由：按路线图 MVP-A 顺序 A1→A6；A5 把核心组装为可用壳之后，路线图要求的下一步就是硬化与本地 Alpha，而非进入 MVP-B。

## 2. 对"12 个可执行语义变更测试"的显式裁决

PRD §24.2 将"12 个可执行语义变更测试"列为 MVP-A 出口项，但全文仅出现一次（§24.2），没有进一步定义。这是本决定必须显式裁决的解释点；裁决如下，理由一并记录，后续若被推翻须经 Change Control 以新 Decision 取代。

候选解释：

- 解释甲：12 个核心对象（PRD §8）各一个语义变更测试。**拒绝**：Episode、Commitment、Goal、Decision、Outcome、Hypothesis 按 §24.3/§24.4 属 MVP-B/C 范围，与 A6"主要范围：MVP-A 尚未完整覆盖的 FR-001..012"（路线图 §4 A6）直接矛盾。
- 解释乙：FR-001..012 各一个可执行的端到端语义变更验收场景，共 12 个，组成 MVP-A 发布验收组，在同一个版本化 Reference Profile 上执行。**采纳**。

采纳理由：

1. 数量与范围同时吻合：12 = FR-001..012 的条数，且路线图把 A6 范围限定为 FR-001..012。
2. 增量价值真实：A1-A5 的 suite 各自在独立 fixture 上证明单个 FR；没有任何既有工件证明 12 个 FR 在同一系统状态下协同成立。A6 的 12 场景在同一集成 profile 上顺序执行，恰好补上这个证明缺口，而不是重复已通过的语义。
3. 不扩张语义：12 个场景只重述已 Approved 的 SPEC 行为，不为任何 FR 补写新产品规则。

12 个场景与 FR 的固定映射（详细 Given/When/Then 由 SPEC-A6 合同定义）：

| 场景 | FR | 验收语义 |
|---|---|---|
| `A6-001` | FR-001/002 | Source append + 独立 receipt；Canonical 不变 |
| `A6-002` | FR-003 | 候选生成（Entity/Assertion/RelationshipState）不成为事实 |
| `A6-003` | FR-004 | 规范写入全部经 ChangeSet；Source append 独立 |
| `A6-004` | FR-005 | 自然语言审查 + 影响预览与发布一致 |
| `A6-005` | FR-006 | 发布后三个 Core View 更新或失效 |
| `A6-006` | FR-007 | 回执、历史、撤销补偿完整可审计 |
| `A6-007` | FR-008 | 六态回答在固定查询下严格分离 |
| `A6-008` | FR-009 | 双时态历史查询区分 valid/recorded |
| `A6-009` | FR-010 | 冲突检测与并列呈现，不自动裁决 |
| `A6-010` | FR-011 | 实体合并候选与拆分回滚 |
| `A6-011` | FR-012 | 权限与舱室在查询层 fail closed |
| `A6-012` | 横切 | 全旅程后 trust/closeness/人格判断与历史不被自动修改；stale base 拒绝；L2 失败 fallback |

## 3. 切片范围

- 集成验收组：单一固定合成 Reference Profile `a6_mvp_a_reference_v1`（版本化数据 + 环境描述符），12 个场景顺序执行。
- Reference Profile 与 SLO：按 PRD §SLO（"所有 SLO 必须绑定版本化 Reference Profile；具体硬件、OS 和 runner 由 ADR 记录，结果不得跨 profile 外推。5 秒 Core View SLO 不是返回旧值的许可"）建立版本化 profile，记录固定 SLO 检查的实际结果。
- 错误恢复：干净机器可启动；启动失败、数据目录不可写、数据库损坏、发布失败回滚、视图 unavailable 的壳层行为可演示且有固定预期；复用已验证的 S3 语义，不新增恢复语义。
- 本地 Alpha 可解释性：用户数据路径、备份、导出、卸载语义以文档 + 可执行 smoke 证明；合成数据与真实数据路径严格分离的声明可验证。

## 4. 非目标

- MVP-B 任何功能（B4 对账、B5 多语言、B6 影子迁移均不在本切片）。
- D2 安装包、签名、升级/卸载程序、D3 GitHub 正式发布与仓库可见性变更。
- 真实个人数据、真实导入渠道、连接器、多设备。
- UI 框架变更、Grant 管理 UI、性能调优（除固定 SLO 检查外）。
- Alpha 发布的版本号、工件内容与发布动作：在 A6 Gate Review 通过后的发布门禁单独决定，本决定不预选。

## 5. 不变量

- 既有全部核心不变量继续成立；本切片的集成执行不得削弱或替代任何已 verified suite 的独立证据。
- Reference Profile 的 SLO 结果只对该 profile 有效，不外推；SLO 未过不得通过返回旧值规避。
- 错误恢复演示不得写入用户真实目录，不得将合成数据混入真实数据路径。
- 所有规范写入仍经 ChangeSet；呈现层仍不成为事实证据。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S6/S7 的 A6 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 A6 业务代码。

无新重开的 deferred question：DQ-001（商标/域名/商店可用性）保持 deferred，因为本地 Alpha 不是品牌发布；DQ-003/004/009 等继续 deferred。
