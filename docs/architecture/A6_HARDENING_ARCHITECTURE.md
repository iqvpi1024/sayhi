# A6 Hardening Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-A6-HARDENING-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-A-HARDENING-001` |
| ADR | `ADR-0010` |
| Contract | `SPEC-A6-HARDENING-001` v0.1 |

## 开发启动面（D0）

```text
python start.py [--data-root PATH] [--clean]
  -> runtime version check (Python >= 3.12)
  -> synthetic dev data root (default <repo>/devdata/, gitignored, declared synthetic)
  -> store init/migrate (ADR-0001 PRAGMA: foreign_keys=ON, journal_mode=DELETE, synchronous=FULL)
  -> minimal preflight + smoke
  -> print local access entry (cli command hints)
  failure -> non-zero exit + actionable, non-leaking error; no partial write; no write outside declared root
  --clean -> delete only after path-prefix verification inside declared synthetic root
```

## Evaluator 执行面

```text
evaluator
  -> tools/validate_a6_suite.py (preflight integrity, exit 0/1)
  -> tests/runner/run_a6_suite.py (single immutable run)
       -> tests/fixtures/a6_hardening_v1/ (versioned synthetic reference data)
       -> tests/integration/a6_hardening_scenarios.json (A6-001..021 fixed order, shared single system state)
       -> a6 testing adapter (noetide_micro.a6_testing_adapter, env-var bound like prior suites)
       -> result JSON: per-scenario status + slo_observation[] + environment stamp
            (platform, python version, wall time, monotonic duration, timezone)
  -> tools/validate_a6_suite.py binds current result into tests/a6_suite_manifest.json
```

- 21 个场景按 A6-001 -> A6-021 固定顺序在同一系统状态上执行；任一场景失败即组失败。
- 集成结果与 A1-A5 等已 verified suite 的独立结果相互独立记录，互不削弱、互不替代。
- SLO observation 仅对 `a6_mvp_a_reference_v1` 有效；环境戳记与 ADR-0010 §5.3 描述符不一致时 result 标记 superseded/失败。

## 错误恢复壳层面

```text
start.py / cli entry
  -> clean_start: init success, exit 0
  -> startup_db_corrupt: detect corruption -> refuse start, non-zero, non-leaking error, no silent repair/overwrite
  -> data_dir_unwritable: write op fails, non-zero, clear error, no write outside declared root
  -> publish_failure: injected mid-publish failure -> S3 atomic rollback, canonical revision unchanged
  -> view_unavailable: L2 projection failure -> canonical fallback or explicit unavailable (S3/A1 semantics)
```

所有恢复路径复用已验证核心语义；壳层不新增绕过 ChangeSet 的写入路径。

## Alpha 可解释性面

- 数据路径可发现：start.py/文档输出声明数据根；合成 profile 路径与默认真实路径不同且可验证分离。
- 备份/导出：复用 Context Pack 已验证能力（Round Trip、校验清单）。
- 卸载语义：默认不删除用户数据目录；删除需独立确认并提示备份/导出副本（D2 卸载程序形态不在本切片）。
