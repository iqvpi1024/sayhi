# v0.1.3 Synthetic Preview 独立公开发布终审

## 结论

`v0.1.3-synthetic-preview` 可作为 D1 合成预览继续公开交付。

| 级别 | 数量 |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |

这不是完整 PRD 或 D2/D3 生产发布的结论。

## 审计范围与证据

| 项目 | 证据 | 结论 |
|---|---|---|
| 产品基线与历史保护 | Product/SPEC baseline validator exit code `0`；PRDv04/PRDv05 hash 通过 | 通过 |
| suite 完整性 | Micro、A1、B1、C1、Synthetic Ingestion、Context Pack validator 均 exit code `0` | 通过 |
| 业务回归 | Python 3.12、`PYTHONPATH=src`、87/87 semantic tests passed | 通过 |
| A1 / C1 current runner | A1 35/35、C1 7/7 immutable result 已绑定 manifest | 通过 |
| GitHub CI | `29654926812`、`29654930604` 及文档提交 `29655180588` 均为 `success` | 通过 |
| tag 与远端 | annotated tag `v0.1.3-synthetic-preview` peel 至 `c340eac939cdbc094d6ec8da7f4e710d879cf1c1` | 通过 |
| Release 元数据 | prerelease、非 draft、四个附件均 uploaded，正文与 `PUBLIC_PREVIEW_V0.1.3_RELEASE_NOTES.md` 一致 | 通过 |
| 附件完整性 | GitHub asset digest 与本地 SHA-256 一致 | 通过 |
| 实际附件启动 | 从 GitHub 下载源码 ZIP 和 portable ZIP，分别完成 D1 / portable smoke，均返回 `Current revision: rev_010` | 通过 |
| 隐私与范围声明 | 发布说明、README、Support、安全策略与状态文件均明确 synthetic-only 和 D1 边界 | 通过 |

## 仍然有效的边界

- 仅允许固定合成 demo 数据，不接受真实个人资料、凭据或工作区外数据。
- 不实现真实导入、通用 NLP、权限/MCP runtime、连接器、同步、分享、升级或完整长期迁移。
- D2/D3 的签名安装包、真实数据生产合同、升级/卸载与普通用户支持仍未开始；这些是后续产品切片，不是本次缺陷。

## 审计后动作

已发布 tag 和 Release 不移动、不重传。任何后续修复使用新版本、新 tag 与新 Release。下一步必须先通过 Product Decision 选择新的产品切片。
