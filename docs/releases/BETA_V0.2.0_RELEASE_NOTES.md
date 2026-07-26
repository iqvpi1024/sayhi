# Noetide beta v0.2.0（草稿，发布时作为 Release 正文）

> 合成演示 Beta。请勿输入真实个人资料、凭据或敏感内容。本软件完全本地运行，不上传任何数据。本安装包未代码签名，Windows SmartScreen 提示属预期；请核对下方 SHA-256。

## 这是什么

识海 Noetide 的 D2 一键安装 Beta：下载、解压、双击 `scripts/Noetide Setup.cmd`，选择你的数据文件夹并完成隐私确认即可启动。首次启动显示真实状态（`Current revision: rev_010` 合成演示库）。

## 安装包

| 附件 | SHA-256 |
|---|---|
| `Noetide-beta-v0.2.0-win64.zip` | `3456b2b67d8788a006c7906629b25556af5d42ba02a84a892542d7f3f0f4b8a8` |
| `SHA256SUMS-0.2.0-win64.txt` | `7cd7fae68d662d0e55a534ed30014a8d02645dec6a1044bdc4716a3495f3f29a` |

## 平台与环境

Windows 10/11 x64；无需预装 Python（自带 3.12.10 runtime）；免管理员权限；离线可用。

## 数据属于你

- 数据目录由你在首次设置中选择，默认不上传（本软件没有任何上传功能）。
- 升级：从新版本包运行 `Noetide Upgrade.cmd`，升级前自动备份数据与旧应用文件，失败时数据不动。
- 卸载：`Noetide Uninstall.cmd` 默认只删除应用；删除数据必须显式确认完整路径，且先自动创建经过校验的备份。
- 导出：`Noetide Shell.cmd export <目录>` 生成可被普通工具读取的导出包（Markdown + JSON）。

## 已知限制

- 未代码签名；无自动更新；仅 Windows。
- 仅支持固定合成演示数据：不是真实数据生产系统。
- 不包含：多设备同步、连接器、真实导入、权限/MCP runtime、多用户。

## 验证与审计

本版本全部声明由真实执行记录支撑：`D2_BETA_V0.2.0_VERIFICATION.md`（clean-install/升级/卸载/失败行为）、`C6_RELEASE_GATE_REVIEW_2026-07-26.md`（发布门禁 P0=0/P1=0，回归 392 tests OK 0 skip，21 个 suite validator 全过）。

## 文档

PRDv05、SPEC S1-S9、ADR-0001..0019、Verification、Gate Review 记录均随仓库 tag 提供。