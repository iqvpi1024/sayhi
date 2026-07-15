# Recovery Point：prd-v05-v0.1-approved

## 1. 身份

| 字段 | 值 |
|---|---|
| Date | 2026-07-15 |
| Scope | `PRODUCT-BASELINE-V05-001` |
| Branch | `codex/prd-v05-consolidation` |
| Commit | 由 annotated tag `prd-v05-v0.1-approved` 解析 |
| Remote | `origin` |
| Remote Verification | branch/tag 推送后使用 `git ls-remote` 复核 |

## 2. 包含内容

- `PRDv05.md` Approved Product Baseline 和 current baseline index。
- v0.4→v0.5 产品整合决定、Readiness Review 与 DQ-001..013 队列。
- 产品基线专用静态校验器和最近验证结果。
- AGENTS、流程、变更控制和 PROJECT_STATE 的当前 PRD 恢复入口。

不包含 SPEC v0.5 兼容结论、SPEC 修订、suite materialization、业务代码、依赖、数据库或最终技术栈。

## 3. 门禁证据

| Evidence | Result | Reference |
|---|---|---|
| Product Decision | Approved | `DEC-PRD-V05-001` |
| PRD Readiness Review | `yes`；P0=0、P1=0 | `docs/reviews/PRD_V05_READINESS_REVIEW.md` |
| PRD v0.5 canonical LF hash | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` | `PRDv05.md` |
| PRD v0.4 immutable hash | `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` | `PRDv04.md` |
| Product Static Validation | exit code 0 | `docs/testing/LATEST_PRODUCT_VALIDATION.md` |
| LF/CRLF Portability | identical portable output | `docs/testing/LATEST_PRODUCT_VALIDATION.md` |
| SPEC Compatibility | `not_executed` | S1-S9 pending review |
| Business Tests | `not_executed` | suite/implementation absent |

## 4. 恢复步骤

```text
git fetch origin --tags
git rev-parse prd-v05-v0.1-approved^{}
git worktree add <new-worktree-path> prd-v05-v0.1-approved
cd <new-worktree-path>
powershell -ExecutionPolicy Bypass -File tools/validate_product_baseline.ps1
```

预期：tag 解析到本产品基线提交；产品静态校验 exit code 0；输出仍明确没有执行 SPEC compatibility 或业务测试。

## 5. 下一步唯一建议动作

从 S1 开始逐份执行 PRD v0.5 Compatibility Review。
