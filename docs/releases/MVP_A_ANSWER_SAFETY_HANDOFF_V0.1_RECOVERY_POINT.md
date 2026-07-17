# MVP-A Answer Safety Handoff v0.1 Recovery Point

## 1. 状态

`published`。当前交接包、多角色提示词、总路线、部署责任链、annotated tag 和远端分支均已发布并可解析。

## 2. 恢复对象

| 字段 | 值 |
|---|---|
| Branch | `codex/mvp-a-answer-safety-planning` |
| Tag | `mvp-a-answer-safety-handoff-v0.1-approved` |
| Tag Target | `5f81f1f6634b07f8890d26f4f84df9322f622e72` |
| Remote Tag Object | `eaf1cbf1f24cab3cd72d0d8eac8806a2a4c3b492` |
| Remote | `origin`，SSH `ssh://ssh.github.com:443/iqvpi1024/sayhi.git` |
| Parent Commit | `264d975271f91f1118238f78fa8fb37303e8caa0` |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Current Phase | `architecture_decided` |
| Current Action | `AS-PRE-001` |
| Scope | 规划、交接、提示词和部署责任链；无业务代码、suite 工件或业务 result |

## 3. 验证

在 tag target 内容上建立恢复点前实际完成：

- Product baseline static validation：exit code `0`。
- SPEC/Trace static validation：exit code `0`；275 Test IDs、133 Invariants、32 FR 主表和 185 unique refs 通过。
- A1 Acceptance/Matrix：11 个场景、24 个唯一 upstream refs、35 个 required IDs、集合差异 0。
- 既有 Micro suite artifact validation：exit code `0`；没有执行 Micro business runner。
- Current Handoff 标准字段缺失 0；9 类角色提示词缺失 0。
- 受保护 PRD/SPEC/源码/测试工件改动 0；`git diff --check` exit code `0`。
- A1 仍为 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。

## 4. 远端核对

```text
5f81f1f6634b07f8890d26f4f84df9322f622e72  refs/heads/codex/mvp-a-answer-safety-planning
eaf1cbf1f24cab3cd72d0d8eac8806a2a4c3b492  refs/tags/mvp-a-answer-safety-handoff-v0.1-approved
5f81f1f6634b07f8890d26f4f84df9322f622e72  refs/tags/mvp-a-answer-safety-handoff-v0.1-approved^{}
```

旧 planning、architecture 和 Micro tags 均未移动。

## 5. 恢复步骤

```powershell
git fetch origin --tags
git checkout mvp-a-answer-safety-handoff-v0.1-approved
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
python .\tools\validate_micro_suite.py
```

恢复后必须读取 `docs/process/CURRENT_HANDOFF.md`，只执行 `AS-PRE-001`。不得直接使用 Implementation Plan 的 `AS-TASK-*`。

## 6. 排除项

- `.workbuddy/`、`Review-report/`、缓存、本机数据和工作区外资料不属于恢复点。
- 本恢复点不证明 A1 业务实现或业务测试通过。
- 本恢复点不是安装包、公开 GitHub Product Release 或一键部署版本。
