from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests/b2_suite_manifest.json"
REQUIRED = [f"B2-{index:03d}" for index in range(1, 9)]
ROLES = {"fixture", "oracle", "scenario_plan", "adapter_protocol", "business_test_module", "offline_runner", "suite_preflight_validator"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    flags = manifest.get("flags")
    expected_flags = {"suite_defined": True, "suite_materialized": True, "suite_executed": False, "suite_passed": False}
    if flags != expected_flags:
        errors.append("B2 must be materialized but not executed")
    if manifest.get("required_scenario_ids") != REQUIRED:
        errors.append("required scenario IDs mismatch")
    artifacts = manifest.get("artifacts", [])
    if {item.get("role") for item in artifacts} != ROLES:
        errors.append("artifact roles mismatch")
    for item in artifacts:
        path = ROOT / item["path"]
        if not path.is_file() or digest(path) != item.get("sha256"):
            errors.append(f"artifact hash mismatch: {item['path']}")
    fixture = json.loads((ROOT / "tests/fixtures/b2_episode_summary_v1/fixture.json").read_text(encoding="utf-8"))
    oracle = json.loads((ROOT / "tests/fixtures/b2_episode_summary_v1/oracles.json").read_text(encoding="utf-8"))
    scenarios = json.loads((ROOT / "tests/integration/b2_episode_summary_scenarios.json").read_text(encoding="utf-8"))
    if fixture.get("synthetic") is not True or fixture.get("external_data_used") is not False:
        errors.append("fixture privacy boundary mismatch")
    if [case.get("scenario_id") for case in fixture.get("cases", [])] != REQUIRED:
        errors.append("fixture scenario IDs mismatch")
    if set(oracle.get("scenarios", {})) != set(REQUIRED):
        errors.append("oracle scenario IDs mismatch")
    if [item.get("scenario_id") for item in scenarios.get("scenarios", [])] != REQUIRED:
        errors.append("scenario plan IDs mismatch")
    test_path = ROOT / "tests/semantic/test_b2_episode_summary_contract.py"
    tree = ast.parse(test_path.read_text(encoding="utf-8"))
    decorated = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and getattr(decorator.func, "id", None) == "scenario" and decorator.args:
                    decorated.append(getattr(decorator.args[0], "value", None))
    if decorated != REQUIRED:
        errors.append("semantic scenario decorators mismatch")
    if errors:
        print("FAILED: " + "; ".join(errors))
        return 1
    print("PASSED: B2 Episode/Summary suite materialized; no business test was executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
