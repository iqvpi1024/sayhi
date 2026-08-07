# C6 MVP Release Gate 切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-C6-RELEASE-001` |
| 版本 | `0.1` |
| 状态 | `Approved for C6 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-C-RELEASE-001` |
| 上游 | S6 v0.5、S7 v0.4 |
| 适用范围 | `SLICE-MVP-C-RELEASE-001`，仅发布就绪审计，无新业务语义 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：以可执行审计证明发布就绪——全量回归真实执行零 skip、安全审计（隐私/依赖/网络隔离/manifest 绑定）、数据恢复演练字节一致、公开 Beta 门禁逐项确认且首年非目标保持关闭。

非目标：新业务能力、真实数据、生产加密、D2 安装包、D3 发布动作、修改任何已 verified artifact。

## 2. 对象与字段

### 2.1 ReleaseAuditResult（immutable 审计结果）

```yaml
audit_id / executed_at（真实执行时间）/ git_commit
checks: C6-001..008 逐项 {check_id, status: passed|failed, detail}
overall: passed | failed          # 任一 failed -> failed
non_goals_closed: true            # 首年非目标保持关闭的确认
```

### 2.2 审计场景定义

| ID | 审计内容 | 通过条件 |
|---|---|---|
| `C6-001` | 全部 suite validator 执行 | 全部 exit 0，输出含 PASSED |
| `C6-002` | 全量 configured-adapter regression | exit 0、0 failed、0 errors、0 skipped |
| `C6-003` | 隐私边界扫描 | 全部 fixture `synthetic=true` 且 `external_data_used=false`；src/fixture 无禁用真实数据标记模式 |
| `C6-004` | 依赖审计 | src/noetide_micro 全部 .py 的 import 均在 stdlib 白名单或本包内 |
| `C6-005` | 网络隔离审计 | src/noetide_micro 无 socket/urllib/http.client/requests 调用面 |
| `C6-006` | manifest 绑定审计 | 全部 suite manifest flags=executed+passed、latest result 路径+sha256 存在且匹配 |
| `C6-007` | 数据恢复演练 | 合成 demo 库 备份->恢复 字节一致、data_revision 一致、源库 hash 不变 |
| `C6-008` | Beta 门禁文档核验 | recovery tag 清单齐全（git tag -l）、PROJECT_STATE/CURRENT_HANDOFF 指向当前切片、非目标关闭清单完整 |

## 3. 状态机

```text
audit: pending --执行--> passed | failed（immutable result 绑定）
beta gate: audit passed -> 门禁文档复核 -> beta_ready=true（仅文档就绪，不代表已发布）
```

## 4. 不变量

- `C6-INV-001`：回归真实执行且零 skip。
- `C6-INV-002`：src 只含 stdlib 导入且无网络调用面。
- `C6-INV-003`：fixture 显式合成；无真实个人数据标记。
- `C6-INV-004`：manifest 全部 executed+passed 且 result 哈希绑定。
- `C6-INV-005`：恢复演练字节一致、revision 一致、源库不变。
- `C6-INV-006`：非目标保持关闭，审计产物不得宣称未就绪能力。
- `C6-INV-007`：审计只读，不修改已 verified artifact、不移动 tag、不写业务库。

## 5. 失败与降级

- 任一审计项失败：该 check `failed` 并记录 detail，overall=`failed`；不得跳过或标记通过。
- 审计执行环境：与官方 runner 一致（网络阻断、stdlib only）。
- 门禁文档与审计结果分离：文档不得引用不存在的 passed 结果。

## 6. 可执行验收

`C6-001..008` 全部由 `tests/runner/run_c6_release_audit.py` 真实执行，产出 immutable `docs/testing/results/c6-20260726.json` 并绑定 manifest。未执行时 C6 保持 `not_executed`。

## 7. 完成定义

只有 audit runner、immutable passed result、manifest 绑定、Beta 门禁复核文档（引用同一次 passed result）与 Gate Review（P0/P1=0）齐全时，C6 才能标记 `verified`。
