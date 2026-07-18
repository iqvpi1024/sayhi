# 识海 Noetide

识海是一个 Local-first、User-owned、Correctable、Portable 的 Personal Context & Growth Engine。本仓库公开提供 `v0.1.3-synthetic-preview`：它只演示一条已批准的合成 Micro 链路，不接收真实个人数据，也不声称实现完整 PRD。

## 当前可运行范围

- 包内合成 Source append。
- 一个 `relationship.contact: active -> no_contact` ChangeSet 的提案、确认、原子发布与补偿撤销。
- `person_card` 与 `relationship_timeline` 两个 Core View。
- 本地 SQLite，Python 3.12 标准库，无网络访问。
- 可导出 owner-private 的合成 Context Pack（JSON、Markdown、Source/Ledger 清单和 SHA-256）；不支持真实数据导入或分享导出。

不包含：真实数据导入、通用 NLP、权限 runtime、MCP、连接器、同步、财务、健康、决策工作流、分享导出、完整长期迁移或公开发布。

## 本地运行

Windows 上可用一个命令准备**仅含合成数据**的本地演示：

```powershell
.\scripts\run-synthetic-demo.ps1 -Recreate
```

这只达到合成预览级 D1；不下载真实数据，也不是普通用户生产安装包。许可证、校验和限制见 `docs/releases/PUBLIC_SYNTHETIC_PREVIEW.md`。

Windows 试用者也可以下载 self-contained portable ZIP，解压后双击 `Noetide Start.cmd`。该包自带 Python runtime，只创建合成 SQLite 数据；它同样是 D1 合成预览，不是签名的生产安装包。

手动等价流程：

```powershell
python -m venv .venv
$env:PYTHONPATH = "$PWD\src"

$dataDir = Join-Path $env:TEMP 'noetide-demo'
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir init
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir intake
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir propose src_micro_001
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir approve --id changeset_micro_001
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir publish --id changeset_micro_001
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir person-card
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir timeline
.\.venv\Scripts\python -m noetide_micro --data-dir $dataDir revert --id changeset_micro_001
```

`intake --text ...` 会被拒绝并返回非零 exit code，因为当前 RC 仅允许包内的合成 demo Source。

## 验证

```powershell
$env:PYTHONPATH = "$PWD\src"
python .\tools\validate_micro_suite.py
python .\tools\validate_answer_safety_suite.py
python -m tests.runner.run_micro_suite --adapter noetide_micro.testing_adapter --output tmp\micro-run.json
python -m tests.runner.run_answer_safety_suite --adapter noetide_micro.answer_testing_adapter --output tmp\answer-run.json
```

测试 adapter 仅用于测试，不被 CLI 导入。当前可复现的验证记录位于 `docs/testing/results/`。

## 开发状态

当前执行阶段与唯一下一动作见 `docs/PROJECT_STATE.md` 和 `docs/process/CURRENT_HANDOFF.md`。产品语义以 `PRDv05.md`、Approved SPEC 和 Decision 为准；不要将 README 示例外推为完整产品能力。
