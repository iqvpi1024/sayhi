# Y2 切片与 Product-Complete 合并 Recovery Record（2026-08-03）

> 形式说明（2026-08-07 补登）：经评估，Y2 起各切片以 annotated tag 注解加本合并记录共同承担 Recovery Record 职责，不再逐切片单建记录文件。本文件是对 `docs/process/README.md` 恢复点产物要求（`recovery_point_published` 阶段表与 §8 产物职责表，对应 :87、:138）的形式补登；各切片的业务验证证据仍以 `docs/testing/results/` 下 immutable JSON 与各 Gate Review 为唯一权威。

| 字段 | 值 |
|---|---|
| Record ID | `Y2-PRODUCT-COMPLETE-RECOVERY-20260803-001` |
| 分支 | `main`（已推送 `origin/main`） |
| 产品基线 | `PRDv06.md` v0.6 Approved，canonical LF SHA-256 `4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8` |
| 覆盖恢复点 | `y2s1-folder-import-rp-20260801`、`y2s2-local-model-rp-20260803`、`y2s3-local-web-ui-rp-20260803`、`y2s4-cloud-model-rp-20260803`、`y2s5-mcp-runtime-rp-20260803`、`product-complete-rp-20260803` |

## 1. 恢复点清单

### 1.1 `y2s1-folder-import-rp-20260801`（Y2-S1 真实文件夹文本导入）

- annotated tag -> commit `f33b614dbfe5c2e225b9f09cb09b684b3e4c51eb`，已推送 origin。
- 验证摘要：official runner `docs/testing/results/y2s1-20260801.json` 同一次 run 10/10 passed/current，网络阻断、stdlib only，manifest 已绑定；全量回归 412 OK 0 skip；22 个 suite validator 全 PASSED；Gate Review `Y2_S1_FOLDER_IMPORT_GATE_REVIEW_2026-08-01.md` P0=0/P1=0。
- 范围边界：只证明合成文件夹树的 Source Vault 导入与单次 poll 监视，不宣告真实数据模式开放。

### 1.2 `y2s2-local-model-rp-20260803`（Y2-S2 本地模型提议式整理）

- annotated tag -> commit `e08eff9fca614969be3b7f6435b459e5cefecbcfc4`，已推送 origin。
- 验证摘要：official runner `docs/testing/results/y2s2-20260803.json` 同一次 run 10/10 passed/current，网络阻断、stdlib only，manifest 已绑定；全量回归 430 OK 0 skip；23 个 suite validator 全 PASSED；Gate Review `Y2_S2_LOCAL_MODEL_GATE_REVIEW_2026-08-03.md` P0=0/P1=0。
- 范围边界：只证明本地模型候选 propose-only 与版本审计，不宣告云端后端、真实模型评估或自动发布。

### 1.3 `y2s3-local-web-ui-rp-20260803`（Y2-S3 本地 Web UI 呈现层）

- annotated tag -> commit `0e2894d671b21edfa29e3c864d30e753583fa181`，已推送 origin。
- 验证摘要：official runner `docs/testing/results/y2s3-20260803.json` 同一次 run 10/10 passed/current，网络阻断、stdlib only，manifest 已绑定；全量回归 447 OK 0 skip；24 个 suite validator 全 PASSED；Gate Review `Y2_S3_LOCAL_WEB_UI_GATE_REVIEW_2026-08-03.md` P0=0/P1=0。
- 范围边界：只证明本地回环 Web 呈现链，不宣告云端后端、MCP、真实数据模式或生产级加密密钥管理。

### 1.4 `y2s4-cloud-model-rp-20260803`（Y2-S4 云端模型可选后端）

