from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests/c6_suite_manifest.json"
REQUIRED = [f"C6-{index:03d}" for index in range(1, 9)]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    flags = manifest.get("flags")
    materialized_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": False, "suite_passed": False}
    passed_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": True, "suite_passed": True}
    if flags not in (materialized_flags, passed_flags):
        errors.append("invalid C6 suite flags")
    if manifest.get("required_scenario_ids") != REQUIRED:
        errors.append("required scenario IDs mismatch")
    for item in manifest.get("artifacts", []):
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item.get("sha256"):
            errors.append("artifact hash mismatch: " + item["path"])
    if flags == passed_flags:
        result_path = ROOT / manifest.get("latest_verification_result_path", "")
        if not result_path.is_file() or digest(result_path) != manifest.get("latest_verification_result_sha256"):
            errors.append("current result hash mismatch")
        else:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("manifest_sha256") != manifest.get("latest_verification_manifest_sha256"):
                errors.append("current result manifest binding mismatch")
            rows = result.get("required_results", [])
            if [row.get("test_id") for row in rows] != REQUIRED or not all(row.get("individual_test_result") == "passed" for row in rows):
                errors.append("current required results mismatch")
    if errors:
        print("FAILED: " + "; ".join(errors))
        return 1
    print("PASSED: C6 MVP Release Gate audit executed and current result is bound" if flags == passed_flags else "PASSED: C6 MVP Release Gate audit materialized; not executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
