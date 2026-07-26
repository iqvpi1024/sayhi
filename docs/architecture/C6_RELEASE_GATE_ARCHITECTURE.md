# C6 MVP Release Gate 架构说明

| 字段 | 值 |
|---|---|
| Slice | `SLICE-MVP-C-RELEASE-001` |
| Contract | `SPEC-C6-RELEASE-001` v0.1 |
| ADR | `ADR-0018` |

## 1. 模块边界

```text
tests/runner/run_c6_release_audit.py   审计编排（子进程 + 扫描 + 恢复演练）
tools/validate_c6_suite.py             C6 manifest/result 绑定 validator
tests/c6_suite_manifest.json           C6 suite manifest
docs/releases/BETA_GATE_REVIEW_*.md    Beta 门禁复核文档（引用同一次 passed result）
```

## 2. 执行流

```text
C6-001 subprocess: python tools/validate_*.py (all) -> exit codes
C6-002 subprocess: python -m unittest discover (16 adapter env vars) -> 0 fail/0 error/0 skip
C6-003 scan: fixtures synthetic flags + forbidden patterns over src/tests fixtures
C6-004 scan: AST import walk over src/noetide_micro -> stdlib whitelist
C6-005 scan: AST call/import walk -> no socket/urllib/http.client/requests
C6-006 scan: all suite manifests -> flags + result path + sha256 binding
C6-007 subprocess-free: temp dir demo store -> create_backup -> restore -> byte/revision match
C6-008 scan: git tag -l recovery points + PROJECT_STATE/HANDOFF current slice + non-goal checklist
```
