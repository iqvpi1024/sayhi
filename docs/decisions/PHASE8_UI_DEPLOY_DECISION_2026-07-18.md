# Phase 8 UI/部署/发布 产品决定

## 文档信息

| 字段 | 值 |
|---|---|
| Decision ID | `DEC-PHASE8-UI-DEPLOY-001` |
| Date | 2026-07-18 |
| Product Baseline | `PRDv05.md` v0.5 Approved |
| Previous Slice | `SLICE-MVP-C-CONNECTOR-001` (completed) |
| Current Slice | `SLICE-PHASE8-UI-DEPLOY-001` |

## 1. 决定内容

Phase 8 目标：让普通用户可以通过 GitHub 一键 clone 并运行识海。

范围极度收缩：
- 更新 README 为最终用户版本
- 创建 setup.py 使项目可 pip install
- 验证干净环境可运行
- 不创建 Web UI、桌面应用或多设备同步

## 2. 目标

1. 用户可 `git clone` + `pip install -e .` 安装
2. 用户可 `noetide init` 初始化
3. 用户可完成完整 Micro-MVP 链路
4. 所有测试可在干净环境运行

## 3. 非目标（明确后置）

- Web UI
- 桌面应用（Electron/Tauri）
- 多设备同步
- 自动更新机制
- 发布到 PyPI
- Docker 镜像
- 营销网站

## 4. 完成定义

- README 包含完整安装和使用说明
- setup.py 存在且可安装
- 干净环境验证通过
- GitHub 仓库可一键 clone 运行

---
