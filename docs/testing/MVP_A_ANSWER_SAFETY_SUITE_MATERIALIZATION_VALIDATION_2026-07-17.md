# MVP-A Answer Safety Suite 物化验证记录

## 0. 元数据

| 字段 | 值 |
|---|---|
| Record ID | `VERIFY-MVP-A-AS-SUITE-001` |
| Date | 2026-07-17 20:00 +08:00 |
| Start HEAD | `99b7e57087059774d37ceec6cafc0af12cccbe90` + 当前 suite/planning 工作树 |
| Branch | `codex/mvp-a-answer-safety-planning` |
| Environment | Windows 11 `10.0.26200`；Python `3.12.8`；SQLite `3.45.3`；PowerShell `7.6.3`；Windows PowerShell `5.1.26100.8875` |
| Suite | `mvp_a_answer_safety_v1` |
| Manifest SHA-256 at Gate | `759878a902c46f2b1eb424eb3146561d09b75ddb780dd697bc0cca598d2e32fc` |
| Business Verification | `not_executed` |

## 1. 物化结果

```yaml
suite_defined: true
suite_materialized: true
suite_executed: false
suite_passed: false
suite_artifact_state: materialized
latest_verification_result: not_executed
latest_run_applicability: not_applicable
required_scenarios: 11
required_upstream_refs: 24
required_result_ids: 35
implementation_module: TBD
```

物化工件：manifest、11-case fixture、独立字段级 oracle、scenario plan、test-only adapter protocol、semantic test module、offline runner、suite validator。不存在 A1 业务 adapter、`answers.py` 或业务结果。

## 2. 实际命令与结果

| 命令 | Exit Code | 真实结果 |
|---|---:|---|
| `powershell -ExecutionPolicy Bypass -File .\tools\validate_product_baseline.ps1` | 0 | PRD v0.4/v0.5 hash、32 FR、12 对象、隐私和 fence 静态通过；未执行业务测试 |
| `powershell -ExecutionPolicy Bypass -File .\tools\validate_spec_baseline.ps1` | 0 | 275 Test ID、133 Invariant、32 FR、185 refs 和现有合同静态通过；未执行业务测试 |
| `python .\tools\validate_micro_suite.py` | 0 | 旧 Micro 8 类工件/hash/隐私通过；未重跑 Micro business runner |
| `python .\tools\validate_answer_safety_suite.py` | 0 | 11 scenario + 24 refs = 35 IDs；hash/locator/digest/AST/stdlib/privacy/四态通过；明确输出 `NOT_EXECUTED` |
| `python -m py_compile tests/runner/answer_safety_adapter_protocol.py tests/semantic/test_answer_safety_contract.py tests/runner/run_answer_safety_suite.py tools/validate_answer_safety_suite.py` | 0 | 四个 Python 测试工件语法通过 |
| AS-011 result writer bootstrap（记录中的 inline Python） | 0 | 注入 `result.output.before_atomic_replace` 后无 passed artifact；未运行 A1 业务场景 |
| `git diff --check` | 0 | 开发就绪文档收口后最终复跑通过 |

## 3. 复算断言

- 11 个 scenario ID 恰为 `AS-001..011`，数据库 identity 11/11 唯一。
- 13 个 query variant 均有且只有一个独立 oracle。
- Source UTF-8 byte length、SHA-256 与 `text_utf8_byte_range_v1` locator 全部复算一致。
- Source、Canonical、Ledger、Projection 初始 digest 使用 `sha256_stable_id_sorted_canonical_json_v1`，输入顺序不改变语义 digest。
- Acceptance §7、scenario plan 和 manifest 的 upstream ref 集合差异为 0。
- 24 个 upstream refs 全部存在于 Approved SPEC；11 + 24 = 35。
- Python suite 工件仅使用 stdlib/local import；fixture/oracle/scenario 隐私扫描无命中。
- manifest artifact raw-byte hash 全部匹配。

## 4. 诊断失败保留

第一次运行 A1 validator 的 exit code 为 `1`：静态隐私扫描把 runner 源码中的“本机路径检测正则”本身识别为本机路径。修正只把 materialization-time 数据隐私扫描限定到 fixture/oracle/scenario；runner 在真实执行时仍扫描 structured result，Python 工件仍由 AST/stdlib 检查。更新 validator raw hash 后复跑 exit code `0`。该诊断不属于业务测试失败，也没有改变 expected。

## 5. 未证明

- 未证明 `schema.sql`/`store.py` 能 seed A1 fixture。
- 未证明 `AnswerEnvelope`、Evidence/Coverage/Freshness/Conflict evaluator。
- 未证明 A1 adapter、只读 digest、六态 actual 或 35/35 通过。
- 未在当前实现提交上重跑 Micro 49/49。
- 未证明 UI、API、权限 runtime、MCP、安装或一键部署。

## 6. 结论

Suite 物化验证通过，业务执行状态保持 `not_executed`。本记录只支持进入 Suite Materialization Gate 和 Implementation Planning Gate。
