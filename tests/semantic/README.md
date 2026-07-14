# Semantic Tests

本目录未来保存直接证明 SPEC 字段语义、状态转换和不变量的可执行测试。当前没有测试文件。

要求：

- test ID 与 SPEC Acceptance Test ID 一致或显式映射。
- 每个测试声明适用 SPEC 版本、fixture、oracle 和 required/optional 分类。
- 必须覆盖正向、禁止转换、冲突、失败、撤销和 protected semantics。
- Derived View 不能被当作 Canonical 事实证据。
- 未运行测试不得在文件名、注释或报告中标记 passed。

首轮只允许物化 `MICRO_MVP_ACCEPTANCE.md` §6 的 exact upstream slices，不一次性实现 269 个目录项。
