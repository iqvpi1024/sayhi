# A5 自然语言审查与最小可用应用壳切片合同

## 0. 文档信息

| 字段 | 值 |
|---|---|
| Contract ID | `SPEC-A5-APP-SHELL-001` |
| 版本 | `0.2` |
| 状态 | `Approved for A5 slice` |
| 产品基线 | `PRDv05.md` v0.5 |
| 产品决定 | `DEC-MVP-A-APP-SHELL-001` |
| 上游 | S1 v0.6、S3 v0.4、S5 v0.4、S6 v0.5、S7 v0.4 |
| 适用范围 | `SLICE-MVP-A-APP-SHELL-001`，仅固定合成数据 |

> v0.6 适用性注记（2026-08-07）：本合同基于 PRDv05 验证；PRDv06 为纯增量并入，v0.6 适用性复核结论见 `docs/reviews/PRD_V06_SPEC_COMPATIBILITY_REVIEW.md` §5，本切片结果继续有效。

## 1. 目标与非目标

目标：证明一个固定合成用户可以通过单一本地入口完成完整操作旅程——记录合成文本、以自然语言审查候选与影响预览、确认发布、读取更新后的 Core View、获取回执、查看历史并撤销——全程不要求理解 ChangeSet 内部结构；壳不引入任何绕过审查的写入路径。

非目标：Web/桌面 UI、营销首页、云账户、多租户、在线强依赖、移动应用、通用 NLP、真实输入渠道、连接器、多设备、权限策略编辑器、真实个人数据。

## 2. 对象与字段

```yaml
shell_command (固定合成用户操作):
  command: record | review | preview | confirm | read_view | receipt | history | revert
  args: per-command fixed synthetic args
  synthetic_profile_id: a5_app_shell_v1

natural_language_review_item (请求时 Derived 呈现, 不持久化):
  candidate_ref: stable candidate ID
  summary_text: fixed synthetic natural-language summary
  evidence_citations: [source refs]
  impact_preview: {will_create: [object refs], will_modify: [object refs], views_affected: [view names]}
  presentation_revision: a5_shell_v1

journey_step_result:
  step: shell_command
  status: completed | rejected
  observable: per-step fixed fields (source_id | changeset_id | published_revision | receipt_id | view freshness | reverted)
```

呈现文本为 Derived：只从 Candidate Envelope 与已发布对象派生，不持久化、不作 Evidence Ref、Assertion input 或 ChangeSet trigger。

## 3. 判定规则

1. 旅程步骤固定顺序：`record -> review -> preview -> confirm -> read_view -> receipt -> history -> revert -> read_view`（恢复确认）。
2. 壳命令到核心能力的固定映射：`record`→Source append（独立审计 receipt）；`review`→候选自然语言呈现；`preview`→影响预览；`confirm`→approve+publish；`read_view`→Core View 读取；`receipt`→发布回执查询；`history`→ChangeSet 历史；`revert`→撤销。
3. 自然语言呈现只从 Candidate Envelope 与已发布 Canonical 对象派生；呈现文本是 Derived，不改变底层语义。
4. 影响预览必须与实际发布结果一致：预览声明的将创建/修改对象集与受影响视图集，等于实际发布改变的对象集与视图集。
5. 壳写操作全部经 ChangeSet；`record` 只 append Source（独立审计 receipt，复用 S3 导入语义），不直接写 Canonical。
6. 撤销后所有 Core View 恢复一致，ChangeSet 历史保留。

## 4. 时间、证据与权限

- 固定 A5 clock 只出现在 fixture；壳操作使用核心能力的固定时间语义，不读系统时钟。
- 呈现文本是请求时 Derived，不持久化、不作证据；预览与发布一致性以对象集比较为准，不以文本比较为准。
- 壳为 owner 本地单用户路径；A4 查询层权限语义不在本切片重判，壳不实现权限旁路。
- 壳默认离线，无网络能力。

## 5. 系统不变量

| ID | 不变量 |
|---|---|
| `A5-INV-001` | 壳所有写操作必经 ChangeSet；`record` 只 append Source + receipt；不存在绕过审查的写入路径。 |
| `A5-INV-002` | 自然语言呈现为 Derived，不改变底层语义、不反向成为证据。 |
| `A5-INV-003` | 影响预览与实际发布结果一致（对象集与视图集）。 |
| `A5-INV-004` | 撤销后全部 Core View 恢复一致；ChangeSet 历史保留。 |
| `A5-INV-005` | trust、closeness、人格判断不因壳操作被自动修改。 |
| `A5-INV-006` | 普通用户路径的呈现不暴露 ChangeSet JSON 内部结构；专家命令可显式查询。 |
| `A5-INV-007` | 壳默认离线，无网络调用。 |

## 6. 失败、撤销与审计

- 壳命令失败：非零退出码 + 非泄露错误信息；不得部分写入。
- 发布失败：原子回滚（复用 S3 已验证语义）；壳只报告失败状态。
- 撤销：复用 Micro 已验证的补偿语义；壳报告补偿 revision。
- 审计：复用 ChangeSet receipt 与 Source append receipt；壳不新增审计对象。

## 7. 可执行验收

| ID | Given / When | Then |
|---|---|---|
| `A5-001` | 固定合成文本 | `record` | Source appended + receipt；Canonical revision 不变 |
| `A5-002` | 已生成候选 | `review` | 自然语言呈现含 summary_text 与 evidence_citations；无 ChangeSet JSON 字段暴露 |
| `A5-003` | 已生成候选 | `preview` | 影响预览列出将创建对象集与受影响视图集 |
| `A5-004` | 已审查候选 | `confirm` | approve+publish 原子完成；revision 前进；回执生成 |
| `A5-005` | 发布完成 | `read_view` | person_card 与 relationship_timeline fresh 且包含新状态 |
| `A5-006` | 发布完成 | `receipt` + `history` | 回执可查；历史含发布条目 |
| `A5-007` | 已发布 | `revert` + `read_view` | 撤销完成；全部 Core View 恢复一致；历史保留撤销条目 |
| `A5-008` | 全旅程执行后 | 检查预览/发布一致性、零绕过、trust/closeness/人格判断 | 预览对象集==发布对象集；所有写经 ChangeSet；trust/closeness/人格判断不变 |

## 8. 完成定义

只有 fixture、oracle、manifest、offline runner、implementation plan 和同一次 immutable `A5-001..008` passed result 存在，且所有 `A5-INV-*` 有正/反证明时，A5 才能标记 `verified`。未执行时必须保持 `not_executed`。

## 9. Change Control 记录

- v0.2（2026-07-24）：`read_view` 的 Core View 集合由 `current_state + person_card` 修订为 `person_card + relationship_timeline`。理由：固定合成 profile `a5_app_shell_v1` 复用 Micro 演示旅程，该旅程实际发布与恢复的 Core View 为 Micro 两视图；`current_state`（A2）是独立 profile 的投影，其固定策略不覆盖 Micro 对象的 `valid_time` 形状，跨 profile 复用会破坏 A2 合同边界。FR-006 的证明不因此减弱：发布使两视图前进到 rev_011、撤销使两视图恢复一致。下游（fixture/oracle/suite）按 v0.2 物化。