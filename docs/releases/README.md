# 发布与恢复说明

## 当前公开交付

当前公开版本是 `v0.1.3-synthetic-preview` GitHub prerelease：

`https://github.com/iqvpi1024/sayhi/releases/tag/v0.1.3-synthetic-preview`

它是 Windows-first、D1 级的合成预览，包含源码 ZIP、self-contained portable ZIP 和 SHA-256 文件。完整验证、tag、CI 和附件 digest 见 `PUBLIC_PREVIEW_V0.1.3_VERIFICATION.md`。

这不表示完整 PRD、真实个人资料支持、签名安装包或 D2/D3 交付已完成。

## 恢复原则

- Recovery Point 是工程恢复基线；Product Release 是面向用户的运行资产，二者不能互相替代。
- 已推送 tag 不移动、不复用；修复发布必须创建新版本和新 tag。
- 发布后发现 P0/P1 时，保留失败证据并发布新的不可变修订版本。
- 恢复时先 `git fetch origin --tags`，再核对 annotated tag 的 peel commit、对应 CI 与发布验证记录。

## 历史记录

本目录中的 Micro、A1、PRD 和流程恢复点记录为当时阶段保留审计价值。它们不覆盖 `docs/PROJECT_STATE.md`、`docs/process/CURRENT_HANDOFF.md` 或当前公开发布状态。

从 D0 到 D3 的长期门禁、已完成 D1 的范围和未完成 D2/D3 的边界见 `ONE_CLICK_DELIVERY_PLAN.md`。
