# 项目状态

## 1. 恢复入口

任何新任务必须按顺序读取：

1. `PRDv04.md`
2. `docs/PROJECT_STATE.md`
3. `docs/decisions/OPEN_QUESTIONS.md`
4. 当前工作对应的 Approved SPEC
5. `docs/traceability/REQUIREMENTS_MATRIX.md`
6. 当前测试与最近验证结果

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试和示例只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-13 |
| 当前阶段 | Specification Baseline Complete |
| 阶段状态 | `approved_specs_implementation_not_started` |
| PRD | `PRDv04.md` v0.4，`Draft for Review`，未修改 |
| PRD SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | 9/9 已完成并 `Approved` |
| Important 产品问题 | `BQ-001..005`、`IQ-001..018` 全部 decided |
| Deferred 问题 | `DQ-001..010` 保持 deferred |
| 实现代码 | 无 |
| 依赖/数据库/最终技术栈 | 无、未选择 |
| 测试 | 245 个合同/场景 ID 已定义；0 个已执行，0 个已通过 |
| Git | `main`，远程 SSH-over-443：`ssh://git@ssh.github.com:443/iqvpi1024/sayhi.git` |
| GitHub 本轮备份 | passed：九份 SPEC 基线提交 `721838f` 与三个批准标签已推送；最新状态以远程 `main` 为准 |

## 3. 当前结论

九份 SPEC 已按权威顺序完成、自审并由产品负责人整体授权批准：

1. Semantic Object Model v0.2
2. Bitemporal & Evidence v0.2
3. ChangeSet & Consistency v0.1
4. Privacy & Access Policy v0.1
5. Shiling Policy v0.1
6. Semantic Test Harness v0.1
7. Storage, Index & Portability v0.1
8. MCP Contract v0.1
9. Ingestion & Migration v0.1

批准只表示语义合同完成。没有业务实现、数据库或测试运行器，任何 suite 都不得称为通过。

## 4. 已完成内容

- Phase 0 PRD 就绪审查、32 条 FR 追踪、SPEC 计划与 Micro-MVP Given/When/Then。
- S1/S2 外部评审有效意见关闭；过期基线误报未导致文档倒退。
- `BQ-001..005`、`IQ-001..018` 全部持久裁决。
- S3-S9 依次完成全部 §0-§21 必备章节。
- 建立对象、双时态、证据、ChangeSet、一致性、权限、识灵、测试、存储、MCP、输入/迁移的完整语义边界。
- 建立 `docs/reviews/SPEC_SUITE_COMPLETION_REVIEW.md` 全套审查报告。
- 在需求矩阵 §19 为 32 条 FR 建立最终 SPEC/Test 映射。
- 保持 Micro-MVP 只包含一条合成 RelationshipState 链路。

## 5. 权威产物

| 文件 | 状态 |
|---|---|
| `docs/reviews/PRD_V04_READINESS_REVIEW.md` | completed |
| `docs/reviews/SPEC_SUITE_COMPLETION_REVIEW.md` | completed |
| `docs/decisions/OPEN_QUESTIONS.md` | Important 全 decided；Deferred 保留 |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | 32/32 FR 完整映射 |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | 10 场景 defined/not_executed |
| `docs/specs/README.md` | 9 份边界/顺序/门禁同步 |
| `docs/specs/01_SEMANTIC_OBJECT_MODEL_SPEC.md` | Approved v0.2 |
| `docs/specs/02_BITEMPORAL_EVIDENCE_SPEC.md` | Approved v0.2 |
| `docs/specs/03_CHANGESET_CONSISTENCY_SPEC.md` | Approved v0.1 |
| `docs/specs/04_PRIVACY_ACCESS_POLICY_SPEC.md` | Approved v0.1 |
| `docs/specs/05_SHILING_POLICY_SPEC.md` | Approved v0.1 |
| `docs/specs/06_SEMANTIC_TEST_HARNESS_SPEC.md` | Approved v0.1 |
| `docs/specs/07_STORAGE_INDEX_PORTABILITY_SPEC.md` | Approved v0.1 |
| `docs/specs/08_MCP_CONTRACT_SPEC.md` | Approved v0.1 |
| `docs/specs/09_INGESTION_MIGRATION_SPEC.md` | Approved v0.1 |

