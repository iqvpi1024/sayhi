# Verification Results

本目录保存实际业务 suite 的不可改写运行结果。当前 Micro 结果为 `micro-ws01-6dd4288-20260718.json`（49/49，`passed/current`）；A1 为 `a1-ws02-85240c5-20260718.json`（35/35，`passed/current`）；Synthetic Ingestion 为 `synthetic-ingestion-ws06-2d689ea-20260718.json`（4/4，`passed/current`）。`synthetic-ingestion-ws06-2939453-20260718.json` 因 validator 工件更新为 `superseded`，保留供审计。这些结果只证明各自窄范围合同，不等于完整 PRD 已实现。

规则：

- 文件名建议为 `<YYYYMMDDTHHMMSSZ>_<slice_id>_<run_id>.md`。
- 每次运行创建新文件；失败、partial 和 superseded 结果均保留。
- 结果必须绑定 commit、manifest、fixture、implementation 和环境。
- 只有同一次 current run 的全部 required tests passed 才能记录 `passed`。
- 静态合同校验继续记录在 `docs/testing/LATEST_STATIC_VALIDATION.md`，不得放入本目录冒充业务结果。

模板：`docs/testing/VERIFICATION_RESULT_TEMPLATE.md`。
