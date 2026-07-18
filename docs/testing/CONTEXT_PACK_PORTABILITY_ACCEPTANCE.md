# Context Pack Portability Acceptance

| 字段 | 值 |
|---|---|
| Contract ID | `ACCEPT-CONTEXT-PACK-001` |
| Suite ID | `context_pack_portability_v1` |
| Required scenarios | `CP-001..006` |

```yaml
context_pack_required_contract_slices:
  CP-001: [SIP-AT-001, SIP-AT-002, SIP-AT-003]
  CP-002: [SIP-AT-004, IMM-AT-015]
  CP-003: [SIP-AT-007, SIP-AT-008]
  CP-004: [SIP-AT-025, IMM-AT-025]
  CP-005: [SIP-AT-026]
  CP-006: [SIP-AT-006]
```

| ID | Given / When | Then |
|---|---|---|
| `CP-001` | seeded synthetic runtime export | manifest、structured layers、Source 清单、Markdown、checksums 均存在且 hash 正确 |
| `CP-002` | 修改一个已列条目 | verifier 返回 `rejected_hash_mismatch`，零 SQLite 写入 |
| `CP-003` | Canonical payload 含 unknown namespaced JSON 字段 | export -> verify 保留字段名、类型、嵌套和值语义 |
| `CP-004` | manifest 使用 `..`、绝对路径或 UNC ref | verifier 返回 `rejected_path`，Pack 外零读取/写入 |
| `CP-005` | 新导出完成后读取旧 Pack | 旧 Pack 的 manifest/hash/内容不变；relation 由 revision 比较得到 |
| `CP-006` | Derived payload 被尝试加入 Canonical evidence | exporter 拒绝，不让 Derived 成为事实证据 |

所有 fixture 为合成数据；runner 禁止网络；suite 未运行前不得称通过。

