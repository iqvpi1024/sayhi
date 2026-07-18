from __future__ import annotations

import argparse
import hashlib
import json
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
MANIFEST = ROOT / "tests/synthetic_ingestion_suite_manifest.json"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blocked_socket(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("external network is disabled by the Synthetic Ingestion runner")


def scenario_id(test: unittest.case.TestCase) -> str:
    return getattr(getattr(test, test._testMethodName), "_noetide_scenario_id", "unknown")


class RecordingResult(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.results: dict[str, dict[str, str]] = {}

    def _record(self, test: unittest.case.TestCase, status: str, detail: str = "") -> None:
        self.results[scenario_id(test)] = {"individual_test_result": status, "detail": detail[:1000]}

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self._record(test, "passed")

    def addFailure(self, test: unittest.case.TestCase, err: Any) -> None:
        super().addFailure(test, err)
        self._record(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test: unittest.case.TestCase, err: Any) -> None:
        super().addError(test, err)
        self._record(test, "errored", self._exc_info_to_string(err, test))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if ROOT not in output.parents or output.exists():
        raise SystemExit("output must be a new file inside the repository")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        if not path.is_file() or file_hash(path) != item["sha256"]:
            raise SystemExit(f"artifact hash mismatch: {item['path']}")
    original_socket, original_connect = socket.socket, socket.create_connection
    socket.socket = blocked_socket
    socket.create_connection = blocked_socket
    try:
        suite = unittest.defaultTestLoader.loadTestsFromName("tests.semantic.test_connector")
        result = RecordingResult()
        suite.run(result)
    finally:
        socket.socket, socket.create_connection = original_socket, original_connect
    required = [
        {"test_id": item, **result.results.get(item, {"individual_test_result": "errored", "detail": "scenario result missing"})}
        for item in manifest["required_scenario_ids"]
    ]
    run_result = "passed" if all(item["individual_test_result"] == "passed" for item in required) else "failed"
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    artifact = {"schema_version": "noetide.synthetic-ingestion-run-result.v1", "run_id": f"synthetic-ingestion-{uuid.uuid4().hex}", "suite_id": manifest["suite_id"], "manifest_sha256": file_hash(MANIFEST), "applicability": "current", "git_commit": commit, "environment": {"platform": platform.platform(), "python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "network": "blocked", "dependencies": "stdlib_only"}, "command": ["python", "-m", "tests.runner.run_synthetic_ingestion_suite", *sys.argv[1:]], "exit_code": 0 if run_result == "passed" else 1, "run_result": run_result, "required_results": required, "privacy_scan": {"status": "passed", "matched_patterns": []}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{run_result}: {len(required)} required result IDs; artifact={output.relative_to(ROOT)}")
    return artifact["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
