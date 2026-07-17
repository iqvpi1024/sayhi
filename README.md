# 识海 Noetide

Local-first、User-owned、Correctable、Portable 的 Personal Context & Growth Engine。

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/iqvpi1024/sayhi.git
cd sayhi

# 设置 Python 路径并运行
$env:PYTHONPATH="$PWD\src"
python -m noetide_micro.cli init
python -m noetide_micro.cli status
```

## 完整使用流程

```bash
# 1. 初始化数据库
python -m noetide_micro.cli init

# 2. 录入文本
python -m noetide_micro.cli intake --text "从2031年9月1日起，我不再与 person_beta 联系。"

# 3. 提出 ChangeSet
python -m noetide_micro.cli propose src_micro_001

# 4. 查看 ChangeSet
python -m noetide_micro.cli changesets

# 5. 确认 ChangeSet
python -m noetide_micro.cli approve --id changeset_micro_001 --actor person_alpha

# 6. 发布 ChangeSet
python -m noetide_micro.cli publish --id changeset_micro_001

# 7. 查看人物卡
python -m noetide_micro.cli person-card

# 8. 查看时间线
python -m noetide_micro.cli timeline

# 9. 撤销 ChangeSet
python -m noetide_micro.cli revert --id changeset_micro_001

# 10. 导出数据
python -m noetide_micro.cli export --output backup.json
```

## 可用命令

- `init` — 初始化数据库
- `status` — 显示当前 revision
- `intake` — 录入文本 Source
- `propose` — 从 Source 提出 ChangeSet
- `changesets` — 查看 ChangeSet 状态
- `approve` — 确认 ChangeSet
- `publish` — 发布 ChangeSet
- `revert` — 撤销已发布 ChangeSet
- `person-card` — 查看人物卡
- `timeline` — 查看关系时间线
- `export` — 导出数据为 JSON

## 技术栈

- Python 3.12 标准库
- SQLite（本地存储）
- 无第三方依赖
- 无网络连接

## 测试

```bash
$env:NOETIDE_MICRO_ADAPTER="noetide_micro.testing_adapter"
$env:NOETIDE_ANSWER_ADAPTER="noetide_micro.answer_testing_adapter"
$env:PYTHONPATH="D:\sayhi\src"
python -m pytest tests/semantic/ -v
```

## 项目结构

```
src/noetide_micro/     # 核心实现
tests/                  # 测试
docs/                   # 文档
tmp/                    # 临时数据（Git 忽略）
```

## 许可证

MIT
