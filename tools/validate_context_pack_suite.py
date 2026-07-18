from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests/context_pack_suite_manifest.json"
REQUIRED = ["CP-001", "CP-002", "CP-003", "CP-004", "CP-005", "CP-006"]
ROLES = {"fixture", "oracle", "business_test_module", "offline_runner", "suite_preflight_validator"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    materialized = {"suite_defined": True, "suite_materialized": True, "suite_executed": False, "suite_passed": False}
    passed = {"suite_defined": True, "suite_materialized": True, "suite_executed": True, "suite_passed": True}
    flags = manifest.get("flags")
    if flags not in (materialized, passed): errors.append("invalid suite flags")
    if manifest.get("required_scenario_ids") != REQUIRED: errors.append("required scenario mismatch")
    if {item.get("role") for item in manifest.get("artifacts", [])} != ROLES: errors.append("artifact roles mismatch")
    for item in manifest.get("artifacts", []):
        path = ROOT / item["path"]
        if not path.is_file() or item.get("sha256") != digest(path): errors.append(f"artifact hash mismatch: {item['path']}")
    if flags == materialized:
        if manifest.get("latest_verification_result") != "not_executed": errors.append("materialized suite claims a run")
    elif flags == passed:
        path = manifest.get("latest_verification_result_path")
        result_path = ROOT / path if isinstance(path, str) else None
        if manifest.get("latest_verification_result") != "passed" or not result_path or not result_path.is_file(): errors.append("missing current passed result")
        elif digest(result_path) != manifest.get("latest_verification_result_sha256"): errors.append("result hash mismatch")
        else:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("manifest_sha256") != manifest.get("latest_verification_manifest_sha256"): errors.append("manifest binding mismatch")
            if result.get("bound_artifacts") != manifest.get("artifacts"): errors.append("artifact binding mismatch")
            if [item.get("test_id") for item in result.get("required_results", [])] != REQUIRED or not all(item.get("individual_test_result") == "passed" for item in result.get("required_results", [])): errors.append("required results mismatch")
    if errors:
        print("FAILED: " + "; ".join(errors))
        return 1
    print("PASSED: Context Pack suite materialized and current result is bound" if flags == passed else "PASSED: Context Pack suite materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
