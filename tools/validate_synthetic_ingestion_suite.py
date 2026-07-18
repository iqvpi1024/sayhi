from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests/synthetic_ingestion_suite_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("flags") != {"suite_defined": True, "suite_materialized": True, "suite_executed": False, "suite_passed": False}:
        errors.append("manifest flags must be materialized/not-executed")
    if manifest.get("latest_verification_result") != "not_executed" or manifest.get("latest_run_applicability") != "not_applicable":
        errors.append("materialized suite cannot claim a run")
    if manifest.get("required_scenario_ids") != ["SI-001", "SI-002", "SI-003", "SI-004"]:
        errors.append("scenario set mismatch")
    roles = {item.get("role") for item in manifest.get("artifacts", [])}
    if roles != {"fixture", "oracle", "business_test_module", "offline_runner"}:
        errors.append("artifact role set mismatch")
    for artifact in manifest.get("artifacts", []):
        path = ROOT / artifact["path"]
        if not path.is_file() or digest(path) != artifact["sha256"]:
            errors.append(f"artifact hash mismatch: {artifact['path']}")
    text = "\n".join((ROOT / item["path"]).read_text(encoding="utf-8") for item in manifest.get("artifacts", []))
    if "synthetic" not in text:
        errors.append("synthetic declaration absent")
    if errors:
        print("FAILED: " + "; ".join(errors))
        return 1
    print("PASSED: Synthetic Ingestion suite materialized with 4 scenarios")
    print("NOT_EXECUTED: Synthetic Ingestion business runner")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
