from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tests/micro_suite_manifest.json"
ACCEPTANCE_PATH = ROOT / "docs/testing/MICRO_MVP_ACCEPTANCE.md"

errors: list[str] = []
checks: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def passed(message: str) -> None:
    checks.append(message)


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def safe_path(relative: str) -> Path:
    candidate = (ROOT / relative).resolve()
    if candidate != ROOT and ROOT not in candidate.parents:
        raise ValueError(f"path escapes repository: {relative}")
    return candidate


def load_json(relative: str) -> dict[str, Any]:
    path = safe_path(relative)
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=no_duplicate_object,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"{relative}: invalid JSON: {exc}")
        return {}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def stable_id(value: dict[str, Any]) -> str:
    keys = (
        "entity_id",
        "relationship_id",
        "state_id",
        "assertion_id",
        "hypothesis_id",
    )
    found = [value[key] for key in keys if key in value]
    if len(found) != 1:
        raise ValueError(f"canonical object has {len(found)} stable IDs")
    return str(found[0])


def parse_authoritative_mapping() -> dict[str, list[str]]:
    text = ACCEPTANCE_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")
    block = re.search(
        r"(?ms)^micro_required_contract_slices:\s*\n(?P<rows>.*?)(?=^[\x60]{3}\s*$)",
        text,
    )
    if not block:
        fail("authoritative Micro required mapping is not parseable")
        return {}
    mapping: dict[str, list[str]] = {}
    for scenario_id, refs in re.findall(
        r"(?m)^\s{2}(MM-[0-9]{3}):\s*\[([^\]]+)\]\s*$",
        block.group("rows"),
    ):
        if scenario_id in mapping:
            fail(f"duplicate authoritative mapping row: {scenario_id}")
        mapping[scenario_id] = [item.strip() for item in refs.split(",")]
    return mapping


