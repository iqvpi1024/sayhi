# A6 MVP-A 硬化与本地 Alpha Gate Review

| 字段 | 值 |
|---|---|
| Gate ID | `A6-HARDENING-GATE-2026-07-25` |
| Slice | `SLICE-MVP-A-HARDENING-001` |
| Gate | `review_passed` |
| 审查日期 | 2026-07-25 |
| Product Baseline | `PRDv05.md` v0.5，hash `34DA32FF0C7CE7223ACC28755C16A9244FD42644C436666C41CC755E9FC4C8D7` |
| 当前实现提交 | `00d146a` |

## 结论

`P0=0`、`P1=0`，允许创建 A6 工程恢复点。

## 审计证据

- A6 official runner：`A6-001..021` 同一次 run 全部 `passed`，exit code `0`；当前 immutable result 为 `docs/testing/results/a6-20260725.json`（`tools/validate_a6_suite.py` exit 0，输出 `materialized and current business runner result is bound`）；环境戳记完整（platform/python/sqlite/network blocked/stdlib only/wall_time_utc/monotonic/timezone），结果绑定 `a6_mvp_a_reference_v1` 并带禁止外推注记。
- A6 manifest 已绑定 runner 所见 manifest SHA、result SHA 与全部 artifact；fixture/oracle/scenarios 自物化（`fb43914`）以来未做任何修改（`git log` 可证）；`start.py`、`alpha_explainability.py`、`a6_journey.py`、`a6_testing_adapter.py`、`cli.py` 窄接线均为任务卡允许的文件，未反向改动合同、fixture 或 oracle。
- 全量 configured-adapter semantic regression：264 passed、0 skipped，exit code `0`（含 A6 contract 21 项真实执行，无 skip）；A6 contract 的权威执行证据以官方 runner 为准。
- Micro、A1、B1、B2、B3、C1、A2、A3、A4、A5、A6、Synthetic Ingestion、Context Pack 共 13 个 suite validator 全部 exit code `0`；product baseline 静态校验 PASSED；`git diff --check` exit code `0`。
- 八个 `A6-INV-001..008` 均有正/反证明：
  - `A6-INV-001`（集成不削弱独立证据）：A6 只编排已 verified 能力，13 个独立 suite validator 全部 PASSED，各切片 result 绑定未受影响。
  - `A6-INV-002`（SLO 不外推）：`A6-021` 结果 `bound_to_profile=a6_mvp_a_reference_v1`、`extrapolation_forbidden=true`，observation 由 `SloCollector` 实测记录。
  - `A6-INV-003`（错误恢复不碰真实目录）：`A6-013..015` 在临时沙箱目录经 start.py 子进程执行，合同 forbidden_mutations 五层不变；`A6-015` 证明未写出声明根之外。
  - `A6-INV-004`（写入全经 ChangeSet）：`A6-003` `bypass_paths_found=0`；`A6-016` 注入失败原子回滚、Canonical revision 不变。
  - `A6-INV-005`（卸载语义）：`A6-020` 默认保留数据目录、删除需独立确认且要求已验证备份副本。
  - `A6-INV-006`（不补写新产品规则）：adapter/journey 仅调用既有模块；FR-003 生成侧保持 §1.1 已知限制，未静默补写。
  - `A6-INV-007`（保护层不变）：`A6-012` `trust_unchanged/closeness_unchanged/personality_unchanged/history_preserved=true`；`A6-002/004/006/009/010/016` forbidden_mutations 覆盖保护层。
  - `A6-INV-008`（视图不可用不冒充 fresh）：`A6-017` `fallback=canonical_or_explicit_unavailable`、`stale_returned_as_fresh=false`；`A6-012` `l2_fallback_available=true`。

## 范围与风险

- A6 仅覆盖固定 `a6_hardening_v1` / `a6_mvp_a_reference_v1` 合成 profile 上的 21 个顺序场景；不实现真实输入渠道、通用 NLP、Web/桌面 UI、云账户、多租户、连接器、多设备或真实个人数据。
- FR-003 生成侧（Entity/Assertion 候选生成）为合同 §1.1 显式记录的已知限制；本切片不闭合该缺口，后续切片需独立 Decision。
- SLO 观测仅对本机 Reference Profile 环境（ADR-0010 §5.3 描述符）有效，禁止外推。
- 当前通过不表示完整 PRD 产品或 D2/D3 一键部署完成；D2/D3（签名、升级/卸载、真实数据安全合同）仍是最终目标，当前交付级别保持 D1 合成预览。
- Alpha 发布的版本号、工件内容与发布动作不在本切片完成定义内，须由独立发布门禁决定。

## 下一步唯一建议动作

创建并推送 A6 recovery tag `a6-hardening-rp-20260725`，然后按 `MASTER_DELIVERY_ROADMAP` 选择下一切片。
