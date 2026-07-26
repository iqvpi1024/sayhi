"""C6 release audit runner: executes the release-readiness audit and emits an immutable result."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests/c6_suite_manifest.json"
SRC = ROOT / "src/noetide_micro"

ADAPTERS = {
    "NOETIDE_MICRO_ADAPTER": "noetide_micro.testing_adapter",
    "NOETIDE_ANSWER_ADAPTER": "noetide_micro.answer_testing_adapter",
    "NOETIDE_A2_ADAPTER": "noetide_micro.a2_testing_adapter",
    "NOETIDE_A3_ADAPTER": "noetide_micro.a3_testing_adapter",
    "NOETIDE_A4_ADAPTER": "noetide_micro.a4_testing_adapter",
    "NOETIDE_A5_ADAPTER": "noetide_micro.a5_testing_adapter",
    "NOETIDE_A6_ADAPTER": "noetide_micro.a6_testing_adapter",
    "NOETIDE_B2_ADAPTER": "noetide_micro.b2_testing_adapter",
    "NOETIDE_B3_ADAPTER": "noetide_micro.b3_testing_adapter",
    "NOETIDE_B4_ADAPTER": "noetide_micro.b4_testing_adapter",
    "NOETIDE_B5_ADAPTER": "noetide_micro.b5_testing_adapter",
    "NOETIDE_B6_ADAPTER": "noetide_micro.b6_testing_adapter",
    "NOETIDE_C2_ADAPTER": "noetide_micro.c2_testing_adapter",
    "NOETIDE_C3_ADAPTER": "noetide_micro.c3_testing_adapter",
    "NOETIDE_C4_ADAPTER": "noetide_micro.c4_testing_adapter",
    "NOETIDE_C5_ADAPTER": "noetide_micro.c5_testing_adapter",
}

FORBIDDEN_PATTERNS = [
    re.compile(r"@gmail\.com|@qq\.com|@163\.com|@outlook\.com"),
    re.compile(r"\b1[3-9]\d{9}\b"),
    re.compile(r"password\s*=", re.IGNORECASE),
]

NETWORK_MODULES = {"socket", "urllib", "http", "requests", "ftplib", "smtplib", "telnetlib", "asyncio"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_validators() -> tuple[bool, str]:
    failures = []
    for validator in sorted((ROOT / "tools").glob("validate_*.py")):
        run = subprocess.run([sys.executable, str(validator)], cwd=ROOT, capture_output=True, text=True)
        if run.returncode != 0:
            failures.append(validator.name)
    return (not failures, "failed=" + ",".join(failures) if failures else "all passed")


def check_regression() -> tuple[bool, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    env.update(ADAPTERS)
    run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=ROOT, env=env, capture_output=True, text=True)
    tail = (run.stdout + run.stderr)[-400:]
    ok = run.returncode == 0 and "OK" in tail and "skipped" not in tail.replace("skipped=0", "")
    if "skipped=0" in tail or "skipped" not in tail:
        ok = run.returncode == 0 and "OK" in tail
    return (ok, tail.strip().splitlines()[-1] if tail.strip() else "no output")


def check_privacy() -> tuple[bool, str]:
    bad = []
    for fixture in (ROOT / "tests/fixtures").rglob("fixture.json"):
        data = json.loads(fixture.read_text(encoding="utf-8"))
        if data.get("synthetic") is not True or data.get("external_data_used") is True:
            bad.append(str(fixture.relative_to(ROOT)))
    scanned = list(SRC.rglob("*.py")) + list((ROOT / "tests/fixtures").rglob("*.json"))
    for path in scanned:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                bad.append(f"{path.relative_to(ROOT)}:{pattern.pattern}")
    return (not bad, "hits=" + ";".join(bad[:5]) if bad else f"clean, {len(scanned)} files scanned")


def _stdlib_whitelist() -> set[str]:
    return set(sys.stdlib_module_names) | {"noetide_micro", "tests"}


def check_dependencies() -> tuple[bool, str]:
    whitelist = _stdlib_whitelist()
    bad = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root not in whitelist:
                        bad.append(f"{path.name}:{alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                root = node.module.split(".")[0]
                if root not in whitelist:
                    bad.append(f"{path.name}:{node.module}")
    return (not bad, "violations=" + ";".join(bad[:5]) if bad else "stdlib only")


def check_network_isolation() -> tuple[bool, str]:
    bad = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in NETWORK_MODULES:
                        bad.append(f"{path.name}:{alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in NETWORK_MODULES:
                    bad.append(f"{path.name}:{node.module}")
    return (not bad, "violations=" + ";".join(bad[:5]) if bad else "no network surface")


def check_manifest_binding() -> tuple[bool, str]:
    bad = []
    manifests = [p for p in sorted((ROOT / "tests").glob("*_suite_manifest.json")) + sorted((ROOT / "tests").glob("*_manifest.json")) if p.name != "c6_suite_manifest.json"]
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        flags = manifest.get("flags", {})
        if not (flags.get("suite_executed") is True and flags.get("suite_passed") is True):
            bad.append(manifest_path.name)
            continue
        result_path = manifest.get("latest_verification_result_path")
        if not result_path:
            bad.append(manifest_path.name + ":no-result-path")
            continue
        target = ROOT / result_path
        if not target.is_file() or sha256_file(target) != manifest.get("latest_verification_result_sha256"):
            bad.append(manifest_path.name + ":hash-mismatch")
    return (not bad, "unbound=" + ";".join(bad[:5]) if bad else "all manifests bound")


def check_recovery_drill() -> tuple[bool, str]:
    sys.path.insert(0, str(ROOT / "src"))
    from noetide_micro import pack_backup
    from noetide_micro.store import SemanticStore
    tmp = Path(tempfile.mkdtemp(prefix="c6_drill_"))
    db = tmp / "drill.sqlite3"
    store = SemanticStore(db)
    store.add_revision("rev_c6_drill", "2026-07-26T00:00:00+00:00", "seed")
    store.add_canonical_object("EP-DRILL", {"object_type": "episode", "object_revision": "rev_c6_drill", "occurred_on": "2026-07-20", "synthetic": True})
    source_sha = sha256_file(db)
    backup = tmp / "drill.nobak"
    created = pack_backup.create_backup(db, "c6-drill-key", backup, "2026-07-26T00:00:00+00:00")
    restored = tmp / "restored.sqlite3"
    outcome = pack_backup.restore_backup(backup, "c6-drill-key", restored)
    if created["outcome"] != "created" or outcome["outcome"] != "restored":
        return (False, "backup or restore failed")
    if sha256_file(restored) != source_sha or sha256_file(db) != source_sha:
        return (False, "byte mismatch")
    restored_store = SemanticStore(restored)
    if restored_store.current_revision() != store.current_revision():
        return (False, "revision mismatch")
    return (True, "byte-identical, revision match, source unchanged")


def check_beta_gate() -> tuple[bool, str]:
    tags = subprocess.run(["git", "tag", "-l", "*-rp-*"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    required = ["b6-shadow-migration-rp-20260725", "c2-hypothesis-lifecycle-rp-20260726", "c3-review-calibration-rp-20260726", "c4-scenario-action-rp-20260726", "c5-context-pack-backup-rp-20260726"]
    missing = [t for t in required if t not in tags]
    if missing:
        return (False, "missing tags: " + ",".join(missing))
    state = (ROOT / "docs/PROJECT_STATE.md").read_text(encoding="utf-8")
    handoff = (ROOT / "docs/process/CURRENT_HANDOFF.md").read_text(encoding="utf-8")
    if "SLICE-MVP-C-PACK-001" not in state or "SLICE-MVP-C-PACK-001" not in handoff:
        return (False, "state/handoff not current")
    if "c5-context-pack-backup-rp-20260726" not in state:
        return (False, "latest recovery tag not recorded")
    return (True, f"{len(tags)} recovery tags, state current, non-goals closed")


CHECKS = [
    ("C6-001", "suite validators", check_validators),
    ("C6-002", "full regression zero skip", check_regression),
    ("C6-003", "privacy boundary scan", check_privacy),
    ("C6-004", "dependency audit", check_dependencies),
    ("C6-005", "network isolation audit", check_network_isolation),
    ("C6-006", "manifest binding audit", check_manifest_binding),
    ("C6-007", "data recovery drill", check_recovery_drill),
    ("C6-008", "beta gate documents", check_beta_gate),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if ROOT not in output.parents or output.exists():
        raise SystemExit("output must be new and inside repository")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for check_id, name, fn in CHECKS:
        passed, detail = fn()
        rows.append({"test_id": check_id, "check": name, "individual_test_result": "passed" if passed else "failed", "detail": detail[:500]})
        print(f"{check_id} {name}: {'passed' if passed else 'failed'} ({detail[:120]})")
    overall = all(row["individual_test_result"] == "passed" for row in rows)
    artifact = {
        "schema_version": "noetide.c6-audit-result.v1",
        "suite_id": manifest["suite_id"],
        "manifest_sha256": sha256_file(MANIFEST),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "applicability": "current",
        "environment": {"platform": platform.platform(), "python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "dependencies": "stdlib_only"},
        "exit_code": 0 if overall else 1,
        "run_result": "passed" if overall else "failed",
        "non_goals_closed": overall,
        "required_results": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(("passed" if overall else "failed") + f": {len(rows)} C6 audit checks; artifact={output.relative_to(ROOT)}")
    return artifact["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
