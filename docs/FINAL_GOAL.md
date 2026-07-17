# 识海 Noetide — 最终目标总纲

> 版本：2026-07-18
> 状态：执行中
> 当前阶段：Phase 4 — Micro-MVP 剩余部分
> 总目标：产品可用（用户可安装、录入数据、查看人物卡/时间线、确认/撤销 ChangeSet）
> 完成前不得打扰用户

---

## 阶段总览

| 阶段 | 名称 | 状态 | 完成标准 |
|------|------|------|----------|
| Phase 0 | PRD 就绪审查 | 完成 | PRDv05 Approved，项目建档 |
| Phase 1 | 九份 SPEC | 完成 | S1-S9 Approved，兼容复核 |
| Phase 2 | Micro-MVP 核心 | 完成 | TASK-001..010，49/49 passed |
| Phase 3 | MVP-A Answer Safety | 完成 | AS-TASK-001..010，35/35 passed |
| Phase 4 | Micro-MVP 剩余 | 进行中 | CLI + 人物卡 + 时间线 + ChangeSet 确认/撤销 |
| Phase 5 | MVP-B Shiling | 待开始 | 审查预算、校准、低打扰 |
| Phase 6 | MVP-C 决策室 | 待开始 | 财务/健康/决策舱室 |
| Phase 7 | 连接器 | 待开始 | 微信/日历/邮件导入 |
| Phase 8 | UI/部署/发布 | 待开始 | 多设备同步、GitHub 一键部署 |

---

## Phase 4 详细任务（当前）

### 目标
用户可以通过命令行完成完整 Micro-MVP 链路：

    录入文本 -> 识灵提出 ChangeSet -> 用户确认 -> 人物卡/时间线更新 -> 历史保留 -> 用户撤销 -> 恢复一致

### 子任务

| ID | 任务 | 交付物 | 验收标准 |
|----|------|--------|----------|
| CLI-001 | 命令行入口 | src/noetide_micro/cli.py | 可启动、可录入、可查询 |
| CLI-002 | 人物卡展示 | 人物卡格式化输出 | 显示当前状态、历史版本 |
| CLI-003 | 关系时间线 | 时间线格式化输出 | 按时间排序、显示变更 |
| CLI-004 | ChangeSet 确认 | 确认/拒绝交互 | 用户输入确认后原子发布 |
| CLI-005 | ChangeSet 撤销 | 撤销交互 | 撤销后 Core View 恢复一致 |
| CLI-006 | 数据导出 | JSON/CSV 导出 | 用户可导出全部数据 |
| CLI-007 | 集成测试 | 端到端测试 | 完整链路 pytest 通过 |
| CLI-008 | 文档更新 | README + 使用说明 | 用户可独立安装使用 |
| CLI-009 | Recovery Point | Git tag + 验证 | 可回滚到可用状态 |
| CLI-010 | GitHub 推送 | 推送到 origin | 他人可 clone 运行 |

---

## Phase 5-8 概要

### Phase 5: MVP-B Shiling
- 审查预算机制
- 识灵校准（低打扰、不越界）
- 人格保护边界

### Phase 6: MVP-C 决策室
- 财务舱室（预算、债务、资产）
- 健康舱室（体检、症状、就医）
- 决策辅助（利弊分析、承诺追踪）

### Phase 7: 连接器
- 微信聊天记录导入（合成测试）
- 日历导入
- 邮件导入
- 文件系统监控

### Phase 8: UI/部署/发布
- Web UI 或桌面应用
- 多设备同步
- 密钥恢复
- GitHub 一键部署脚本
- 公开发布

---

## 用户可验收标准（最终）

1. 安装：git clone + python -m pip install -e . 或等价命令
2. 启动：python -m noetide_micro 或 noetide 命令启动
3. 录入：输入文本，系统生成 ChangeSet
4. 确认：用户确认后，人物卡/时间线更新
5. 查看：查看人物卡、关系时间线
6. 撤销：撤销 ChangeSet，数据恢复一致
7. 导出：导出全部数据为 JSON/CSV
8. 隐私：不联网、不泄露、本地存储
9. 测试：pytest 全部通过
10. 回滚：Git tag 可回滚到任何可用版本

---

## 禁止事项（贯穿全部阶段）

- 不得修改 PRDv05.md
- 不得引入真实用户数据
- 不得提前建设多租户、多 Agent、A2A
- 不得跳过门禁（SPEC -> Test -> Implementation -> Verification）
- 未执行测试不得记为 passed
- 每次结束必须更新 PROJECT_STATE.md

---

## 当前状态

- 阶段：Phase 4 CLI-001 准备开始
- 上一完成：AS-TASK-010 Gate Review PASSED
- 下一动作：建立 CLI-001 Implementation Plan + Task Cards
- 预计：Phase 4 全部完成后，产品进入可用状态

---

> 本文件由 Codex 主模型维护，每次开始工作时读取，每次结束工作时更新。