## 6. 最近验证结果

| 检查 | 结果 |
|---|---|
| PRD SHA-256 | passed：基线未变 |
| 每份 SPEC 章节 | passed：9/9 均为 §0-§21，无缺失 |
| SPEC 状态 | passed：9/9 `Approved` |
| 测试编号 | passed：235 个 SPEC Test + 10 个 MM，连续且无未知引用 |
| 不变量 | passed：S1-S9 共 111 条，均有覆盖说明 |
| Markdown 围栏 | passed：每个文件成对 |
| FR 追踪 | passed：PRD 与矩阵均为 32 个唯一 FR，无缺失 |
| 产品问题 | passed：Important open=0 |
| 隐私静态扫描 | passed：新增 SPEC/审查未复制 PRD 合成人物名；无真实数据 |
| 实现文件 | passed：0；仓库只有 Markdown/TXT |
| 合同测试执行 | `suite_executed=false`；没有实现/集成测试 |

不得把本节的“静态验证 passed”解释为业务测试通过。

## 7. 核心裁决摘要

- 12 个核心对象封闭；RelationshipState 是 State。
- assertion kind、review status、answer status 正交，回答采用六态。
- Source Append 独立；Canonical 语义写入只经 ChangeSet。
- State 使用半开区间；valid/recorded/source/ingested time 分离。
- `base_revision` 为全局 revision，撤销产生补偿 revision。
- Micro Core View 仅人物卡和关系时间线。
- 多舱室取最严格交集；sealed 无旁路；删除逐层诚实回执。
- 识灵是单协调内核，模型输出先是 candidate。
- 私有完整导出与外部分享分离。
- 未知结构字段保语义，opaque 内容保字节/hash。

完整裁决见 `docs/decisions/OPEN_QUESTIONS.md`。

## 8. 范围锁

在 Micro-MVP 合成链路实际通过前，禁止：

- 财务、健康、决策和成长业务实现。
- 多设备同步、连接器、真实历史迁移。
- 多租户、多 Agent、A2A、数字遗产。
- 通用图数据库平台和全量依赖语言。
- 导入任何真实个人数据。

九份 SPEC 中对这些能力的描述只锁定未来边界，不是当前建设授权。

## 9. 风险

| 风险 | 控制 |
|---|---|
| 把 Approved SPEC 当成成品 | 实现=0、测试 executed=false 明示 |
| 技术选型反向改语义 | 实现前 ADR 必须服从 Approved SPEC |
| 长期 FR 拉大 Micro | 范围锁 + 矩阵区分合同与实现 |
| 删除/权限虚假承诺 | S4/S7 分层 receipt 与 fail closed |
| 外部评审基线过期 | 评审需记录版本、hash、Git commit |
| 测试误报 | S6 要求命令、环境、exit code、artifact |

## 10. 下一步唯一建议动作

**建立 Micro-MVP 最小实现计划与必要 ADR，只选择能验证合成 RelationshipState 链路的技术，然后先实现真实测试运行器和该一条链路。**

未经新的明确开发任务，不开始业务代码或技术选型。

## 11. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | PRD 审查、追踪、SPEC 计划、Micro 验收、Git 基线 |
| 2026-07-13 | S1/S2 | 外部评审关闭，v0.2 Approved |
| 2026-07-13 | S3-S9 | 逐份完成、自审、裁决并 Approved；未写实现 |
| 2026-07-13 | Spec Suite | 9/9 SPEC、32/32 FR、245 test IDs 静态验证完成 |
| 2026-07-13 | GitHub Backup | 提交 `721838f` 与 `spec-som-v0.2-approved`、`spec-bte-v0.2-approved`、`spec-suite-v0.1-approved` 已通过 SSH-over-443 推送 |
