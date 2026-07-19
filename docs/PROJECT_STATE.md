# 项目状态

## 1. 恢复入口

每次任务按 `AGENTS.md` 的顺序恢复。当前产品语义以 `docs/product/CURRENT_PRODUCT_BASELINE.md` 指向的 `PRDv05.md` v0.5 为准；历史 PRD、SPEC、结果和 tag 保留审计价值，不得覆盖动态状态。

## 2. 当前快照

| 字段 | 值 |
|---|---|
| 项目 | 识海 Noetide |
| 当前产品基线 | `PRDv05.md` v0.5 Approved，canonical LF SHA-256 `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前公开发布 | `PUBLIC-PREVIEW-D1-001` 已发布 |
| 当前工作切片 | `SLICE-MVP-B-COMMITMENT-001` |
| 当前阶段 | `architecture_decided` |
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
5. B2 Episode/summary 已完成合同、ADR、suite、实现、官方 runner、Gate Review 与 recovery point；它只证明 FR-103 的固定合成切片。
6. B2 official suite 的 `B2-001..008` 为 8/8 passed/current；recovery tag `b2-episode-summary-rp-20260719` 已推送。
14. `DEC-MVP-B-COMMITMENT-001` 已选择 B3 的固定合成 Commitment 生命周期切片；尚未开始 B3 代码或 suite 物化。
15. B3 applicability review 结论为 `pass_with_slice_contract_required`；基础 SPEC 不足以直接授权 Commitment 业务实现。
16. `SPEC-B3-COMMITMENT-001` 与合同复核已完成；尚未建立 B3 traceability、ADR、suite 或代码。
17. B3 FR-104 traceability 已建立；尚未物化 B3 suite 或实现。
18. `ADR-0005` 与 `ARCH-B3-COMMITMENT-001` 已接受；未创建 B3 fixture、oracle、runner 或代码。

## 4. 真实验证结果

| 范围 | 真实结果 |
|---|---|
| Product / SPEC baseline validator | exit code `0` |
| Micro、A1、B1、C1、Synthetic Ingestion、Context Pack suite validator | 全部 exit code `0` |
| 全量 semantic regression | B2 current verification 时 107/107 passed |
| D1 source demo | exit code `0`，初始化后 `Current revision: rev_010` |
| tag 构建 portable smoke | exit code `0`，初始化后 `Current revision: rev_010` |
| GitHub Actions | `29654926812`、`29654930604` 均为 `success` |
| Release 附件 digest | GitHub API 与本地构建 SHA-256 一致 |
| 独立公开发布终审 | `PUBLIC_PREVIEW_V0.1.3_INDEPENDENT_AUDIT.md`：P0=0、P1=0 |
| B2-TASK-002 | `b2-task002-6944b22-20260719.json`：定向 5/5 passed；全量 semantic regression 103 passed、B2 contract 8 skipped；B2 official suite `not_executed` |
| B2-TASK-003 | `b2-task003-c2fba31-20260719.json`：定向 4/4 passed；全量 semantic regression 107 passed、B2 contract 8 skipped；B2 official suite `not_executed` |
| B2 官方 suite | `b2-a810513-20260719.json`：8/8 passed/current；全量 semantic regression 107 passed |

完整命令、环境、哈希和限制见 `docs/releases/PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。静态校验不被表述为业务测试通过；历史失败运行结果仍保留在 `docs/testing/results/`。

## 5. 风险与边界

- 当前发布只允许固定合成 demo 数据。不得输入、导入、提交或推断真实个人资料、凭据或工作区外数据。
- 该版本不是完整 PRD 产品，不实现真实导入、通用 NLP、权限/MCP runtime、同步、连接器、分享、签名安装包、升级或真实数据生产合同。
- D2/D3 所需签名、升级/卸载、真实数据安全合同和普通用户生产支持仍未完成；不得因 portable ZIP 存在而宣称已完成。

## 6. 下一步唯一建议动作

**物化 B3 executable suite：固定合成 fixture、oracle、manifest、adapter protocol、offline runner 与 preflight validator。**
