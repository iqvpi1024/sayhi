# Micro Relationship Architecture View

## 0. 元数据

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-MICRO-REL-001` |
| Slice | `SLICE-MICRO-RELATIONSHIP-001` |
| Status | `Accepted Design Baseline` |
| Date | `2026-07-16` |
| PRD | `PRDv05.md` v0.5 |
| SPEC | S1 v0.6；S2 v0.5；S3-S5 v0.4；S6 v0.5；S7-S8 v0.3；S9 v0.4 |
| ADR | `ADR-0001` |
| Verification | `not_executed` |

本文只描述当前 Micro 组件责任，不证明实现存在或测试通过。

## 1. 组件责任

| 组件 | 责任 | 明确非责任 |
|---|---|---|
| `FixtureLoader` | 加载版本化合成 fixture、固定 Clock 与 failure plan | 不读取工作区外文件，不生成 expected |
| `IntakeService` | 校验 synthetic text、初始化 policy、原子保存 Source 与 Append Receipt | 不解析为事实，不写 Canonical |
| `ContactCandidateBuilder` | 从唯一固定 Source 构造 allowlisted contact Candidate/ChangeSet | 不做通用 NLP，不修改 protected semantics |
| `ChangeSetService` | review、approve、preflight、publish、idempotency、receipt、revert | 不绕过权限/状态机，不直接读写 View 作为事实 |
| `SemanticStore` | 提供 Source/Canonical/Ledger/Projection 的逻辑分层和事务边界 | 不用触发器创造业务语义，不暴露数据库作为事实接口 |
| `CoreViewProjector` | 更新人物卡和关系时间线，记录 actual revision/freshness | 不生成 Evidence Ref，不回写 Canonical |
| `CoreViewReader` | 返回 fresh View、current Canonical fallback 或 updating/unavailable | 不把旧 payload 冒充 current |
| `MicroRunner` | 编排 `MM-001..010`、failure injection、actual capture 与 oracle compare | 不从实现生成 expected，不汇总跨 run 的 required pass |

## 2. 数据与信任边界

```text
synthetic fixture + fixed Clock
        |
        v
  IntakeService ------> Source + Append Receipt
        |
        v
ContactCandidateBuilder ---> Candidate / proposed ChangeSet
        |
        v
 ChangeSetService -- single SQLite transaction --> Canonical + Revision + receipt summary
        |
        +------> person_card projector
        |
        +------> relationship_timeline projector
                         |
                         v
                   CoreViewReader
```

- SQLite 是当前切片的物理事务载体；Source、Canonical、Ledger、Projection 仍是独立逻辑域。
- 只有 `ChangeSetService` 能写 Canonical；只有 `CoreViewProjector` 能写 Projection。
- `CoreViewReader` 不把 Projection、receipt 或 ChangeSet 当 Evidence Ref。
- 所有输入、数据库、actual result 和日志位于测试运行的仓库内临时根；网络访问为零。

## 3. 写入路径

1. `IntakeService` 使用固定 profile 保存 58-byte UTF-8 Source 与 stored receipt；失败返回 rejected 且不解析。
2. `ContactCandidateBuilder` 只创建 end old State + add no_contact State 两个原子 proposal。
3. 用户确认事件使 ChangeSet 进入 approved，但不直接改变 Canonical。
4. `ChangeSetService` 先建立可恢复 Publish Attempt/idempotency binding，再执行 revision/digest/reference/protected-path preflight。
5. preflight 通过后，一个 SQLite transaction 发布两个 proposal、增加一次 revision、绑定 ChangeSet outcome 与 receipt summary。
6. transaction 提交后分别更新两个 L2 Projection；每项实际结果追加到 receipt。

## 4. 读取与一致性

- Canonical current/historical 查询按 valid time 和 recorded time读取，不覆盖旧 State。
- fresh Projection 必须声明 `data_revision=view_revision=current data_revision`。
- 任一 L2 失败时，不返回旧 payload；读取 current Canonical fallback，或返回无旧 payload 的 updating/unavailable。
- Publish Barrier 以同会话观察新 Canonical 或明确不可用为完成条件；5 秒只作为后续 SLO 测量。

## 5. 失败与恢复

| 注入点 | 安全结果 |
|---|---|
| Source 持久化失败 | rejected receipt；无 Source、Candidate 或 Canonical 写入 |
| proposal 2 写入失败 | 整个 L1 transaction rollback；revision 不增加 |
| stale `base_revision` | conflicted attempt/receipt；不进入 publishing |
| 非冲突 preflight failure | failed attempt/receipt；无 L1 写入 |
| 单个 Projection 失败 | L1 保留；失败 View updating/unavailable 或 Canonical fallback |
| compensation 前出现介入变更 | conflict；不覆盖介入变更 |
| compensation 成功 | 新 revision 恢复发布前等价语义；发布和撤销历史均保留 |

## 6. 审计路径

- Source receipt、Candidate、ChangeSet、review event、Publish Attempt、revision、传播项和 compensation 都有 stable ID。
- runner 保存命令、环境、起止时间、exit code、actual/expected digest、失败断言和隐私扫描结果。
- 失败 run 与旧 result 不被覆盖；新 run 使用新 `run_id`。

## 7. 排除范围

不包含权限 runtime、MCP、连接器、在线模型、通用解析、模糊时间、实体消歧、提醒、Commitment、财务、健康、决策、迁移、多设备、同步、多租户、多 Agent、A2A、数字遗产、向量库或图数据库。

## 8. 风险与待验证假设

- Python/SQLite 组合尚未执行任何业务场景。
- SQLite 的事务边界必须由故障注入证明，不能由 ADR 宣称。
- Projection fallback 必须证明不会从旧 View 拼接 current 答案。
- 物理表 Schema 仍需 Implementation Plan 限定；任何新增状态/字段语义必须回到 SPEC。
