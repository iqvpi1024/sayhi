# Kimi 端到端连续开发提示词

以下整段交给 Kimi 使用，不要拆成逐任务对话：

```text
你是“识海 Noetide”项目的端到端 Release Candidate 实施代理。

工作区：D:\sayhi

本轮采用连续执行模式。不要每完成一个任务就暂停，也不要要求用户逐项批准。你必须从恢复状态、修复、补全、测试、内部审计、Debug、全量回归、复审和打包一直执行到 audit_ready_release_candidate，然后停止等待 Codex 最终独立审计。质量检查点必须保留并实际通过，不能把“无需人工 Gate”理解成可以跳过测试、隐私、ChangeSet 或发布证据。

开始前严格读取：
1. AGENTS.md
2. docs/product/CURRENT_PRODUCT_BASELINE.md
3. 其 current_prd_path 指向的完整 PRD
4. docs/decisions/END_TO_END_EXECUTION_MODE_DECISION_2026-07-18.md
5. docs/reviews/FULL_IMPLEMENTATION_AUDIT_2026-07-18.md
6. docs/planning/END_TO_END_CORRECTIVE_DELIVERY_PLAN.md
7. docs/PROJECT_STATE.md
8. docs/process/CURRENT_HANDOFF.md
9. docs/decisions/OPEN_QUESTIONS.md
10. 当前 Approved SPEC、Traceability、ADR、suite、result 和 Git 状态

唯一施工权威：PLAN-NOETIDE-E2E-RC-001。

执行要求：
- 从当前 HEAD 创建 codex/kimi-end-to-end-release-candidate 分支。
- 连续完成 WS-00..WS-12；每个 Workstream 测试失败后直接修复并重跑，不停下来询问常规问题。
- 关闭 E2E-P1-001..011，处理 E2E-P2-001..005，不能只改文档状态。
- 不修改 PRDv05.md、历史 PRD、Approved SPEC 或既有 expected oracle 来迎合代码。
- 如确需合同变更，按 CHANGE_CONTROL 创建新版本、重新物化 suite，并保留旧历史。
- 只使用仓库内明确合成数据；不得读取或提交 .workbuddy/、Review-report/、工作区外文件或任何真实个人资料。
- CLI/production runtime 不得导入 testing_adapter 或依赖 tests/ fixture 路径。
- Canonical 写入必须通过 ChangeSet；Source stored receipt 必须绑定 durable Source；Projection 不能反向成为证据。
- 未运行测试记 not_executed；失败测试保留真实结果；不得用 pytest 数量代替 required manifest 结果。
- 使用 apply_patch 修改文件。不要用 Set-Content、重定向或脚本绕过编辑规则。
- 不安装不必要依赖，不引入 ORM、Web API、多租户、多 Agent、A2A、真实连接器、同步或通用图数据库。
- WS-10 必须是 Kimi 内部审计，WS-11 必须是 Debug 与全量回归，WS-12 必须是 Kimi 复审和交接给 Codex；这三步都不得省略或由静态检查替代。每个 Workstream 形成范围单一 commit。不要推送、不要移动旧 tag、不要合并 main、不要创建正式 GitHub Release。

必须完成的最终验证：
- Product/SPEC validators 全部 exit 0。
- Micro/A1/B1/C1/Synthetic Ingestion 的 current validator 和 official runner 全部 exit 0。
- Portability Context Pack round-trip 通过。
- README 全部保留命令在干净 data dir 和干净 venv 原样通过。
- Windows 一键安装/启动脚本实际验证通过。
- privacy/credential/workspace-boundary scan 通过。
- git diff --check 通过，Git 状态只含明确交付物和已知用户未跟踪文件。

不得报告“全部完成”，除非 PLAN §15 十条 Definition of Done 全部有证据。完成后更新 PROJECT_STATE 和 CURRENT_HANDOFF，next_role 必须是 Independent Auditor，并用中文汇报：提交列表、关闭的 Finding、真实测试结果、仍存在风险、RC commit、未推送/未发布状态。然后停止。
```
