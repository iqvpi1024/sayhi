# 产品基线索引

本文件是当前 PRD 的唯一机器可读入口。任何 SPEC、ADR、测试或实现不得自行选择另一个 PRD 版本。

```yaml
current_prd_path: PRDv06.md
current_prd_version: 0.6
current_prd_status: approved
current_prd_canonical_lf_sha256: 4513B26860A334190AF8B8656A2A506D27224D78F88B567B37BB08DF423BCAD8
previous_prd_path: PRDv05.md
previous_prd_version: 0.5
previous_prd_status: superseded_read_only
previous_prd_canonical_lf_sha256: 34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7
approval_decision: DEC-PRD-V06-001
```

规则：

- 上述 YAML 中的 PRD 路径均相对于仓库根目录解析。
- `PRDv04.md`、`PRDv05.md` 是不可修改的历史基线，不因 superseded 失去审计价值。
- 新版本必须创建新文件；不得覆盖旧版本来伪造历史连续性。
- current 变化后，所有下游 SPEC、Matrix、suite、ADR、plan 和 result 必须做 applicability/兼容复核。
- PRD Approved 不表示 SPEC 兼容、suite 物化、业务实现或业务测试通过。
