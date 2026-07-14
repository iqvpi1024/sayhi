# 变更控制

## 1. 目的

变更控制用于判断“应该改哪一层、哪些下游产物必须失效”。它不是审批表演，也不要求为文字修正创建复杂流程。

## 2. 先分类再修改

| 变更类型 | 权威层 | 示例 | 必须动作 |
|---|---|---|---|
| 产品价值/范围/行为 | PRD / Product Decision | Micro 是否包含第三个 View | 产品负责人决定；必要时发布新 PRD 基线 |
| 语义合同 | SPEC | 新状态、字段含义、失败终态 | SPEC 升版、测试/矩阵/下游审计 |
| 技术选择 | ADR | 存储、语言、事务或测试框架 | 记录方案比较、代价、回退和验证 |
| 测试物化 | Manifest/Fixture/Oracle | required 集、固定时钟、故障注入 | 不得改变 SPEC；冲突时回 SPEC |
| 实施分解 | Implementation Plan/TODO | 模块、顺序、完成条件 | 每项绑定 SPEC/Test/ADR |
| 实现修复 | Code | 满足现有合同的 bug fix | 新 Verification Run；不倒推产品规则 |
| 流程维护 | Process/Template | 新 gate checklist | 不自动改变产品/SPEC/已运行结果 |

无法唯一分类时，先记录问题并停止，不同时修改多层掩盖冲突。

## 3. 下游失效规则

| 上游变化 | 默认需要复核或 supersede 的下游 |
|---|---|
| PRD 基线 | Decision、SPEC、Matrix、ADR、suite、plan、result、review、recovery point |
| Product Decision | 相关 SPEC、Matrix、ADR、suite、plan、result、review |
| SPEC 语义/版本 | Matrix、相关 ADR、suite artifact、plan、旧 result applicability、review |
| Trace required set | suite manifest、plan、Verification Result、review |
| ADR 技术合同 | architecture view、suite runner contract、plan、implementation result |
| Fixture/Oracle | plan、当前/旧 result applicability、review |
| Implementation Module | Verification Result、review、recovery point |
| Process 文档 | 只复核流程符合性；不自动使业务结果失效 |

`superseded` 只表示“不再适用于当前基线”，不得覆盖、删除或篡改历史结果。

## 4. 已批准 SPEC 的修改

1. 记录触发来源：Finding、Decision、失败测试或兼容问题。
2. 判断是否属于产品裁决；若是，先更新 Decision，不让 SPEC 代产品决定。
3. 升 SPEC 版本并更新精确章节、状态机、不变量、正反例和 Acceptance Test。
4. 更新 Matrix、Micro required mapping 和静态校验器。
5. 标记受影响 artifact/result 的 applicability。
6. 重新静态验证和 Gate Review。

只改版本号、不更新测试和追踪，或只改测试迎合实现，均不允许。

## 5. PRD 保护

- `PRDv04.md` 当前只读；任何字节变化必须有产品负责人明确授权和新基线决定。
- 换行差异使用 canonical LF hash 识别，不得误判为语义修订。
- SPEC/ADR/代码不能用“实现需要”静默补充产品规则。
- PRD 中无法唯一推导的行为进入 OPEN_QUESTIONS。

## 6. 测试与实现冲突

当测试和实现冲突时按以下顺序判断：

1. Fixture 是否违反 SPEC 或使用了错误基线。
2. Oracle 是否可由 SPEC 唯一推导。
3. SPEC 是否内部矛盾或缺少产品裁决。
4. 实现是否违反合同。

不得先修改 expected 让失败消失。任何 oracle 调整必须说明依据，并使旧结果 applicability=`superseded`。

## 7. 紧急修复

当前 Micro 尚无生产环境。未来若出现必须紧急处理的数据损坏或隐私问题，可以先隔离/停止写入，但仍必须：

- 保留 Source、日志和最小审计证据，除非执行明确 hard delete。
- 不绕过 ChangeSet 修正规范语义。
- 补写 Decision/SPEC/ADR/Test/Verification 中缺失的适用产物。
- 在 Gate Review 中说明为何偏离正常顺序及如何恢复。

“紧急”不能成为跳过隐私、历史或审计不变量的理由。

## 8. 变更完成检查

- [ ] 修改层级正确，没有跨层代决策。
- [ ] 触发依据和受影响范围已记录。
- [ ] 下游失效/supersede 已处理。
- [ ] 追踪链和当前版本已更新。
- [ ] 实际检查已运行，未执行项仍明确。
- [ ] PROJECT_STATE 已更新。
- [ ] PRD 和隐私边界未被意外改变。
