# 当前模型交接包

本文件是动态执行入口，不替代 `AGENTS.md`、PRD、Approved SPEC、ADR、suite、fixture/oracle 或 Implementation Plan。

```yaml
handoff_id: HANDOFF-Y2-S4-VERIFIED-001
slice_id: SLICE-Y2-S4-CLOUD-MODEL-001
current_phase: recovery_point_published_y2s4
product_baseline:
  path: PRDv06.md
  version: 0.6
  canonical_lf_sha256: 4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8
release:
  tag: v0.2.0-beta
  commit: 08095cc4aca88adad6469ffe3bedc9f25bdabaf7
  url: https://github.com/iqvpi1024/sayhi/releases/tag/v0.2.0-beta
  prerelease: true
  published_at: 2026-07-26T06:59:35Z
  delivery_level: D3_github_release_beta
latest_recovery_points:
  - y2s4-cloud-model-rp-20260803
  - y2s3-local-web-ui-rp-20260803
  - y2s2-local-model-rp-20260803
  - y2s1-folder-import-rp-20260801
  - v0.2.0-beta
  - d2-installer-rp-20260726
  - c6-mvp-release-gate-rp-20260726
  - c5-context-pack-backup-rp-20260726
decision_ref: DEC-PRD-V06-001 (baseline), DEC-Y2-ENTRY-001 (scope), DEC-Y2-S4-001 (slice)
adr_ref: ADR-0019 (installer/upgrade/signing/channel), ADR-0021 (Y2-S2 local model), ADR-0022 (Y2-S3 local Web UI), ADR-0023 (Y2-S4 cloud model)
verification: docs/testing/results/y2s4-20260803.json (10/10 passed/current) + docs/reviews/Y2_S4_CLOUD_MODEL_GATE_REVIEW_2026-08-03.md (P0=0/P1=0)
next_role: Slice Decision Owner (Y2-S5)
next_single_action: 重开 DQ-013 并形成 DEC-Y2-S5-001（MCP runtime 最小子集）切片决策，本地优先、最小工具、显式授权、只读优先与 fail closed
scope_in:
  - Y2-S5 切片决策与 SPEC applicability review
  - slice contract 起草准备
scope_out:
  - real personal data
  - fixture/oracle changes, moving existing tags
  - 超出 Y2-S5 授权的 Year 2 业务编码（需新 Product Decision）
  - 修改已发布 Release 附件或移动既有 tag
  - 超出 DEC-Y2-ENTRY-001 授权范围的新产品语义（须回到产品负责人）
stop_condition: Y2-S5 切片超出 DEC-Y2-ENTRY-001 授权范围时停止并回到产品负责人
```

## 当前事实

- 首年路线图全部完成：Micro、A1-A6、B1-B6、C1-C6、D0-D3 均 verified 并有 recovery tag。
- `v0.2.0-beta` prerelease 已发布（2026-07-26T06:59:35Z）：tag 已推送、ZIP + SHA256SUMS 两附件已上传、GitHub API 复核远端 digest 与本地一致。
- `PRDv06.md` 是当前产品基线（canonical LF SHA-256 `4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8`）；v04/v05 历史 PRD 只读。
- Y2-S1 已 verified（2026-08-01）：文件夹导入 + 单次 poll 监视全链通过；official runner 10/10 passed/current；回归 412 OK 0 skip。
- Y2-S2 已 verified（2026-08-03）：本地模型 propose-only 全链通过；official runner 10/10 passed/current；回归 430 OK 0 skip；23 validators PASSED。
- Y2-S3 已 verified（2026-08-03）：本地 Web UI 呈现层全链通过；official runner 10/10 passed/current（`y2s3-20260803.json`）；回归 447 OK 0 skip；24 validators PASSED；Gate Review P0=0/P1=0；recovery tag `y2s3-local-web-ui-rp-20260803`。
- Y2-S4 已 verified（2026-08-03）：云端模型可选后端全链通过；official runner 10/10 passed/current（`y2s4-20260803.json`）；回归 462 OK 0 skip；25 validators PASSED；Gate Review P0=0/P1=0；recovery tag `y2s4-cloud-model-rp-20260803`。

## 回归基线（2026-08-03）

- 全量 configured-adapter semantic regression：462 tests OK、0 skipped（20 个 adapter 环境变量，值为模块路径形式 `noetide_micro.<x>_testing_adapter`）。
- suite validators：25 个全部 PASSED。
- 已 verified：Micro、A1-A6、B1-B6、C1-C6、Synthetic Ingestion、Context Pack、D2 Installer、D3 Release、Y2-S1、Y2-S2、Y2-S3、Y2-S4。
- 剩余路线：Y2-S5（MCP runtime 最小子集）。