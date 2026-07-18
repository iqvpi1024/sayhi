# 项目状态

## 1. 恢复入口

每次任务按 `AGENTS.md` 的顺序恢复。当前产品语义以 `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的 `PRDv05.md` v0.5 为准；历史 PRD、SPEC、结果和 tag 保留审计价值，不得覆盖动态状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 当前产品基线 | `PRDv05.md` v0.5 Approved，canonical LF SHA-256 `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前公开发布 | `PUBLIC-PREVIEW-D1-001` 已发布 |
| 当前工作切片 | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| 当前阶段 | `implementation_planned` |
| 当前公开版本 | `v0.1.3-synthetic-preview` GitHub prerelease |
| tag / commit | annotated tag `v0.1.3-synthetic-preview` -> `c340eac939cdbc094d6ec8da7f4e710d879cf1c1` |
| GitHub Release | `https://github.com/iqvpi1024/sayhi/releases/tag/v0.1.3-synthetic-preview` |
| 交付级别 | 已发布 D1 Windows-first 合成预览；D2/D3 未完成 |
| 分支 | `main`，已推送至 `origin/main` |

## 3. 已完成内容

1. PRD v0.5、S1-S9 Approved 语义基线、Micro 关系链路、Answer Safety、Candidate Review、Decision/Outcome、合成导入和私有合成 Context Pack 均保留为当前实现范围内的合成能力。
2. A1 suite 完整性绑定已修复，官方 runner 在 `8556eea` 实际通过 35/35；C1 runner 场景映射已修复，官方 runner 在同一提交实际通过 7/7。
3. `v0.1.3-synthetic-preview` 已发布源码 ZIP、Windows portable ZIP 及各自 SHA-256 校验文件。portable 包自带 Python runtime，解压后可初始化合成 SQLite 并读取 `rev_010`。
4. GitHub Actions 对 `main` 和 tag 的两个 run 均通过，包含 Linux 合同/语义回归与 Windows portable smoke。
5. `DEC-MVP-B-EPISODE-SUMMARY-001` 与 `SPEC-B2-EPISODE-SUMMARY-001` 已定义 B2 Episode 与分层摘要的仅合成、Derived-only 合同；追踪已建立，尚未开始业务代码。
6. `ADR-0004` 与 `ARCH-B2-EPISODE-SUMMARY-001` 已接受 SQLite 分层持久化与 Derived rebuild 边界；suite 尚未物化。
7. B2 fixture、oracle、manifest、adapter protocol、offline runner 与 validator 已物化；尚未执行 B2 业务测试。
8. `PLAN-MVP-B-B2-IMPL-001` 与任务卡已批准；只授权从 `B2-TASK-001` 开始。
9. `B2-TASK-001` 已完成 Episode/Derived storage foundation；定向 3/3 passed，B2 official suite 仍为 `not_executed`。

## 4. 真实验证结果

| 范围 | 真实结果 |
|---|---|
| Product / SPEC baseline validator | exit code `0` |
| Micro、A1、B1、C1、Synthetic Ingestion、Context Pack suite validator | 全部 exit code `0` |
| 全量 semantic regression | 87/87 passed |
| D1 source demo | exit code `0`，初始化后 `Current revision: rev_010` |
| tag 构建 portable smoke | exit code `0`，初始化后 `Current revision: rev_010` |
| GitHub Actions | `29654926812`、`29654930604` 均为 `success` |
| Release 附件 digest | GitHub API 与本地构建 SHA-256 一致 |
| 独立公开发布终审 | `PUBLIC_PREVIEW_V0.1.3_INDEPENDENT_AUDIT.md`：P0=0、P1=0 |

完整命令、环境、哈希和限制见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。静态校验不被表述为业务测试通过；历史失败运行结果仍保留在 `docs/testing/results/`。

## 5. 风险与边界

- 当前发布只允许固定合成 demo 数据。不得输入、导入、提交或推断真实个人资料、凭据或工作区外数据。
- 该版本不是完整 PRD 产品，不实现真实导入、通用 NLP、权限/MCP runtime、同步、连接器、分享、签名安装包、升级或真实数据生产合同。
- D2/D3 所需签名、升级/卸载、真实数据安全合同和普通用户生产支持仍未完成；不得因 portable ZIP 存在而宣称已完成。

## 6. 下一步唯一建议动作

**执行 `B2-TASK-002`：实现 fixed Episode candidate 的 ChangeSet publish/revert 边界。**
