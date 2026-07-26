# SBOM：Noetide beta v0.2.0（win64 portable）

| 组件 | 版本 | 来源 | 完整性 | 许可证 |
|---|---|---|---|---|
| noetide_micro（本仓库源码） | 0.2.0-beta | git tag `v0.2.0-beta`（发布时创建） | git commit 不可变引用 | 见仓库 `LICENSE` |
| Python embedded runtime | 3.12.10 | https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip | SHA-256 `4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3`（构建时强制校验） | PSF-2.0 |
| Python 第三方包 | 无 | — | — | — |
| PowerShell/CMD 脚本 | 随仓库 | git 仓库 `scripts/` | git commit 不可变引用 | 见仓库 `LICENSE` |

声明：`src/noetide_micro` 仅使用 Python 3.12 标准库（C6 发布门禁已以 AST 审计证明，见 `C6_RELEASE_GATE_REVIEW_2026-07-26.md`）；构建过程不下载除上述 pinned runtime 外的任何组件。