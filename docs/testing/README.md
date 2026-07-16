# 测试与验证说明

## 1. 四种不同状态

测试合同、可运行测试、一次运行和通过结论必须分开：

| 状态 | 含义 | 当前 Micro |
|---|---|---|
| `suite_defined` | SPEC 和验收场景已经定义 oracle | `true` |
| `suite_materialized` | manifest、fixture、oracle 和 runner contract 已成为机器可读取产物 | `true` |
| `suite_executed` | 对适用版本实际运行并保存结果 | `false` |
| `suite_passed` | 同一次 current run 的全部 required tests 通过 | `false` |

依据：PRD v0.5 §6.14、§22；S6 v0.5；`MICRO_MVP_ACCEPTANCE.md`。

## 2. 目录职责

| 路径 | 内容 |
|---|---|
| `docs/testing/MICRO_MVP_ACCEPTANCE.md` | 人类可读验收合同与 exact required mapping |
| `docs/testing/SUITE_MATERIALIZATION_CHECKLIST.md` | 从合同到机器 suite 的门禁清单 |
| `tests/fixtures/` | 版本化合成输入和初始状态 |
| `tests/semantic/` | 单个语义不变量和状态机测试 |
| `tests/integration/` | 当前切片端到端与失败注入测试 |
| `docs/testing/results/` | 不可改写的 Verification Result |

静态文档校验器只验证合同基线结构，不属于业务 runner。

## 3. suite 物化要求

一个 suite 只有同时具备以下产物才可设置 `suite_materialized=true`：

- 唯一 manifest，绑定 slice、SPEC 版本、fixture 版本和 required Test Ref。
- 固定合成 fixture、确定性时钟、稳定 locator/hash。
- 字段级 expected/forbidden oracle，包含失败与撤销断言。
- runner contract，明确离线环境、命令、exit code 和 artifact 格式。
- required/optional/deferred 分类可被机器读取。
- 从 manifest 到 PRD/SPEC/Test 的反向追踪可检查。

目录存在或 Markdown 场景完整都不能单独满足该状态。

## 4. 运行与结论规则

- required tests 必须在同一次 applicable run 中执行，不能跨 run 拼接为 passed。
- required skip、缺失、错误或版本不一致只能得到 `partial|failed|errored`。
- 失败结果和旧结果保留；新 run 新建结果文件。
- 测试与 SPEC 冲突时按 Change Control 处理，不能先改 expected 迎合实现。
- 静态校验通过只能写 `static validation passed`，不能写业务合同通过。

结果模板见 `VERIFICATION_RESULT_TEMPLATE.md`。

## 5. 当前下一步

exact Micro suite 已按 `MICRO_MVP_ACCEPTANCE.md` §6 物化为 10 个 `MM-*` 场景和 39 个去重 upstream refs。下一门禁是编制 Implementation Plan；在业务实现存在前不得运行并声称 suite 通过，也不得把矩阵中的长期测试目录整体提升为 Micro required。
