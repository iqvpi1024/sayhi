# Noetide v0.1.3 Synthetic Preview

## 发布范围

这是仅含合成数据的 Windows-first D1 预览版。它不接收真实个人资料，也不表示完整 PRD、生产安装包或已签名的 D2/D3 交付。

## 本次更新

- 修复 Answer Safety 与 C1 suite 的完整性绑定，重新运行 A1 35/35 和 C1 7/7 官方 runner。
- 修复 C1 runner 对批准场景 `C1-001` 至 `C1-007` 的映射。
- 修复 Windows portable CI 对含空格 launcher 路径的调用。
- 提供 self-contained Windows portable ZIP，解压后可运行 `Noetide Start.cmd`，无需预装 Python。

## 启动

- 源码预览 ZIP：需要 Windows 与 Python 3.12 或更新版本，执行 `scripts\run-synthetic-demo.ps1 -Recreate`。
- Portable ZIP：解压后双击 `Noetide Start.cmd`，仅初始化本地合成 SQLite 数据。

发布附件包含 SHA-256 校验文件。校验不匹配时不要运行该压缩包。

## 限制

- 只使用固定合成 demo 数据；请勿输入真实个人资料、凭据或敏感内容。
- 不包含真实导入、通用 NLP、权限/MCP runtime、连接器、同步、分享、签名安装包、升级或完整长期迁移。
- 这是预发布版本，不是个人资料生产系统。
