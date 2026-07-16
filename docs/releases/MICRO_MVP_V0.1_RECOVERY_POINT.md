# Micro-MVP v0.1 Recovery Point

## 1. 状态

`pending_publish`。本记录先固定恢复合同；只有 annotated tag 创建、推送且远端可解析后，才可改为 `published`。

## 2. 恢复对象

| 字段 | 值 |
|---|---|
| Branch | `codex/micro-development-readiness` |
| Planned tag | `micro-mvp-v0.1-validated` |
| Verified implementation commit | `195a8fb2dfe3716c1f97a19edd8d7ec5c34d80de` |
| Business result | `docs/testing/results/micro-task009-lf-20260717.json` |
| Business result SHA-256 | `20fabfafb061c20fcf1d941c0e84b191ea9bb32be28769aadeaab961a10f2817` |
| Scope | 仅合成 Micro RelationshipState 变更链路 |

tag 指向的恢复提交包含实现与验证记录；业务 runner 的 `git_commit` 指向执行时的实现提交。验证记录是该提交的可审计证据，后续只增加 Gate/Recovery 元数据，不修改已验证业务源码或 fixture/oracle。

## 3. 恢复与复验

```powershell
git fetch origin --tags
git checkout micro-mvp-v0.1-validated
$env:PYTHONPATH='src'; python -m tests.runner.run_micro_suite --adapter noetide_micro.testing_adapter --output docs/testing/results/<new-run-id>.json
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

新运行必须使用不存在的 `<new-run-id>.json`，不得覆盖历史 Verification Result。

## 4. 排除项

`.workbuddy/`、`Review-report/`、`tmp/`、`__pycache__/` 和任何本地未跟踪文件不属于恢复点。恢复点不包含真实个人数据、外部网络访问、权限 runtime、同步、连接器或其他 deferred 能力。
