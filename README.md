# 识海 Noetide

Local-first、User-owned、Correctable、Portable 的 Personal Context & Growth Engine。

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/iqvpi1024/sayhi.git
cd sayhi

# 安装（Python 3.12+）
pip install -e .

# 初始化数据库
noetide init

# 查看状态
noetide status
```

### 完整使用流程

```bash
# 1. 初始化
noetide init

# 2. 录入文本
noetide intake --text "从2031年9月1日起，我不再与 person_beta 联系。"

# 3. 提出 ChangeSet
noetide propose src_micro_001

# 4. 查看 ChangeSet
noetide changesets

# 5. 确认 ChangeSet
noetide approve --id changeset_micro_001 --actor person_alpha

# 6. 发布 ChangeSet
noetide publish --id changeset_micro_001

# 7. 查看人物卡
noetide person-card

# 8. 查看时间线
noetide timeline

# 9. 撤销 ChangeSet
noetide revert --id changeset_micro_001

# 10. 导出数据
noetide export --output backup.json

# 11. 查看候选队列（Review Budget）
noetide review --max-items 3
```

### 决策与成长

```bash
# 创建 Decision
noetide decision --question "Should I change jobs?" --options "stay,leave"

# 记录 Outcome
noetide outcome --decision-id decision_001 --result "better salary"

# 查看校准
noetide calibrate --decision-id decision_001

# 创建情景推演
noetide scenario --decision-id decision_001 --kind baseline --result "moderate raise"
```

## 可用命令

| 命令 | 功能 |
|------|------|
| `init` | 初始化数据库 |
| `status` | 显示当前 revision |
| `intake` | 录入文本 Source |
| `propose` | 从 Source 提出 ChangeSet |
| `changesets` | 查看 ChangeSet 状态 |
| `approve` | 确认 ChangeSet |
| `publish` | 发布 ChangeSet |
| `revert` | 撤销已发布 ChangeSet |
| `person-card` | 查看人物卡 |
| `timeline` | 查看关系时间线 |
| `review` | 查看候选队列 |
| `export` | 导出数据为 JSON |

## 技术栈

- Python 3.12 标准库
- SQLite（本地存储）
- 无第三方依赖
- 无网络连接

## 测试

```bash
# 设置环境变量
export NOETIDE_MICRO_ADAPTER=noetide_micro.testing_adapter
export NOETIDE_ANSWER_ADAPTER=noetide_micro.answer_testing_adapter

# 运行测试
python -m pytest tests/semantic/ -v
```

## 项目结构

```
src/noetide_micro/     # 核心实现
tests/                  # 测试
docs/                   # 文档
tmp/                    # 临时数据（Git 忽略）
```

## 核心原则

1. **用户拥有最终裁决权** — AI 可以提出，不得伪装成用户确认
2. **Source 永远不是自动生成结论的替代品** — 原始材料必须保留来源和定位
3. **事实不能来源于 View** — 摘要、画像和统计只能派生，不能反向成为证据
4. **Current 不覆盖 Historical** — 当前状态变化必须保留历史有效区间
5. **Hypothesis 不得自动升级为 Fact** — 必须经过用户确认或符合明确的外部验证规则

## 隐私

- 本地存储，不联网
- 不收集真实个人数据
- 所有测试使用合成数据
- 可导出、可删除、可迁移

## 许可证

MIT
