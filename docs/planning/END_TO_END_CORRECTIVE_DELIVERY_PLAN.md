# Noetide 端到端修正与 Release Candidate 总施工计划

## 0. 文档状态

| 字段 | 值 |
|---|---|
| Plan ID | `PLAN-NOETIDE-E2E-RC-001` |
| Status | `Approved for continuous execution` |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Process Decision | `DEC-E2E-EXEC-001` |
| Audit Input | `AUDIT-NOETIDE-IMPL-20260718-001` |
| Manual task approval | `not_required` |
| Final target | `audit_ready_release_candidate` |
| Public release | 独立审计通过前禁止 |

## 1. 最终目标

交付一个可在干净 Windows 环境从仓库安装、使用本地 SQLite、完成批准的合成端到端链路、导出可移植 Context Pack、运行全部 current suite，并能由独立审计者复现结果的 Release Candidate。

本计划不把 PRD 全部 32 条 FR 宣称为完成。Release Candidate 必须明确列出 implemented、specified_not_implemented 和 deferred 能力，不得用版本号或 README 掩盖范围。

## 2. 全局执行规则

1. 从当前 HEAD 创建独立 `codex/kimi-end-to-end-release-candidate` 分支；不触碰用户未跟踪文件。
2. 连续执行全部 Workstream，不因单项通过停下来等待用户。
3. 每个 Workstream 结束立即运行定向测试和所有受影响回归；失败直接修复。
4. 不修改 PRD、Approved SPEC 和既有 expected oracle 来迎合实现。
5. 必须修改合同时，先按 Change Control 创建新版本和 applicability 复核，不覆盖历史。
6. 只使用仓库内合成数据；不得读取 `.workbuddy/`、`Review-report/` 和工作区外资料。
7. Runtime 保持 Python 3.12 stdlib + SQLite；build/test 工具必须与 runtime dependency 分开说明。
8. 每个持久对象写入必须遵守 Source append 或 ChangeSet 合同；View 不得成为事实证据。
9. 每个失败路径必须有稳定错误码、非 0 CLI exit code和不泄露内部 traceback 的用户输出。
10. 不推送、不移动旧 tag、不合并 `main`、不创建正式 Release；完成后交独立审计。

## 3. Workstream 总表

| Workstream | 目标 | 关键交付物 | 完成条件 |
|---|---|---|---|
| `WS-00` | 状态与证据复位 | current state/handoff/matrix/manifest 对齐 | 无相互冲突状态；旧错误结果保留但标记 superseded |
| `WS-01` | Micro L1 修正 | 单一恢复事务、完整 preflight、CS-AT-031 测试 | crash boundary、digest/ref/protected failure 和 49-ID mapping 诚实通过 |
| `WS-02` | A1 重新闭环 | current manifest、validator、result、Gate | validator 0；35/35 同 commit；result 被 Git 跟踪且 hash 可复算 |
| `WS-03` | 生产 runtime 与 CLI | production factory、data dir、错误模型、真实 README 流程 | 不再调用 test-only adapter；干净目录全链路成功 |
| `WS-04` | B1 Candidate Review | Candidate persistence、聚合、预算、review action、受控 posthoc | S5 字段/状态/失败合同与 materialized suite 全通过 |
| `WS-05` | C1 Decision/Outcome | Decision/Outcome ChangeSet、Scenario Assertion、Calibration、CLI | Canonical 写入、历史、证据、撤销和端到端 suite 全通过 |
| `WS-06` | Synthetic Ingestion | durable Source append、duplicate/rejected、policy receipt | stored 只在 durable 成功后返回；无默认 synthetic 放行 |
| `WS-07` | Portability | Context Pack JSON/Markdown/Source/checksums/import verifier | export 可独立读取，round-trip 不丢 required/unknown 字段 |
| `WS-08` | Packaging | install metadata、license、module/console entry、one-click scripts | 新建干净 venv 后本地安装、启动、卸载和重装可复现 |
| `WS-09` | 完整验证 | suite、CLI、package、privacy、recovery rehearsal | 所有 required 同一 RC commit 通过，无 required skip |
| `WS-10` | Kimi 内部审计 | finding 台账、独立复验命令、范围和风险核对 | 当前 RC 无 P0/P1，所有声明均有可复现证据 |
| `WS-11` | Debug 与全量回归 | P0/P1 修复、完整 result、失败保留记录 | WS-10 finding 关闭或诚实降级，所有 required 同一 commit 通过 |
| `WS-12` | Kimi 复审与审计交接 | RC record、diff、风险、复验命令、handoff | `audit_ready_release_candidate`，交给 Codex 最终独立审计 |

