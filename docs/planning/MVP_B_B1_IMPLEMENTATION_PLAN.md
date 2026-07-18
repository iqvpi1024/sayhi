# Implementation Plan: MVP-B B1 Candidate Review

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-B-B1-IMPL-001` |
| Status | `Draft` |
| Slice | `SLICE-MVP-B-SHILING-001` |
| Product Decision | `DEC-MVP-B-SHILING-001` |
| SPEC Review | `REVIEW-MVP-B-SHILING-SPEC-001` |
| Trace | Requirements Matrix §4.2 (待建立) |
| ADR / Architecture | 待建立 |
| Acceptance | 待建立 |
| Task Cards | 待建立 |
| Suite | 待物化 |

## 1. 目标

实现识灵的候选聚合、Review Budget 和事后可撤销策略，使用户能够：
1. 看到聚合后的候选（不重复提问同一语义变更）
2. 按审查预算控制打扰频率
3. 对低风险变更采用事后可撤销策略

## 2. 范围

### 2.1 范围内

- Candidate 聚合服务（去重、合并、价值评分）
- Review Budget 服务（时间预算、数量预算、频率控制）
- 审查分级策略（Critical/High/Normal/Low）
- 事后可撤销策略的触发条件
- CLI 扩展：review 命令查看候选列表

### 2.2 范围外（明确后置）

- Episode 聚类与分层摘要（B2）
- Commitment 提取与提醒（B3）
- 增量对账与 Semantic Diff（B4）
- 多语言对照（B5）
- 影子迁移（B6）
- 实体合并拆分（A3）
- 权限 runtime（A4）
- 决策引擎（C1）
- 连接器、同步、多设备

## 3. 模块边界

| 模块 | 责任 | 禁止责任 |
|---|---|---|
| `candidate_aggregator.py` | 候选聚合、去重、价值评分 | 不写 Canonical、不自动发布 |
| `review_budget.py` | Review Budget 计算、分级、频率控制 | 不改变候选内容、不删除证据 |
| `cli.py` | 新增 review 命令 | 不新增业务逻辑 |

## 4. 任务列表

| Task ID | 范围 | 主要场景 | 完成条件 | 当前状态 |
|---|---|---|---|---|
| `B1-TASK-001` | Candidate Aggregator 基础 | 聚合、去重、价值评分 | 候选可聚合、可评分、不重复 | `pending` |
| `B1-TASK-002` | Review Budget 服务 | 预算计算、分级策略 | 预算控制打扰频率 | `pending` |
| `B1-TASK-003` | 事后可撤销策略 | 低风险变更的 posthoc | 可撤销、明显标识 | `pending` |
| `B1-TASK-004` | CLI 扩展 | review 命令 | 用户可查看候选列表 | `pending` |
| `B1-TASK-005` | 集成测试 | 端到端链路 | 完整 B1 链路通过 | `pending` |
| `B1-TASK-006` | Verification | 统一 runner | 所有测试通过 | `pending` |
| `B1-TASK-007` | Gate Review + Recovery Point | 审计、Git tag | P0/P1=0，tag 推送 | `pending` |

## 5. 固定顺序

```
B1-TASK-001 -> B1-TASK-002 -> B1-TASK-003 -> B1-TASK-004 -> B1-TASK-005 -> B1-TASK-006 -> B1-TASK-007
```

## 6. 技术约束

- Python 3.12 标准库
- SQLite
- 不安装第三方依赖
- 不引入 ORM、Web API、通用框架

## 7. 验证

每个 Task 完成后：
- 定向语义测试
- 受影响 Micro/A1 回归测试
- Product/SPEC 静态验证
- git diff --check

---
