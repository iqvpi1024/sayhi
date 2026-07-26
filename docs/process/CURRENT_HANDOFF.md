# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-D2-INSTALLER-001
slice_id: SLICE-D2-INSTALLER-001
current_phase: release_prepared_pending_user_confirmation
product_baseline:
  path: PRDv05.md
  version: 0.5
  canonical_lf_sha256: 34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7
release:
  tag: v0.1.3-synthetic-preview
  commit: c340eac939cdbc094d6ec8da7f4e710d879cf1c1
  url: https://github.com/iqvpi1024/sayhi/releases/tag/v0.1.3-synthetic-preview
  prerelease: true
  delivery_level: D1_synthetic_preview
latest_recovery_points:
  - c5-context-pack-backup-rp-20260726
  - c6-mvp-release-gate-rp-20260726
  - d2-installer-rp-20260726
decision_ref: DEC-D2-INSTALLER-001
adr_ref: ADR-0019 (installer/upgrade/signing/channel)
verification: docs/releases/D2_BETA_V0.2.0_VERIFICATION.md (all real executions passed)
artifact: dist/Noetide-beta-v0.2.0-win64.zip (sha256 3798971cb5471043bf3b0bf79e32b668bb85c6fdd9807ad70dd120bc47264147, local only, unpublished)
next_role: Public Releaser (requires explicit user confirmation)
next_single_action: D3 release plan is complete (docs/releases/D3_RELEASE_PLAN.md, SBOM-v0.2.0.md, BETA_V0.2.0_RELEASE_NOTES.md); WAIT for explicit user confirmation, then execute D3_RELEASE_PLAN.md section 3 (tag v0.2.0-beta, rebuild+rehash check, push tag, create prerelease, upload artifacts, verify remote digests)
scope_in:
  - D3 release preparation documents only (no publish)
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - GitHub Release publication, version tag push, external notification (all require explicit user confirmation)
  - code signing (no certificate; D3 decision item)
stop_condition: D3 preparation complete and pushed; any publish action (version tag, GitHub Release, artifact upload, external notice) requires explicit user confirmation
```

## 当前事实

- D2 切片 verified，recovery tag `d2-installer-rp-20260726` 已推送；全部验证为真实执行（`D2_BETA_V0.2.0_VERIFICATION.md`）。
- `DEC-D2-INSTALLER-001`（2026-07-26）+ `ADR-0019` Accepted：Windows-first portable ZIP + 首次设置向导；升级前自动数据备份；卸载默认保留数据、显式删除强制引擎校验备份；仅 SHA-256 校验、未签名如实披露；本轮不发布。
- 构建产物 `dist/Noetide-beta-v0.2.0-win64.zip`（构建提交 `cb211f4`，SHA-256 `3798971c...4147`）仅在本机，未上传。
- 验证发现并修复两处脚本缺陷（默认参数 $PSScriptRoot 空、备份产物路径假设错误）；修复后全部验证通过。
- 全量回归 392 OK 0 skip；21 个 suite validator 全 PASSED。
- MVP C 系列全部 verified，beta_ready=true；D1 `v0.1.3-synthetic-preview` 仍是唯一公开发布。

## 回归基线（2026-07-26）

- 全量 configured-adapter semantic regression：392 tests OK、0 skipped（16 个 adapter 环境变量，值为模块路径形式 `noetide_micro.<x>_testing_adapter`）。
- suite validators：21 个全部 PASSED。
- 已 verified：Micro、A1-A6、B1-B6、C1-C6、Synthetic Ingestion、Context Pack、D2 Installer。
- 剩余路线：D3 GitHub Release（发布动作需用户明确确认）。
