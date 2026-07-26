# D2 Beta v0.2.0 一键安装验证记录

## 1. 标识

| 字段 | 值 |
|---|---|
| Slice | `SLICE-D2-INSTALLER-001`（`DEC-D2-INSTALLER-001`） |
| ADR | `ADR-0019` Accepted |
| 构建提交 | `cb211f4`（D2 foundation） |
| 构建命令 | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build-d2-beta.ps1 -Version 0.2.0 -Ref HEAD` |
| 构建 exit code | 0 |
| 产物 | `dist/Noetide-beta-v0.2.0-win64.zip` |
| 产物 SHA-256 | `3798971cb5471043bf3b0bf79e32b668bb85c6fdd9807ad70dd120bc47264147` |
| 校验文件 | `dist/SHA256SUMS-0.2.0-win64.txt` |
| 交付级别 | D2（本机验证完成，未发布 GitHub Release） |

## 2. 环境

Windows 11，PowerShell 5.1，embedded Python 3.12.10（构建时校验 SHA-256 `4acbed6d...25a3c3` 一致）。验证工作区 `%TEMP%\noetide-d2-verify`；验证前 `%LOCALAPPDATA%\Noetide` 不存在（无既有用户状态需要保护）。

## 3. 验证结果（全部真实执行）

| # | 验证 | 实际命令 | exit | 结果 |
|---|---|---|---:|---|
| 1 | clean-install 首次设置 | `setup-noetide.ps1 -Yes -DataDirectory <vroot>\userdata` | 0 | init 成功，`Current revision: rev_010`，`privacy.json`（noetide.privacy.v1，三项 ack=true）与 `data_dir.txt` 落盘 |
| 2 | 真实状态入口 | `scripts\Noetide Shell.cmd status` | 0 | `Current revision: rev_010` |
| 3 | 升级 | `upgrade-noetide.ps1 -Yes -TargetInstall <old-install>`（从新包运行） | 0 | 数据备份 `pre-upgrade-data-20260726-093441.zip`（5564 bytes）生成并校验；旧应用文件保存到 `pre-upgrade-app-20260726-093441`；应用文件替换；替换后 `status` = rev_010；数据目录未改动 |
| 4 | 卸载（默认保留数据） | `uninstall-noetide.ps1 -Yes -InstallRoot <uninstall-keep>` | 0 | 应用目录删除；`userdata\noetide.sqlite3` 保留 |
| 5 | 卸载（显式删除数据） | `uninstall-noetide.ps1 -Yes -DeleteData -ConfirmPath <data>` | 0 | 先自动创建引擎校验备份（`pre-uninstall-20260726-093629`，4 entries，sha256 manifest verified，roundtrip verified: True），引擎删除数据目录；应用目录删除；备份保留 |
| 6 | 失败行为：数据目录在应用目录内 | `setup-noetide.ps1 -Yes -DataDirectory <bundle>\app\data-inside` | 1 | 拒绝：`the data folder must be outside the application folder`；未创建任何目录（D2-INV-001） |
| 7 | 失败行为：路径不可写 | `setup-noetide.ps1 -Yes -DataDirectory <blocker-file>\sub` | 1 | 拒绝：`data folder is not writable`；exit 1 |
| 8 | 失败行为：删除确认路径不匹配 | `uninstall-noetide.ps1 -Yes -DeleteData -ConfirmPath C:\wrong\path` | 1 | 拒绝：`confirmation path does not match the data folder; deletion refused, nothing was deleted`；数据与应用目录均保留 |
| 9 | 全量语义回归 | `PYTHONPATH=src` + 16 个 adapter env（模块路径形式）+ `python -m unittest discover -s tests -t .` | 0 | Ran 392 tests，OK，0 skipped |
| 10 | suite validators | `Get-ChildItem tools\validate_*.py` 逐个 `python <validator>` | 0 | 21/21 通过 |

## 4. 验证中发现并已修复的问题

- `build-d2-beta.ps1` 默认参数 `$PSScriptRoot` 在 `powershell -File` 下为空：改为空默认 + 函数体内回退解析（已修复）。
- `uninstall-noetide.ps1` 初次假设备份产物为 `noetide_reference_pack.json`：实际 C5 备份产物为目录（`manifest.json` + `checksums.sha256` + 4 个 JSON）。已修复为校验目录并传目录给引擎 `uninstall-info --confirm-delete --backup <dir>`。修复后验证 #5 通过。首次失败运行未删除任何数据（删除前置校验正确拒绝）。

## 5. 限制（如实披露）

- 未代码签名：SmartScreen 可能提示，属预期；首次设置中明示。签名列为 D3 裁决项。
- Windows-only；无自动更新；升级由用户显式从新包运行升级脚本。
- 仍是合成演示产品：不接受真实个人资料输入；不宣称真实数据生产就绪。
- D3（GitHub Release 发布）未执行，需用户确认。