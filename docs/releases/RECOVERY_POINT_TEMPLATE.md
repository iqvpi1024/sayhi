# Recovery Point：<tag>

## 0. 身份

| 字段 | 值 |
|---|---|
| Date | `<YYYY-MM-DD>` |
| Scope | `<slice/process scope>` |
| Branch | `<branch>` |
| Commit | `<full commit>` |
| Annotated Tag | `<tag>` |
| Remote | `<remote name>` |
| Remote Verified | `<yes/no>` |

## 1. 包含内容

列出本恢复点新增或改变的权威产物，以及明确未包含的业务能力。

## 2. 门禁证据

| Evidence | Result | Reference |
|---|---|---|
| Gate Review | `<result>` | `<path>` |
| Static Validation | `<result>` | `<path + digest>` |
| Business Verification | `<result/not_executed>` | `<path or absent>` |
| PRD Hash | `<hash>` | `PRDv04.md` |
| Privacy Check | `<result>` | `<reference>` |

## 3. 限制

明确本 tag 不能证明什么，特别是尚未物化/执行的 suite 和尚不存在的实现。

## 4. 恢复步骤

```text
git fetch <remote> --tags
git rev-parse <tag>^{}
git worktree add <new-path> <tag>
<validation command>
```

实际记录不得包含本机用户名、凭据或工作区外个人路径；使用占位符说明本地目标路径。

## 5. 校验预期

记录恢复后应看到的 branch/tag/commit 关系、校验 exit code 和允许的 `not_executed` 项。

## 6. 后续动作

只写恢复点之后的一个建议动作；不得把恢复动作本身解释为进入下一产品阶段。
