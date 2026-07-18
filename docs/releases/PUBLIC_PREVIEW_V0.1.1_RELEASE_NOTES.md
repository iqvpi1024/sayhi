# Noetide v0.1.1 Synthetic Preview

## 修复

- 修复 Windows 一键预览对 `setuptools` 的隐式依赖。启动器现在仅使用 Python 3.12 标准库 venv、仓库内 `src` 和本地 `noetide.cmd`，不构建 wheel，不下载构建依赖。
- GitHub Actions Windows 烟测覆盖该无构建依赖路径。

## 启动方式

解压 `Noetide-synthetic-preview-v0.1.1.zip` 后，在根目录执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run-synthetic-demo.ps1 -Recreate
```

需要 Windows 与 Python 3.12 或更新版本。请先将 ZIP SHA-256 与 `SHA256SUMS.txt` 对照。

## 重要限制

- 只使用合成演示数据。请勿输入真实个人资料、凭据或敏感内容。
- 不包含真实导入、权限/MCP runtime、同步、连接器、分享、签名安装包或升级功能。
- 这是预发布版本，不是完整个人资料生产系统。
