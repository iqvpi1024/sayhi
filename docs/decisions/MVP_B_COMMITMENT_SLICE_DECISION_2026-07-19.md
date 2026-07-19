# MVP-B Commitment 切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-MVP-B-COMMITMENT-001` |
| Date | 2026-07-19 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-B-EPISODE-SUMMARY-001`（已发布 recovery point） |
| Current Slice | `SLICE-MVP-B-COMMITMENT-001` |

## 1. 决定内容

选择 MVP-B 的 B3 Commitment 作为下一条窄切片，仅验证一个固定合成 Commitment 的受控生命周期：经 ChangeSet 创建、显式完成或带原因取消、补偿撤销，以及由确定性 clock 派生的 due-status。

## 2. 产品依据

- PRD §8：`Commitment` 是 12 个 Canonical 对象之一，`Obligation` 只是其语义配置。
- PRD §10.2-§10.4：Commitment 和提醒属于一致性/影响边界，Derived 不得伪装为事实。
- PRD §11-§12：Canonical 写入、纠正和撤销必须经过 ChangeSet 与补偿 revision。
- PRD §20 FR-104：Commitment 提取、状态和提醒。
- PRD §26 Case 4、7：结清，以及完成/取消/失效的合成验收情形。

## 3. 切片范围

- 单一固定合成 `CommitmentCandidate`，明确 Source locator、responsible entity、due time 和 synthetic profile。
- `proposed -> approved -> published`，后续 `completed | cancelled` 仅由用户确认的 ChangeSet 触发。
- `open | completed | cancelled` Canonical status 与补偿撤销历史。
- 固定 clock 下的 Derived `due_status`（如 `upcoming | due | overdue | closed`），它不写回 Canonical，且不成为 Evidence/ChangeSet trigger。

## 4. 非目标

- 自然语言提取、LLM、真实提醒推送、后台调度、日历/邮件/任务连接器、外部行动。
- 关系变化自动取消、完成、延期或重分配 Commitment。
- 自动发布、预授权自动写入、财务/健康/法律语义、权限/MCP runtime、同步和多设备。
- 完整 FR-104 或 Reminder 产品能力声明。

## 5. 不变量

- 关系状态变化不得自动改变 Commitment。
- due-status 是 Derived，不得作为事实证据或 Canonical 写入输入。
- 未确认 candidate 不得创建 Canonical Commitment 或 revision。
- 取消必须含原因；撤销使用新补偿 revision，保留发布/完成/取消历史。
- 固定 synthetic profile 外输入 fail closed 且无写入。

## 6. 授权与下一步

本决定只授权 S1/S2/S3/S5/S6/S7 的 B3 applicability review、追踪和测试合同设计。完成这些开发前产物前不得编写 B3 业务代码。
