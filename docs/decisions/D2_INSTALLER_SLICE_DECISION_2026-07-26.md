# D2 一键安装切片产品决定

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-D2-INSTALLER-001` |
| Date | 2026-07-26 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Gate | `C6-MVP-RELEASE`（已 verified，beta_ready=true，recovery tag `c6-mvp-release-gate-rp-20260726`） |
| Current Slice | `SLICE-D2-INSTALLER-001` |

## 1. 决定内容

选择 D2 一键安装作为下一阶段（`ONE_CLICK_DELIVERY_PLAN.md` Level D2：普通用户下载受支持平台安装包，点击安装并启动；首次设置只要求选择数据位置和隐私选项）。具体决定：

1. 交付形态：Windows-first 自包含 portable ZIP + 交互式首次设置向导（免管理员权限）。不引入 MSI/NSIS/Inno 安装器（理由见 ADR-0019）。
2. 数据目录完全由用户拥有：默认 `%LOCALAPPDATA%\Noetide\data`，首次设置可改选；应用目录绝不写用户数据。
3. 隐私选项进入首次设置：明示 local-only、无上传、合成 demo 可选项；选择结果落盘为 `privacy.json`。
4. 升级路径：应用目录可整体替换；替换前自动对用户数据目录做兼容备份（zip 快照到 `%LOCALAPPDATA%\Noetide\backups\`）；升级失败数据不丢失。
5. 卸载路径：卸载只移除应用目录，绝不默认删除用户数据；数据删除必须独立键入确认，且先提示导出（C5 pack）。
6. 完整性：SHA-256 校验文件随包发布；Authenticode 签名本轮暂缓（无证书），在发布说明中如实披露，列为 D3 裁决项。
7. 本轮只构建并在本机真实验证，不发布 GitHub Release（D3 需用户确认）。

## 2. 产品依据

- `ONE_CLICK_DELIVERY_PLAN.md` §5：D2 八条验收（校验值、数据目录选择、真实状态、升级备份、升级失败保留、卸载不删数据、导出可读、失败行为明确）。
- `ONE_CLICK_DELIVERY_PLAN.md` §2：installer/更新/签名/release-channel ADR 应在 C5/C6 后建立——本切片建立 ADR-0019。
- PRD 核心不可违反：用户必须能够纠正、撤销、封存、删除和导出——卸载/升级语义必须服从用户数据所有权。
- C6 Beta 门禁已确认全部首年切片 verified，具备 D2 构建前提。

## 3. 切片范围

- `scripts/portable/` 新增/更新：`Noetide Setup.cmd`、`setup-noetide.ps1`（首次设置向导：数据目录 + 隐私选项 + 真实状态显示）、`Noetide Upgrade.cmd`、`upgrade-noetide.ps1`（升级前备份 + 应用替换）、`Noetide Uninstall.cmd`、`uninstall-noetide.ps1`（保留数据、显式确认删除）。
- `scripts/build-d2-beta.ps1`：构建 `Noetide-beta-v0.2.0-win64.zip` + SHA256SUMS（复用 embedded Python 3.12.10 runtime 与既有 pin hash）。
- 真实验证记录 `docs/releases/D2_BETA_V0.2.0_VERIFICATION.md`：clean-install、首次设置、升级、卸载、失败行为、全量回归、validator 全过。
- `ONE_CLICK_DELIVERY_PLAN.md` §9 状态更新为 D2 已验证（未发布）。

## 4. 非目标

- 发布 GitHub Release、推送版本 tag 到远端 release、对外通知（D3，需用户确认）。
- MSI/NSIS/Inno 安装器、自动更新通道、Authenticode 签名、代码签名证书采购。
- 真实个人数据生产合同：本包仍只允许合成/用户自行录入的演示用途；不宣称真实数据生产就绪。
- GUI 框架选型、macOS/Linux 安装包、容器交付。
- 修改任何已 verified 切片的 fixture/oracle/结果或业务代码语义。

## 5. 不变量

- `D2-INV-001`：应用目录只读于用户数据；所有用户数据只写入用户选择/确认的数据目录。
- `D2-INV-002`：首次设置必须显式呈现数据位置与隐私选项；不得静默默认开启任何上传（本项目无任何上传面）。
- `D2-INV-003`：升级前必须存在可验证的用户数据备份；升级失败时旧数据保持可用。
- `D2-INV-004`：卸载默认保留用户数据；删除数据需独立显式确认并先行提示导出。
- `D2-INV-005`：构建产物必须附 SHA-256；未签名事实必须如实披露，不得宣称已签名。
- `D2-INV-006`：全部验证为真实执行并记录命令/环境/exit code；不得把 D2 宣称成 D3 或完整一键部署。

## 6. 授权与下一步

本决定授权 ADR-0019（installer/升级/签名/channel 技术裁决）与 D2 脚本实现和本机真实验证。发布动作（D3）仍需用户明确确认。