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
    materialized_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": False, "suite_passed": False}
    passed_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": True, "suite_passed": True}
    flags = manifest.get("flags")
    if flags not in (materialized_flags, passed_flags):
        errors.append("manifest flags must be materialized/not-executed or executed/passed")
    if manifest.get("required_scenario_ids") != ["SI-001", "SI-002", "SI-003", "SI-004"]:
        errors.append("scenario set mismatch")
    roles = {item.get("role") for item in manifest.get("artifacts", [])}
    if roles != {"fixture", "oracle", "business_test_module", "offline_runner", "suite_preflight_validator"}:
        errors.append("artifact role set mismatch")
    for artifact in manifest.get("artifacts", []):
        path = ROOT / artifact["path"]
        if not path.is_file() or digest(path) != artifact["sha256"]:
            errors.append(f"artifact hash mismatch: {artifact['path']}")
    text = "\n".join((ROOT / item["path"]).read_text(encoding="utf-8") for item in manifest.get("artifacts", []))
    if "synthetic" not in text:
        errors.append("synthetic declaration absent")
    if flags == materialized_flags:
        if manifest.get("latest_verification_result") != "not_executed" or manifest.get("latest_run_applicability") != "not_applicable":
            errors.append("materialized suite cannot claim a run")
        if manifest.get("latest_verification_result_path") is not None:
            errors.append("materialized suite cannot reference a result")
    elif flags == passed_flags:
        result_path_value = manifest.get("latest_verification_result_path")
        if manifest.get("latest_verification_result") != "passed" or manifest.get("latest_run_applicability") != "current":
            errors.append("passed suite must claim a current passed run")
        if not isinstance(result_path_value, str):
            errors.append("passed suite must reference a result")
        else:
            result_path = ROOT / result_path_value
            if not result_path.is_file():
                errors.append("current result is absent")
            else:
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if result.get("suite_id") != manifest.get("suite_id"):
                    errors.append("result suite ID mismatch")
                if result.get("run_result") != "passed" or result.get("exit_code") != 0:
                    errors.append("current result is not passed")
                required = result.get("required_results", [])
                if [item.get("test_id") for item in required] != manifest.get("required_scenario_ids"):
                    errors.append("result scenario IDs mismatch")
                if not all(item.get("individual_test_result") == "passed" for item in required):
                    errors.append("result contains non-passed scenarios")
                if result.get("manifest_sha256") != manifest.get("latest_verification_manifest_sha256"):
                    errors.append("result manifest binding mismatch")
                if digest(result_path) != manifest.get("latest_verification_result_sha256"):
                    errors.append("result raw hash mismatch")
                if result.get("bound_artifacts") != manifest.get("artifacts"):
                    errors.append("result artifact binding mismatch")
    if errors:
        print("FAILED: " + "; ".join(errors))
        return 1
    print("PASSED: Synthetic Ingestion suite materialized with 4 scenarios")
    if flags == passed_flags:
        print("PASSED: Synthetic Ingestion current business runner result is bound")
    else:
        print("NOT_EXECUTED: Synthetic Ingestion business runner")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