- annotated tag -> commit `af9a61e189cd1261a329e75914c5915ceaf7edf8`，已推送 origin。
- 验证摘要：official runner `docs/testing/results/y2s4-20260803.json` 同一次 run 10/10 passed/current，网络阻断、stdlib only，manifest 已绑定；全量回归 462 OK 0 skip；25 个 suite validator 全 PASSED；Gate Review `Y2_S4_CLOUD_MODEL_GATE_REVIEW_2026-08-03.md` P0=0/P1=0。
- 范围边界：只证明云端可选后端的授权门、红线门、预览门、审计与诚实降级，不宣告 MCP runtime、真实数据模式或自动上传。

### 1.5 `y2s5-mcp-runtime-rp-20260803`（Y2-S5 MCP runtime 最小子集）

- annotated tag -> commit `b30bcd11feb59a0c328eb8a59fde5dc466e720cc`，已推送 origin。
- 验证摘要：official runner `docs/testing/results/y2s5-20260803.json` 同一次 run 10/10 passed/current，网络阻断、stdlib only，manifest 已绑定；全量回归 480 OK 0 skip；26 个 suite validator 全 PASSED；Gate Review `Y2_S5_MCP_RUNTIME_GATE_REVIEW_2026-08-03.md` P0=0/P1=0。
- 范围边界：只证明 MCP runtime 最小子集的只读接入，不宣告 controlled mutate、A2A、多 Agent、真实数据模式或云端调用。

### 1.6 `product-complete-rp-20260803`（完整产品实现完成）

- annotated tag（tag object `a64fb893d59ba20358cea6e54c0be4179d9e8aa9`）-> commit `9e3875d0c32c7a1aab249a90d6b7cd84911f533d`（当时 HEAD），已创建并推送 origin。
- 验证摘要：产品定向测试 5/5 OK；全量 configured-adapter regression 485 OK、0 skipped（2026-08-03，网络禁用）；26 个 suite validator 全 PASSED；portable 空库初始化与 `/api/health` 启动检查通过；端到端服务验证（启动空库、导入文本、识灵分析、API overview、桌面/移动 Web UI）通过。
- 产物哈希：`dist/Noetide-beta-v0.3.0-win64.zip` SHA-256 `55c26e39aca14ef3839978093d55856403ce19f6ca8e222e6543f0aecb3b80f2`（portable 已构建，未发布 GitHub Release）。
- 范围边界：完整产品以本地 Web/HTTP 服务形态交付，不含 A2A、多租户账户体系、连接器、自动同步或托管云控制台；portable 未代码签名、Windows-only、无自动更新。

## 2. 恢复步骤

1. `git fetch --tags origin`，确认上述 tag 均可解析到对应 commit（`git rev-parse <tag>^{commit}`）。
2. 检出目标 commit，确认 `git status --short` 干净。
3. 执行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` 与 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1`，均须 exit code `0`。
4. 设置 `PYTHONPATH` 为仓库 `src` 并注入 21 个 `NOETIDE_*_ADAPTER` 环境变量（清单见 `tests/runner/run_c6_release_audit.py` 与 y2s1-y2s5 各 runner），运行 `python -m unittest discover -s tests -t .`；对应时期的全量回归须与各节记录的 OK 数一致或更多，且 0 skip。
5. 各 suite 的 current immutable JSON 由对应 manifest 指向，逐套运行 validator 复核绑定。
6. v0.3.0 portable 恢复：重新构建或核对 `dist/Noetide-beta-v0.3.0-win64.zip` 的 SHA-256 与 §1.6 记录一致，再执行空库初始化与 `/api/health` 检查。

## 3. 已知限制

- 本记录是形式补登：tag 创建与推送发生于 2026-08-01/2026-08-03，本文件于 2026-08-07 补写，不回填任何历史验证结果，全部数据抄自 `docs/PROJECT_STATE.md` §4 已记录的真实结果。
- Y2 各切片仅证明固定合成数据范围，不开放真实数据模式；完整产品虽支持用户真实资料，仓库仍不得新增真实个人数据。
- v0.3.0 portable 未发布 GitHub Release；公开发布仍只到 `v0.2.0-beta`。