def validate_ast(relative: str) -> ast.Module | None:
    path = safe_path(relative)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
    except (OSError, UnicodeError, SyntaxError) as exc:
        fail(f"{relative}: Python syntax invalid: {exc}")
        return None
    allowed_roots = {
        "__future__",
        "argparse",
        "ast",
        "copy",
        "datetime",
        "hashlib",
        "importlib",
        "json",
        "os",
        "pathlib",
        "platform",
        "re",
        "socket",
        "sqlite3",
        "subprocess",
        "sys",
        "tempfile",
        "typing",
        "unittest",
        "uuid",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".", 1)[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            roots = [(node.module or "").split(".", 1)[0]]
        else:
            continue
        for root in roots:
            if root and root not in allowed_roots:
                fail(f"{relative}: non-stdlib static import is not allowed: {root}")
    return tree


manifest = load_json("tests/micro_suite_manifest.json")
expected_mm = [f"MM-{number:03d}" for number in range(1, 11)]
expected_flags = {
    "suite_defined": True,
    "suite_materialized": True,
    "suite_executed": False,
    "suite_passed": False,
}
executed_flags = {
    "suite_defined": True,
    "suite_materialized": True,
    "suite_executed": True,
    "suite_passed": True,
}
flags = manifest.get("flags")
if flags != expected_flags and flags != executed_flags:
    fail(f"manifest flags are not a valid materialized or passed state: {flags}")
if flags == expected_flags:
    if manifest.get("latest_verification_result") != "not_executed":
        fail("materialized/no-run state must not claim a verification result")
    if manifest.get("latest_run_applicability") != "not_applicable":
        fail("materialized/no-run state must use not_applicable")
elif flags == executed_flags:
    result_path = manifest.get("latest_verification_result_path")
    if not isinstance(result_path, str):
        fail("passed state must name its immutable Verification Result")
    else:
        result = load_json(result_path)
        result_digest = sha256_file(safe_path(result_path))
        if (
            result.get("run_result") != "passed"
            or result.get("exit_code") != 0
            or result.get("privacy_scan", {}).get("status") != "passed"
            or len(result.get("required_results", [])) != 49
        ):
            fail("passed state does not bind a complete passing Verification Result")
        if result.get("manifest_sha256") != manifest.get("latest_verification_manifest_sha256"):
            fail("passed state does not bind the materialized manifest used by the run")
        if result.get("bound_artifacts") != manifest.get("artifacts"):
            fail("passed state does not bind the exact artifact set used by the run")
        if result_digest != manifest.get("latest_verification_result_sha256"):
            fail("passed state does not bind the raw immutable Verification Result")
    if manifest.get("latest_verification_result") != "passed":
        fail("passed state must report latest_verification_result=passed")
    if manifest.get("latest_run_applicability") != "current":
        fail("passed state must report latest_run_applicability=current")
if manifest.get("suite_artifact_state") != "materialized":
    fail("suite_artifact_state must be materialized")
if manifest.get("required_scenario_ids") != expected_mm:
    fail("required scenario IDs are not ordered MM-001..MM-010")
if manifest.get("privacy") != {
    "synthetic_only": True,
    "external_network": False,
    "workspace_external_reads": False,
    "real_personal_data": False,
}:
    fail("manifest privacy boundary is not the closed Micro profile")
if not errors:
    passed("manifest state, scope and privacy flags are closed")

expected_versions = {
    "S1": "0.6",
    "S2": "0.5",
    "S3": "0.4",
    "S4": "0.4",
    "S5": "0.4",
    "S6": "0.5",
    "S7": "0.3",
    "S8": "0.3",
    "S9": "0.4",
}
baseline = manifest.get("baseline", {})
if baseline.get("product_version") != "0.5":
    fail("manifest does not bind PRD v0.5")
if baseline.get("spec_versions") != expected_versions:
    fail("manifest SPEC version map is stale or incomplete")
if baseline.get("adr_refs") != ["ADR-0001"]:
    fail("manifest does not bind the Accepted Micro ADR")
passed("product, SPEC and ADR baseline bindings are present")

authoritative = parse_authoritative_mapping()
scenario_plan = load_json("tests/integration/micro_relationship_scenarios.json")
scenario_rows = scenario_plan.get("scenarios", [])
scenario_mapping: dict[str, list[str]] = {}
for row in scenario_rows:
    scenario_id = row.get("scenario_id")
    if scenario_id in scenario_mapping:
        fail(f"duplicate scenario plan row: {scenario_id}")
        continue
    scenario_mapping[scenario_id] = row.get("required_contract_refs", [])
if sorted(scenario_mapping) != expected_mm:
    fail("scenario plan does not contain MM-001..MM-010 exactly once")
for scenario_id in expected_mm:
    if scenario_mapping.get(scenario_id) != authoritative.get(scenario_id):
        fail(f"{scenario_id}: manifest scenario refs differ from authoritative mapping")
unique_upstream = sorted({ref for refs in authoritative.values() for ref in refs})
if len(unique_upstream) != 39:
    fail(f"authoritative required upstream ref count is {len(unique_upstream)}, expected 39")
if manifest.get("required_upstream_test_refs") != unique_upstream:
    fail("manifest required upstream Test Ref set/order differs from authority")
if not errors:
    passed("10 scenarios and 39 unique upstream Test Refs match the sole authority")

fixture = load_json("tests/fixtures/micro_relationship_v1/fixture.json")
if fixture.get("synthetic") is not True or fixture.get("external_data_used") is not False:
    fail("fixture is not explicitly synthetic-only")
if fixture.get("determinism") != {
    "clock": "2031-10-15T02:00:00Z",
    "timezone": "Asia/Shanghai",
    "locale": "zh-CN",
    "random_seed": 0,
    "id_strategy": "fixed_fixture_ids_v1",
}:
    fail("fixture determinism profile differs from the acceptance contract")
source_ids: set[str] = set()
for source in fixture.get("source_records", []):
    source_id = source.get("source_id")
    source_ids.add(source_id)
    content = source.get("inline_content", "").encode("utf-8")
    digest = hashlib.sha256(content).hexdigest()
    if len(content) != source.get("byte_length"):
        fail(f"{source_id}: UTF-8 byte length mismatch")
    if digest != source.get("content_hash"):
        fail(f"{source_id}: UTF-8 SHA-256 mismatch")
    locator = source.get("locator", {})
    if locator != {"start_byte": 0, "end_byte_exclusive": len(content)}:
        fail(f"{source_id}: locator does not cover exact UTF-8 bytes")
if source_ids != {"src_micro_001", "src_history_001"}:
    fail(f"fixture Source IDs are not the exact pair: {sorted(source_ids)}")
receipt = fixture.get("expected_append_receipt", {})
if receipt.get("status") != "stored" or receipt.get("byte_length") != 58:
    fail("expected append receipt is not the fixed stored 58-byte result")
if not errors:
    passed("both synthetic Source locators, lengths and hashes reproduce")

objects: dict[str, dict[str, Any]] = {}
try:
    for item in fixture["initial_state"]["canonical_objects"]:
        object_id = stable_id(item)
        if object_id in objects:
            fail(f"duplicate Canonical stable ID: {object_id}")
        objects[object_id] = item
except (KeyError, TypeError, ValueError) as exc:
    fail(f"initial Canonical fixture invalid: {exc}")
oracles = load_json("tests/fixtures/micro_relationship_v1/oracles.json")
protected_ids = fixture.get("protected_semantics", {}).get("object_ids", [])
if not protected_ids:
    fail("protected object set is empty")
seed_digests = oracles.get("protected_seed_digests", {})
if set(seed_digests) != set(protected_ids):
    fail("protected seed digest IDs do not equal fixture protected IDs")
for object_id in protected_ids:
    if object_id not in objects:
        fail(f"protected object missing from Canonical fixture: {object_id}")
        continue
    expected_digest = seed_digests.get(object_id)
    if expected_digest != canonical_digest(objects[object_id]):
        fail(f"protected seed digest mismatch: {object_id}")
if sorted(oracles.get("scenario_oracles", {})) != expected_mm:
    fail("oracle file does not contain MM-001..MM-010 exactly")
for scenario_id, rows in oracles.get("scenario_oracles", {}).items():
    if not rows:
        fail(f"{scenario_id}: oracle group is empty")
    ids = [item.get("oracle_id") for item in rows]
    if len(ids) != len(set(ids)) or any(not item for item in ids):
        fail(f"{scenario_id}: oracle IDs are missing or duplicated")
if not errors:
    passed("initial Canonical objects and non-empty protected seed digests are stable")

runner_contract = load_json("tests/runner/runner_contract.json")
result_contract = runner_contract.get("result_contract", {})
if result_contract.get("individual_test_result_values") != [
    "passed",
    "failed",
    "errored",
    "skipped_with_reason",
]:
    fail("runner individual result enum differs from S6")
if result_contract.get("run_result_values") != [
    "passed",
    "failed",
    "errored",
    "partial",
]:
    fail("runner aggregate result enum differs from S6")
if runner_contract.get("environment", {}).get("external_network") != "blocked":
    fail("runner contract does not block external network")
passed("runner contract keeps individual/run result enums separate")

python_paths = [
    "tests/runner/adapter_protocol.py",
    "tests/semantic/test_micro_relationship_contract.py",
    "tests/runner/run_micro_suite.py",
    "tools/validate_micro_suite.py",
]
trees = {path: validate_ast(path) for path in python_paths}
test_tree = trees["tests/semantic/test_micro_relationship_contract.py"]
test_source = safe_path(
    "tests/semantic/test_micro_relationship_contract.py"
).read_text(encoding="utf-8")
if 'RUN_ROOT = ROOT / "tmp/micro-runs"' not in test_source or "dir=RUN_ROOT" not in test_source:
    fail("Micro tests do not confine temporary runtime data to repository tmp/micro-runs")
decorated_scenarios: list[str] = []
if test_tree:
    for node in ast.walk(test_tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "scenario"
                and len(decorator.args) == 1
                and isinstance(decorator.args[0], ast.Constant)
            ):
                decorated_scenarios.append(str(decorator.args[0].value))
if sorted(decorated_scenarios) != expected_mm:
    fail(f"executable test methods do not map exactly to MM-001..010: {decorated_scenarios}")
if not errors:
    passed("Python suite files are stdlib-only, syntactically valid and expose 10 scenarios")

artifact_paths: set[str] = set()
for artifact in manifest.get("artifacts", []):
    relative = artifact.get("path", "")
    if relative in artifact_paths:
        fail(f"duplicate manifest artifact path: {relative}")
        continue
    artifact_paths.add(relative)
    try:
        path = safe_path(relative)
    except ValueError as exc:
        fail(str(exc))
        continue
    if not path.is_file():
        fail(f"manifest artifact missing: {relative}")
        continue
    actual = sha256_file(path)
    if artifact.get("sha256") != actual:
        fail(f"manifest artifact digest mismatch: {relative}")
if not errors:
    passed(f"{len(artifact_paths)} manifest artifact digests match raw file bytes")

privacy_patterns = {
    "email-like": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    "phone-like": re.compile(r"(?<![0-9A-Za-z])1[3-9][0-9]{9}(?![0-9A-Za-z])"),
    "local-user-path": re.compile(r"(?i)(?:[A-Z]:\\Users\\|/Users/)"),
}
privacy_paths = {
    "tests/micro_suite_manifest.json",
    "tests/fixtures/micro_relationship_v1/fixture.json",
    "tests/fixtures/micro_relationship_v1/oracles.json",
    "tests/integration/micro_relationship_scenarios.json",
    "tests/runner/runner_contract.json",
    "tests/runner/adapter_protocol.py",
    "tests/semantic/test_micro_relationship_contract.py",
}
# Runner source contains the detector regex literals; runtime scans fixture and result data.
for relative in sorted(privacy_paths):
    text = safe_path(relative).read_text(encoding="utf-8")
    for label, pattern in privacy_patterns.items():
        if pattern.search(text):
            fail(f"{relative}: privacy heuristic matched {label}")
if not errors:
    passed(f"privacy heuristic scanned {len(privacy_paths)} data-bearing suite artifacts")

print("Noetide Micro suite materialization validation")
print(f"Root: {ROOT}")
for message in checks:
    print(f"PASS: {message}")
for message in errors:
    print(f"FAIL: {message}")
print(f"Manifest SHA-256: {sha256_file(MANIFEST_PATH)}")
if errors:
    print(f"RESULT: FAILED ({len(errors)} error(s)); no business test was executed")
    raise SystemExit(1)
if flags == executed_flags:
    print("RESULT: PASSED (suite artifact checks passed; current business runner result is bound)")
else:
    print("RESULT: PASSED (suite artifact checks only; no business test was executed)")
