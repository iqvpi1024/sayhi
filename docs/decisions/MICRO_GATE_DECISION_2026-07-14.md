# Micro Gate 产品门禁决定

## 1. 决定信息

| 字段 | 值 |
|---|---|
| 决定 ID | `DEC-MICRO-GATE-001` |
| 决定日期 | 2026-07-14 |
| 决策人 | 产品负责人 |
| 决定状态 | `decided` |
| PRD 基线 | `PRDv04.md` v0.4 |
| PRD canonical LF SHA-256 | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 被审计规范基线 commit | `15e3ff87cd4c773b637a3bab9fba0cb614eaff45` |
| 多模型审计保存 commit | `0c7e2d2` |
| 审计结论 | `no`：当前基线不得直接进入 Micro 业务实现 |

PRD hash 指 Git 规范文本按 UTF-8 解码、换行归一化为 LF、无 BOM 重新编码后的 SHA-256。工作树 CRLF/LF 差异不得被解释为产品语义变化。

## 2. 产品裁决

产品负责人已明确批准以下推荐裁决：

1. `PRDv04.md` v0.4 作为当前产品需求基线，PRD 原文保持只读。
2. PRD §27.3 六项产品边界按现有 `BQ-*`、`IQ-*` 决定和九份 SPEC 的规范解释确认；这不等于当前即可开工。
3. 只授权执行 `Micro Gate Corrective Revision`，范围限于 `MMF-001`、`MMF-002`、`MMF-003`、`MMF-004`、`MMF-005`、`MMF-006`、`MMF-008`，以及与门禁可信度直接耦合的 `MMF-007`、`MMF-016`。
4. 在上述 P1 全部关闭、静态结果可复现且关闭性复审通过前，Micro 业务实现门禁保持 `closed`。
5. Personality protected oracle 采用一个只读、预置、全合成的 `Hypothesis` sentinel，只比较发布/撤销前后的规范 digest。该 sentinel 不授权生成、修改、查询产品能力或实现 Hypothesis 生命周期。

依据：PRD §6.5-§6.7、§6.14、§11、§13.3-§13.4、§22.1、§24.1、§27.3；`MULTI_MODEL_FINAL_AUDIT.md` §7-§11。

## 3. 本次允许修改

- Source append 的 policy/subject 初始化合同和对应合成 fixture。
- ChangeSet preflight attempt、合法终态、receipt、幂等与 retry oracle。
- Micro 历史 Source evidence、非空 trust/closeness opinion 和只读 personality sentinel。
- S6 individual test、run、suite artifact、applicability 与 verification result 的分轴枚举。
- Micro required upstream Test Ref 的唯一清单。
- 静态校验的 EOL、结构化 invariant mapping、正向枚举和隐私启发式检查。
- 受影响 SPEC 版本、追踪矩阵、验证结果、关闭性复审和项目状态。

## 4. 本次禁止修改

- `PRDv04.md` 的任何字节或产品语义。
- 数据库、语言、框架、模型、队列、索引和最终技术栈选择。
- 业务实现、runner、机器 fixture 或把任何业务 suite 标为通过。
- 权限 runtime、MCP runtime、连接器、同步、真实迁移、财务、健康、决策、多 Agent、A2A 或数字遗产。
- `MMF-009` 至 `MMF-015`、`MMF-017` 的非直接耦合 deferred 修订。

## 5. 门禁退出条件

只有同时满足以下条件，关闭性复审才可给出 `yes` 或 `yes_with_conditions`：

1. 九个本轮 Finding 均有正文、验收 oracle 和验证证据。
2. 静态校验在 LF 与 CRLF 输入条件下结果一致且 exit code 为 0。
3. `LATEST_STATIC_VALIDATION.md` 只报告脚本实际执行的检查。
4. 所有 suite 继续保持 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。
5. 关闭性复审单独保存，不能改写原多模型审计快照。

本决定只解除产品裁决缺失，不自动把业务实现门禁改为 `open`。纠偏完成后仍必须停止并报告复审结论，由后续明确任务决定是否开始实现。
