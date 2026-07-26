# D3 GitHub Release 发布准备（待用户确认后执行）

| 字段 | 值 |
|---|---|
| 状态 | `prepared_pending_user_confirmation` |
| 拟定版本 | `v0.2.0-beta`（prerelease） |
| 基线提交 | D2 recovery tag `d2-installer-rp-20260726` 指向的提交 |
| 依据 | `ONE_CLICK_DELIVERY_PLAN.md` §6；`DEC-D2-INSTALLER-001`；`ADR-0019` |

## 1. 发布内容清单（§6 全项）

- [ ] 版本号与 source tag：`v0.2.0-beta` annotated tag（执行时才创建，不移动既有 tag）。
- [ ] 支持平台与最低环境：Windows 10/11 x64；无需预装 Python（自带 3.12.10 embedded runtime）；免管理员权限。
- [ ] 安装包及 SHA-256：`Noetide-beta-v0.2.0-win64.zip`（从 tag `v0.2.0-beta` 重建，SHA-256 `3456b2b67d8788a006c7906629b25556af5d42ba02a84a892542d7f3f0f4b8a8`）+ `SHA256SUMS-0.2.0-win64.txt`（`7cd7fae68d662d0e55a534ed30014a8d02645dec6a1044bdc4716a3495f3f29a`）；附件 digest 发布后与本地复核一致才宣告完成。注：ZIP 含构建时间戳，非逐字节可复现；来源内容以 tag 为准。
- [ ] 构建 provenance：`scripts/build-d2-beta.ps1 -Version 0.2.0 -Ref <tag>`；embedded runtime 来源与哈希见 `SBOM-v0.2.0.md`。
- [ ] 依赖清单/SBOM：`SBOM-v0.2.0.md`（零第三方 Python 依赖声明）。
- [ ] 许可证：仓库 `LICENSE` 随包分发。
- [ ] 实际验证结果引用：clean-install、首次设置、升级/回滚、卸载（保留/删除）、失败行为、隐私 smoke——全部引用 `D2_BETA_V0.2.0_VERIFICATION.md` 的真实记录。
- [ ] 数据格式/兼容说明：SQLite 库 + C5 导出 pack；旧 D1 数据目录可由 D2 首次设置直接指向；升级语义见 ADR-0019。
- [ ] 安全报告入口：`SUPPORT.md` / SECURITY 说明。
- [ ] 隐私说明与合成数据声明：发布说明顶部明示「仅合成演示数据、勿输入真实个人资料、未签名」。
- [ ] 文档链接：PRDv05、S1-S9 SPEC、ADR-0001..0019、Verification、Gate Review、Release Record。

## 2. 发布说明草稿

见 `BETA_V0.2.0_RELEASE_NOTES.md`（草稿，发布时作为 Release 正文）。

## 3. 执行步骤（用户确认后）

1. `git tag -a v0.2.0-beta -m "Noetide beta v0.2.0 (D2 one-click installer)" d2-installer-rp-20260726`
2. 以该 tag 重新构建产物并复核 SHA-256 与本记录一致；不一致则停止并报告。
3. `git push origin v0.2.0-beta`。
4. 创建 GitHub prerelease，正文用 `BETA_V0.2.0_RELEASE_NOTES.md`，上传 ZIP + SHA256SUMS。
5. 通过 GitHub API 复核附件 digest 与本地 SHA-256 一致；记录 run 链接与结果。
6. 更新 `PROJECT_STATE.md` / `CURRENT_HANDOFF.md`：公开发布 = v0.2.0-beta。

## 4. 不得执行的动作（无用户确认）

- 创建/推送 `v0.2.0-beta` 版本 tag。
- 创建 GitHub Release 或上传任何附件。
- 任何对外通知或宣称「完整一键部署」。