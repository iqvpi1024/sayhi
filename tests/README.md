# 可执行测试目录

本目录用于保存机器可运行的 fixture、semantic tests 和 integration tests。Micro、A1、B1、C1、Synthetic Ingestion 与 Context Pack 都有独立 manifest；每个 suite 的 current result 必须由自身 manifest 指向，历史 result 不得冒充 current。

规则：

- 测试必须证明 Approved SPEC，不能反向发明业务规则。
- 所有数据必须合成、确定、离线，不得扫描或导入工作区外个人数据。
- required 集必须来自当前 suite manifest；目录中的文件数量不代表 required 数量。
- 每个 test ID 能回到 SPEC Section 和验收合同。
- expected、forbidden changes、failure 和 audit oracle 都必须机器可读。
- 测试失败优先判断 fixture/oracle/SPEC/implementation 的责任层，不直接改 expected。
- 真实运行结果写入 `docs/testing/results/`，本目录不保存“已通过”声明。

子目录：

- `fixtures/`：合成输入、初始规范状态、预期状态和 hash 清单。
- `semantic/`：单个字段、状态机和不变量合同测试。
- `integration/`：当前切片端到端、失败注入和撤销测试。
- `runner/`：离线 runner、结果聚合和实现适配器协议。

权威 manifest 位于 `tests/*_suite_manifest.json`；没有单一 manifest 可替代其余 suite 的 required 集。

物化门禁见 `docs/testing/SUITE_MATERIALIZATION_CHECKLIST.md`。
