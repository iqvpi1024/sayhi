# Suite Materialization 门禁清单

本清单用于审查 suite 是否已经真正可运行。勾选清单本身不会改变 suite 状态；只有对应 artifact 存在且静态校验通过，才可设置 `suite_materialized=true`。

## 1. 基线绑定

- [x] `slice_id` 唯一且与 PROJECT_STATE 一致。
- [x] PRD hash、Decision、SPEC 版本和 traceability 基线已固定。
- [x] Accepted ADR 已列出，且没有用测试补产品规则。
- [x] manifest 记录自身 schema/version 和 artifact digest 策略。

## 2. Required 集合

- [x] required Test Ref 来自一个权威映射。
- [x] required、optional、deferred 能机器区分。
- [x] 每个 required ID 唯一、可解析且指向现有合同。
- [x] 未将长期 FR 或后置 SPEC 隐式扩大进当前切片。

## 3. Fixture

- [x] 全部数据为合成数据，并有显式 synthetic 标记。
- [x] 没有工作区外个人资料、凭据、真实姓名或联系方式。
- [x] 固定时钟、时区、locale、随机种子和 ID 策略已声明。
- [x] Source byte locator、长度和 hash 可重复计算。
- [x] 初始 Canonical、Source receipt 和 protected sentinel 有稳定 digest。

## 4. Oracle

- [x] expected state、forbidden changes 和审计结果分别声明。
- [x] Current/Historical、Canonical/Derived、Fact/Hypothesis 不混淆。
- [x] 原子失败、stale base、L2 失败和撤销有可观察断言。
- [x] 空集合或未检查字段不能误报 protected semantics 通过。
- [x] 每个 oracle 能回到 SPEC Section 和 Test Ref。

## 5. Runner Contract

- [x] 单一入口命令可在干净本地环境离线运行。
- [x] 不依赖在线模型、外部网络、真实服务或人工点选。
- [x] exit code、stdout/stderr、单项结果和 artifact schema 已定义。
- [x] runner 能报告 `passed|failed|errored|partial`，不吞掉 skipped/errored。
- [x] runner 记录 commit、环境、开始/结束时间和依赖锁定信息。

## 6. 追踪与验证

- [x] manifest -> Fixture/Oracle/Runner 的引用完整。
- [x] PRD -> SPEC -> Test -> Implementation Module -> Result 链可检查；Module/Result 在下一门禁前诚实为 `TBD/not_executed`。
- [x] 隐私扫描、schema 检查和 deterministic dry validation 已执行。
- [x] `suite_materialized=true` 的变更与实际 artifact 将进入同一 Recovery Point。
- [x] `suite_executed` 和 `suite_passed` 仍保持实际运行结果，不因物化自动变为 true。

## 7. Gate 结论

| 字段 | 值 |
|---|---|
| Review Date | `2026-07-16` |
| Manifest | `tests/micro_suite_manifest.json`；SHA-256 `54d70b993dbd5ce117605f6b07c305d2b97eba67df6a782c0e75f3afc28a5390` |
| Result | `ready` |
| Blocking Findings | `none`；首次自匹配隐私误报已修正并复验 |
| Reviewer | Noetide Technical Lead |
