# Release Candidate Recovery Record

| 字段 | 值 |
|---|---|
| Record ID | `RC-RECOVERY-20260718-001` |
| 分支 | `codex/kimi-end-to-end-release-candidate` |
| 被测实现提交 | `5a324f9` |
| 产品基线 | `PRDv05.md` v0.5，Approved |
| 发布权限 | 未授权推送、合并 `main`、正式 tag 或 GitHub Release |

## 已验证范围

- Micro：49/49 required IDs passed，`a603085`。
- A1 Answer Safety：35/35 required IDs passed，`a603085`。
- B1 Candidate Review：5/5 required IDs passed，`a603085`。
- C1 Decision/Outcome：7/7 required IDs passed，`5a324f9`；未映射 C1 integration test 失败会使 runner 失败。
- Synthetic Ingestion：4/4 required IDs passed，`a603085`。
- Context Pack：6/6 required IDs passed，`a603085`。
- 完整 semantic discovery：在 `PYTHONPATH=src` 及两个 test-only adapter 注入下 87/87 passed。
- Windows D0/D1 合成一键演示：local wheel、isolated venv、module 和 console smoke passed，记录见 `docs/testing/results/packaging-ws12-cdf1de6-20260718.json`。
- 静态基线、六个 suite validator 与 `git diff --check` 均实际返回 exit code `0`。

每个 suite 的 current immutable JSON 由对应 `tests/*_suite_manifest.json` 指向。证据提交本身可能晚于被测实现提交；这不会改变已被测代码。任何后续实现改动都必须使受影响 suite 重新运行，不能复用本记录。

## 恢复步骤

1. 检出本分支中承载本记录的 commit，确认 `git status --short` 只出现已知用户隔离文件。
2. 执行 `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` 与 `powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1`。
3. 设置 `PYTHONPATH` 为仓库 `src`，分别运行六个 manifest validator 和对应 offline runner；输出必须为新的 JSON 文件，不能覆盖现有 result。
4. 运行 `powershell -ExecutionPolicy Bypass -File .\scripts\run-synthetic-demo.ps1 -InstallRoot .\tmp\recovery-demo -Recreate`。
5. 仅在独立审计无 P0/P1 后，才考虑建立新的恢复点；不得把本记录当作正式公开发布。

## 已知限制

- 仅合成数据；不读写真实个人资料，不实现真实导入、分享导出、权限 runtime、MCP runtime、连接器、同步或多 Agent。
- D2/D3 普通用户安装与 GitHub Release 仍受 `DQ-005` 和后续产品/发布工作限制。
- 未推送、未合并 `main`、未创建正式 tag 或 Release。
