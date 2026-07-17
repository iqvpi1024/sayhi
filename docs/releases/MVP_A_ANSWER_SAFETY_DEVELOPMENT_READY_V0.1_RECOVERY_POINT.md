# MVP-A Answer Safety Development Ready v0.1 Recovery Point

## 0. 元数据

| 字段 | 值 |
|---|---|
| Recovery ID | `RECOVERY-MVP-A-AS-DEV-READY-001` |
| Date | 2026-07-17 |
| Remote | `origin` = `ssh://git@ssh.github.com:443/iqvpi1024/sayhi.git` |
| Branch | `codex/mvp-a-answer-safety-planning` |
| Content Commit | `7e28546c3f1766afeb5c3524bc55a97ff1102e3f` |
| Handoff / Tag Target Commit | `80a920aa8f07571bb866ce223039033c56b5dd72` |
| Annotated Tag | `mvp-a-answer-safety-development-ready-v0.1-approved` |
| Remote Tag Object | `443f539bb4789dfe76dbe0d50392374a14d0d36c` |
| Remote Tag Peel | `80a920aa8f07571bb866ce223039033c56b5dd72` |
| Product | `PRDv05.md` v0.5 Approved |
| A1 Manifest SHA-256 | `759878a902c46f2b1eb424eb3146561d09b75ddb780dd697bc0cca598d2e32fc` |

这是开发前工程恢复点，不是 A1 业务验证、普通用户安装包或公开 Product Release。

## 1. 恢复点包含

- `CARDS-MVP-A-AS-001`：`AS-TASK-001..009` 逐任务施工合同。
- `PLAN-MVP-A-AS-IMPL-001 Approved`。
- A1 manifest、11 个隔离合成 case、字段级 oracle、scenario plan、adapter protocol、semantic tests、offline runner 和 validator。
- `GATE-MVP-A-AS-SUITE-001` 与 `GATE-MVP-A-AS-DEVELOPMENT-READY-001`，均 P0=0/P1=0。
- `CURRENT_HANDOFF.next_single_action=AS-TASK-001`。
- Product/SPEC/Micro/A1 静态验证和 AS-011 result-writer bootstrap 记录。

## 2. 恢复点不证明

```yaml
a1_business_implementation: absent
a1_suite_executed: false
a1_suite_passed: false
a1_verification_result: not_executed
micro_regression_on_a1_implementation: not_executed
ui_api_permission_mcp_deployment: absent
```

不得用上一 Micro 的 49/49 historical pass 代替 A1 35/35，也不得把 suite materialized 描述为业务 passed。

## 3. 远端核验

实际执行：

```powershell
git push origin codex/mvp-a-answer-safety-planning
git push origin refs/tags/mvp-a-answer-safety-development-ready-v0.1-approved
git ls-remote origin 'refs/heads/codex/mvp-a-answer-safety-planning' 'refs/tags/mvp-a-answer-safety-development-ready-v0.1-approved' 'refs/tags/mvp-a-answer-safety-development-ready-v0.1-approved^{}'
```

结果：三个命令 exit code 均为 `0`。远端 branch 与 peeled tag 均解析到 `80a920aa8f07571bb866ce223039033c56b5dd72`；tag object 为 `443f539bb4789dfe76dbe0d50392374a14d0d36c`。旧 tags 未移动。

## 4. 恢复步骤

```powershell
git fetch origin codex/mvp-a-answer-safety-planning --tags
git rev-parse mvp-a-answer-safety-development-ready-v0.1-approved^{}
git cat-file -t mvp-a-answer-safety-development-ready-v0.1-approved
git worktree add <empty-recovery-path> mvp-a-answer-safety-development-ready-v0.1-approved
```

期望：`rev-parse` 输出 `80a920aa8f07571bb866ce223039033c56b5dd72`，`cat-file -t` 输出 `tag`。恢复 worktree 后先按 `AGENTS.md` 读取状态，不得直接写代码。

## 5. 恢复后重验

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
python .\tools\validate_micro_suite.py
python .\tools\validate_answer_safety_suite.py
python -m py_compile tests/runner/answer_safety_adapter_protocol.py tests/semantic/test_answer_safety_contract.py tests/runner/run_answer_safety_suite.py tools/validate_answer_safety_suite.py
git diff --check
```

前四类静态/编译检查期望 exit code `0`；A1 validator 必须继续输出 `NOT_EXECUTED: Answer Safety business runner`。不得在恢复验证中运行完整 A1 runner并声称通过。

## 6. 范围与隐私

- `.workbuddy/`、`Review-report/`、`tmp/`、`__pycache__/` 和本机资料不属于恢复点。
- PRD v0.4/v0.5、Approved SPEC、`src/noetide_micro` 和旧 Micro expected 未在本恢复点修改。
- 新 fixture/oracle 只含中性合成数据；无网络、真实个人数据或第三方依赖。

## 7. 下一步唯一动作

由 Implementer 按 Approved Plan、Approved Task Cards 和 `CURRENT_HANDOFF` 只执行 `AS-TASK-001`；完成后停止，不得开始 `AS-TASK-002`。
