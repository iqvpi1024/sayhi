# MVP-C C1 Decision-Outcome 逐任务施工卡

## 0. 文档状态

| 字段 | 值 |
|---|---|
| Card Set ID | `CARDS-MVP-C-C1-001` |
| Slice | `SLICE-MVP-C-DECISION-001` |
| Parent Plan | `PLAN-MVP-C-C1-IMPL-001` |
| Status | `Draft Companion` |
| Product Baseline | `PRDv05.md` v0.5 Approved |

## 1. 全局执行合同

### 1.1 每个 Task 的固定开始动作

1. 完整读取 `AGENTS.md`，并按其恢复顺序读取当前权威文件。
2. 核验 `CURRENT_HANDOFF.current_phase=implementation_planned|implementing`。
3. 核验 Implementation Plan 和本卡集均为 Approved，且 `next_single_action` 恰好等于本 Task ID。
4. 运行 `git status --short --branch`，确认相关改动可归属。
5. 记录开始 HEAD、Python/SQLite/OS 版本和本 Task 适用的测试入口。

### 1.2 所有 Task 共同禁止

- 修改 `PRDv05.md`、Product Decision、Approved SPEC 或 Acceptance expected。
- 修改旧 Micro/A1/B1 fixture、oracle、历史 result 或已发布 tag。
- 从实现 actual 生成、补全或更新 oracle。
- 引入第三方依赖、ORM、Web API、UI、插件系统、服务总线、在线模型或外部服务。
- 实现权限 runtime、MCP、通用问答/RAG、通用规则引擎、冲突裁决、Canonical `value=unknown`、ChangeSet 写入或第三个 View。
- 读取真实个人数据，或新增真实姓名、地址、组织、电话、邮箱、凭据、债务、健康或亲密关系资料。
- 把定向测试通过写成 C1 suite passed。
- 覆盖 failed/errored/partial result，移动已发布 tag，或把静态检查描述为业务验证。

### 1.3 允许更新的公共记录

每个 Task 完成后只允许按真实结果更新：
- `docs/PROJECT_STATE.md`
- `docs/process/CURRENT_HANDOFF.md`
- `docs/planning/MVP_C_C1_IMPLEMENTATION_PLAN.md`
- 当前 Task 的定向验证记录

## 2. 总映射

| Task | 主要职责 | 允许文件 |
|---|---|---|
| `C1-TASK-001` | Decision 对象 | `src/noetide_micro/decision.py` |
| `C1-TASK-002` | Outcome 对象 | `src/noetide_micro/outcome.py` |
| `C1-TASK-003` | Calibration | `src/noetide_micro/outcome.py` |
| `C1-TASK-004` | Scenario 推演 | `src/noetide_micro/scenario.py` |
| `C1-TASK-005` | CLI 扩展 | `src/noetide_micro/cli.py` |
| `C1-TASK-006` | 集成测试 | `tests/semantic/test_c1_*.py` |
| `C1-TASK-007` | Verification | 验证记录 |
| `C1-TASK-008` | Gate Review + Recovery Point | 状态记录、Git tag |

## 3. C1-TASK-001: Decision 对象

### 3.1 入口门禁
- `next_single_action=C1-TASK-001`
- Implementation Plan 和 Task Cards 已 Approved

### 3.2 权威输入
- PRD §18.7 决策室
- SOM-001 §8 核心对象模型（Decision 对象）
- SPEC-CS-001 ChangeSet 生命周期

### 3.3 必须行为
1. Decision 至少包含：问题、选项、约束、假设、选择
2. Decision 通过 ChangeSet 写入 Canonical
3. Decision 状态：open -> decided -> closed
4. 记录创建时间、actor、evidence refs

### 3.4 明确禁止
- 自动选择"最优"选项（必须用户确认）
- 将预测自动填充为结果
- 替代专业意见

### 3.5 Task 验证
- 定向测试：创建、读取、状态转换
- 回归 Micro/A1/B1 测试
- 静态验证

### 3.6 完成与交接
验证通过后，下一动作=`C1-TASK-002`。

## 4. C1-TASK-002: Outcome 对象

### 4.1 入口门禁
- `C1-TASK-001=completed`
- `next_single_action=C1-TASK-002`

### 4.2 权威输入
- PRD §18.7 决策室
- SOM-001 §8 核心对象模型（Outcome 对象）

### 4.3 必须行为
1. Outcome 至少包含：结果、副作用、实际发生时间
2. Outcome 链接到对应 Decision
3. Outcome 通过 ChangeSet 写入
4. 预测不自动成为结果

### 4.4 明确禁止
- 自动填充 Outcome（必须用户记录）
- 将预测值复制为实际结果

### 4.5 Task 验证
- 定向测试：创建、链接、读取
- 回归测试

### 4.6 完成与交接
验证通过后，下一动作=`C1-TASK-003`。

## 5. C1-TASK-003: Calibration

### 5.1 入口门禁
- `C1-TASK-002=completed`
- `next_single_action=C1-TASK-003`

### 5.2 权威输入
- PRD §22.4 模型升级门禁
- FR-202 Calibration 闭环

### 5.3 必须行为
1. 比较 Decision 的预测与实际 Outcome
2. 计算校准度（预测准确度）
3. 记录校准历史
4. 不修改原始 Decision 或 Outcome

### 5.4 明确禁止
- 用校准结果自动修改未来预测
- 删除或修改历史预测

### 5.5 Task 验证
- 定向测试：校准计算、历史记录
- 回归测试

### 5.6 完成与交接
验证通过后，下一动作=`C1-TASK-004`。

## 6. C1-TASK-004: Scenario 推演

### 6.1 入口门禁
- `C1-TASK-003=completed`
- `next_single_action=C1-TASK-004`

### 6.2 权威输入
- PRD §18.7 决策室
- FR-204 情景推演
- SPEC-SHP-001 §6.5 非 Micro 对象的政策边界

### 6.3 必须行为
1. 支持三种情景：基准、乐观、悲观
2. 情景保持 `predicted`/`fictional` 类型
3. 情景不写入 `observed` Canonical
4. 情景可追溯到 Decision 和假设

### 6.4 明确禁止
- 将情景自动写入 observed
- 用情景替代实际 Outcome

### 6.5 Task 验证
- 定向测试：创建、读取、类型检查
- 回归测试

### 6.6 完成与交接
验证通过后，下一动作=`C1-TASK-005`。

## 7. C1-TASK-005: CLI 扩展

### 7.1 入口门禁
- `C1-TASK-004=completed`
- `next_single_action=C1-TASK-005`

### 7.2 必须行为
1. `noetide decision` 创建/查看 Decision
2. `noetide outcome` 记录 Outcome
3. `noetide scenario` 创建情景推演
4. `noetide calibrate` 查看校准结果

### 7.3 完成与交接
验证通过后，下一动作=`C1-TASK-006`。

## 8. C1-TASK-006: 集成测试

### 8.1 必须行为
1. 端到端测试：Decision -> Outcome -> Calibration
2. 情景推演类型检查
3. 所有 C1 场景测试通过

### 8.2 完成与交接
验证通过后，下一动作=`C1-TASK-007`。

## 9. C1-TASK-007: Verification

### 9.1 必须行为
1. 统一 runner 执行完整 C1 suite
2. Micro 回归 49/49 passed
3. A1 回归 35/35 passed
4. B1 回归 8/8 passed

### 9.2 完成与交接
验证通过后，下一动作=`C1-TASK-008`。

## 10. C1-TASK-008: Gate Review + Recovery Point

### 10.1 必须行为
1. P0/P1=0
2. 创建 Recovery Point
3. Git tag 推送

---
