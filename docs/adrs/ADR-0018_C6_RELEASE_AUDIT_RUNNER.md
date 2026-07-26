# ADR-0018：C6 发布就绪审计的执行形态

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-26 |
| Slice | `SLICE-MVP-C-RELEASE-001` |
| Contract | `SPEC-C6-RELEASE-001` v0.1 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes / Superseded By | `none` / `none` |

## 1. 决策问题

C6 需要一个裁决：发布就绪审计以什么形态执行——人工清单、CI 工作流，还是仓库内可执行审计 runner。

## 2. 适用基线

| 类型 | 引用 |
|---|---|
| PRD / Decision | 路线图 C6；`DEC-MVP-C-RELEASE-001` |
| SPEC | `SPEC-C6-RELEASE-001` §2..§5；S6 v0.5、S7 v0.4 |
| Acceptance Test | `C6-001..008` |
| Traceability | 矩阵 §4.20 |

## 3. 候选方案

### Option A：仓库内可执行审计 runner（stdlib 子进程编排）

- 做法：`tests/runner/run_c6_release_audit.py` 以子进程真实执行 20 个 suite validator 与全量 regression（16 个 adapter 环境变量），机器扫描隐私/依赖/网络隔离，复用 `pack_backup` 做恢复演练，产出 immutable JSON result 并绑定 manifest（复用既有 manifest/validator 机制）。
- 优点：与全仓"未执行不得称通过"铁律一致；本地可复现；零新依赖；结果可绑定可审计。
- 代价：审计 runner 自身需要被 validator 覆盖（沿用既有模式，runner 是 bound artifact）。

### Option B：人工清单 + 文档声明

- 代价：违反"未执行不得称通过"铁律；不可复现。拒绝。

### Option C：CI 工作流为唯一审计面

- 代价：本地不可复现；与 offline runner 模式不一致；可作为补充而非替代。拒绝。

## 4. 决定

采纳 Option A。审计只读：不修改任何已 verified artifact；恢复演练在临时目录进行；扫描为纯读取。隐私扫描模式清单：`password`、`@gmail.com`、`@qq.com`、`@163.com`、`1[3-9]\d{9}`（手机号模式）、`身份证`、`debt`、`健康`（ fixture 合成文案允许 `synthetic` 前缀的健康类占位——本仓库无此类，扫描命中即失败并人工复核）。依赖白名单：Python 3.12 stdlib + `noetide_micro` 包内导入。

## 5. 后果

- 正面：发布就绪从文档声明变为可执行证明；D2/D3 可直接复用该审计 runner。
- 代价：审计 runner 全量执行约 1 分钟；可接受。
- 回退：删除 `run_c6_release_audit.py` 与 C6 manifest；不影响任何已 verified 切片。