## 4. WS-00 状态与证据复位

- 将 A1 旧 result 标记为 superseded，不删除历史。
- 更新 A1 manifest 的真实 flags、implementation module 和 current artifact hashes。
- Requirements Matrix 新增 B1/C1/Synthetic Ingestion active-slice 行；未 materialized 前保持 `not_executed`。
- 关闭 `CURRENT_HANDOFF` 的损坏 Markdown/YAML 和旧 `AS-TASK-009` 动作。
- `FINAL_GOAL.md` 不再作为权威入口。
- 把 `.workbuddy/`、`Review-report/`、根目录 `test*.py/test_output.txt` 和临时 result 纳入明确的本地隔离策略，但不读取、不删除用户文件。

## 5. WS-01 Micro L1 修正

- 接受 publish 命令后先持久化 attempt 与 idempotency binding。
- preflight 校验 `base_revision`、`before_digest`、target existence/type、protected paths 和引用完整性。
- Canonical proposals、new revision、ChangeSet published outcome 和 receipt summary 在同一 SQLite transaction 中提交。
- 注入 transaction 内任意阶段失败时，Canonical/Revision/Ledger 全部回滚。
- L2 projection 保持事务外可重建，但 receipt 必须诚实记录 target/actual revision 与 fallback。
- 补齐 `CS-AT-031` 三种失败测试；重新审查 MM-009 mapping。

## 6. WS-02 A1 重新闭环

- A1 production boundary 仍只覆盖批准的固定合成 Answer Safety cases，不扩建通用问答系统。
- `claim_ref`、predicate、perspective、valid time、coverage scope 的不匹配必须 fail closed。
- 多 coverage window 使用批准的 scope/union 规则；gap 和 malformed time 不得 fail open。
- Evidence freshness 只使用实际 selected evidence，不读取无关第一条 Source。
- runner 必须在执行前验证所有 manifest artifact raw hashes。
- Verification Result 记录实际 invocation、环境、commit、manifest/result digest 和 exit code。

## 7. WS-03 生产 runtime 与 CLI

- 新建 production system factory；`testing_adapter.py` 和 `answer_testing_adapter.py` 继续 test-only，CLI 禁止导入它们。
- 默认数据目录可以位于用户本地目录，并有明确权限、初始化、schema migration 和 corruption 行为。
- `init` 必须验证已有数据库，不把“文件存在”当初始化成功。
- `intake` 接受当前批准的合成演示输入；rejected 返回非 0，且不打印误导性 Source ID。
- `changesets` 真正列出数据，不硬编码固定 ID。
- `review` 读取持久候选，不生成演示候选冒充当前队列。
- `python -m noetide_micro` 与 console script 使用同一入口。
- README 中每条命令必须由 clean-environment acceptance 原样执行。

## 8. WS-04 B1

- Candidate Envelope 补齐 `model_or_rule_version`、条件 `assertion_kind`、typed value、stable target 和状态。
- 去重 key 使用规范 canonical representation，区分数字/字符串、perspective、valid time 和 target；candidate ID 冲突 fail closed。
- 聚合保留 evidence family/provenance，不把重复次数当 truth confidence。
- critical 永远优先呈现且不能被普通预算 suppress；预算只控制打扰，不删证据或降风险。
- 实现 session/weekly budget、suppression expiry、later/reject/never-ask 和审计。
- `posthoc_revertible` 仅限现有最保守 profile 批准的确定性 Source receipt metadata；Canonical personal semantics 仍需确认。
- 建立 B1 acceptance、fixture、oracle、manifest、runner 和 immutable result。

## 9. WS-05 C1

- `Decision` 和 `Outcome` 使用 S1 最小对象边界，补齐稳定 ID、revision、owner/subject/recorder、证据和时间。
- create/decide/close/outcome/correct/revert 的 Canonical 写入全部通过 ChangeSet。
- initial `choice` 必须属于 options；Decision/Outcome reference 必须校验存在与类型。
- Scenario 不建立第 13 个对象，使用 `Assertion(assertion_kind=predicted|fictional)` 并引用 Decision。
- Calibration 是 Outcome 子结构，不建立独立 Canonical 对象；时间由注入 Clock 提供，不硬编码。
- 实现或删除 README 中 `decision/outcome/calibrate/scenario` 声称；保留的命令必须有 CLI acceptance。
- 建立 C1 materialized suite、runner、result 和回归。

