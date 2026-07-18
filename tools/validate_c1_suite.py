from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests/c1_suite_manifest.json"
REQUIRED = [f"C1-{index:03d}" for index in range(1, 8)]
ROLES = {
    "fixture",
    "oracle",
    "boundary_test_module",
    "changeset_test_module",
    "integration_test_module",
    "offline_runner",
    "suite_preflight_validator",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    passed_flags = {
        "suite_defined": True,
        "suite_materialized": True,
        "suite_executed": True,
        "suite_passed": True,
    }
    materialized_flags = {
        "suite_defined": True,
        "suite_materialized": True,
        "suite_executed": False,
        "suite_passed": False,
    }
    flags = manifest.get("flags")
    if flags not in (materialized_flags, passed_flags):
        errors.append("invalid suite flags")
    if manifest.get("required_scenario_ids") != REQUIRED:
        errors.append("required scenario mismatch")
    artifacts = manifest.get("artifacts", [])
    if {item.get("role") for item in artifacts} != ROLES:
        errors.append("artifact roles mismatch")
    for item in artifacts:
        path = ROOT / item["path"]
        if not path.is_file() or item.get("sha256") != digest(path):
            errors.append(f"artifact hash mismatch: {item['path']}")
    if flags == materialized_flags:
        if manifest.get("latest_verification_result") != "not_executed":
            errors.append("materialized suite claims a run")
    elif flags == passed_flags:
        result_path = ROOT / manifest.get("latest_verification_result_path", "")
        if not result_path.is_file():
            errors.append("missing current passed result")
        elif digest(result_path) != manifest.get("latest_verification_result_sha256"):
            errors.append("result hash mismatch")
        else:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("manifest_sha256") != manifest.get("latest_verification_manifest_sha256"):
                errors.append("manifest binding mismatch")
            if result.get("bound_artifacts") != artifacts:
                errors.append("artifact binding mismatch")
            rows = result.get("required_results", [])
            if [item.get("test_id") for item in rows] != REQUIRED:
                errors.append("required result identifiers mismatch")
            elif not all(item.get("individual_test_result") == "passed" for item in rows):
                errors.append("required results mismatch")
    if errors:
        print("FAILED: " + "; ".join(errors))
        return 1
    print("PASSED: C1 Decision/Outcome suite materialized and current result is bound" if flags == passed_flags else "PASSED: C1 Decision/Outcome suite materialized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
