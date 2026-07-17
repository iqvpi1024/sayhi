from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import re
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "tests/answer_safety_suite_manifest.json"
SCENARIOS_PATH = ROOT / "tests/integration/answer_safety_scenarios.json"
TEST_MODULE = "tests.semantic.test_answer_safety_contract"


class ResultArtifactWriteError(RuntimeError):
    def __init__(self, failure_record: dict[str, Any]) -> None:
        super().__init__(failure_record["reason_code"])
        self.failure_record = failure_record


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def scenario_id(test: unittest.case.TestCase) -> str:
    method = getattr(test, test._testMethodName)
    return getattr(method, "_noetide_scenario_id", "unknown")


class RecordingResult(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.scenario_results: dict[str, dict[str, Any]] = {}

    def _record(self, test: unittest.case.TestCase, result: str, detail: str = "") -> None:
        self.scenario_results[scenario_id(test)] = {
            "individual_test_result": result,
            "detail": detail[:4000],
        }

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self._record(test, "passed")

    def addFailure(self, test: unittest.case.TestCase, err: Any) -> None:
        super().addFailure(test, err)
        self._record(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test: unittest.case.TestCase, err: Any) -> None:
        super().addError(test, err)
        self._record(test, "errored", self._exc_info_to_string(err, test))

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self._record(test, "skipped_with_reason", reason)


def aggregate_result(values: list[str]) -> str:
    order = {"passed": 0, "skipped_with_reason": 1, "failed": 2, "errored": 3}
    return max(values, key=order.__getitem__)


def run_result_for(individual: list[str]) -> str:
    if any(value == "errored" for value in individual):
        return "errored"
    if any(value == "failed" for value in individual):
        return "failed"
    if any(value == "skipped_with_reason" for value in individual):
        return "partial"
    return "passed"


def blocked_socket(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("external network is disabled by the Answer Safety runner")


def write_result_artifact(
    output: Path,
    payload: Mapping[str, Any],
    failure_point: str | None = None,
) -> None:
    """Write one immutable LF JSON result with an atomic replace boundary."""
    resolved = output.resolve()
    if ROOT not in resolved.parents:
        raise ValueError("result output must stay inside the repository")
    if output.exists():
        raise FileExistsError("result output already exists; result records are immutable")
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if failure_point == "result.output.before_atomic_replace":
            raise ResultArtifactWriteError(
                {
                    "run_result": "errored",
                    "reason_code": "result_artifact_write_failed",
                    "failure_stage": failure_point,
                    "current_passed_artifact_created": False,
                    "target": str(output),
                }
            )
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--inject-result-write-failure",
        action="store_true",
        help="exercise output failure without publishing a current result artifact",
    )
    return parser.parse_args()


def _privacy_matches(blob: str) -> list[str]:
    patterns = {
        "email-like": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
        "phone-like": re.compile(r"(?<![0-9A-Za-z])1[3-9][0-9]{9}(?![0-9A-Za-z])"),
        "local-user-path": re.compile(r"(?i)(?:[A-Z]:\\Users\\|/Users/)"),
        "credential-assignment": re.compile(
            r"(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*[^\s,}]+"
        ),
    }
    return [label for label, pattern in patterns.items() if pattern.search(blob)]


def main() -> int:
    args = parse_args()
    resolved_output = args.output.resolve()
    if ROOT not in resolved_output.parents:
        raise SystemExit("result output must stay inside the repository")
    if resolved_output.exists():
        raise SystemExit("result output already exists; result records are immutable")
    relative_output = resolved_output.relative_to(ROOT)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))["scenarios"]
    started_at = utc_now()
    run_id = f"answer-safety-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    os.environ["NOETIDE_ANSWER_ADAPTER"] = args.adapter
    os.environ["NOETIDE_NETWORK_DISABLED"] = "1"
    adapter_path = "not_available"

    original_socket = socket.socket
    original_create_connection = socket.create_connection
    socket.socket = blocked_socket
    socket.create_connection = blocked_socket
    try:
        adapter_module = importlib.import_module(args.adapter)
        module_file = getattr(adapter_module, "__file__", None)
        if module_file:
            adapter_path = str(Path(module_file).resolve().relative_to(ROOT))
        suite = unittest.defaultTestLoader.loadTestsFromName(TEST_MODULE)
        result = RecordingResult()
        suite.run(result)
    except Exception as exc:
        result = RecordingResult()
        for item in manifest["required_scenario_ids"]:
            result.scenario_results[item] = {
                "individual_test_result": "errored",
                "detail": f"{type(exc).__name__}: {exc}",
            }
    finally:
        socket.socket = original_socket
        socket.create_connection = original_create_connection

    required_results: list[dict[str, Any]] = []
    for as_id in manifest["required_scenario_ids"]:
        recorded = result.scenario_results.get(
            as_id,
            {
                "individual_test_result": "errored",
                "detail": "required scenario result missing",
            },
        )
        required_results.append(
            {"test_id": as_id, **recorded, "coverage_scenarios": [as_id]}
        )

    ref_to_scenarios: dict[str, list[str]] = {}
    for item in scenarios:
        for ref in item["required_contract_refs"]:
            ref_to_scenarios.setdefault(ref, []).append(item["scenario_id"])
    for ref in manifest["required_upstream_test_refs"]:
        coverage = ref_to_scenarios[ref]
        statuses = [
            result.scenario_results.get(
                as_id, {"individual_test_result": "errored"}
            )["individual_test_result"]
            for as_id in coverage
        ]
        required_results.append(
            {
                "test_id": ref,
                "individual_test_result": aggregate_result(statuses),
                "coverage_scenarios": coverage,
                "detail": "",
            }
        )

    fixture_text = (ROOT / "tests/fixtures/answer_safety_v1/fixture.json").read_text(
        encoding="utf-8"
    )
    oracle_text = (ROOT / "tests/fixtures/answer_safety_v1/oracles.json").read_text(
        encoding="utf-8"
    )
    privacy_matches = _privacy_matches(
        fixture_text + oracle_text + json.dumps(required_results, ensure_ascii=False)
    )
    individual_values = [item["individual_test_result"] for item in required_results]
    run_result = run_result_for(individual_values)
    if privacy_matches:
        run_result = "failed"
    exit_codes = {"passed": 0, "failed": 1, "errored": 2, "partial": 3}
    exit_code = exit_codes[run_result]
    artifact = {
        "schema_version": "noetide.answer-safety-run-result.v1",
        "run_id": run_id,
        "suite_id": manifest["suite_id"],
        "suite_artifact_version": manifest["suite_artifact_version"],
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "applicability": "current",
        "started_at": started_at,
        "finished_at": utc_now(),
        "git_commit": git_commit(),
        "implementation_adapter": args.adapter,
        "implementation_adapter_path": adapter_path,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "dependencies": "stdlib_only",
            "network": "blocked",
            "business_clock": "fixture_injected",
            "timezone": "UTC",
            "locale": "en-US",
            "random_seed": 0,
        },
        "command": [
            "python",
            "-m",
            "tests.runner.run_answer_safety_suite",
            "--adapter",
            args.adapter,
            "--output",
            str(relative_output),
            *(["--inject-result-write-failure"] if args.inject_result_write_failure else []),
        ],
        "exit_code": exit_code,
        "run_result": run_result,
        "suite_passed": run_result == "passed",
        "required_results": required_results,
        "bound_artifacts": manifest["artifacts"],
        "privacy_scan": {
            "status": "failed" if privacy_matches else "passed",
            "scope": "synthetic fixture, oracle, and structured result fields",
            "matched_patterns": privacy_matches,
        },
    }
    failure_point = (
        "result.output.before_atomic_replace"
        if args.inject_result_write_failure
        else None
    )
    try:
        write_result_artifact(resolved_output, artifact, failure_point=failure_point)
    except ResultArtifactWriteError as exc:
        print(json.dumps(exc.failure_record, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2

    print(
        f"{run_result}: {len(required_results)} required result IDs; "
        f"artifact={relative_output}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
