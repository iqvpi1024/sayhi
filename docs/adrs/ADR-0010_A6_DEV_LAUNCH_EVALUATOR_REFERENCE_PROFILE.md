# ADR-0010：A6 开发启动入口、evaluator package 与 Reference Profile 环境描述符

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-25 |
| Slice | `SLICE-MVP-A-HARDENING-001` |
| Contract | `SPEC-A6-HARDENING-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes | `none` |
| Superseded By | `none` |

## 1. 决策问题

A6 硬化切片需要三个相互独立但同层的技术裁决：开发启动（D0 唯一入口命令）的具体形态；evaluator package（评审者如何执行验证）的具体形态；`a6_mvp_a_reference_v1` 环境描述符的具体记录值与结果戳记方式。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | `PRDv05.md` §21.2、§24.2；`DEC-MVP-A-HARDENING-001` §3；`ONE_CLICK_DELIVERY_PLAN.md` §2/§3/§4 |
| SPEC | `SPEC-A6-HARDENING-001` §2/§3/§6/§7/§9；S6 §IQ-014 计时边界与环境记录 |
| Acceptance Test | `A6-013..021` |
| Traceability | 矩阵 §4.12 |

## 3. 约束与非目标

- stdlib only（Python 3.12）；不引入第三方依赖、打包器、容器或网络能力。
- 默认运行本地可用，不以云账号、在线模型或外部数据库为前置。
- 入口命令失败时必须非零退出、给出可行动错误，不下载或读取工作区外个人资料。
- SLO 结果仅对声明 profile 有效，不外推；结果必须戳记实际观察到的环境与计时（wall time、monotonic duration、时区）。
- 本 ADR 不决定：D2 installer/签名/升级卸载程序、D3 发布动作、支持平台全集、容器化（`ONE_CLICK_DELIVERY_PLAN.md` §2 留待 C5/C6 前 ADR）；Alpha 版本号与发布动作（A6 Gate Review 后发布门禁）。

## 4. 候选方案

### Option A：仓库根 `start.py` + 复用 runner/validator 作为 evaluator package + ADR 记录环境描述符

- 做法：根目录 `start.py` 作为 D0 唯一入口（自处理 `src` 路径，无需 PYTHONPATH）；evaluator package = 仓库内版本化 fixture/oracle/runner/validator/manifest + 固定调用命令；本 ADR §5 记录环境描述符具体值，runner 在 result JSON 戳记实际观察值。
- 优点：干净机器 `python start.py` 即可执行；与既有 12 套 suite 模式一致；零新依赖。
- 代价与风险：`start.py` 是脚本形态而非安装包，普通用户体验问题留待 D2。
- 可逆性：纯新增文件与文档，可整体回退。

### Option B：扩展 `cli.py` 增加 dev/start 子命令作为唯一入口

- 做法：入口收进包内。
- 优点：单一模块。
- 代价与风险：从仓库根运行需先设 `PYTHONPATH=src` 或安装包，违背 D0 干净机器"一个入口命令"的可执行性。

### Option C：暂不决定

会阻塞 `A6-013/015/018/020/021` 的 suite 物化（无固定入口与 profile 环境值），不可接受。

## 5. 决定

采纳 Option A，三项裁决如下。

**5.1 开发启动入口**：仓库根 `start.py`（`python start.py`），stdlib-only，职责固定按 `ONE_CLICK_DELIVERY_PLAN.md` §3 D0：检查受支持 runtime 版本（Python >= 3.12）→ 创建/确认合成开发数据根（默认 `<repo>/devdata/`，`--data-root` 可覆盖；均视为合成路径并加入 .gitignore）→ 初始化/迁移数据库（ADR-0001 PRAGMA）→ 运行最小 preflight + smoke → 输出本地访问入口（可用 cli 命令提示）→ 失败时非零退出 + 可行动错误；`--clean` 仅在路径前缀校验确认位于声明的合成数据根内时删除该目录；不得访问网络、不得读取/写入声明路径以外的位置。

**5.2 Evaluator package**：A6 评审执行面 = 仓库内版本化工件（`tests/fixtures/a6_hardening_v1/`、scenarios、oracle、`tests/runner/a6_hardening_adapter_protocol.py`、`tests/runner/run_a6_suite.py`、`tools/validate_a6_suite.py`、`tests/a6_suite_manifest.json`）+ `docs/testing/` 固定调用命令记录；不引入新打包形式。官方 runner 输出同一次 run 的不可变 result JSON，含逐场景结果、SLO observations 与环境戳记。D1 评审包形态沿用既有发布记录。

**5.3 Reference Profile `a6_mvp_a_reference_v1` 环境描述符**：

| 项 | 值 |
|---|---|
| OS | Microsoft Windows 11 专业工作站版 10.0.26200（x86-64） |
| CPU | AMD Ryzen 5 5600H with Radeon Graphics |
| Python | CPython 3.12.8（stdlib only） |
| Runner | `tests/runner/run_a6_suite.py`（仓库内离线 runner，`python` 直接执行） |
| Storage | SQLite（ADR-0001 PRAGMA：`foreign_keys=ON`、`journal_mode=DELETE`、`synchronous=FULL`） |

runner 必须在 result JSON 中戳记实际观察到的 platform、Python 版本、wall time、monotonic duration 与时区；观察值与描述符不一致时 result 标记 `superseded`/失败而非静默放行。所有 SLO 结果仅对 `a6_mvp_a_reference_v1` 有效，不得跨 profile 外推。

## 6. 后果

### 正向后果

- `A6-013/015/018/020` 有固定可执行入口；错误表面（非零退出、不部分写入、不越界写）可由 suite 断言。
- `A6-021` 的 SLO 记录可审计、可绑定 profile；跨 profile 比较在合同层面被拒绝。
- evaluator package 复用既有 runner/validator 模式，物化成本可控，不阻塞后续 D2 决策。

### 负向后果与债务

- `start.py` 是脚本形态而非安装包；普通用户安装体验、签名与升级/卸载程序仍为 D2 债务。
- 环境描述符绑定当前开发机；换机执行需新 profile 版本或重标记，不得静默复用旧结果。

## 7. 验证与回退

- 验证方式：`A6-013..021` 可执行场景；`tools/validate_a6_suite.py` preflight；result JSON 环境戳记与描述符一致性检查。
- 失败信号：入口命令非零退出缺失、越界写入、戳记缺失或与描述符不一致、SLO 结果被跨 profile 引用。
- 回退步骤：删除 `start.py` 与 A6 suite 工件、回退本 ADR 状态；不影响任何已 verified suite。
- 数据兼容：本 ADR 不引入 schema 变更；备份/导出复用既有 Context Pack 能力。

## 8. 下游影响

| 产物 | 所需动作 |
|---|---|
| Architecture View | 创建 `ARCH-A6-HARDENING-001` |
| Suite Materialization | 按 §5.2 物化 A6 suite；preflight 后业务测试保持 `not_executed` |
| Implementation Plan | 创建 `PLAN-MVP-A-A6-IMPL-001` 与任务卡 |
| Portability / Privacy | `devdata/` 加入 .gitignore；`--clean` 路径前缀校验 |

## 9. 未决项

- D2 installer/签名/升级卸载程序与 D3 发布动作：`ONE_CLICK_DELIVERY_PLAN.md` §2 留待 C5/C6 前 ADR。
- Alpha 版本号、工件内容与发布动作：A6 Gate Review 后发布门禁单独决定。
- 以上均不影响本决定成立。
