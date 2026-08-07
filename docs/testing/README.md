# 测试与验证说明

## 1. 四种不同状态

测试合同、可运行测试、一次运行和通过结论必须分开：

| 状态 | 含义 | 当前 Micro |
|---|---|---|
| `suite_defined` | SPEC 和验收场景已经定义 oracle | `true` |
| `suite_materialized` | manifest、fixture、oracle 和 runner contract 已成为机器可读取产物 | `true` |
| `suite_executed` | 对适用版本实际运行并保存结果 | `true` |
| `suite_passed` | 同一次 current run 的全部 required tests 通过 | `true` |

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

## 4.1 官方回归命令（canonical）

在仓库根目录、Git Bash 下执行全量回归的 canonical 命令是：

```bash
PYTHONPATH=src \
NOETIDE_MICRO_ADAPTER=noetide_micro.testing_adapter \
NOETIDE_ANSWER_ADAPTER=noetide_micro.answer_testing_adapter \
NOETIDE_A2_ADAPTER=noetide_micro.a2_testing_adapter \
NOETIDE_A3_ADAPTER=noetide_micro.a3_testing_adapter \
NOETIDE_A4_ADAPTER=noetide_micro.a4_testing_adapter \
NOETIDE_A5_ADAPTER=noetide_micro.a5_testing_adapter \
NOETIDE_A6_ADAPTER=noetide_micro.a6_testing_adapter \
NOETIDE_B2_ADAPTER=noetide_micro.b2_testing_adapter \
NOETIDE_B3_ADAPTER=noetide_micro.b3_testing_adapter \
NOETIDE_B4_ADAPTER=noetide_micro.b4_testing_adapter \
NOETIDE_B5_ADAPTER=noetide_micro.b5_testing_adapter \
NOETIDE_B6_ADAPTER=noetide_micro.b6_testing_adapter \
NOETIDE_C2_ADAPTER=noetide_micro.c2_testing_adapter \
NOETIDE_C3_ADAPTER=noetide_micro.c3_testing_adapter \
NOETIDE_C4_ADAPTER=noetide_micro.c4_testing_adapter \
NOETIDE_C5_ADAPTER=noetide_micro.c5_testing_adapter \
NOETIDE_Y2S1_ADAPTER=noetide_micro.y2s1_testing_adapter \
NOETIDE_Y2S2_ADAPTER=noetide_micro.y2s2_testing_adapter \
NOETIDE_Y2S3_ADAPTER=noetide_micro.y2s3_testing_adapter \
NOETIDE_Y2S4_ADAPTER=noetide_micro.y2s4_testing_adapter \
NOETIDE_Y2S5_ADAPTER=noetide_micro.y2s5_testing_adapter \
python -m unittest discover -s tests -t .
```

- 21 个 adapter 环境变量必须全部设置；缺哪一个，对应 contract 模块整体 `skip`（`@unittest.skipUnless`），不会 error。
- 裸跑 `PYTHONPATH=src python -m unittest discover -s tests -t .`（不设 adapter）应全部 skip、0 error。
- 仓库根的 `pytest.ini` 已声明 `pythonpath = src`，pytest 直跑无需再设 `PYTHONPATH`。
- 该 discover 命令是套件级回归；每个 suite 的权威结论仍以各自 official runner（`tests/runner/run_*_suite.py`）产生的不可改写 Verification Result 为准。

## 5. 当前验证状态

exact Micro suite 已按 `MICRO_MVP_ACCEPTANCE.md` §6 物化为 10 个 `MM-*` 场景和 39 个去重 upstream refs。Micro suite 的 current 绑定以 `tests/micro_suite_manifest.json` 为准（当前 `micro-ws12-a603085-pyspath-20260718.json`）；该绑定结果 49 个 required result IDs 均为 `passed`，隐私扫描为 `passed`，因此 `suite_executed=true`、`suite_passed=true`。该结论只覆盖已定义的 Micro 合同，不替代后续 Gate Review 与 Recovery Point。

当前 A1 的 `MVP_A_ANSWER_SAFETY_ACCEPTANCE.md` 已物化为独立 manifest、11 个 `AS-*` 场景和 24 个唯一 upstream refs，共 35 个 required result IDs。当前 A1 official runner 在 `8556eea` 实际通过 35/35，当前绑定结果为 `docs/testing/results/a1-release-8556eea-20260719.json`。C1 official runner 在同一提交实际通过 7/7，当前绑定结果为 `docs/testing/results/c1-release-8556eea-20260719.json`；历史失败结果保留为诊断证据，未被改写。
