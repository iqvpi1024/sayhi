# Noetide v0.1.0 Synthetic Preview

## 这是一个什么版本

这是 Local-first、Python/SQLite 的合成演示预览。它演示受控 Source append、RelationshipState ChangeSet、Core View 一致性、补偿撤销和私有合成 Context Pack。

## 启动方式

解压 `Noetide-synthetic-preview-v0.1.0.zip` 后，在根目录执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run-synthetic-demo.ps1 -Recreate
```

需要 Windows 和 Python 3.12 或更新版本。运行前请对照 `SHA256SUMS.txt` 校验 ZIP。

## 重要限制

- 只使用合成演示数据。请勿输入真实个人资料、凭据或敏感内容。
- 不是完整识海产品，也不是生产个人资料系统。
- 不包含真实导入、权限/MCP runtime、同步、连接器、分享、签名安装包或升级功能。
- 采用 MIT 许可证；项目名不主张注册商标权。

详细验证与恢复步骤见 `docs/releases/PUBLIC_PREVIEW_V0.1.0_VERIFICATION.md`。
