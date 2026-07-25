from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import socket
import sqlite3
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests/c4_suite_manifest.json"
TEST_MODULE = "tests.semantic.test_c4_scenario_contract"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blocked_socket(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("external network is disabled by the C4 runner")


def scenario_id(test: unittest.case.TestCase) -> str:
    method = getattr(test, test._testMethodName)
    return getattr(method, "_noetide_scenario_id", "unknown")


class RecordingResult(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.rows: dict[str, dict[str, str]] = {}

    def _record(self, test: unittest.case.TestCase, status: str, detail: str = "") -> None:
        self.rows[scenario_id(test)] = {"individual_test_result": status, "detail": detail[:2000]}

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self._record(test, "passed")

    def addFailure(self, test: unittest.case.TestCase, error: Any) -> None:
        super().addFailure(test, error)
        self._record(test, "failed", self._exc_info_to_string(error, test))

    def addError(self, test: unittest.case.TestCase, error: Any) -> None:
        super().addError(test, error)
        self._record(test, "errored", self._exc_info_to_string(error, test))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if ROOT not in output.parents or output.exists():
        raise SystemExit("output must be new and inside repository")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = manifest["artifacts"]
    for item in artifacts:
        path = ROOT / item["path"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise SystemExit(f"artifact hash mismatch: {item['path']}")
    required = manifest["required_scenario_ids"]
    previous_adapter = os.environ.get("NOETIDE_C4_ADAPTER")
    original_socket, original_connection = socket.socket, socket.create_connection
    socket.socket, socket.create_connection = blocked_socket, blocked_socket
    try:
        os.environ["NOETIDE_C4_ADAPTER"] = args.adapter
        importlib.invalidate_caches()
        suite = unittest.defaultTestLoader.loadTestsFromName(TEST_MODULE)
        result = RecordingResult()
        suite.run(result)
    finally:
        socket.socket, socket.create_connection = original_socket, original_connection
        if previous_adapter is None:
            os.environ.pop("NOETIDE_C4_ADAPTER", None)
        else:
            os.environ["NOETIDE_C4_ADAPTER"] = previous_adapter
    rows = [{"test_id": item, **result.rows.get(item, {"individual_test_result": "errored", "detail": "scenario result missing"})} for item in required]
    passed = all(row["individual_test_result"] == "passed" for row in rows) and not result.errors and not result.failures
    artifact = {
        "schema_version": "noetide.c4-run-result.v1",
        "run_id": f"c4-{uuid.uuid4().hex}",
        "suite_id": manifest["suite_id"],
        "manifest_sha256": sha256_file(MANIFEST),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "applicability": "current",
        "environment": {"platform": platform.platform(), "python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "network": "blocked", "dependencies": "stdlib_only"},
        "command": ["python", "-m", "tests.runner.run_c4_suite", *sys.argv[1:]],
        "exit_code": 0 if passed else 1,
        "run_result": "passed" if passed else "failed",
        "required_results": rows,
        "bound_artifacts": artifacts
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{'passed' if passed else 'failed'}: {len(rows)} C4 scenarios; artifact={output.relative_to(ROOT)}")
    return artifact["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
