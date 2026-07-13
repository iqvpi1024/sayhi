# 独立规范基线审计

## 1. 审计结论

2026-07-13 的“九份 SPEC 全部完成”结论只能证明文件齐全，不能证明九份文件合起来只有一种实现语义。本轮不继承原 `Approved` 结论作为正确前提，重新检查 PRD、S1-S9、Micro 验收、开放问题、追踪矩阵和项目状态。

结论：发现 16 类实质问题，其中 13 类会导致实现分叉或错误验收，3 类会导致项目状态过度陈述。所有可从 PRD 和既有裁决唯一推导的问题已修复；没有新增 blocking/important 产品问题。`DQ-001..010` 继续 deferred。

修订后基线：S1/S2 v0.3，S3-S9 v0.2，状态保持 `Approved`。这表示语义合同完成独立审计，不表示测试已物化、执行或通过。

## 2. 审计边界

| 项目 | 结果 |
|---|---|
| PRD | `PRDv04.md` 只读，SHA-256 为 `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 输入范围 | 仅工作区文件；未扫描、导入或推断工作区外个人数据 |
| 数据 | 文档、示例和 fixture 只使用合成标识/内容 |
| 实现 | 未写业务代码、未建数据库、未选择最终技术栈、未安装依赖 |
| 测试 | 合同目录已定义；suite 未物化、未执行、未通过 |

依据：PRD §1、§6、§21.4、§22；项目隐私边界。

## 3. 发现与处理

| ID | 严重度 | 发现 | PRD/裁决依据 | 处理 |
|---|---|---|---|---|
| A-01 | high | S1 与 S3 的 `confirmation_policy` 使用两套枚举 | PRD §11.2 | 统一为 `single_confirmation/double_confirmation` |
| A-02 | high | S1 proposal 使用 `before/on_success/source_evidence_refs`，S3 使用另一套字段 | PRD §11.2、§22.2 | 统一为 `target_ref/before_digest/after_value/valid_time/evidence_refs/protected_paths` |
| A-03 | high | Source 被列为核心语义对象，但 Source Append 又不增加 Canonical revision，边界未闭合 | PRD §7.2、§11.1、§18.2；BQ-003 | 明确 Source Vault 记录不属于 `data_revision` 管理的 Canonical Context；其规范语义修改仍经 ChangeSet |
| A-04 | high | S2 把会重算的 evidence family/dimensions 嵌入 Canonical Evidence Ref | PRD §6.3、§9.3、§16.5 | 拆为 Canonical Evidence Ref 与 Derived EvidenceAssessment，禁止派生评估反向持久化成事实证据 |
| A-05 | high | S3 未定义 L1 已提交但 outcome/revision/receipt 不一致的恢复边界 | PRD §10、§11.2、§21.1 | 要求 Canonical L1、revision、ChangeSet outcome、receipt summary 同一恢复边界；详细传播 receipt 可追加 |
| A-06 | high | 撤销没有处理介入变更，且把 hard delete 也隐含为可撤销 | PRD §12.3-§12.4；IQ-008/011 | 补偿以 current revision 为 base，冲突不覆盖；新增 `reversibility`，不可逆操作不得伪造 rollback |
| A-07 | high | S4 用单一状态机混合 archive、seal、soft/hard delete | PRD §12.4、§16.4、§17.3 | `retention_state` 与 `sensitivity=sealed` 正交；解封用 `pre_seal_sensitivity` 恢复；`retrieval_activation` 继续独立 |
| A-08 | high | policy engine 失败时允许凭缓存 policy 浏览，违反 fail closed | PRD §17.4、§25.2 | 所有受控 payload/mutate/external 请求 fail closed；拒绝响应不泄露资源 |
| A-09 | high | hard delete 后旧 verified 答案和 Derived 副本的处置未定义 | PRD §6.3、§6.13、§12.4 | 删除证据后依赖 Answer/View 必须失效重评，Derived 不得复原正文 |
| A-10 | high | S5 把 ChangeSet `risk_level=medium` 与审查 `priority=normal` 混为同一枚举 | PRD §11.2、§15.3 | 拆分 `risk_level` 与 `review_priority`，两者都不改变 truth/confidence |
| A-11 | high | `suite_defined=true` 被当成已有可运行测试；实际只有 Markdown 目录 | PRD §6.14、§22.1 | 新增 `suite_materialized`；当前全部 false；required test 必须同一次 run 全部通过 |
| A-12 | high | exported Pack 会被新导出 supersede，且未禁止越界路径/主动内容 | PRD §7.2、§17、§21.4 | Pack 成为不可变 revision 快照；绝对/越界/逃逸引用 quarantine；导入内容一律 inert |
| A-13 | high | MCP 的 execution、Answer、View freshness 混用 `stale/not_covered`，denied 响应还要求返回 revision | PRD §9.4、§10、§17、§19 | 三轴分离；denied 使用 `result_status=denied` 且 revision/payload withheld；修正 `PolicyRequest` 错名 |
| A-14 | high | S9 把 stored Source 继续转成 parsing/parse_failed，破坏 Source receipt 终态；迁移无 verification_failed | PRD §7.2、§19.4、§25.2 | Intake 与 Parse Attempt 独立；迁移增加 verifying/verification_failed/compensation rollback |
| A-15 | high | Micro fixture 使用 `source_type/entity_type/participants/valid_to:null` 等非法字段，并把 trust/closeness 当 State | PRD §8-§9、§13.3、§24.1；S1/S2 | 改为唯一合法 fixture；trust/closeness 保持 opinion Assertion；locator 固定为 UTF-8 byte range + hash |
| A-16 | medium | 追踪矩阵把长期 FR 的边界占位写成“32/32 权威闭环”，且 root 历史报告误计 34 条 FR | PRD §20、§24；S6 | 合并为一张 32 行权威表，增加 coverage level；15 条明确为 `boundary_only_deferred` |

## 4. 追踪诚实性

32 条 FR 全部已登记，但完成程度不同：

| Coverage Level | 数量 | 含义 |
|---|---:|---|
| `micro_required_slice` | 9 | 当前合成链路需要的部分，不代表整条 FR；FR-105 仅取传播失败切片 |
| `specified_not_implemented` | 8 | 合同足以指导后续实现，但无实现和 run |
| `boundary_only_deferred` | 15 | 只锁边界或禁止旁路，完整能力未写完/后置 |

FR-301/302/304/305/306 没有功能验收 suite，继续保持显式 `TBD`。不能再用 Pack 冲突、通用授权或 MCP 边界测试声称同步、连接器、专业模板、数字遗产或 A2A 已完成规范。

## 5. 静态验证

实际执行：

```powershell
& .\tools\validate_spec_baseline.ps1
```

结果：`PASSED`。检查内容：

- PRD hash 与只读基线一致。
- 9 份 SPEC 均有 §0-§21，版本与 Approved 状态匹配。
- 257 个 SPEC Acceptance Test ID 连续且唯一。
- 123 条 invariant 连续且有覆盖引用。
- `MM-001..010` 完整。
- Micro 合成文本 SHA-256、58 字节长度和 UTF-8 locator 一致。
- 权威矩阵 32 行与 PRD 32 个唯一 FR 完全一致。
- Coverage Level 数量为 9/8/15，未出现未知等级。
- 权威矩阵展开后的 103 个唯一 Test Ref 均解析到存在的 SPEC/MM Test ID。
- 已知字段别名、错误状态转换和 Markdown fence 漂移不存在。
- 启发式隐私扫描未发现电话或本机用户目录；仅命中已知 Git SSH endpoint，不是 fixture/个人内容。

这是静态合同检查，不是业务测试。加上 10 个 MM 场景，共有 267 个合同/场景 ID；全部 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。

## 6. 未决与风险

- 新增 blocking：0。
- 新增 important：0。
- Deferred：`DQ-001..010` 保持不变。
- 最大剩余风险不是文档缺章节，而是尚无机器可读 fixture、runner、实现模块和真实 Verification Result。
- 任何 SPEC 后续修改都可能使旧静态/业务结果 superseded，必须重新运行校验。

## 7. 下一步唯一建议动作

建立 Micro-MVP 最小实现计划和必要 ADR，然后只物化 `MM-001..010` 的 manifest、fixture、forbidden-change oracle 与离线 runner。不得把 15 条 `boundary_only_deferred` FR 带入第一条实现链路。
