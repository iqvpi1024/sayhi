# D0 一键本地合成演示验收

本合同只证明开发者/审计者级别的 D0/D1 本地合成演示，不是普通用户安装包或 GitHub Release。

```powershell
.\scripts\run-synthetic-demo.ps1 -InstallRoot <empty-local-directory> -Recreate
```

通过条件：脚本检查 Python >=3.12、创建隔离 venv、从当前本地仓库安装零 runtime dependency 包、初始化合成 SQLite 数据、运行 module 与 console smoke，并在失败时返回非零。脚本不读取工作区外个人资料，不下载 demo 数据，不创建网络服务。

未证明：安装包签名、升级/卸载、真实数据、数据目录选择 UI、公开发布、许可证、D2/D3。
