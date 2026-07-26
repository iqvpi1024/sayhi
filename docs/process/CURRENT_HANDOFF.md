# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-D3-RELEASE-002
slice_id: none_awaiting_year2_product_decision
current_phase: release_published
product_baseline:
  path: PRDv05.md
  version: 0.5
  canonical_lf_sha256: 34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7
release:
  tag: v0.2.0-beta
  commit: 08095cc4aca88adad6469ffe3bedc9f25bdabaf7
  url: https://github.com/iqvpi1024/sayhi/releases/tag/v0.2.0-beta
  prerelease: true
  published_at: 2026-07-26T06:59:35Z
  delivery_level: D3_github_release_beta
latest_recovery_points:
  - v0.2.0-beta
  - d2-installer-rp-20260726
  - c6-mvp-release-gate-rp-20260726
  - c5-context-pack-backup-rp-20260726
previous_release:
  tag: v0.1.3-synthetic-preview
  commit: c340eac939cdbc094d6ec8da7f4e710d879cf1c1
decision_ref: DEC-D2-INSTALLER-001
adr_ref: ADR-0019 (installer/upgrade/signing/channel)
verification: docs/releases/D2_BETA_V0.2.0_VERIFICATION.md + D3 remote digest check via GitHub API (2026-07-26, matched)
artifact: Noetide-beta-v0.2.0-win64.zip (sha256 3456b2b67d8788a006c7906629b25556af5d42ba02a84a892542d7f3f0f4b8a8, published)
next_role: Product Owner decision required
next_single_action: 等待产品负责人拍板 Year 2 入口决策（模型接入方式/真实数据红线/首个连接器/界面形态/MCP 开放时机），形成 Product Decision；此前不得开始新业务编码
scope_in:
  - 状态文档维护与小修正
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - 任何 Year 2 业务编码（需新 Product Decision）
  - 修改已发布 Release 附件或移动既有 tag
stop_condition: 无 active slice；任何新产品语义须回到 Product Decision / 新 PRD 基线流程
```

## 当前事实

- 首年路线图全部完成：Micro、A1-A6、B1-B6、C1-C6、D0-D3 均 verified 并有 recovery tag。
- `v0.2.0-beta` prerelease 已发布（2026-07-26T06:59:35Z）：tag 已推送、ZIP + SHA256SUMS 两附件已上传、GitHub API 复核远端 digest 与本地一致（ZIP `3456b2b6...f4b8a8`，SHA256SUMS `7cd7fae6...f29a`）。
- 计划偏差如实记录：tag 实际打在 `08095cc`（含发布说明文档），而非 D3 计划 §3.1 字面指定的 `db2f0cc`。
- 已发布版本如实披露：仅合成演示数据、未代码签名、Windows-only、无自动更新。
- 全量回归 392 OK 0 skip；21 个 suite validator 全 PASSED（C6 审计 `c6-20260726.json` 8/8 passed）。

## 回归基线（2026-07-26）

- 全量 configured-adapter semantic regression：392 tests OK、0 skipped（16 个 adapter 环境变量，值为模块路径形式 `noetide_micro.<x>_testing_adapter`）。
- suite validators：21 个全部 PASSED。
- 已 verified：Micro、A1-A6、B1-B6、C1-C6、Synthetic Ingestion、Context Pack、D2 Installer、D3 Release。
- 剩余路线：Year 2 入口产品决策（FR-301/302/304/305/306 均 deferred，需重开对应 DQ）。
