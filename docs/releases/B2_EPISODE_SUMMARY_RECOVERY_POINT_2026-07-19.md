# B2 Episode 与分层摘要 Recovery Point

| 字段 | 值 |
|---|---|
| Recovery Tag | `b2-episode-summary-rp-20260719` |
| Slice | `SLICE-MVP-B-EPISODE-SUMMARY-001` |
| Gate Review | `B2_EPISODE_SUMMARY_GATE_REVIEW_2026-07-19.md` |
| Verification | `docs/testing/results/b2-a810513-20260719.json` |

## 恢复步骤

```powershell
git fetch origin --tags
git checkout b2-episode-summary-rp-20260719
python tools/validate_b2_suite.py
```

该 tag 是工程恢复点，不是新的 GitHub 产品发布，不移动或替代 `v0.1.3-synthetic-preview`。
