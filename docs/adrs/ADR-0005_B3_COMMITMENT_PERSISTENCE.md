# ADR-0005：B3 Commitment 的最小持久化与 due-status 分层

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Slice | `SLICE-MVP-B-COMMITMENT-001` |
| Contract | `SPEC-B3-COMMITMENT-001` |

## 决定

复用现有 Python 标准库 + SQLite runtime 与 ChangeSet Ledger。Commitment 作为 Canonical 对象，经显式 ChangeSet 写入；`due_status` 作为可删除、可重建的 Derived projection，输入仅为 Canonical Commitment、直接 Source locator、明确的固定 clock 与 data revision。

## 不采用的方案

- 后台通知/队列/cron：会提前引入真实提醒调度与失败重试产品语义。
- 将 due-status 写回 Commitment：会把 clock 计算伪装为 Canonical 事实并制造无用户确认 revision。
- 外部日历/任务服务：超出固定合成、离线切片范围。

## 后果与验证

- Canonical 状态变更使用现有事务、foreign key、`DELETE/FULL` SQLite PRAGMA 与补偿 revision。
- Derived 行可独立删除；rebuild 失败只产生 stale/unavailable receipt。
- B3 suite 必须证明：关系变化不自动改变 Commitment，due projection 不能当 evidence/trigger，删除后等价重建。
