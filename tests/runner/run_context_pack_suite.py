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
MANIFEST = ROOT / "tests/context_pack_suite_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blocked_socket(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("external network is disabled by the Context Pack runner")


def scenario_id(test: unittest.case.TestCase) -> str:
    return getattr(getattr(test, test._testMethodName), "_noetide_scenario_id", "unknown")


class Result(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.items: dict[str, dict[str, str]] = {}

    def _record(self, test: unittest.case.TestCase, status: str, detail: str = "") -> None:
        self.items[scenario_id(test)] = {"individual_test_result": status, "detail": detail[:1000]}

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
    bound = []
    for artifact in manifest["artifacts"]:
        path = ROOT / artifact["path"]
        if not path.is_file() or digest(path) != artifact["sha256"]:
            raise SystemExit(f"artifact hash mismatch: {artifact['path']}")
        bound.append({"role": artifact["role"], "path": artifact["path"], "sha256": artifact["sha256"]})
    original_socket, original_connect = socket.socket, socket.create_connection
    socket.socket = blocked_socket
    socket.create_connection = blocked_socket
    try:
        suite = unittest.defaultTestLoader.loadTestsFromName("tests.semantic.test_portability")
        result = Result()
        suite.run(result)
    finally:
        socket.socket, socket.create_connection = original_socket, original_connect
    required = [{"test_id": item, **result.items.get(item, {"individual_test_result": "errored", "detail": "scenario result missing"})} for item in manifest["required_scenario_ids"]]
    passed = all(item["individual_test_result"] == "passed" for item in required)
    artifact = {"schema_version": "noetide.context-pack-run-result.v1", "run_id": f"context-pack-{uuid.uuid4().hex}", "suite_id": manifest["suite_id"], "manifest_sha256": digest(MANIFEST), "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip(), "applicability": "current", "environment": {"platform": platform.platform(), "python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "network": "blocked", "dependencies": "stdlib_only"}, "command": ["python", "-m", "tests.runner.run_context_pack_suite", *sys.argv[1:]], "exit_code": 0 if passed else 1, "run_result": "passed" if passed else "failed", "required_results": required, "bound_artifacts": bound}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{artifact['run_result']}: {len(required)} required result IDs; artifact={output.relative_to(ROOT)}")
    return artifact["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
