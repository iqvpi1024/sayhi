# 识海 Noetide — 最终目标总纲

> 版本：2026-07-18
> 状态：执行中
> 当前阶段：Phase 4 — Micro-MVP CLI 已完成
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
| Phase 4 | Micro-MVP CLI | 完成 | CLI-001..006 实现并验证 |
| Phase 5 | MVP-B Shiling | 待开始 | 审查预算、校准、低打扰 |
| Phase 6 | MVP-C 决策室 | 待开始 | 财务/健康/决策舱室 |
| Phase 7 | 连接器 | 待开始 | 微信/日历/邮件导入 |
| Phase 8 | UI/部署/发布 | 待开始 | 多设备同步、GitHub 一键部署 |

---

## Phase 4 完成总结

### 已实现命令

| 命令 | 功能 | 验证状态 |
|------|------|----------|
| `init` | 初始化数据库 | 通过 |
| `status` | 显示当前 revision | 通过 |
| `intake` | 录入文本 Source | 通过 |
| `propose` | 从 Source 提出 ChangeSet | 通过 |
| `changesets` | 查看 ChangeSet 状态 | 通过 |
| `approve` | 确认 ChangeSet | 通过 |
| `publish` | 发布 ChangeSet | 通过 |
| `revert` | 撤销已发布 ChangeSet | 通过 |
| `person-card` | 查看人物卡 | 通过 |
| `timeline` | 查看关系时间线 | 通过 |
| `export` | 导出数据为 JSON | 通过 |

### 完整链路验证

```
intake -> propose -> approve -> publish -> person-card -> timeline -> revert -> person-card -> timeline
```

所有步骤验证通过，数据一致性正确。

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

- 阶段：Phase 4 CLI 已完成
- 上一完成：CLI-001..006 实现并验证
- 下一动作：CLI-007 集成测试 + CLI-008 文档 + CLI-009 Recovery Point
- 预计：Phase 4 全部完成后，产品进入可用状态

---

> 本文件由 Codex 主模型维护，每次开始工作时读取，每次结束工作时更新。
