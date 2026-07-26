# ADR-0019：D2 安装、升级、签名与发布通道的技术裁决

| 字段 | 值 |
|---|---|
| Status | `Accepted` |
| Date | 2026-07-26 |
| Slice | `SLICE-D2-INSTALLER-001` |
| Decision | `DEC-D2-INSTALLER-001` |
| Plan | `docs/releases/ONE_CLICK_DELIVERY_PLAN.md` §2、§5 |
| Decision Owner | 主力工程代理（用户已全权授权） |
| Supersedes / Superseded By | `none` / `none` |

## 1. 决策问题

D2 需要同时裁决四件事：安装器形态、升级策略、签名策略、发布通道。

## 2. 候选与裁决

### 2.1 安装器形态

- Option A：自包含 portable ZIP + 首次设置向导（`Noetide Setup.cmd` -> `setup-noetide.ps1`，WinForms 目录选择 + 隐私确认）。免管理员、零第三方构建依赖、与 D1 portable 管线一致。**采纳。**
- Option B：MSI/NSIS/Inno 图形安装器。需要引入新构建链与签名证书才能避免 SmartScreen 阻断；当前无证书且违反「不引入不必要依赖」。拒绝，列为 D3 候选。
- Option C：MSIX 商店包。需要开发者账号与签名。拒绝。

### 2.2 升级策略

- 应用目录（`runtime/`、`app/`、`scripts/`）视为可整体替换的不可变单元；用户数据目录与应用目录物理分离（`data_dir.txt` 指针存放于 `%LOCALAPPDATA%\Noetide\`）。
- `upgrade-noetide.ps1`：替换前把用户数据目录压缩为 `%LOCALAPPDATA%\Noetide\backups\pre-upgrade-<timestamp>.zip`（仅当数据目录存在）；校验备份生成成功后才允许替换应用文件；失败即中止，旧应用与数据保持可用（D2-INV-003）。
- 不做自动下载更新；升级由用户显式运行新版本包内的升级脚本触发。

### 2.3 签名策略

- 本轮仅提供 SHA-256 校验文件（`SHA256SUMS-0.2.0-win64.txt`），并在发布说明与首次设置中如实披露「未签名」：Windows SmartScreen 可能提示，属预期行为。
- Authenticode/OV 证书签名需要证书采购与私钥管理流程，属于 D3 裁决；不得以任何方式伪造或暗示已签名（D2-INV-005）。

### 2.4 发布通道

- 工程通道沿用：main 分支 + recovery tag 推送（GitHub `iqvpi1024/sayhi`）。
- 产品发布通道（GitHub Release 附件、版本 tag、对外说明）为 D3，需用户确认后执行；D2 只产出本地构建与验证证据。

## 3. 数据与隐私布局

```text
%LOCALAPPDATA%\Noetide\
  data_dir.txt        # 用户数据目录指针（UTF-8，单行绝对路径）
  privacy.json        # 首次设置隐私选择（schema: noetide.privacy.v1）
  backups\            # 升级前数据备份 zip
  data\               # 默认用户数据目录（可在首次设置改选）
```
- `privacy.json` 字段：`schema_version`、`chosen_at`、`data_directory`、`load_synthetic_demo`(bool)、`acknowledged_local_only`(bool)、`acknowledged_unsigned`(bool)。
- 应用包内不含任何用户数据；包内 `RUNTIME_MANIFEST.json` 如实声明 `synthetic_only=true`。

## 4. 失败行为（D2 验收第 8 条）

- 无管理员权限：不要求提权，全部路径在用户 profile 内。
- 路径不可写/磁盘不足：`New-Item`/`Compress-Archive` 失败即中止并以可行动文案报错，exit code 1。
- 数据库损坏：设置向导在 init/status 失败时不覆盖既有目录，报错并提示使用 C5 备份恢复或重新选择空目录。
- 卸载：`uninstall-noetide.ps1` 默认仅删除应用目录；加 `-DeleteData` 仍需交互键入数据目录完整路径作为确认，且先打印导出提示。

## 5. 后果

- 正面：普通 Windows 用户下载-解压-双击 `Noetide Setup.cmd` 即可完成 D2 级安装；升级/卸载语义服从用户数据所有权。
- 代价：无签名导致 SmartScreen 提示；无自动更新；macOS/Linux 不支持。全部如实披露。
- 回退：删除 `scripts/build-d2-beta.ps1` 与 portable 新脚本即回到 D1 状态；不影响任何已 verified 切片。