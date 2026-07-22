# ADR-0006：A2 current_state 的 Derived 投影最小持久化

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Slice | `SLICE-MVP-A-CURRENT-STATE-001` |
| Contract | `SPEC-A2-CURRENT-STATE-001` |

## 决定

复用现有 Python 标准库 + SQLite runtime 与 `projection_rows` 分层。`current_state` 作为第三个 Core View 以 Derived projection 持久化：输入仅为 Canonical 对象（entity/relationship/state/assertion）、直接 Source、fixture clock 与 data revision。Canonical 变更沿用既有 ChangeSet 边界；视图构建/重建不产生新 Canonical revision。

## 不采用的方案

- 通用查询引擎/索引层：会提前引入查询语言与平台化抽象。
- 将"当前有效"缓存写回 Canonical：会把视图计算伪装为事实并制造无确认 revision。
- 新建独立数据库或外部缓存服务：超出固定合成、离线切片范围。

## 后果与验证

- 投影行可独立删除；rebuild 失败只产生 stale/unavailable receipt；fresh 判定严格依赖 `data_revision == view_revision == 当前全局 revision`。
- "当前有效"判定为纯函数：`valid_time.start <= clock` 且 `end` 为 `null` 或 `> clock`；历史区间永不进入 payload。
- A2 suite 必须证明：stale 不伪装 current、删除后等价重建、投影内容不能当 evidence/trigger、非合成输入 fail closed。
