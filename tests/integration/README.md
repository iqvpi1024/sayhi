# Integration Tests

本目录未来保存当前切片跨模块的端到端可执行测试。当前没有测试文件。

Micro 首个 integration suite 只允许覆盖：合成 Source append、单个联系状态 ChangeSet、用户确认、原子发布、两个 Core View、历史保留、protected semantics、stale base、L2 失败和整包撤销。

当前机器动作与 failure injection 计划为 `micro_relationship_scenarios.json`；它必须与 manifest 和人类可读权威映射精确一致。

要求：

- 默认禁用外部网络和在线模型。
- 使用固定时钟、合成 fixture 和可控故障注入。
- 单次 run 绑定同一 commit、manifest、fixture 和 implementation。
- 验证 Canonical、Derived View、receipt 和 audit history，不能只测 HTTP/CLI 成功码。
- 不扩展到权限 runtime、MCP、连接器、同步、财务、健康、决策、多 Agent、A2A 或真实迁移。
