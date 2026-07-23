# A5 App Shell Architecture View

| 字段 | 值 |
|---|---|
| Architecture ID | `ARCH-A5-APP-SHELL-001` |
| Status | `Accepted Design Baseline` |
| Slice | `SLICE-MVP-A-APP-SHELL-001` |
| ADR | `ADR-0009` |

```text
synthetic user shell_command (record|review|preview|confirm|read_view|receipt|history|revert)
  -> App Shell (cli.py + app_shell.py, stdlib argparse)
       record   -> runtime.intake (Source append + receipt)
       review   -> presentation layer (pure function, read-only Candidate Envelope -> NL review items)
       preview  -> presentation layer (impact preview: object sets + view sets)
       confirm  -> runtime.approve + runtime.publish (ChangeSet atomic publish)
       read_view-> runtime.view (current_state | person_card)
       receipt  -> store receipt query (read-only)
       history  -> store changeset history query (read-only)
       revert   -> runtime.revert (ChangeSet compensation)
  -> presentation output (in-memory Derived NL text, never persisted)
  -> writes only via verified core ChangeSet path; zero bypass
```

- 呈现层为纯函数，不持有 store 写路径；只读 Candidate Envelope 与 Canonical 对象。
- 壳模块不出现对 store 写方法的直接调用；写操作全部委托 runtime 已验证核心。
- 引导旅程（`guide`）按固定顺序串联上述命令，每步输出可观察结果。
- 默认离线；壳无 socket 调用。