# MVP-A Answer Safety Architecture v0.1 Recovery Point

## 1. 状态

`published`。A1 SPEC applicability、exact contract、Trace、ADR、Architecture、suite-only Plan、Pre-Suite Gate、annotated tag 和远端分支均已发布并可解析。

## 2. 恢复对象

| 字段 | 值 |
|---|---|
| Branch | `codex/mvp-a-answer-safety-planning` |
| Tag | `mvp-a-answer-safety-architecture-v0.1-approved` |
| Tag Target | `3c9d0fa0bee01c19219c6fbcfb8f853b701863ed` |
| Remote Tag Object | `716a9929bed81cd9e949b2558d6f01ce5bb22d5a` |
| Remote | `origin`，SSH `ssh://ssh.github.com:443/iqvpi1024/sayhi.git` |
| Parent Commit | `c4ec6b45970e00b1dd92a82aa9a1bca2a5342370` |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Product Decision | `DEC-MVP-A-AS-001` |
| Gate | `GATE-MVP-A-AS-PRE-SUITE-001` |
| Scope | A1 架构与 suite 物化门禁；无业务代码、fixture、runner 或业务 result |

## 3. 验证

在 tag target 内容上建立恢复点前实际完成：

- Product baseline static validation：exit code `0`。
- SPEC/Trace static validation：exit code `0`；275 Test IDs、133 Invariants、32 FR 主表和 185 unique refs 通过。
- A1 Acceptance/Matrix 机械比对：11 个场景、24 个唯一 upstream refs、35 个 required IDs、集合差异 0，exit code `0`。
- 既有 Micro suite artifact validation：exit code `0`；没有执行 Micro business runner。
- `git diff --check`：exit code `0`。
- A1 suite：`defined=true`、`materialized=false`、`executed=false`、`passed=false`。

完整命令、环境、诊断失败和未证明项见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

## 4. 远端核对

推送后 `git ls-remote` 返回：

```text
3c9d0fa0bee01c19219c6fbcfb8f853b701863ed  refs/heads/codex/mvp-a-answer-safety-planning
716a9929bed81cd9e949b2558d6f01ce5bb22d5a  refs/tags/mvp-a-answer-safety-architecture-v0.1-approved
3c9d0fa0bee01c19219c6fbcfb8f853b701863ed  refs/tags/mvp-a-answer-safety-architecture-v0.1-approved^{}
```

annotated tag 指向已验证规划提交。旧 `mvp-a-answer-safety-planning-v0.1-approved` 与 `micro-mvp-v0.1-validated` 未移动。

## 5. 恢复步骤

```powershell
git fetch origin --tags
git checkout mvp-a-answer-safety-architecture-v0.1-approved
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
python .\tools\validate_micro_suite.py
```

恢复后下一步只能执行 `PLAN-MVP-A-AS-SUITE-001` 的 `AS-PRE-001`，创建固定合成 fixture/oracle。不得执行 Draft Implementation Plan 的任何 `AS-TASK-*`。

## 6. 排除项

- `.workbuddy/`、`Review-report/`、缓存和工作区外资料不属于恢复点。
- 本恢复点没有 A1 业务实现或业务测试结果。
- 本恢复点不是安装包、GitHub Product Release 或一键部署版本。
