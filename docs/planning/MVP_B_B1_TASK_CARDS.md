# MVP-B B1 Candidate Review 逐任务施工卡

## 0. 文档状态

| 字段 | 值 |
|---|---|
| Card Set ID | `CARDS-MVP-B-B1-001` |
| Slice | `SLICE-MVP-B-SHILING-001` |
| Parent Plan | `PLAN-MVP-B-B1-IMPL-001` |
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
- 修改旧 Micro fixture、oracle、历史 result 或已发布 tag。
- 从实现 actual 生成、补全或更新 oracle。
- 引入第三方依赖、ORM、Web API、UI、插件系统、服务总线、在线模型或外部服务。
- 实现权限 runtime、MCP、通用问答/RAG、通用规则引擎、冲突裁决、Canonical `value=unknown`、ChangeSet 写入或第三个 View。
- 读取真实个人数据，或新增真实姓名、地址、组织、电话、邮箱、凭据、债务、健康或亲密关系资料。
- 把定向测试通过写成 B1 suite passed。
- 覆盖 failed/errored/partial result，移动已发布 tag，或把静态检查描述为业务验证。

### 1.3 允许更新的公共记录

每个 Task 完成后只允许按真实结果更新：
- `docs/PROJECT_STATE.md`
- `docs/process/CURRENT_HANDOFF.md`
- `docs/planning/MVP_B_B1_IMPLEMENTATION_PLAN.md`
- 当前 Task 的定向验证记录

## 2. 总映射

| Task | 主要职责 | 允许文件 |
|---|---|---|
| `B1-TASK-001` | Candidate Aggregator | `src/noetide_micro/candidate_aggregator.py` |
| `B1-TASK-002` | Review Budget | `src/noetide_micro/review_budget.py` |
| `B1-TASK-003` | Posthoc Revertible | `src/noetide_micro/review_budget.py` |
| `B1-TASK-004` | CLI review command | `src/noetide_micro/cli.py` |
| `B1-TASK-005` | Integration tests | `tests/semantic/test_b1_*.py` |
| `B1-TASK-006` | Verification | 验证记录 |
| `B1-TASK-007` | Gate Review + Recovery Point | 状态记录、Git tag |

## 3. B1-TASK-001: Candidate Aggregator

### 3.1 入口门禁
- `next_single_action=B1-TASK-001`
- Implementation Plan 和 Task Cards 已 Approved

### 3.2 权威输入
- SPEC-SHP-001 §6.1 Candidate Envelope
- SPEC-SHP-001 §7 状态机
- SPEC-SHP-001 §8 允许/禁止转换

### 3.3 必须行为
1. 接收多个 Candidate，按 `candidate_kind` + `source_refs` + `proposed_value` 去重
2. 计算 Value Score（影响范围、风险、时效性、重复次数）
3. 聚合后生成单一 Review Item
4. 不修改 Canonical、不自动发布

### 3.4 明确禁止
- 模型直接 confirmed/verified
- 预算不足删除高价值证据
- 被拒候选改写成别的类型绕过

### 3.5 Task 验证
- 定向测试：聚合、去重、评分、不重复
- 回归 Micro/A1 测试
- 静态验证

### 3.6 完成与交接
全部验证通过后，Task=`completed`，下一动作=`B1-TASK-002`。

## 4. B1-TASK-002: Review Budget

### 4.1 入口门禁
- `B1-TASK-001=completed`
- `next_single_action=B1-TASK-002`

### 4.2 权威输入
- SPEC-SHP-001 §6.3 Review Budget
- PRD §15.3 审查策略

### 4.3 必须行为
1. 新用户单次最多 3 个高价值问题
2. 稳定使用每周中位审查目标不超过 5 分钟
3. 高价值积压超预算时停止生成低价值语义候选
4. 预算只影响提示时机，不影响证据、状态或权限

### 4.4 明确禁止
- 预算不足时自动删除候选
- 预算不足时降低风险等级
- 预算控制 Canonical 状态

### 4.5 Task 验证
- 定向测试：预算计算、分级、频率控制
- 回归测试

### 4.6 完成与交接
验证通过后，下一动作=`B1-TASK-003`。

## 5. B1-TASK-003: Posthoc Revertible

### 5.1 入口门禁
- `B1-TASK-002=completed`
- `next_single_action=B1-TASK-003`

### 5.2 权威输入
- SPEC-SHP-001 §6.2 Risk 与 Review Priority
- SPEC-SHP-001 §6.5 非 Micro 对象的政策边界

### 5.3 必须行为
1. 确定性机器元数据（hash、bytes）可按授权自动发布
2. 低风险机械变更可事后可撤销
3. 明显标识 posthoc 变更
4. 用户可随时撤销，恢复一致状态

### 5.4 明确禁止
- Canonical personal semantics 以 posthoc 先发布
- Micro contact 始终单次确认
- 高风险个人语义自动发布

### 5.5 Task 验证
- 定向测试：自动发布、撤销、标识
- 回归测试

### 5.6 完成与交接
验证通过后，下一动作=`B1-TASK-004`。

## 6. B1-TASK-004: CLI Review Command

### 6.1 入口门禁
- `B1-TASK-003=completed`
- `next_single_action=B1-TASK-004`

### 6.2 必须行为
1. `noetide review` 显示当前候选列表
2. 显示每个候选的 value score、risk level、review priority
3. 显示预算状态

### 6.3 完成与交接
验证通过后，下一动作=`B1-TASK-005`。

## 7. B1-TASK-005: Integration Tests

### 7.1 必须行为
1. 端到端测试：多个 Source -> 聚合 -> Review Budget -> 用户查看 -> 确认/撤销
2. 所有 B1 场景测试通过

### 7.2 完成与交接
验证通过后，下一动作=`B1-TASK-006`。

## 8. B1-TASK-006: Verification

### 8.1 必须行为
1. 统一 runner 执行完整 B1 suite
2. Micro 回归 49/49 passed
3. A1 回归 35/35 passed

### 8.2 完成与交接
验证通过后，下一动作=`B1-TASK-007`。

## 9. B1-TASK-007: Gate Review + Recovery Point

### 9.1 必须行为
1. P0/P1=0
2. 创建 Recovery Point
3. Git tag 推送

---
