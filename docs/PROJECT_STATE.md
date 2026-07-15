# 项目状态

## 1. 恢复入口

任何新任务必须按顺序读取：

1. `docs/product/CURRENT_PRODUCT_BASELINE.md`
2. 读取其中 `current_prd_path` 指向的完整 PRD
3. `docs/PROJECT_STATE.md`
4. `docs/decisions/OPEN_QUESTIONS.md`
5. `docs/process/README.md`
6. 当前切片适用的 Approved SPEC
7. `docs/traceability/REQUIREMENTS_MATRIX.md`
8. 当前 suite/verification 记录
9. 当前 ADR、Implementation Plan 和 Gate Review（存在时）

当前产品批准读 `docs/decisions/PRD_V05_BASELINE_DECISION_2026-07-15.md`；SPEC 兼容结论读 `docs/reviews/PRD_V05_SPEC_COMPATIBILITY_REVIEW.md`；最近验证读 `docs/testing/LATEST_STATIC_VALIDATION.md`。历史审计报告不能覆盖当前状态。

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试、示例和 fixture 只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-15 |
| 当前阶段 | PRD v0.5 与九份 SPEC 已批准并完成兼容复审 |
| 当前切片 | `SLICE-MICRO-RELATIONSHIP-001` |
| 当前切片交付阶段 | `traceable` |
| 当前 PRD | `PRDv05.md` v0.5，`Approved Product Baseline` |
| PRD v0.5 canonical LF SHA-256 | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 历史 PRD | `PRDv04.md` v0.4，`superseded_read_only`，hash `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 正式 SPEC | S1 v0.5；S2-S6 v0.4；S7-S8 v0.3；S9 v0.4，全部 `Approved/current` |
| 产品问题 | blocking=0、important=0；`DQ-001..013` deferred |
| 兼容 Finding | P0=0、P1=0、P2=0；P3=1 accepted debt（`MMF-017`） |
| 追踪 | 32/32 FR current；Coverage Level 9 micro / 8 specified / 15 boundary |
| Micro required | `MM-001..010`；39 个去重 upstream Test Ref，未扩张 |
| 测试状态 | 全部 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 实现代码 | 无业务实现；只有静态校验脚本 |
| ADR / Implementation Plan | `absent` / `absent` |
| 依赖/数据库/最终技术栈 | 无、未选择 |
| Git | 分支 `codex/spec-v05-compatibility`；内容提交 `066d0ef55279bfe91e9bc13568c6de269460d085`；Recovery tag `spec-v05-compatibility-v0.1-approved` 已推送并验证 |

## 3. 本轮完成内容

1. 按 S1→S9 完整复核历史 Approved SPEC 对 PRD v0.5 的 applicability。
2. 升版为 S1 v0.5、S2-S6 v0.4、S7-S8 v0.3、S9 v0.4，并保持全部 `Approved`。
3. 闭合 Source Append/Intake receipt、Canonical unknown 保守查询、隐私逆向 operation、automatic 最小边界、MCP 不可逆 gate/denied profile 和 migration 部分回滚。
4. 保持 `DQ-011..013` deferred；只规定重开前最保守行为，没有替产品做永久裁决。
5. 同步 SPEC README、Requirements Matrix、Micro suite 版本绑定和静态校验器。
6. 建立 `PRD_V05_SPEC_COMPATIBILITY_REVIEW.md`，结论 `yes`。
7. 保持 Micro 10 场景/39 required slices 不变，没有把新增长期测试隐式提升为 Micro required。

## 4. 验证结果

实际执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

两条命令最终均 exit code 0。SPEC 结果为 `PASSED (static contract checks only; no business test was executed)`。

| 检查 | 结果 |
|---|---|
| PRD hash / index | v0.4 immutable 与 v0.5 Approved passed |
| SPEC structure | 9 份当前版本；275 Test ID；133 Invariant passed |
| Traceability | 32 FR；174 唯一 Test Ref；9/8/15 Coverage passed |
| Closed enum | 20 个正向闭集 passed |
| Micro | 10 场景、两个 58-byte Source、39 required tests passed（仅静态引用） |
| Privacy / Markdown | 43 份权威文件启发式未命中；56 份 Markdown fence parity passed |
| EOL portability | Product 与 SPEC 的 LF/CRLF 四次隔离运行均 exit code 0，同类输出 digest 一致 |
| Business tests | `not_executed` |

完整环境、校验器 hash、输出 digest 和一次已记录的中间 BOM 诊断失败见 `docs/testing/LATEST_STATIC_VALIDATION.md`。

## 5. 当前权威产物

| 文件 | 当前职责 |
|---|---|
| `docs/product/CURRENT_PRODUCT_BASELINE.md` | 当前/历史 PRD 唯一指针和 hash |
| `PRDv05.md` | 当前 Approved 产品需求基线 |
| `docs/specs/01..09` | 当前 Approved PRD v0.5-compatible 语义合同 |
| `docs/specs/README.md` | 九份 SPEC 顺序、边界、版本与门禁 |
| `docs/traceability/REQUIREMENTS_MATRIX.md` | 32 FR 的当前追踪 |
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | Micro v3 合同；尚未物化/执行 |
| `docs/reviews/PRD_V05_SPEC_COMPATIBILITY_REVIEW.md` | 当前兼容 Gate Review |
| `docs/testing/LATEST_STATIC_VALIDATION.md` | 最近产品/SPEC/EOL 静态验证 |
| `tools/validate_product_baseline.ps1` | 产品基线静态校验 |
| `tools/validate_spec_baseline.ps1` | PRD v0.5/SPEC/Matrix/Micro 静态校验 |
| `docs/releases/SPEC_V05_COMPATIBILITY_V0.1_RECOVERY_POINT.md` | 本轮 Git 定位、验证和恢复步骤 |

## 6. 未决问题与后置项

- 当前 PRD/Micro blocking=0、important=0。
- `DQ-001..013` 均 deferred，按记录阶段重开；S2/S5/S8 的保守规则不等于永久产品决定。
- `MMF-017` 保持 P3：长期 275 个合同测试按切片逐套物化，不一次性扩张 Micro。
- ADR、Architecture View、suite manifest/fixture/oracle/runner、Implementation Plan 和业务实现均不存在。

## 7. 范围锁与风险

| 风险 | 当前控制 |
|---|---|
| 把静态 passed 当业务 passed | suite flags 全 false，明确 business `not_executed` |
| deferred 被 SPEC 暗中裁决 | DQ 保留，正文只给可撤销的最保守临时行为 |
| 新增长期测试扩大 Micro | Micro required 映射保持 10 场景/39 refs |
| 隐私逆向动作混入整包撤销 | S3/S4 一一映射 unarchive/unseal/restore |
| MCP 非 verified 触发不可逆动作 | S8 fail closed；DQ-013 未重开前无例外 |
| migration 部分成功后失去回滚路径 | S9 显式 failed/rolling_back/rollback_failed |
| 真实个人数据进入项目 | 合成数据规则和权威文件隐私启发式扫描 |

在 Micro required suite 真实物化并通过前，继续禁止财务、健康、决策、成长、多设备、连接器、真实迁移、多租户、多 Agent、A2A、数字遗产和通用图数据库平台实现。

## 8. 下一步唯一建议动作

**只为 `SLICE-MICRO-RELATIONSHIP-001` 编制必要的最小 ADR；不得直接编码，不得借 ADR 选择长期数据库平台或扩大 Micro。**

ADR Accepted 后仍必须先物化 exact required suite，再编制 Implementation Plan，最后才允许业务开发。

## 9. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | PRD v0.4 审查、产品裁决、追踪与 Micro 验收 |
| 2026-07-13 | Initial Spec Suite | S1-S9 首次 Approved；测试未执行 |
| 2026-07-14 | Multi-model / Corrective | P1 从 7 关闭到 0；业务测试未执行 |
| 2026-07-15 | Delivery Workflow Foundation | 建立长期交付门禁和 Git 恢复点 |
| 2026-07-15 | PRD v0.5 Consolidation | v0.5 Approved；SPEC applicability 进入 review_required |
| 2026-07-15 | SPEC v0.5 Compatibility | S1-S9 current-compatible；静态/EOL passed；恢复 `traceable` |
