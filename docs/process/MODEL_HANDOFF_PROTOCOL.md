# 模型接力与交付协议

## 1. 目的

本文规定规划模型、开发模型、审计模型、Debug 模型和发布模型如何顺序接力。它是工程协作流程，不是产品内的多 Agent 或 A2A 系统。

任何模型开始前都必须读取 `AGENTS.md` 并按仓库恢复顺序工作。聊天记录不是权威状态，仓库文件和实际工具结果才是。

当前交接实例见 `CURRENT_HANDOFF.md`；可直接交给不同模型的完整提示词见 `AI_EXECUTION_PROMPTS.md`。本文件定义协议，前两者分别定义“现在做什么”和“如何向角色下达任务”。

## 2. 角色边界

| Role | 允许 | 禁止 | 完成产物 |
|---|---|---|---|
| `Planner` | Product Decision、SPEC review、Trace、ADR 候选、suite 合同、Implementation Plan | 写业务代码、伪造测试通过、替产品补规则 | 可施工的批准切片 |
| `Implementer` | 按 Approved Plan 修改指定模块和窄测试 | 改 PRD/SPEC/oracle 迎合实现、扩大切片 | Code + task verification |
| `Auditor` | 只读检查行为、测试覆盖、隐私、Git 范围 | 先改代码再给结论、以风格意见冒充 P1 | Findings + Gate recommendation |
| `Debugger` | 复现已确认缺陷、定位责任层、修复并回归 | 跳过复现、删除失败结果、降低 expected | Fix + new Verification Result |
| `Releaser` | 构建、签名、clean-install smoke、tag、push、release record | 自行改变产品语义、移动已发布 tag、公开仓库 | Recovery Point / Product Release |

同一轮可以由同一模型承担多个角色，但每次角色切换必须重新读取对应输入，并保留审计独立性；实现者不能把自己的自查称为独立审计。

## 3. 标准交接包

上一个角色必须留下：

```yaml
slice_id: stable ID
current_phase: delivery_phase value
product_baseline: path + version + hash
decision_refs: [Product Decision]
spec_refs: [versioned Approved SPEC]
traceability_ref: path
adr_refs: [Accepted ADR]
suite_manifest: path | absent
implementation_plan: path | absent
verification_result: path | not_executed
gate_review: path | absent
git_branch: branch
git_commit: commit
scope_in: [explicit]
scope_out: [explicit]
open_blockers: []
next_single_action: one action
```

缺少任何适用项时写 `absent` 或 `not_executed`，不得依赖聊天猜测。

## 4. 开发模型启动条件

开发模型只有在以下条件同时成立时才可写业务代码：

- active slice 至少为 `implementation_planned`。
- Product Decision、适用 SPEC、Trace、Accepted ADR、materialized suite 和 Approved Plan 都存在。
- `suite_executed=false` 与 `suite_passed=false` 被如实记录。
- Plan 指定了本轮唯一 Task、文件范围、验收条件和停止条件。
- 工作树相关改动可以归属；外部目录和个人资料不在范围内。

开发提示词必须要求模型完成一个或明确的一组连续 Task 后停止，不允许“顺手”实现下一路线。

## 5. 审计模型协议

审计输入至少包括：

- Approved PRD/Decision/SPEC/ADR/Plan。
- 当前 diff 和实现模块。
- suite manifest、fixture、oracle、runner 与真实 result。
- 上一次 Finding 和关闭证据。

审计输出按 P0-P3 排序，每项必须包含：稳定 Finding ID、严重度、文件/测试定位、违反的权威合同、可复现证据、影响范围、关闭条件。没有证据的偏好不得列为阻塞。

审计默认只读。若用户另行授权修复，也必须先冻结审计报告，再进入 Debug 角色。

## 6. Debug 模型协议

处理每个 Finding 的固定顺序：

1. 在未修改工作树上复现。
2. 判断责任层：fixture、oracle、SPEC、implementation、runner、环境或文档。
3. 若需要产品裁决或 SPEC 变更，停止代码修复并回上游。
4. 若为实现缺陷，添加最小回归测试并修复。
5. 运行失败场景、相关 suite 和静态基线检查。
6. 保存新 result；旧失败 result 不覆盖。
7. 审计模型复核关闭，不能由 Debug 模型单方面关闭 P0/P1。

## 7. 发布模型协议

发布模型必须确认：

- Gate Review P0=0、P1=0。
- current result 与 commit、manifest、artifact hash 匹配。
- PRD 历史未修改，隐私扫描通过。
- clean install / upgrade / rollback / smoke 真实运行。
- Release Record、支持范围和已知限制已更新。
- 只暂存当前发布文件；`.workbuddy/`、`Review-report/`、缓存和本机数据不提交。
- annotated tag 创建后推送并由远端解析；已发布 tag 不移动。

仓库从 private 变为 public、创建公开 Release 或向外部用户发通知，都需要用户明确授权。

## 8. 模型提示词骨架

### Implementer

```text
恢复仓库状态，只执行 <slice_id>/<task_id>。以 Approved Plan、SPEC、ADR、fixture/oracle 为唯一合同。不得修改产品语义、expected 或 deferred 范围。实现后运行指定验证，更新 PROJECT_STATE；未运行测试写 not_executed。
```

### Auditor

```text
对 <slice_id> 做独立只读审计。先核验产品到结果的完整追踪，再检查代码、测试、隐私和 Git 范围。Findings 按 P0-P3 排序并给可复现证据；不要修改文件，不把未运行检查写为通过。
```

### Debugger

```text
只处理审计已确认的 Finding ID。先复现并判断责任层；若涉及产品/SPEC 歧义则停止并记录。实现修复后生成新的不可覆盖 result，旧结果保留，更新关闭证据但不自行宣布独立审计通过。
```

### Releaser

```text
只执行已通过 Gate 的发布任务。核验 clean install、smoke、升级、回滚、artifact hash、隐私和 Git 范围；创建不可移动 tag 和 Recovery/Release Record，推送后验证远端。未经明确授权不得公开仓库。
```

## 9. 分支与结果策略

- 规划、实现、修复和发布可以在同一受控 feature branch 顺序进行；并行工作必须使用独立 worktree/branch。
- 每个角色提交范围单一，commit message 只描述真实完成内容。
- failed、errored、partial 和 superseded result 永久保留。
- 只有 Review Gate 通过后才能建立 Recovery Point；只有 Product Release Gate 通过后才能称为可部署版本。

## 10. 交接文件更新责任

- Planner：建立 active slice 的第一份 `CURRENT_HANDOFF.md`。
- Suite Materializer / Implementer：完成单一 Task 后，只更新真实 Task 状态和 `next_single_action`。
- Verifier：填入 current result path、commit 和 applicability，不改历史结果。
- Auditor：填入 audit report 和 open Finding IDs，不改实现状态。
- Debugger：填入修复 result 和待复审 Finding，不自行关闭 P0/P1。
- Releaser：填入 branch、commit、tag、remote verification 和下一切片入口。

任何角色发现 `CURRENT_HANDOFF.md` 与仓库事实不一致时，必须先修正文档或停止；不得按聊天中的旧任务继续。
