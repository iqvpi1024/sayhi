# 识海 Noetide 仓库工作规则

本文件适用于整个仓库。它只规定协作流程，不替代 PRD、Decision、SPEC、ADR 或测试合同。

## 每次开始

严格按以下顺序恢复项目状态：

1. `PRDv04.md`
2. `docs/PROJECT_STATE.md`
3. `docs/decisions/OPEN_QUESTIONS.md`
4. `docs/process/README.md`
5. 当前切片适用的 Approved SPEC
6. `docs/traceability/REQUIREMENTS_MATRIX.md`
7. 当前 suite/verification 记录
8. 当前 ADR、Implementation Plan 和 Gate Review（存在时）

以 `docs/PROJECT_STATE.md` 的“下一步唯一建议动作”为默认工作入口；用户的新明确指令优先，但不得静默跨过产品或实现门禁。

## 不可违反

- `PRDv04.md` 是只读产品基线；没有产品负责人明确授权不得修改。
- 不扫描、引用、导入或推断工作区外个人数据。
- 示例、fixture、测试和演示只使用显式合成数据。
- 不在仓库新增真实姓名、地址、组织、电话、邮箱、凭据、债务、健康或亲密关系资料。
- Source、事实、观点、推断、预测、虚构和 Derived View 证据边界不得混淆。
- Current State 不覆盖 Historical State；Hypothesis 不自动升级为 Fact。
- 所有规范语义写入遵守 ChangeSet 合同；Derived View 不反向成为事实证据。
- 未运行的测试只能记为 `not_executed`，静态检查不得冒充业务通过。
- 不因长期愿景提前建设多租户、多 Agent、A2A、数字遗产、全连接器或通用图数据库平台。

## 交付顺序

每个切片遵守：

```text
PRD -> Decisions -> SPEC -> Traceability -> ADR -> Executable Tests
-> Implementation Plan -> Development -> Verification -> Review -> Recovery Point
```

TODO 不能代替 ADR、suite/oracle 或验收合同。技术选择只在当前切片需要时进入 ADR；测试物化和 Implementation Plan 完成前不得开始业务编码。完整规则见 `docs/process/README.md` 和 `docs/process/CHANGE_CONTROL.md`。

## 每次结束

- 更新 `docs/PROJECT_STATE.md`：阶段、完成内容、真实验证、未决问题、风险和下一步唯一动作。
- 检查 PRD 未被意外修改，检查没有引入真实个人数据。
- 运行与变更相称的检查并记录命令、环境、exit code 和结果。
- 上游变化时按 Change Control 标记下游 `superseded` 或重新审查。
- 只提交当前任务范围；达到门禁后才创建并推送可验证 Git Recovery Point。
