# MVP-A Answer Safety Planning v0.1 Recovery Point

## 1. 状态

`published`。规划提交、annotated tag 和远端分支均已推送并可解析。

## 2. 恢复对象

| 字段 | 值 |
|---|---|
| Branch | `codex/mvp-a-answer-safety-planning` |
| Tag | `mvp-a-answer-safety-planning-v0.1-approved` |
| Tag Target | `bf333a30b5f4df7b06c63dd6dd9dbb4569f31dca` |
| Remote | `origin`（SSH remote 已核验） |
| Parent Commit | `593aeac10ef8320c4929433126e8d12b933704a1` |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-AS-001` |
| Gate | `GATE-MVP-A-AS-PRODUCT-001` |
| Scope | 路线图、模型交接、部署门禁、A1 产品切片；无业务代码 |

## 3. 验证

- 产品基线校验：exit code `0`。
- SPEC/Trace/Micro 静态校验：exit code `0`。
- Micro suite artifact 校验：exit code `0`，不冒充 A1 业务测试。
- `git diff --check`：exit code `0`。
- A1 suite：`not_executed`，因为 suite 尚不存在。

## 4. 恢复步骤

```powershell
git fetch origin --tags
git checkout mvp-a-answer-safety-planning-v0.1-approved
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

恢复后只能进入 SPEC applicability review，不得直接开发 A1。

## 5. 排除项

`.workbuddy/`、`Review-report/`、缓存、本机数据和任何工作区外资料不属于本恢复点。该恢复点不代表应用、安装包或 GitHub Product Release 已完成。
