# Verification Result：<run_id>

创建真实结果时复制本模板到 `docs/testing/results/`。结果文件是不可改写的运行记录；修复后创建新 `run_id`，不要覆盖旧失败。

## 0. 元数据

| 字段 | 值 |
|---|---|
| Run ID | `<run_id>` |
| Slice | `<slice_id>` |
| Result | `not_executed` |
| Applicability | `current` |
| Started At | `<ISO-8601 or not_executed>` |
| Finished At | `<ISO-8601 or not_executed>` |
| Git Commit | `<commit>` |
| Suite Manifest | `<path + digest>` |
| Fixture Set | `<path + digest>` |
| Implementation | `<module refs>` |

`Result` 必须使用 S6 的封闭语义：`not_executed | passed | failed | errored | partial`。模板中的 `not_executed` 不是一次运行结果。

## 1. 环境

记录 OS、runtime、依赖锁文件 digest、locale、timezone、随机种子、网络模式和任何故障注入。敏感环境变量只记录名称或是否存在，不记录值。

## 2. 实际命令

```text
<exact command or not_executed>
```

| 字段 | 值 |
|---|---|
| Exit Code | `<integer or not_executed>` |
| Stdout Artifact | `<path + digest or absent>` |
| Stderr Artifact | `<path + digest or absent>` |
| Result Artifact | `<path + digest or absent>` |

## 3. Required 结果

| Test ID | Individual Result | Duration | Artifact / Failure |
|---|---|---:|---|
| `<test_id>` | `<passed/failed/errored/skipped_with_reason>` | `<duration>` | `<reference>` |

## 4. 汇总

| 分类 | 数量 |
|---|---:|
| Required total | `<n>` |
| Passed | `<n>` |
| Failed | `<n>` |
| Errored | `<n>` |
| Skipped with reason | `<n>` |

只有 required 全部在本次 current run 中 passed，结果才可为 `passed`。

## 5. 未执行与限制

明确列出未运行、不可适用和本结果未证明的事项。静态检查和业务测试分开报告。

## 6. 追踪回填

| PRD Requirement | SPEC Section | Acceptance Test | Implementation Module | Verification Result |
|---|---|---|---|---|
| `<FR>` | `<section>` | `<test>` | `<module>` | `<run_id + result>` |

## 7. 后续处置

记录 Finding、Change Control、重跑或 Gate Review 的引用。不得在本文件内改写 SPEC 或测试 oracle。
