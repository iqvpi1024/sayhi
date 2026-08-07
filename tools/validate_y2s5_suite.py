from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests/y2s5_suite_manifest.json"
REQUIRED = [f"Y2S5-{index:03d}" for index in range(1, 11)]
INVARIANTS = {f"Y2S5-INV-{index:03d}" for index in range(1, 10)}
ROLES = {"fixture", "oracle", "scenario_plan", "adapter_protocol", "business_test_module", "offline_runner", "suite_preflight_validator"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    flags = manifest.get("flags")
    materialized_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": False, "suite_passed": False}
    passed_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": True, "suite_passed": True}
    if flags not in (materialized_flags, passed_flags):
        errors.append("invalid Y2S5 suite flags")
    if manifest.get("required_scenario_ids") != REQUIRED:
        errors.append("required scenario IDs mismatch")
    artifacts = manifest.get("artifacts", [])
    if not {item.get("role") for item in artifacts} >= ROLES:
        errors.append("artifact roles mismatch")
    for item in artifacts:
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item.get("sha256"):
            errors.append(f"artifact hash mismatch: {item['path']}")
    fixture = json.loads((ROOT / "tests/fixtures/y2s5_mcp_runtime_v1/fixture.json").read_text(encoding="utf-8"))
    oracle = json.loads((ROOT / "tests/fixtures/y2s5_mcp_runtime_v1/oracles.json").read_text(encoding="utf-8"))
    scenarios = json.loads((ROOT / "tests/integration/y2s5_mcp_runtime_scenarios.json").read_text(encoding="utf-8"))
    if fixture.get("synthetic") is not True or fixture.get("external_data_used") is not False:
        errors.append("fixture privacy boundary mismatch")
    if fixture.get("synthetic_profile_id") != "y2s5_mcp_runtime_v1":
        errors.append("fixture synthetic profile mismatch")
    if [case.get("scenario_id") for case in fixture.get("cases", [])] != REQUIRED:
        errors.append("fixture scenario IDs mismatch")
    if set(oracle.get("scenarios", {})) != set(REQUIRED):
        errors.append("oracle scenario IDs mismatch")
    if [item.get("scenario_id") for item in scenarios.get("scenarios", [])] != REQUIRED:
        errors.append("scenario plan IDs mismatch")
    plan_invariants = set()
    for item in scenarios.get("scenarios", []):
        refs = item.get("contract_refs", [])
        if not refs or not set(refs) <= INVARIANTS:
            errors.append(f"scenario plan invariant mismatch: {item.get('scenario_id')}")
        plan_invariants.update(refs)
    if plan_invariants != INVARIANTS:
        errors.append("scenario plan invariant coverage mismatch")
    test_path = ROOT / "tests/semantic/test_y2s5_mcp_runtime_contract.py"
    tree = ast.parse(test_path.read_text(encoding="utf-8"))
    decorated = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and getattr(decorator.func, "id", None) == "scenario" and decorator.args:
                    decorated.append(getattr(decorator.args[0], "value", None))
    if decorated != REQUIRED:
        errors.append("semantic scenario decorators mismatch")
    if flags == passed_flags:
        result_path = ROOT / manifest.get("latest_verification_result_path", "")
        if not result_path.is_file() or digest(result_path) != manifest.get("latest_verification_result_sha256"):
            errors.append("current result hash mismatch")
        else:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if result.get("manifest_sha256") != manifest.get("latest_verification_manifest_sha256"):
                errors.append("current result manifest binding mismatch")
            if result.get("bound_artifacts") != artifacts:
                errors.append("current result artifact binding mismatch")
            rows = result.get("required_results", [])
            if [row.get("test_id") for row in rows] != REQUIRED or not all(row.get("individual_test_result") == "passed" for row in rows):
                errors.append("current result rows mismatch")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASSED: Y2S5 suite materialized and current business runner result is bound" if flags == passed_flags else "PASSED: Y2S5 suite materialization preflight; no business test was executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
