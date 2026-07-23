# A4 Access Policy Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-A4-ACCESS-POLICY-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-A-ACCESS-POLICY-001` |
| ADR | `ADR-0008` |

```text
fixed synthetic AccessRequest
  -> Access Policy Evaluator (pure function)
       inputs: fixture Grants + object policy labels (sensitivity/compartments, read-only)
       rules: grant validity -> scope match -> field allow-intersect/deny-union -> sealed exclusion
  -> PolicyDecision (in-memory Derived: allow | allow_with_redaction | deny + non-leaking reason_code)
  -> zero writes: no revision, no Canonical mutation, no persisted decision
```

- Evaluator 不持有 store 写路径；对象标注只读。
- Grant 由 fixture 注入；无 Grant 存储、无生命周期管理。
- Derived View 查询入口在判决之后；视图内容永不作为权限证据。
- 任何求值失败 fail closed 为 `deny`，不返回部分字段。
