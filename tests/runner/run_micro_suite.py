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
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "tests/micro_suite_manifest.json"
SCENARIOS_PATH = ROOT / "tests/integration/micro_relationship_scenarios.json"
TEST_MODULE = "tests.semantic.test_micro_relationship_contract"


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
    order = {
        "passed": 0,
        "skipped_with_reason": 1,
        "failed": 2,
        "errored": 3,
    }
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
    raise RuntimeError("external network is disabled by the Micro runner")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    if ROOT not in output.parents:
        raise SystemExit("result output must stay inside the repository")
    if output.exists():
        raise SystemExit("result output already exists; result records are immutable")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))["scenarios"]
    started_at = utc_now()
    run_id = f"micro-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    os.environ["NOETIDE_MICRO_ADAPTER"] = args.adapter
    os.environ["NOETIDE_NETWORK_DISABLED"] = "1"

    original_socket = socket.socket
    original_create_connection = socket.create_connection
    socket.socket = blocked_socket
    socket.create_connection = blocked_socket
    try:
        importlib.import_module(args.adapter)
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
    for mm_id in manifest["required_scenario_ids"]:
        recorded = result.scenario_results.get(
            mm_id,
            {
                "individual_test_result": "errored",
                "detail": "required scenario result missing",
            },
        )
        required_results.append({"test_id": mm_id, **recorded, "coverage_scenarios": [mm_id]})

    ref_to_scenarios: dict[str, list[str]] = {}
    for item in scenarios:
        for ref in item["required_contract_refs"]:
            ref_to_scenarios.setdefault(ref, []).append(item["scenario_id"])
    for ref in manifest["required_upstream_test_refs"]:
        coverage = ref_to_scenarios[ref]
        statuses = [
            result.scenario_results.get(
                mm_id, {"individual_test_result": "errored"}
            )["individual_test_result"]
            for mm_id in coverage
        ]
        required_results.append(
            {
                "test_id": ref,
                "individual_test_result": aggregate_result(statuses),
                "coverage_scenarios": coverage,
                "detail": "",
            }
        )

    privacy_blob = (
        (ROOT / "tests/fixtures/micro_relationship_v1/fixture.json").read_text(encoding="utf-8")
        + (ROOT / "tests/fixtures/micro_relationship_v1/oracles.json").read_text(encoding="utf-8")
        + json.dumps(required_results, ensure_ascii=False)
    )
    privacy_patterns = {
        "email-like": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
        "phone-like": re.compile(
            r"(?<![0-9A-Za-z])1[3-9][0-9]{9}(?![0-9A-Za-z])"
        ),
        "local-user-path": re.compile(r"(?i)(?:[A-Z]:\\Users\\|/Users/)"),
    }
    privacy_matches = [
        label for label, pattern in privacy_patterns.items() if pattern.search(privacy_blob)
    ]
    individual_values = [item["individual_test_result"] for item in required_results]
    run_result = run_result_for(individual_values)
    if privacy_matches:
        run_result = "failed"
    exit_codes = {"passed": 0, "failed": 1, "errored": 2, "partial": 3}
    exit_code = exit_codes[run_result]
    artifact = {
        "schema_version": "noetide.micro-run-result.v1",
        "run_id": run_id,
        "suite_id": manifest["suite_id"],
        "suite_artifact_version": manifest["suite_artifact_version"],
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "applicability": "current",
        "started_at": started_at,
        "finished_at": utc_now(),
        "git_commit": git_commit(),
        "implementation_adapter": args.adapter,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "dependencies": "stdlib_only",
            "network": "blocked",
            "business_clock": "fixture_injected",
            "timezone": "fixture_injected",
            "locale": "zh-CN",
            "random_seed": 0,
        },
        "command": ["python", "-m", "tests.runner.run_micro_suite", *sys.argv[1:]],
        "exit_code": exit_code,
        "run_result": run_result,
        "required_results": required_results,
        "bound_artifacts": manifest["artifacts"],
        "privacy_scan": {
            "status": "failed" if privacy_matches else "passed",
            "scope": "synthetic fixture and structured result fields",
            "matched_patterns": privacy_matches,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"{run_result}: {len(required_results)} required result IDs; "
        f"artifact={output.relative_to(ROOT)}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
