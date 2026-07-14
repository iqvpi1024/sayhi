# Suite Materialization 门禁清单

本清单用于审查 suite 是否已经真正可运行。勾选清单本身不会改变 suite 状态；只有对应 artifact 存在且静态校验通过，才可设置 `suite_materialized=true`。

## 1. 基线绑定

- [ ] `slice_id` 唯一且与 PROJECT_STATE 一致。
- [ ] PRD hash、Decision、SPEC 版本和 traceability 基线已固定。
- [ ] Accepted ADR 已列出，且没有用测试补产品规则。
- [ ] manifest 记录自身 schema/version 和 artifact digest 策略。

## 2. Required 集合

- [ ] required Test Ref 来自一个权威映射。
- [ ] required、optional、deferred 能机器区分。
- [ ] 每个 required ID 唯一、可解析且指向现有合同。
- [ ] 未将长期 FR 或后置 SPEC 隐式扩大进当前切片。

## 3. Fixture

- [ ] 全部数据为合成数据，并有显式 synthetic 标记。
- [ ] 没有工作区外个人资料、凭据、真实姓名或联系方式。
- [ ] 固定时钟、时区、locale、随机种子和 ID 策略已声明。
- [ ] Source byte locator、长度和 hash 可重复计算。
- [ ] 初始 Canonical、Source receipt 和 protected sentinel 有稳定 digest。

## 4. Oracle

- [ ] expected state、forbidden changes 和审计结果分别声明。
- [ ] Current/Historical、Canonical/Derived、Fact/Hypothesis 不混淆。
- [ ] 原子失败、stale base、L2 失败和撤销有可观察断言。
- [ ] 空集合或未检查字段不能误报 protected semantics 通过。
- [ ] 每个 oracle 能回到 SPEC Section 和 Test Ref。

## 5. Runner Contract

- [ ] 单一入口命令可在干净本地环境离线运行。
- [ ] 不依赖在线模型、外部网络、真实服务或人工点选。
- [ ] exit code、stdout/stderr、单项结果和 artifact schema 已定义。
- [ ] runner 能报告 `passed|failed|errored|partial`，不吞掉 skipped/errored。
- [ ] runner 记录 commit、环境、开始/结束时间和依赖锁定信息。

## 6. 追踪与验证

- [ ] manifest -> Fixture/Oracle/Runner 的引用完整。
- [ ] PRD -> SPEC -> Test -> Implementation Module -> Result 链可检查。
- [ ] 隐私扫描、schema 检查和 deterministic dry validation 已执行。
- [ ] `suite_materialized=true` 的变更与实际 artifact 在同一提交。
- [ ] `suite_executed` 和 `suite_passed` 仍保持实际运行结果，不因物化自动变为 true。

## 7. Gate 结论

| 字段 | 值 |
|---|---|
| Review Date | `<YYYY-MM-DD>` |
| Manifest | `<path + digest>` |
| Result | `<ready/not_ready>` |
| Blocking Findings | `<ids or none>` |
| Reviewer | `<role>` |
