# 一键部署与 GitHub 发布计划

## 0. 定位

本文件定义“别人可以一键部署”的验收含义和分阶段门禁，不选择当前尚不需要的 UI 框架、打包器、容器平台或云服务。

识海是 Local-first、User-owned 产品。面向普通用户的最终交付不能只提供 Docker、源码命令或数据库说明。

## 1. 四级交付目标

| Level | 使用者 | 成功标准 | 最早阶段 |
|---|---|---|---|
| `D0` | 开发模型/工程师 | 干净仓库通过一个入口命令准备环境、运行检查和启动开发模式 | MVP-A |
| `D1` | 审计者/试用者 | 无需手工建库或改 Schema，即可启动全合成演示并运行 smoke | MVP-A Alpha |
| `D2` | 普通用户 | 下载受支持平台安装包，点击安装并启动；首次设置只要求选择数据位置和隐私选项 | MVP-C Beta |
| `D3` | GitHub 用户 | Release 页面提供源码 tag、安装包、校验值、签名、变更、限制、升级和恢复说明 | Product Release |

最终目标是同时达到 `D2 + D3`。`D0` 或 Docker 单独通过不得宣传为“一键部署”。

## 2. 运行与打包决策时点

- A5 开始前建立 UI/runtime ADR，比较桌面应用、本地 Web 壳和其他可行方案。
- A6 前建立开发启动与 evaluator package ADR。
- C5/C6 前建立 installer、更新、签名和 release-channel ADR。
- 支持平台、Windows-first 与否、是否提供容器属于届时决策；本文件不提前裁决。
- 默认运行必须本地可用，不以云账号、在线模型或外部数据库为前置。

## 3. D0：一个入口命令

入口必须完成或明确拒绝：

- 检查受支持 runtime 版本。
- 创建仓库内或用户选择的合成开发数据根。
- 初始化/迁移测试数据库。
- 运行最小 preflight 和 smoke。
- 启动应用并输出本地访问入口。
- 失败时给出可行动错误，不下载或读取工作区外个人资料。

具体命令名称由实现 ADR 决定。文档不得在命令存在前写“可一键启动”。

## 4. D1：评审包

Given 干净机器和 Release Candidate 工件，When 评审者执行唯一启动入口，Then：

- 不要求手工 SQL、环境变量拼接或编辑配置文件。
- 只加载版本化合成 demo pack。
- 网络不可用时核心功能仍可启动。
- 运行 smoke 后能完整清除合成数据。
- 失败不会修改用户真实目录或覆盖现有数据。

## 5. D2：普通用户安装包

安装验收至少覆盖：

1. 安装包签名和校验值可验证。
2. 用户可选择或确认数据目录，默认不上传。
3. 首次启动显示真实状态，不将 demo 数据混入用户数据。
4. 升级前创建兼容备份或提供明确回滚点。
5. 升级失败保留旧 Canonical/Source，可回到上一版本。
6. 卸载程序不得默认删除用户拥有的数据；删除必须独立确认并说明备份/导出副本。
7. 导出包可在不运行当前版本的情况下被普通工具读取。
8. 无管理员权限、磁盘不足、路径不可写和数据库损坏均有明确失败行为。

## 6. D3：GitHub Release

每个公开 Release 必须包含：

- 版本号、source tag 和不可移动 commit。
- 支持平台、最低环境和已知限制。
- 安装包及 SHA-256；条件允许时提供签名。
- 构建 provenance、依赖清单/SBOM 和许可证信息。
- clean-install、upgrade、rollback、backup/restore、privacy smoke 的实际结果。
- 数据格式/Schema 兼容说明和降级路径。
- 安全报告入口、隐私说明和合成 demo 数据声明。
- 对应 PRD/SPEC/ADR/Verification/Gate/Release Record 链接。

公开仓库还必须有 `README`、`LICENSE`、`SECURITY`、`CONTRIBUTING`、版本支持策略和秘密扫描。具体许可证需要在 `DQ-005` 裁决后决定。

## 7. CI/CD 门禁

未来 CI 只负责可复现检查和构建，不能替代产品裁决或人工发布授权。推荐流水线阶段：

```text
static baseline
-> semantic suites
-> privacy/secret scan
-> build
-> clean-install smoke
-> upgrade/rollback smoke
-> artifact hash/SBOM/sign
-> manual Product Release approval
-> GitHub Release
```

required job 的 skip、取消或缺失不能合并为 green。公共发布使用受保护 tag/release 环境；凭据不得进入仓库或测试 result。

## 8. 回滚与支持

- Recovery Point 面向工程恢复；Product Release rollback 面向用户数据和应用版本，两者必须同时存在。
- 每个迁移必须声明 forward、rollback 或 restore-only 策略。
- 如果旧版本不能读取新数据，升级前必须有可验证备份和兼容警告。
- 发布后发现 P0/P1 时停止分发，保留失败证据，发布新修复版本；不移动旧 tag。

## 9. 当前状态

当前仅达到 Micro 工程 Recovery Point，尚未达到 `D0`。仓库没有用户 UI、安装包、发布构建或 Product Release；任何文档不得声称已经可以一键部署。

当前 A1 处于 `implementation_planned`，下一动作是 `AS-TASK-001`，不是部署。A1 suite 已物化但未执行；A1 只需保证未来 runtime 决策不会破坏本地、离线、可测试和可移植边界。

## 10. 模型责任链

| 阶段 | 责任角色 | 必须留下的证据 |
|---|---|---|
| D0/D1 规划 | Planner | runtime/package ADR、Acceptance、clean-machine suite、Approved Plan |
| 构建实现 | Implementer | 范围内代码、构建脚本、定向测试，不含发布凭据 |
| 安装验证 | Verifier | clean install、first run、offline smoke、cleanup 的不可覆盖 result |
| 安全审计 | Auditor | P0-P3 Findings、secret/privacy/SBOM/路径证据 |
| 修复回归 | Debugger + Re-auditor | 复现、修复、新 result、P0/P1 独立关闭 |
| D2/D3 发布 | Public Releaser | artifact/hash/signature/SBOM/tag/Release Record/远端核对 |

角色提示词见 `docs/process/AI_EXECUTION_PROMPTS.md`。公开仓库、公开 Release 和外部通知始终需要用户明确授权。
