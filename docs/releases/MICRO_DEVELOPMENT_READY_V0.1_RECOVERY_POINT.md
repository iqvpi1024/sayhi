# Micro Development Ready v0.1 Recovery Point

## 1. 标识

| 字段 | 值 |
|---|---|
| Recovery ID | `RP-MICRO-DEV-READY-001` |
| 日期 | 2026-07-16 |
| 分支 | `codex/micro-development-readiness` |
| 基础 tag | `spec-v05-compatibility-v0.1-approved` |
| 内容提交 | `581e2838093b21db6a9f80c348d3980878c275ae` |
| Recovery tag | `micro-development-ready-v0.1-approved` |
| Recovery commit | 由上述 annotated tag 解析；包含本记录、最终 PROJECT_STATE 与验证记录 |
| 远端 | `origin`，SSH |

## 2. 可恢复内容

- PRD v0.5 Approved 与 PRD v0.4 历史只读 hash 均未改变。
- S1 v0.6、S2 v0.5、S6 v0.5 的开发前一致性修订；其余 Approved SPEC 保持兼容。
- `ADR-0001`、`ARCH-MICRO-REL-001` 与 `PLAN-MICRO-REL-001`。
- exact Micro suite：10 个 MM 场景、39 个 upstream refs、固定合成 fixture、结构化 oracle、adapter protocol、离线 runner 和 manifest。
- suite manifest SHA-256：`54d70b993dbd5ce117605f6b07c305d2b97eba67df6a782c0e75f3afc28a5390`。
- 开发前 Gate Review 结论 yes，P0=0、P1=0。

不包含业务实现、第三方依赖、数据库实例、真实个人数据或业务 Verification Result。

## 3. 验证证据

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
python .\tools\validate_micro_suite.py
powershell -ExecutionPolicy Bypass -File .\tools\validate_pre_development_gate.ps1
git diff --check
```

最终预期均 exit code 0。环境、工具 hash、输出 digest、诊断失败和限制见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

业务状态：

```yaml
suite_defined: true
suite_materialized: true
suite_executed: false
suite_passed: false
business_verification: not_executed
```

## 4. 限制

- 本 tag 只证明开发前产物闭合，不能证明业务原子性、历史查询、View 一致性、撤销或性能。
- SQLite/Python 只为当前 Micro 切片 Accepted，不是长期最终技术栈。
- `.workbuddy/` 与 `Review-report/` 等本地未跟踪目录不属于恢复点。
- annotated tag 未配置 GPG 签名，不使用 `git verify-tag` 冒充签名验证。

## 5. 恢复步骤

```powershell
git fetch origin --tags
git cat-file -t micro-development-ready-v0.1-approved
git rev-parse 'micro-development-ready-v0.1-approved^{}'
git switch -c restore/micro-development-ready micro-development-ready-v0.1-approved
powershell -ExecutionPolicy Bypass -File .\tools\validate_pre_development_gate.ps1
```

`git cat-file -t` 预期为 `tag`，Gate 预期 exit code 0。恢复后业务状态仍必须是 `not_executed`。

若只需查看状态：

```powershell
git show micro-development-ready-v0.1-approved:docs/PROJECT_STATE.md
```

## 6. 下一步唯一动作

执行 `PLAN-MICRO-REL-001` 的 TASK-001：只建立 package、SQLite Schema 和 `store.py` 基础，不跨任务实现 Intake、Candidate、View 或业务链路。
