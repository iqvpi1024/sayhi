# Noetide 识海

**A local-first, user-owned, correctable personal context engine — with proof, not promises.**

[English](#english) | [中文](#中文)

---

## English

Noetide is an open-source **Personal Context & Growth Engine** that runs entirely on your machine. Your data lives in a folder *you* choose. Nothing is uploaded — there is no upload code at all. Every claim in this README is backed by executable audits you can re-run yourself.

### Why it's different

Most "personal AI memory" projects ask you to trust them. Noetide is built so you don't have to:

- **Facts, hypotheses and fiction are strictly separated.** A hypothesis never auto-promotes to a fact.
- **History is never overwritten.** Current state and historical state are bitemporal — corrections create new revisions, old ones stay auditable.
- **Every write goes through a ChangeSet** you explicitly confirm, and every confirmation can be reverted with compensation.
- **Uninstall never deletes your data.** Deleting data requires typing the full path *and* creates a verified backup first.
- **392 semantic tests, 21 suite validators, 0 skips** — plus a release-gate audit that re-checks all of it before any version ships.

### Quick start (Windows, 2 minutes)

1. Download `Noetide-beta-v0.2.0-win64.zip` from [Releases](../../releases) and verify the SHA-256.
2. Unzip anywhere (no admin rights needed, no Python install needed).
3. Double-click `scripts/Noetide Setup.cmd` → pick your data folder → done.

```text
> scripts\Noetide Shell.cmd status
Current revision: rev_010
```

Export everything anytime — human-readable Markdown + JSON, no lock-in:

```text
> scripts\Noetide Shell.cmd export my-backup
backup pack: my-backup
data revision: rev_010 (4 entries, sha256 manifest verified)
roundtrip verified: True
```

### Engineering honesty

| Claim | Proof |
|---|---|
| 392 tests OK, 0 skipped | `python -m unittest discover -s tests -t .` (16 adapter env vars) |
| Stdlib-only, zero network calls | AST audit in the C6 release gate |
| Synthetic fixtures only | Machine privacy scan in the C6 release gate |
| Backup/restore byte-identical | Recovery drill in the C6 release gate |

Full trail: PRD → 9 SPECs → 19 ADRs → per-slice executable suites → gate reviews → recovery tags, all in [`docs/`](docs/).

### Honest limitations (v0.2.0-beta)

- **Synthetic demo data only** — do not enter real personal information.
- Windows-only, not code-signed (SmartScreen warning is expected), no auto-update.
- No sync, no connectors, no real-data import, no multi-user — by design, for now.

## 中文

识海是一个**完全运行在你自己电脑上**的个人上下文与成长引擎。数据放在你选的文件夹里，没有任何上传代码。本 README 里的每一条声明，都有你可以亲手重跑的可执行审计支撑。

### 三分钟体验（Windows）

1. 在 [Releases](../../releases) 下载 `Noetide-beta-v0.2.0-win64.zip`，核对 SHA-256。
2. 解压到任意位置（免管理员、免装 Python）。
3. 双击 `scripts/Noetide Setup.cmd`，选择数据文件夹，完成隐私确认即可。

### 设计红线

- 事实、假设、虚构严格分离；假设永远不会自动变成事实。
- 历史永不覆盖；每次纠正都产生新版本，旧版本全程可审计。
- 所有写入必须经过你确认的 ChangeSet；确认过的也能补偿撤销。
- 卸载默认绝不删除你的数据；删除数据必须输入完整路径，且先强制生成校验备份。

### 如实说明

当前版本是**合成演示 Beta**：只接受内置合成数据，请勿输入真实个人信息。未签名、仅 Windows、无自动更新。路线图见 [`docs/releases/ONE_CLICK_DELIVERY_PLAN.md`](docs/releases/ONE_CLICK_DELIVERY_PLAN.md)。

## License

See [LICENSE](LICENSE). Security & privacy notes: [SUPPORT.md](SUPPORT.md).
