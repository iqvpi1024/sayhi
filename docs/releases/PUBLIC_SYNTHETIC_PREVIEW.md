# v0.1.0 Synthetic Preview

## 交付范围

`v0.1.0-synthetic-preview` 是 Windows-first、Python 3.12、Local-first 的合成演示。它证明固定的 Source append、RelationshipState ChangeSet、Core View、补偿撤销、若干合成验证和 private Context Pack 边界。

它不是完整 PRD 产品，也不接受真实个人资料。公开预览不实现真实导入、权限 runtime、MCP runtime、连接器、同步、分享、数字遗产或多 Agent。

## 启动

从源码或发布压缩包解压后的根目录运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run-synthetic-demo.ps1 -Recreate
```

该命令会在本地创建隔离 venv 和合成 SQLite 数据目录；它不上传数据，也不下载 demo 内容。前提是本机已有 Python 3.12 或更高版本。

## 完整性

发布压缩包旁提供 `SHA256SUMS.txt`。在 PowerShell 中执行：

```powershell
Get-FileHash .\Noetide-synthetic-preview-v0.1.0.zip -Algorithm SHA256
```

将输出与 `SHA256SUMS.txt` 对照。校验不匹配时不要运行该压缩包。

## 发布维护

维护者在已完成 GitHub CLI 登录后，执行 `scripts\publish-synthetic-preview.ps1`。脚本从 `v0.1.0-synthetic-preview` tag 重建资产、生成 checksum，并创建 GitHub Release；它不会移动 tag。
