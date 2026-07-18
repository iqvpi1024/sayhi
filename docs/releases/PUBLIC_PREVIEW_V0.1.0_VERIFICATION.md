# v0.1.0 Synthetic Preview 验证记录

| 字段 | 值 |
|---|---|
| Release Candidate Commit | `6fa49c06309117eec57992b6c5fb341575682e4f` |
| Archive | `Noetide-synthetic-preview-v0.1.0.zip` |
| SHA-256 | `42349472a5573fbc4b3c0f51c25b6a602af1f7e96679b146a162152011613e60` |
| 平台 | Windows 11；Python 3.12.8；SQLite 3.45.3 |
| 数据范围 | 仅合成数据 |
| D1 | `passed` |
| D2/D3 | `not_completed` |

## 实际验证

1. `powershell -ExecutionPolicy Bypass -File .\scripts\build-public-preview.ps1 -OutputDirectory .\tmp\public-preview-final -Version 0.1.0`，exit code `0`。
2. `Get-FileHash` 与 `SHA256SUMS.txt` 的 SHA-256 完全一致。
3. `Expand-Archive` 到新的临时目录后，确认 ZIP 含 `LICENSE`、`SECURITY.md`、`CONTRIBUTING.md`、`SUPPORT.md` 与 `scripts/run-synthetic-demo.ps1`。
4. 从解压目录运行 `run-synthetic-demo.ps1 -Recreate`，exit code `0`；实际完成 local wheel、隔离 venv、module/console smoke 和合成 SQLite 初始化。

## 结论与限制

该资产可以让有 Python 3.12 的 Windows 用户在解压后用一个 PowerShell 命令启动本地合成演示。它不是签名安装包，不支持升级/卸载、真实个人数据、普通用户生产部署或完整 D2/D3 发布承诺。

## Git 引用

- `main` 与 `codex/kimi-end-to-end-release-candidate` 已推送到 GitHub。
- annotated tag `v0.1.0-synthetic-preview` 已推送，指向生成该 archive 的 `6fa49c0`。
- GitHub Release 页面与附件上传需要单独的 GitHub 网页或 CLI 登录；SSH push 成功不代表 Release 已创建。
