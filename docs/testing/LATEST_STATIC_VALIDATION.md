# 最近静态验证结果

## 1. 运行信息

| 字段 | 值 |
|---|---|
| 日期 | 2026-07-14 |
| 命令 | `& .\tools\validate_spec_baseline.ps1` |
| 结果 | `PASSED` |
| 范围 | PRD/SPEC/追踪/测试目录的静态合同检查 |
| 业务测试 | 未执行 |

## 2. 已检查

- `PRDv04.md` SHA-256 与只读基线一致。
- 9 份 SPEC 均包含 §0-§21，版本与 `Approved` 状态匹配。
- 257 个 SPEC Acceptance Test ID 连续且唯一。
- 123 条 invariant 连续且有覆盖引用。
- 10 个 Micro 场景 `MM-001..010` 存在。
- Micro 合成文本的 SHA-256、58 字节长度和 UTF-8 locator 完全一致。
- 需求矩阵 32 行与 PRD 的 32 个唯一 FR 完全一致。
- Coverage Level 数量为 9/8/15，未出现未知等级。
- 需求矩阵展开后的 103 个唯一 Test Ref 全部指向存在的 SPEC/MM Test ID。
- 已知跨规范别名和错误状态转换不存在。
- 20 个 Markdown 文件的代码围栏成对。
- 工作区内启发式扫描未发现电话或本机用户目录；唯一 email-like 命中是已知 Git SSH endpoint `git@ssh.github.com`，不是 fixture/个人内容。

## 3. 未证明

- 没有 suite manifest、机器 fixture、runner 或 Implementation Module。
- 所有 suite 仍为 `suite_materialized=false`、`suite_executed=false`、`suite_passed=false`。
- 静态扫描不能证明业务原子性、权限隔离、撤销、删除或性能 SLO。
- 隐私检查只能确认本轮未引入真实数据来源；它不是法律或取证级证明。

后续任何 SPEC、测试目录或需求矩阵修改后，本结果自动视为 superseded，必须重新运行并更新本文。
