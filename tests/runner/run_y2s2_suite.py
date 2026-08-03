from __future__ import annotations

import argparse
import hashlib
import importlib
import ipaddress
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
MANIFEST = ROOT / "tests/y2s2_suite_manifest.json"
TEST_MODULE = "tests.semantic.test_y2s2_local_model_contract"

_ORIGINAL_SOCKET = socket.socket
_ORIGINAL_CREATE_CONNECTION = socket.create_connection


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_loopback_address(address: Any) -> bool:
    if not isinstance(address, tuple) or len(address) < 2:
        return False
    host = address[0]
    if not isinstance(host, str):
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return host.lower() in {"localhost", "::1", "127.0.0.1"}
    return any(
        ipaddress.ip_address(info[4][0]).is_loopback
        for info in infos
        if len(info) >= 5 and isinstance(info[4][0], str)
    )


class LoopbackOnlySocket(_ORIGINAL_SOCKET):
    def connect(self, address: Any) -> None:
        if not _is_loopback_address(address):
            raise RuntimeError("external network is disabled by the Y2S2 runner")
        return super().connect(address)

    def connect_ex(self, address: Any) -> int:
        if not _is_loopback_address(address):
            raise RuntimeError("external network is disabled by the Y2S2 runner")
        return super().connect_ex(address)


def loopback_create_connection(address: Any, *args: Any, **kwargs: Any) -> Any:
    if not _is_loopback_address(address):
        raise RuntimeError("external network is disabled by the Y2S2 runner")
    return _ORIGINAL_CREATE_CONNECTION(address, *args, **kwargs)


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
    previous_adapter = os.environ.get("NOETIDE_Y2S2_ADAPTER")
    socket.socket, socket.create_connection = LoopbackOnlySocket, loopback_create_connection
    try:
        os.environ["NOETIDE_Y2S2_ADAPTER"] = args.adapter
        importlib.invalidate_caches()
        suite = unittest.defaultTestLoader.loadTestsFromName(TEST_MODULE)
        result = RecordingResult()
        suite.run(result)
    finally:
        socket.socket, socket.create_connection = _ORIGINAL_SOCKET, _ORIGINAL_CREATE_CONNECTION
        if previous_adapter is None:
            os.environ.pop("NOETIDE_Y2S2_ADAPTER", None)
        else:
            os.environ["NOETIDE_Y2S2_ADAPTER"] = previous_adapter
    rows = [{"test_id": item, **result.rows.get(item, {"individual_test_result": "errored", "detail": "scenario result missing"})} for item in required]
    passed = all(row["individual_test_result"] == "passed" for row in rows) and not result.errors and not result.failures
    artifact = {
        "schema_version": "noetide.y2s2-run-result.v1",
        "run_id": f"y2s2-{uuid.uuid4().hex}",
        "suite_id": manifest["suite_id"],
        "manifest_sha256": sha256_file(MANIFEST),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "applicability": "current",
        "environment": {"platform": platform.platform(), "python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "network": "loopback_only", "dependencies": "stdlib_only"},
        "command": ["python", "-m", "tests.runner.run_y2s2_suite", *sys.argv[1:]],
        "exit_code": 0 if passed else 1,
        "run_result": "passed" if passed else "failed",
        "required_results": rows,
        "bound_artifacts": artifacts
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{'passed' if passed else 'failed'}: {len(rows)} Y2S2 scenarios; artifact={output.relative_to(ROOT)}")
    return artifact["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())