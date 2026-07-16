# Micro 开发前 SPEC 一致性复审

## 1. 结论

当前结论：`yes`。允许 `SLICE-MICRO-RELATIONSHIP-001` 进入最小 ADR；不允许直接开发。

Finding 计数：P0=0、P1=0、P2=0、P3=0。业务 suite 仍未物化、未执行、未通过。

## 2. 触发与范围

恢复读取 Approved SPEC 时发现三个开发前一致性残留：

| Finding | 严重度 | 处置 |
|---|---|---|
| S1 §7.1 定义 `received -> validating -> stored|duplicate|rejected`，§8.1 却遗漏 validating/duplicate | P1 | S1 升为 v0.6，§8.1 与状态机精确对齐 |
| S2 §21 错引上游 S1 v0.3，且 S1/S2 完成定义仍使用测试三态措辞 | P1 | S2 升为 v0.5；S1/S2 均改为 defined/materialized/executed/passed |
| S6 HTH-AT-024..027 的 Markdown 行多出一列，破坏三列表结构 | P1 | S6 升为 v0.5，只合并 Given/When 文本，不改变 Then oracle |

依据：PRD v0.5 §6.14、§8、§22.1；S1 §7.1；S6 §6-§9；`docs/process/CHANGE_CONTROL.md` §2-§4。

## 3. 版本与兼容性

| SPEC | 旧版 -> 当前版 | 语义影响 |
|---|---|---|
| S1 | v0.5 -> v0.6 | 无新状态、字段、不变量或 Test ID；只消除同文状态路径矛盾 |
| S2 | v0.4 -> v0.5 | 无时间/证据/查询状态变化；只修引用和测试四态措辞 |
| S6 | v0.4 -> v0.5 | 无结果枚举、状态机、required 映射或 Test ID 变化；只修表结构 |
| S3-S5 | 保持 v0.4 | 对当前 S1/S2 继续适用 |
| S7-S8 | 保持 v0.3 | 对当前 S1/S2/S6 继续适用 |
| S9 | 保持 v0.4 | 对当前 S1/S2/S6 继续适用 |

独立 SPEC 不要求齐步升版。未发生产品行为、Micro 范围或 oracle 变化，因此下游 S3-S5/S7-S9 无需制造版本震荡；其当前 applicability 经本复审保持 `current`。

## 4. 追踪与 Micro 影响

- 32/32 FR 保持登记；Coverage Level 仍为 9 micro / 8 specified / 15 boundary。
- 275 个 SPEC Test ID 与 133 个 Invariant 均未增加、删除或重编号。
- `MM-001..010` 与 39 个去重 required upstream Test Ref 保持精确相同。
- Implementation Module 仍为 `TBD`；Verification Result 仍为 `not_executed`。
- 没有修改 `PRDv05.md` 或历史只读 `PRDv04.md`。

## 5. 实际验证

首次修订后运行 SPEC 校验返回 exit code 1：S6 的产品基线元数据缺少明确文本 `PRD v0.5`。该失败已保留在本报告中，随后把元数据统一为 `PRDv05.md，PRD v0.5` 并重跑。

最终实际命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1
powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1
```

最终结果：

| 检查 | Exit code | 结果 |
|---|---:|---|
| Product baseline | 0 | PASSED，静态产品检查；未执行 SPEC 兼容或业务测试 |
| SPEC baseline | 0 | PASSED，含新增 SOM/BTE/HTH 一致性回归守卫；未执行业务测试 |

新增静态守卫会拒绝：S1 状态摘要再次遗漏、S2 上游再次漂移、S1/S2/S6 回退为测试三态措辞，以及 S6 验收表不再是三列。

## 6. 未证明

- 没有 suite manifest、fixture artifact、oracle runner 或 Implementation Module。
- 没有证明原子发布、L2 传播、历史查询、protected semantics 或补偿撤销。
- `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`、`business_verification=not_executed`。

## 7. 下一门禁

只创建服务于 `SLICE-MICRO-RELATIONSHIP-001` 的最小 ADR。ADR 不得选择长期数据库、云服务、图平台、MCP、连接器、多 Agent 或多设备架构；Accepted 后仍须先物化 exact Micro suite，再编制 Implementation Plan。
