# 架构决策记录规则

## 1. 目的

ADR 记录“为满足已批准语义合同，为什么选择某项技术方案，以及放弃了什么”。ADR 不产生产品需求，不修改 SPEC，也不证明实现已经正确。

依据：PRD §21、§24.1、§25；`docs/process/README.md`；`docs/process/CHANGE_CONTROL.md`。

## 2. 创建门禁

创建 ADR 前必须满足：

1. 当前切片的 blocking 产品问题为 0。
2. 适用 SPEC 为 `Approved`。
3. PRD -> SPEC -> Acceptance Test 的追踪已存在。
4. 决策确实是当前切片开工所必需，不能推迟到实现时再决定。

尚未达到这些条件时，将问题记录到 OPEN_QUESTIONS 或 Gate Review，不建立“占位 Accepted ADR”。

## 3. 状态和编号

- 文件名：`ADR-XXXX_<SHORT_TITLE>.md`，编号只增不复用。
- `Proposed`：正在比较方案，不能作为开工依据。
- `Accepted`：当前切片可以依赖该决定。
- `Rejected`：保留比较历史，不作为实现依据。
- `Superseded`：被新 ADR 替代；原文件保留并指向新编号。

Accepted ADR 的实质决定不原地改写。需要改变时创建新 ADR，并将旧 ADR 标为 `Superseded`。

## 4. 必填内容

- 当前切片与适用基线。
- 要解决的一个具体技术问题。
- 来自 PRD/SPEC/Test 的约束，不得新增业务语义。
- 至少两个可行方案及“不现在决定”的方案。
- 决定、理由、代价、风险和可逆性。
- 对 suite、实施计划、可移植性、隐私和恢复的影响。
- 如何验证决定，以及失败时如何回退。

模板见 `ADR_TEMPLATE.md`。

## 5. 当前状态

ADR 的当前生效集合与切片进展是动态信息，不在本规则文件中固化；以 `docs/PROJECT_STATE.md` 为动态状态的唯一权威来源，各 ADR 的编号、状态与 Superseded 链以 `docs/adrs/` 目录内文件自身为准。