## 10. WS-06 Synthetic Ingestion

- 只接收显式 `synthetic=true` 且匹配批准 profile/fixture schema 的输入；无法证明时拒绝。
- Source payload、hash/bytes、policy、append receipt 同一 durable 边界写入。
- duplicate、idempotency mismatch、storage failure 和 invalid subject refs 有稳定结果。
- 不把电话/邮件正则当 synthetic truth 判定器。
- 不实现真实第三方连接器，不关闭 `DQ-008` 的 Year 2 产品问题。

## 11. WS-07 Portability

最小 Context Pack 必含：

- `manifest.json`：版本、文件、SHA-256、数据 revision、导出时间和范围。
- `canonical.json`：当前和必要历史规范语义。
- `ledger.json`：ChangeSet、receipt、attempt、approval、revert 和审计。
- `sources/` 或明确的 Source manifest + inline synthetic content。
- `README.md`/人类可读 Markdown：对象、时间、证据和限制说明。
- unknown extension round-trip fixture 和 verifier。

导出不能只复制 Projection。导入 verifier 默认 dry-run，不直接写 Canonical。

## 12. WS-08 Packaging 与一键安装

- 使用明确的现代 package metadata；runtime dependency 必须为 0，build/test dependency 单独声明。
- `schema.sql`、必要 package data 和合成 demo fixture 必须进入安装包，不依赖仓库 `tests/` 路径。
- 补充真实适用的 LICENSE；不能确认时移除错误的 MIT classifier 并记录 blocker。
- 提供 Windows PowerShell 一键安装/启动脚本；可选提供 POSIX 脚本，但不得虚假声称未验证平台。
- one-click 脚本必须检查 Python 版本、创建隔离 venv、安装本地包、运行 smoke check，并在失败时保留诊断和非 0 exit code。
- README 的 `git clone` 在独立审计前使用 RC branch/tag 指令；正式发布后才切换默认 `main` 示例。

## 13. WS-09 Required Verification

至少运行并记录：

```text
Product baseline validator
SPEC baseline validator
Micro suite validator + official runner
A1 suite validator + official runner
B1 suite validator + official runner
C1 suite validator + official runner
Synthetic Ingestion suite validator + official runner
Portability export/import round-trip
CLI clean-data-dir end-to-end
clean venv package install + module/console smoke
privacy/credential/workspace-boundary scan
git diff --check
```

每项记录 command、cwd、Python/SQLite/OS、commit、exit code、result artifact 和 SHA-256。required 结果必须来自同一 RC commit，不能跨 run 拼接。

## 14. WS-10 至 WS-12：内部审计、Debug、复审与交接

`WS-10` 必须在与实现分离的审计步骤中逐项复验 P1/P2、manifest/result binding、CLI、package、portability、隐私边界和文档声明。发现 P0/P1 后进入 `WS-11`，不得把失败改写为通过。

`WS-11` 修复经内部审计确认的问题，并从干净环境执行全部 §13 Required Verification。每次修复后的 result 必须绑定同一 RC commit；不得拼接旧 run。

`WS-12` 复审通过后必须留下：

- `docs/PROJECT_STATE.md`：phase=`audit_ready_release_candidate` 或真实失败状态。
- `docs/process/CURRENT_HANDOFF.md`：next_role=`Independent Auditor`，final_auditor=`Codex`。
- current Requirements Matrix。
- 每套 suite current immutable result。
- Release Candidate Recovery Record，包含 commit、复验命令和已知 P2/P3。
- `git status --short --branch` 输出说明。
- 未推送的 RC commit；不创建正式 release tag。

## 15. Definition of Done

只有同时满足以下条件才可向用户报告“开发完成，等待审计”：

1. `E2E-P1-001..011` 全部 closed，并有代码/测试/结果证据。
2. 所有 current validator exit code 0。
3. 所有 current required suite 在同一 RC commit passed，无 required skip。
4. README 命令在干净环境逐字执行成功。
5. 默认 CLI 不依赖 test adapter、仓库 tests 路径或工作区限制。
6. Export 满足最小 Context Pack 和 round-trip。
7. 一键脚本在声明平台实际验证通过。
8. 没有读取/提交真实个人数据和用户私有目录。
9. 项目状态、handoff、matrix、manifest、result 和 Git commit 一致。
10. 已完成 Kimi 内部审计、Debug、全量回归和复审；未合并 `main`、未推正式 tag、未发布 GitHub Release，等待 Codex 独立审计。
