# v0.1.3 Synthetic Preview 验证记录

## 1. 发布标识

| 字段 | 值 |
|---|---|
| Tag | `v0.1.3-synthetic-preview`，annotated tag |
| Tag object | `beb0e143fd5aa486597452ef8bee284b2ff6083d` |
| Tagged commit | `c340eac939cdbc094d6ec8da7f4e710d879cf1c1` |
| GitHub prerelease | `https://github.com/iqvpi1024/sayhi/releases/tag/v0.1.3-synthetic-preview` |
| 交付级别 | D1 Windows-first synthetic preview |

## 2. 本地验证

| 验证 | 实际命令/环境 | exit code | 结果 |
|---|---|---:|---|
| 合同与基线 | Python 3.12 stdlib，执行六个 suite validator 与 Product/SPEC baseline validator | 0 | 全部通过 |
| 语义回归 | `PYTHONPATH=src`、Micro/A1 adapter 环境变量、`python -m unittest discover -s tests/semantic -v` | 0 | 87/87 passed |
| D1 source demo | `scripts/run-synthetic-demo.ps1 -Recreate`，临时目录 | 0 | 初始化后 `Current revision: rev_010` |
| 发布构建 | `scripts/publish-synthetic-preview.ps1 -Version 0.1.3 -Tag HEAD -BuildOnly` | 0 | 源码与 portable 资产均生成 |
| tag portable smoke | 解压 tag 构建的 `Noetide-synthetic-preview-v0.1.3-win64.zip`，执行 setup 与 `Noetide Console.cmd status` | 0 | 初始化后 `Current revision: rev_010` |

当前 A1 official runner 在 `8556eea` 实际通过 35/35，C1 official runner在同一提交实际通过 7/7；对应 immutable result 已由各自 manifest 绑定。此前失败运行结果保留在 `docs/testing/results/`，不参与 current passed 声明。

## 3. GitHub CI

| Run | Ref | 结果 | 覆盖 |
|---|---|---|---|
| `29654926812` | `main` / `c340eac` | `success` | Linux 合同/语义回归与 Windows preview smoke |
| `29654930604` | tag / `c340eac` | `success` | Linux 合同/语义回归与 Windows preview smoke |

## 4. 发布资产与完整性

| 附件 | SHA-256 |
|---|---|
| `Noetide-synthetic-preview-v0.1.3.zip` | `a2ca5a4c0cda5cec4a77bf4e1a40b05eefdc611317fc36b048563fc289a58520` |
| `Noetide-synthetic-preview-v0.1.3-win64.zip` | `a418a52a04fb4c22affca2b007319f48aa96b0116a6387c5f713323ec354f19a` |
| `SHA256SUMS.txt` | `4f5699a1d904c5d5554a55d7a4ffab5019cb8447cf1e51ad6cc458caca3dc4fb` |
| `SHA256SUMS-0.1.3-win64.txt` | `f5e91431d94446de0194b6291193f441f966801dd14a4218492da2cfeb2c6d7a` |

GitHub Release API 返回的两个 ZIP asset digest 与本地 SHA-256 一致。Release 为 `isPrerelease=true`、`isDraft=false`，正文来自 `PUBLIC_PREVIEW_V0.1.3_RELEASE_NOTES.md`。

## 5. 限制

- 只允许固定合成 demo 数据；不得输入真实个人资料、凭据或敏感内容。
- 这不是完整 PRD、真实数据生产系统、签名安装包或 D2/D3 发布。
- 不包含真实导入、通用 NLP、权限/MCP runtime、同步、连接器、分享、升级或完整长期迁移。
