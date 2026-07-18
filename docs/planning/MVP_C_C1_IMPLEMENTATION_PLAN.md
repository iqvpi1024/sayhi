# Implementation Plan: MVP-C C1 Decision-Outcome

## 0. 状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-MVP-C-C1-IMPL-001` |
| Status | `Draft` |
| Slice | `SLICE-MVP-C-DECISION-001` |
| Product Decision | `DEC-MVP-C-DECISION-001` |
| SPEC Review | `REVIEW-MVP-C-DECISION-SPEC-001` |
| Trace | Requirements Matrix §4.3 (待建立) |
| ADR / Architecture | 待建立 |
| Acceptance | 待建立 |
| Task Cards | 待建立 |
| Suite | 待物化 |

## 1. 目标

实现 Decision、Outcome 和 Calibration 闭环，让用户能够：
1. 记录一个 Decision（问题、选项、约束、假设、选择）
2. 记录 Decision 的 Outcome（结果、副作用）
3. 进行 Calibration（预测 vs 实际结果对比）
4. 创建情景推演（保持 predicted/fictional）

## 2. 范围

### 2.1 范围内

- Decision 对象创建（问题、选项、约束、假设、选择）
- Outcome 对象创建（结果、副作用、校准）
- Calibration 服务（预测 vs 实际对比）
- Scenario 推演（基准、乐观、悲观，保持 predicted/fictional）
- CLI 扩展：decision、outcome、scenario 命令

### 2.2 范围外（明确后置）

- Hypothesis 完整生命周期（C2）
- 周/月/年度复盘（C3）
- Context Pack 备份（C5）
- MVP 公开发布（C6）
- 健康/法律/财务专业建议
- 自动因果推断

## 3. 模块边界

| 模块 | 责任 | 禁止责任 |
|---|---|---|
| `decision.py` | Decision 对象创建、读取 | 不写 Canonical（通过 ChangeSet） |
| `outcome.py` | Outcome 记录、Calibration | 不自动填充预测结果 |
| `scenario.py` | 情景推演（predicted/fictional） | 不写入 observed |
| `cli.py` | 新增 decision/outcome/scenario 命令 | 不新增业务逻辑 |

## 4. 任务列表

| Task ID | 范围 | 主要场景 | 完成条件 | 当前状态 |
|---|---|---|---|---|
| `C1-TASK-001` | Decision 对象 | 创建、读取 Decision | Decision 可记录 | `pending` |
| `C1-TASK-002` | Outcome 对象 | 记录 Outcome | Outcome 可记录 | `pending` |
| `C1-TASK-003` | Calibration | 预测 vs 实际对比 | Calibration 可计算 | `pending` |
| `C1-TASK-004` | Scenario 推演 | 基准/乐观/悲观 | 情景保持 predicted/fictional | `pending` |
| `C1-TASK-005` | CLI 扩展 | decision/outcome/scenario 命令 | 用户可操作 | `pending` |
| `C1-TASK-006` | 集成测试 | 端到端链路 | 完整 C1 链路通过 | `pending` |
| `C1-TASK-007` | Verification | 统一 runner | 所有测试通过 | `pending` |
| `C1-TASK-008` | Gate Review + Recovery Point | 审计、Git tag | P0/P1=0，tag 推送 | `pending` |

## 5. 固定顺序

```
C1-TASK-001 -> C1-TASK-002 -> C1-TASK-003 -> C1-TASK-004 -> C1-TASK-005 -> C1-TASK-006 -> C1-TASK-007 -> C1-TASK-008
```

## 6. 技术约束

- Python 3.12 标准库
- SQLite
- 不安装第三方依赖
- 不引入 ORM、Web API、通用框架

## 7. 验证

每个 Task 完成后：
- 定向语义测试
- 受影响 Micro/A1/B1 回归测试
- Product/SPEC 静态验证
- git diff --check

---
