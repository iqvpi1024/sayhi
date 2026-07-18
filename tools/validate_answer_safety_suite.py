from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tests/answer_safety_suite_manifest.json"
FIXTURE_PATH = ROOT / "tests/fixtures/answer_safety_v1/fixture.json"
ORACLE_PATH = ROOT / "tests/fixtures/answer_safety_v1/oracles.json"
SCENARIOS_PATH = ROOT / "tests/integration/answer_safety_scenarios.json"
ACCEPTANCE_PATH = ROOT / "docs/testing/MVP_A_ANSWER_SAFETY_ACCEPTANCE.md"
PROTOCOL_PATH = ROOT / "tests/runner/answer_safety_adapter_protocol.py"
TEST_PATH = ROOT / "tests/semantic/test_answer_safety_contract.py"
RUNNER_PATH = ROOT / "tests/runner/run_answer_safety_suite.py"

EXPECTED_MAPPING = {
    "AS-001": ["SOM-AT-008", "BTE-AT-020"],
    "AS-002": ["BTE-AT-021"],
    "AS-003": ["BTE-AT-024"],
    "AS-004": ["SOM-AT-021", "BTE-AT-030"],
    "AS-005": ["BTE-AT-012", "BTE-AT-013"],
    "AS-006": ["BTE-AT-026", "BTE-AT-027"],
    "AS-007": ["BTE-AT-025"],
    "AS-008": ["SOM-AT-009", "BTE-AT-034", "SIP-AT-006"],
    "AS-009": ["SOM-AT-018"],
    "AS-010": ["HTH-AT-006", "HTH-AT-007", "HTH-AT-008", "HTH-AT-009", "HTH-AT-013"],
    "AS-011": ["HTH-AT-002", "HTH-AT-019", "HTH-AT-020", "HTH-AT-023"],
}
EXPECTED_ANSWER_STATUSES = {
    "AS-001": ["verified"],
    "AS-002": ["verified", "unknown"],
    "AS-003": ["unconfirmed"],
    "AS-004": ["disputed"],
    "AS-005": ["not_covered", "not_covered"],
    "AS-006": ["stale", "verified"],
    "AS-007": ["unknown"],
    "AS-008": ["unknown"],
    "AS-009": ["unknown"],
    "AS-010": ["verified"],
    "AS-011": [],
}
EXPECTED_ARTIFACTS = {
    "fixture": "tests/fixtures/answer_safety_v1/fixture.json",
    "oracle": "tests/fixtures/answer_safety_v1/oracles.json",
    "scenario_plan": "tests/integration/answer_safety_scenarios.json",
    "adapter_protocol": "tests/runner/answer_safety_adapter_protocol.py",
    "business_test_module": "tests/semantic/test_answer_safety_contract.py",
    "offline_runner": "tests/runner/run_answer_safety_suite.py",
    "suite_preflight_validator": "tools/validate_answer_safety_suite.py",
}
REQUIRED_ENVELOPE_FIELDS = {
    "answer_status",
    "answer_value",
    "verification_scope",
    "valid_time",
    "recorded_as_of",
    "evaluated_at",
    "evidence_refs",
    "coverage",
    "reason_codes",
    "data_revision",
    "assessment_policy_ref",
}
ALLOWED_STATUS = {"verified", "unconfirmed", "disputed", "not_covered", "stale", "unknown"}
ALLOWED_SCOPE = {"record_accuracy", "statement_occurrence", "viewpoint", "world_claim"}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def equal(self, actual: Any, expected: Any, message: str) -> None:
        if actual != expected:
            self.errors.append(f"{message}: expected={expected!r}, actual={actual!r}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_lf_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def stable_id(item: Mapping[str, Any]) -> str:
    for key in ("source_id", "assertion_id", "object_id", "record_id", "view_name"):
        value = item.get(key)
        if isinstance(value, str):
            return value
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def layer_digest(items: list[Mapping[str, Any]]) -> str:
    ordered = sorted(items, key=stable_id)
    encoded = json.dumps(
        ordered, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def decorated_scenarios(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "scenario"
                and len(decorator.args) == 1
                and isinstance(decorator.args[0], ast.Constant)
                and isinstance(decorator.args[0].value, str)
            ):
                values.append(decorator.args[0].value)
    return values


def acceptance_mapping(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"answer_safety_required_contract_slices:\s*\n"
        r"(?P<body>(?:\s{2}AS-[0-9]{3}:\s*\[[^\n]+\]\s*\n)+)",
        text,
    )
    if match is None:
        return {}
    mapping: dict[str, list[str]] = {}
    for line in match.group("body").splitlines():
        scenario, raw_refs = line.strip().split(":", 1)
        mapping[scenario] = [
            item.strip() for item in raw_refs.strip().strip("[]").split(",")
        ]
    return mapping


def protocol_methods(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    methods: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in {
            "AnswerSafetySystem",
            "AnswerSafetyAdapterModule",
        }:
            methods.update(
                child.name for child in node.body if isinstance(child, ast.FunctionDef)
            )
    return methods


def all_source_refs(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        if "source_id" in value and "locator" in value:
            yield value
        for child in value.values():
            yield from all_source_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_source_refs(child)


def validate_manifest(v: Validation, manifest: Mapping[str, Any]) -> None:
    v.equal(manifest.get("suite_id"), "mvp_a_answer_safety_v1", "suite_id")
    v.equal(manifest.get("slice_id"), "SLICE-MVP-A-ANSWER-SAFETY-001", "slice_id")
    materialized_flags = {
        "suite_defined": True, "suite_materialized": True,
        "suite_executed": False, "suite_passed": False,
    }
    passed_flags = {
        "suite_defined": True, "suite_materialized": True,
        "suite_executed": True, "suite_passed": True,
    }
    flags = manifest.get("flags")
    v.require(flags in (materialized_flags, passed_flags), "suite flags")
    v.equal(manifest.get("suite_artifact_state"), "materialized", "artifact state")
    if flags == materialized_flags:
        v.equal(manifest.get("latest_verification_result"), "not_executed", "verification state")
        v.equal(manifest.get("latest_run_applicability"), "not_applicable", "run applicability")
        v.equal(manifest.get("latest_verification_result_path"), None, "result path before execution")
    elif flags == passed_flags:
        result_path = manifest.get("latest_verification_result_path")
        v.require(isinstance(result_path, str) and (ROOT / result_path).is_file(), "current result path")
        v.equal(manifest.get("latest_verification_result"), "passed", "verification state")
        v.equal(manifest.get("latest_run_applicability"), "current", "run applicability")
        if isinstance(result_path, str) and (ROOT / result_path).is_file():
            result = load_json(ROOT / result_path)
            v.equal(result.get("run_result"), "passed", "current result run state")
            v.equal(result.get("exit_code"), 0, "current result exit code")
            v.equal(len(result.get("required_results", [])), 35, "current required result count")
            v.require(all(item.get("individual_test_result") == "passed" for item in result.get("required_results", [])), "current required results")
            v.equal(result.get("bound_artifacts"), manifest.get("artifacts"), "current result artifact binding")
            v.equal(result.get("manifest_sha256"), manifest.get("latest_verification_manifest_sha256"), "result manifest binding")
            v.equal(sha256_file(ROOT / result_path), manifest.get("latest_verification_result_sha256"), "result raw hash")
    baseline = manifest.get("baseline", {})
    v.equal(baseline.get("product_path"), "PRDv05.md", "product path")
    v.equal(
        baseline.get("product_canonical_lf_sha256"),
        canonical_lf_sha256(ROOT / "PRDv05.md"),
        "product canonical LF hash",
    )
    v.equal(baseline.get("decision_refs"), ["DEC-MVP-A-AS-001"], "decision refs")
    v.equal(baseline.get("adr_refs"), ["ADR-0002"], "ADR refs")
    v.equal(baseline.get("architecture_ref"), "ARCH-MVP-A-AS-001", "architecture ref")

    artifacts = manifest.get("artifacts", [])
    by_role = {item.get("role"): item for item in artifacts}
    v.equal(set(by_role), set(EXPECTED_ARTIFACTS), "artifact roles")
    for role, relative in EXPECTED_ARTIFACTS.items():
        item = by_role.get(role, {})
        v.equal(item.get("path"), relative, f"{role} path")
        path = ROOT / relative
        v.require(path.is_file(), f"{relative} is absent")
        if path.is_file():
            v.equal(item.get("sha256"), sha256_file(path), f"{role} raw-byte hash")

    scenario_ids = list(EXPECTED_MAPPING)
    upstream = sorted({ref for refs in EXPECTED_MAPPING.values() for ref in refs})
    v.equal(manifest.get("required_scenario_ids"), scenario_ids, "required scenario IDs")
    v.equal(manifest.get("required_upstream_test_refs"), upstream, "required upstream refs")
    v.equal(manifest.get("required_upstream_count"), 24, "required upstream count")
    v.equal(manifest.get("required_result_count"), 35, "required result count")
    expected_module = "TBD" if flags == materialized_flags else "src/noetide_micro/answers.py"
    v.equal(manifest.get("implementation_module"), expected_module, "implementation module")
    privacy = manifest.get("privacy", {})
    v.equal(
        privacy,
        {
            "synthetic_only": True,
            "external_network": False,
            "workspace_external_reads": False,
            "real_personal_data": False,
        },
        "manifest privacy boundary",
    )


def validate_fixture_and_oracle(
    v: Validation,
    fixture: Mapping[str, Any],
    oracles: Mapping[str, Any],
) -> None:
    v.equal(fixture.get("fixture_id"), "answer_safety_v1", "fixture_id")
    v.equal(fixture.get("synthetic"), True, "fixture synthetic flag")
    v.equal(fixture.get("external_data_used"), False, "external data flag")
    v.equal(fixture.get("owner_ref"), "synthetic_owner_001", "owner ref")
    v.equal(fixture.get("subject_ref"), "synthetic_subject_001", "subject ref")
    determinism = fixture.get("determinism", {})
    v.equal(determinism.get("clock"), "2032-01-15T12:00:00Z", "fixture clock")
    v.equal(determinism.get("timezone"), "UTC", "fixture timezone")
    v.equal(determinism.get("random_seed"), 0, "fixture random seed")
    v.equal(
        determinism.get("canonical_digest"),
        "sha256_stable_id_sorted_canonical_json_v1",
        "layer digest strategy",
    )

    cases = fixture.get("cases", [])
    case_ids = [case.get("scenario_id") for case in cases]
    v.equal(case_ids, list(EXPECTED_MAPPING), "fixture case IDs/order")
    database_ids = [case.get("database_identity") for case in cases]
    v.equal(len(set(database_ids)), 11, "isolated database identities")
    oracle_scenarios = oracles.get("scenarios", {})
    v.equal(set(oracle_scenarios), set(EXPECTED_MAPPING), "oracle scenario IDs")
    v.equal(set(oracles.get("answer_status_values", [])), ALLOWED_STATUS, "answer status enum")
    v.equal(set(oracles.get("verification_scope_values", [])), ALLOWED_SCOPE, "scope enum")

    for case in cases:
        scenario_id = case["scenario_id"]
        state = case.get("initial_state", {})
        v.equal(state.get("data_revision"), "as_rev_001", f"{scenario_id} revision")
        sources = state.get("source_records", [])
        source_by_id = {item.get("source_id"): item for item in sources}
        for source in sources:
            content = source.get("inline_content", "")
            raw = content.encode("utf-8")
            v.equal(source.get("byte_length"), len(raw), f"{scenario_id} source byte length")
            v.equal(
                source.get("content_hash"),
                hashlib.sha256(raw).hexdigest(),
                f"{scenario_id} source content hash",
            )
            locator = source.get("locator", {})
            v.equal(locator.get("scheme"), "text_utf8_byte_range_v1", f"{scenario_id} locator scheme")
            v.equal(locator.get("start_byte"), 0, f"{scenario_id} locator start")
            v.equal(locator.get("end_byte_exclusive"), len(raw), f"{scenario_id} locator end")

        layer_keys = {
            "source": "source_records",
            "canonical": "canonical_objects",
            "ledger": "ledger_records",
            "projection": "projection_rows",
        }
        for layer, key in layer_keys.items():
            items = state.get(key, [])
            v.require(isinstance(items, list), f"{scenario_id} {key} must be a list")
            if isinstance(items, list):
                v.equal(
                    case.get("expected_initial_layer_digests", {}).get(layer),
                    layer_digest(items),
                    f"{scenario_id} {layer} digest",
                )

        for ref in all_source_refs(state.get("canonical_objects", [])):
            source = source_by_id.get(ref.get("source_id"))
            v.require(source is not None, f"{scenario_id} evidence source is absent")
            if source is not None:
                v.equal(ref.get("locator"), source.get("locator"), f"{scenario_id} evidence locator")

        coverage_ids = {
            item.get("coverage_window_id") for item in state.get("coverage_windows", [])
        }
        query_ids: list[str] = []
        for query in case.get("query_requests", []):
            query_id = query.get("query_id")
            query_ids.append(query_id)
            refs = query.get("coverage_window_refs", [])
            v.require(set(refs).issubset(coverage_ids), f"{scenario_id}/{query_id} coverage ref absent")
            v.equal(query.get("recorded_as_of"), "current", f"{scenario_id}/{query_id} cutoff")

        expected_answers = oracle_scenarios.get(scenario_id, {}).get("expected_answers", {})
        v.equal(set(expected_answers), set(query_ids), f"{scenario_id} query/oracle IDs")
        statuses: list[str] = []
        for query_id in query_ids:
            answer = expected_answers[query_id]
            v.require(
                REQUIRED_ENVELOPE_FIELDS.issubset(answer),
                f"{scenario_id}/{query_id} envelope fields missing",
            )
            status = answer.get("answer_status")
            statuses.append(status)
            v.require(status in ALLOWED_STATUS, f"{scenario_id}/{query_id} invalid status")
            if status == "verified":
                v.require(
                    answer.get("verification_scope") in ALLOWED_SCOPE,
                    f"{scenario_id}/{query_id} verified scope absent",
                )
            else:
                v.equal(
                    answer.get("verification_scope"),
                    None,
                    f"{scenario_id}/{query_id} non-verified scope",
                )
            v.equal(
                answer.get("evaluated_at"),
                determinism.get("clock"),
                f"{scenario_id}/{query_id} evaluated_at",
            )
            v.equal(
                answer.get("data_revision"),
                state.get("data_revision"),
                f"{scenario_id}/{query_id} data revision",
            )
            for evidence_ref in answer.get("evidence_refs", []):
                source = source_by_id.get(evidence_ref.get("source_id"))
                v.require(source is not None, f"{scenario_id}/{query_id} oracle evidence absent")
                if source is not None:
                    v.equal(
                        evidence_ref.get("locator"),
                        source.get("locator"),
                        f"{scenario_id}/{query_id} oracle evidence locator",
                    )
        v.equal(statuses, EXPECTED_ANSWER_STATUSES[scenario_id], f"{scenario_id} answer statuses")

    v.equal(
        oracle_scenarios["AS-008"]["expected_answers"]["as008_derived_forbidden"]["evidence_refs"],
        [],
        "derived-only evidence refs",
    )
    v.equal(
        oracle_scenarios["AS-009"]["expected_answers"]["as009_fictional_isolated"]["answer_status"],
        "unknown",
        "fictional world claim status",
    )
    writer = oracle_scenarios["AS-011"].get("result_writer_contract", {})
    v.equal(writer.get("current_passed_artifact_created"), False, "AS-011 current artifact")
    v.equal(writer.get("suite_passed_published"), False, "AS-011 suite pass")


def validate_scenarios(v: Validation, scenarios: Mapping[str, Any]) -> None:
    items = scenarios.get("scenarios", [])
    mapping = {item.get("scenario_id"): item.get("required_contract_refs") for item in items}
    v.equal(mapping, EXPECTED_MAPPING, "scenario-to-upstream exact mapping")
    v.equal(
        acceptance_mapping(ACCEPTANCE_PATH),
        EXPECTED_MAPPING,
        "Acceptance section 7 exact mapping",
    )
    v.equal(
        scenarios.get("fixture_ref"),
        "tests/fixtures/answer_safety_v1/fixture.json",
        "scenario fixture ref",
    )
    v.equal(
        scenarios.get("oracle_ref"),
        "tests/fixtures/answer_safety_v1/oracles.json",
        "scenario oracle ref",
    )


def validate_python_contract(v: Validation) -> None:
    expected_scenarios = list(EXPECTED_MAPPING)
    v.equal(decorated_scenarios(TEST_PATH), expected_scenarios, "semantic test scenario decorators")
    v.equal(
        protocol_methods(PROTOCOL_PATH),
        {"evaluate", "layer_snapshot", "inject_failure", "create_system"},
        "adapter protocol methods",
    )
    allowed_local_roots = {"tests", "noetide_micro"}
    for path in (PROTOCOL_PATH, TEST_PATH, RUNNER_PATH, Path(__file__)):
        roots = imported_roots(path)
        third_party = {
            root
            for root in roots
            if root not in sys.stdlib_module_names
            and root not in allowed_local_roots
            and root != "__future__"
        }
        v.equal(third_party, set(), f"{path.relative_to(ROOT)} third-party imports")
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")
    for required in (
        "socket.socket = blocked_socket",
        "output.exists()",
        "os.replace(temporary, output)",
        "ResultArtifactWriteError",
        "result.output.before_atomic_replace",
        "verify_bound_artifacts",
    ):
        v.require(required in runner_text, f"runner missing safety mechanism: {required}")
    test_text = TEST_PATH.read_text(encoding="utf-8")
    v.require("NOETIDE_ANSWER_ADAPTER" in test_text, "adapter env binding absent")
    v.require("oracles.json" in test_text, "independent oracle load absent")


def validate_privacy(v: Validation, paths: Iterable[Path]) -> None:
    blob = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    patterns = {
        "email-like": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
        "phone-like": re.compile(r"(?<![0-9A-Za-z])1[3-9][0-9]{9}(?![0-9A-Za-z])"),
        "local-user-path": re.compile(r"(?i)(?:[A-Z]:\\Users\\|/Users/)"),
        "github-token-like": re.compile(r"(?:ghp_|github_pat_)[A-Za-z0-9_]+"),
    }
    matches = [label for label, pattern in patterns.items() if pattern.search(blob)]
    v.equal(matches, [], "synthetic privacy scan")
    v.require("synthetic" in blob, "synthetic declaration absent")


def main() -> int:
    v = Validation()
    for path in (
        MANIFEST_PATH,
        FIXTURE_PATH,
        ORACLE_PATH,
        SCENARIOS_PATH,
        PROTOCOL_PATH,
        TEST_PATH,
        RUNNER_PATH,
        ACCEPTANCE_PATH,
    ):
        v.require(path.is_file(), f"required artifact absent: {path.relative_to(ROOT)}")
    if v.errors:
        for error in v.errors:
            print(f"ERROR: {error}")
        return 1

    manifest = load_json(MANIFEST_PATH)
    fixture = load_json(FIXTURE_PATH)
    oracles = load_json(ORACLE_PATH)
    scenarios = load_json(SCENARIOS_PATH)
    validate_manifest(v, manifest)
    validate_fixture_and_oracle(v, fixture, oracles)
    validate_scenarios(v, scenarios)
    validate_python_contract(v)
    validate_privacy(
        v,
        (FIXTURE_PATH, ORACLE_PATH, SCENARIOS_PATH),
    )

    if v.errors:
        for error in v.errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(v.errors)} Answer Safety suite validation errors")
        return 1
    print("PASSED: Answer Safety suite materialized with 11 scenarios + 24 upstream refs = 35 result IDs")
    print("PASSED: fixture/oracle hashes, locators, digests, AST, stdlib, privacy, and four-state contract")
    if manifest.get("flags", {}).get("suite_executed"):
        print("PASSED: Answer Safety current business runner result is bound")
    else:
        print("NOT_EXECUTED: Answer Safety business runner")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
