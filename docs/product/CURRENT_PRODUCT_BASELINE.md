# 产品基线索引

本文件是当前 PRD 的唯一机器可读入口。任何 SPEC、ADR、测试或实现不得自行选择另一个 PRD 版本。

```yaml
current_prd_path: PRDv05.md
current_prd_version: 0.5
current_prd_status: approved
current_prd_canonical_lf_sha256: 34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7
previous_prd_path: PRDv04.md
previous_prd_version: 0.4
previous_prd_status: superseded_read_only
previous_prd_canonical_lf_sha256: F2A4D795FC8A8131176F9E2FC3B624270038B455851D895B5AD97E05D4F171BC
approval_decision: DEC-PRD-V05-001
```

规则：

- `PRDv04.md` 是不可修改的历史基线，不因 superseded 失去审计价值。
- 新版本必须创建新文件；不得覆盖旧版本来伪造历史连续性。
- current 变化后，所有下游 SPEC、Matrix、suite、ADR、plan 和 result 必须做 applicability/兼容复核。
- PRD Approved 不表示 SPEC 兼容、suite 物化、业务实现或业务测试通过。
