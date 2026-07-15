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

当前产品批准读 `docs/decisions/PRD_V05_BASELINE_DECISION_2026-07-15.md`；v0.5 就绪证据读 `docs/reviews/PRD_V05_READINESS_REVIEW.md`。历史审计报告不能覆盖当前状态。

除用户明确指定的评审附件外，不使用工作区外或历史知识库作为产品事实来源。测试、示例和 fixture 只允许合成数据。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 日期 | 2026-07-15 |
| 当前阶段 | PRD v0.5 已批准；九份 SPEC 兼容复核待开始 |
| 当前切片 | `SLICE-MICRO-RELATIONSHIP-001` |
| 当前切片交付阶段 | `product_decided` |
| 当前 PRD | `PRDv05.md` v0.5，`Approved Product Baseline` |
| PRD v0.5 canonical LF SHA-256 | `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 历史 PRD | `PRDv04.md` v0.4，`superseded_read_only`，hash `F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC` |
| 产品决定 | `DEC-PRD-V05-001`；blocking=0、important=0 |
| 正式 SPEC | S1-S9 保留历史 Approved 正文；current applicability=`compatibility_review_required` |
| 产品问题 | BQ/IQ 均 decided 并已整合；DQ-001..013 deferred |
| 追踪 | 32/32 FR 保持；对 v0.5 的 compatibility 尚未证明 |
| 测试状态 | 全部 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false` |
| 实现代码 | 无业务实现；只有只读静态校验脚本 |
| 依赖/数据库/最终技术栈 | 无、未选择 |
| 当前下游产物 | ADR=`absent`；Implementation Plan=`absent`；Business Verification=`not_executed` |
| Git | 当前分支 `codex/prd-v05-consolidation`；基于 tag `project-delivery-workflow-v0.1-validated` |

## 3. 本轮完成内容

1. 保留 `PRDv04.md` 原文和历史 hash，创建独立 `PRDv05.md`。
2. 将 BQ/IQ 已决定的产品级语义整合回 PRD，清除五态/六态、对象别名、Source/ChangeSet、Micro View、撤销、删除/导出和 SPEC 顺序冲突。
3. 保持 32 条 FR、路线图和首年非目标不变，不增加功能或技术选择。
4. 将历史 42 条评审评分留在 v0.4/审计材料，v0.5 只保留当前有效要求。
5. 新增 `DQ-011..013`，使预授权范围、Canonical unknown 和 MCP 不可逆例外进入权威 deferred 队列。
6. 建立产品基线索引、`DEC-PRD-V05-001`、v0.5 Readiness Review 和专用静态校验器。
7. 明确 S1-S9 必须逐份兼容复核，不能因历史 Approved 自动继续开工。

此前 Micro Gate Corrective Revision 与 Delivery Workflow Foundation 的历史成果继续有效，详见 Git tag 和对应审查文件。

## 4. 验证结果

实际执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
```

结果：exit code 0，`PASSED (product baseline static checks only; no SPEC compatibility or business test was executed)`。

| 检查 | 结果 |
|---|---|
| PRD hash | v0.4 immutable 与 v0.5 Approved hash 均 passed |
| PRD structure | 27 章、32 FR、12 对象 passed |
| Closed enum | 8 Assertion kind、6 Answer Status passed |
| Deferred queue | DQ-001..013 各一次 |
| Privacy / Markdown | 启发式未命中；fence parity passed |
| EOL portability | LF/CRLF 隔离副本 exit code 0，portable digest 一致 |
| SPEC compatibility | `not_executed` |
| Business tests | `not_executed` |

准确环境、hash 和输出 digest 见 `docs/testing/LATEST_PRODUCT_VALIDATION.md`。旧 `LATEST_STATIC_VALIDATION.md` 只适用于流程建档时的 v0.4/SPEC 基线，不能证明 v0.5 兼容。

## 5. 当前权威产物

| 文件 | 当前职责 |
|---|---|
| `docs/product/CURRENT_PRODUCT_BASELINE.md` | 当前/历史 PRD 唯一指针和 hash |
| `PRDv05.md` | 当前 Approved 产品需求基线 |
| `PRDv04.md` | superseded 只读历史基线 |
| `docs/decisions/PRD_V05_BASELINE_DECISION_2026-07-15.md` | v0.5 产品批准与下游失效决定 |
| `docs/decisions/OPEN_QUESTIONS.md` | BQ/IQ 历史裁决和 DQ-001..013 队列 |
| `docs/reviews/PRD_V05_READINESS_REVIEW.md` | v0.5 就绪审查 |
| `docs/testing/LATEST_PRODUCT_VALIDATION.md` | v0.5 最近静态验证 |
| `tools/validate_product_baseline.ps1` | 产品基线静态校验，不是 SPEC/业务测试 |
| `docs/specs/01..09` | 历史 Approved；等待逐份 v0.5 兼容复核 |

## 6. 未决问题与后置项

- 当前 PRD/Micro blocking=0、important=0。
- `DQ-001..013` 均 deferred，按记录阶段重开。
- `MMF-009..015` 保持 P2；`MMF-017` 保持 P3，不带入首轮 Micro。
- SPEC Compatibility、Traceability current applicability 和业务验证仍未完成。

## 7. 范围锁与风险

| 风险 | 当前控制 |
|---|---|
| 把历史 SPEC Approved 当 v0.5 兼容 | 全部标记 `compatibility_review_required` |
| 把 PRD 静态 passed 当业务 passed | 明示 SPEC/business `not_executed` |
| PRD 新版覆盖历史 | v0.4 独立文件+hash 永久保留 |
| v0.5 借整合扩大 Micro | FR 集合与 Micro 非目标静态检查 |
| deferred 被暗中裁决 | DQ-001..013 权威队列和最保守行为 |
| 真实个人数据进入项目 | 合成数据规则和隐私启发式扫描 |

在 Micro required suite 真实物化并通过前，继续禁止财务、健康、决策、成长、多设备、连接器、真实迁移、多租户、多 Agent、A2A、数字遗产和通用图数据库平台实现。

## 8. 下一步唯一建议动作

**从 S1 `Semantic Object Model SPEC` 开始，逐份执行 PRD v0.5 Compatibility Review；不兼容先升版修订，再进入下一份。**

## 9. 变更日志

| 日期 | 阶段 | 记录 |
|---|---|---|
| 2026-07-13 | Phase 0 | PRD v0.4 审查、产品裁决、追踪与 Micro 验收 |
| 2026-07-13 | Initial Spec Suite | S1-S9 首次 Approved；测试未执行 |
| 2026-07-14 | Multi-model / Corrective | P1 从 7 关闭到 0；业务测试未执行 |
| 2026-07-15 | Delivery Workflow Foundation | 建立长期交付门禁和 Git 恢复点 |
| 2026-07-15 | PRD v0.5 Consolidation | v0.5 Approved，P0/P1=0；SPEC compatibility 与业务测试未执行 |
