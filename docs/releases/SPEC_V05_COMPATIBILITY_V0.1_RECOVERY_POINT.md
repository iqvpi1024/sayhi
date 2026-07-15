# SPEC v0.5 Compatibility v0.1 Recovery Point

## 1. 标识

| 字段 | 值 |
|---|---|
| Recovery ID | `RP-SPEC-V05-COMPAT-001` |
| 日期 | 2026-07-15 |
| 分支 | `codex/spec-v05-compatibility` |
| 基础 tag | `prd-v05-v0.1-approved` |
| 内容提交 | `066d0ef55279bfe91e9bc13568c6de269460d085` |
| Recovery tag | `spec-v05-compatibility-v0.1-approved` |
| Recovery commit | 由上述 annotated tag 解析；包含本恢复记录与最终 PROJECT_STATE |
| 远端 | `origin`，SSH |

## 2. 可恢复内容

- PRD v0.5 保持 Approved 且 hash 不变；PRD v0.4 历史 hash 不变。
- S1 v0.5；S2-S6 v0.4；S7-S8 v0.3；S9 v0.4，全部 current Approved。
- PRD→SPEC→Acceptance Test 追踪已更新，32 FR 全部登记。
- Micro 保持 10 个场景和 39 个去重 required upstream Test Ref。
- Compatibility Gate Review 结论 `yes`；P0/P1/P2=0，P3=1 accepted debt。
- 没有 ADR、Implementation Plan、业务代码、数据库或依赖。

## 3. 验证证据

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

两条命令在内容提交工作树均 exit code 0。最终 LF/CRLF 两类隔离副本中的 Product/SPEC 四次运行也均 exit code 0，同类输出 digest 一致。详细 hash、digest、环境和中间诊断失败见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

业务 suite 状态继续为：

```yaml
suite_materialized: false
suite_executed: false
suite_passed: false
business_verification: not_executed
```

## 4. 恢复步骤

```powershell
git fetch origin --tags
git verify-tag spec-v05-compatibility-v0.1-approved
git switch -c restore/spec-v05-compatibility spec-v05-compatibility-v0.1-approved
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

若只需查看，不创建分支，可使用：

```powershell
git show spec-v05-compatibility-v0.1-approved:docs/PROJECT_STATE.md
```

## 5. 下一门禁

恢复后下一步仍是只为 `SLICE-MICRO-RELATIONSHIP-001` 建立最小 ADR。不得从此 tag 直接开始编码，也不得把静态 passed 解释为业务通过。
