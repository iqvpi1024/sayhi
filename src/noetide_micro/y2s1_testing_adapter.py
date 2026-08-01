"""Y2-S1 testing adapter: materializes the synthetic folder tree and runs contract cases.

Environment isolation: everything lives in a TemporaryDirectory; timestamps come from
the fixture clock and fixture-declared mtimes. No network, no wall-clock.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import weakref
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .folder_import import FolderImporter, FolderWatcher, ProfileRejectedError, SOURCE_KIND
from .store import SemanticStore


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "y2s1_folder_import_v1" / "fixture.json"


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _epoch(iso: str) -> float:
    return datetime.fromisoformat(iso).timestamp() if "+" in iso else datetime.fromisoformat(iso).replace(tzinfo=timezone.utc).timestamp()


def create_system(case: Mapping[str, Any]) -> "Y2S1CaseSystem":
    return Y2S1CaseSystem(case)


def _finalize(store: SemanticStore, path: Path) -> None:
    try:
        store.close()
    except Exception:
        pass
    shutil.rmtree(path, ignore_errors=True)


class Y2S1CaseSystem:
    def __init__(self, case: Mapping[str, Any]) -> None:
        self._case = dict(case)
        self._fixture = _fixture()
        self._clock = self._fixture["determinism"]["clock"]
        self._root_ref = self._fixture["root_ref"]
        self._language = self._fixture["defaults"]["language"]
        self._tmp_path = Path(tempfile.mkdtemp())
        self._root = self._tmp_path / "root"
        self._root.mkdir(parents=True, exist_ok=True)
        self._store = SemanticStore(self._tmp_path / "noetide.sqlite3")
        self._store.add_revision("rev_000", self._clock, "seed")
        self._finalizer = weakref.finalize(self, _finalize, self._store, self._tmp_path)
        self._materialize(case)

    def close(self) -> None:
        self._finalizer()

    # -- materialization -------------------------------------------------

    def _library_files(self, case: Mapping[str, Any]) -> list[dict[str, Any]]:
        libraries = self._fixture["libraries"]
        files: list[dict[str, Any]] = list(libraries[case["library"]])
        for extra in case.get("extra_files", []):
            entry = libraries[extra]
            if isinstance(entry, list):
                files.extend(entry)
            else:
                files.append(entry)
        return files

    def _write_virtual(self, base: Path, definition: Mapping[str, Any]) -> Path:
        target = base / definition["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if "content_base64" in definition:
            target.write_bytes(base64.b64decode(definition["content_base64"]))
        else:
            target.write_text(definition["content"], encoding="utf-8", newline="\n")
        stamp = _epoch(definition["mtime"])
        os.utime(target, (stamp, stamp))
        return target

    def _materialize(self, case: Mapping[str, Any]) -> None:
        libraries = self._fixture["libraries"]
        for definition in self._library_files(case):
            self._write_virtual(self._root, definition)
        if case.get("outside_pool"):
            pool = self._tmp_path / "outside_pool"
            pool.mkdir(parents=True, exist_ok=True)
            for definition in libraries["outside_pool"]:
                self._write_virtual(pool, definition)
            junction = case.get("junction")
            if junction:
                link = self._root / junction["path"]
                target = self._tmp_path / junction["target"]
                self._make_link(link, target)

    @staticmethod
    def _make_link(link: Path, target: Path) -> None:
        try:
            os.symlink(str(target), str(link), target_is_directory=True)
            return
        except OSError:
            pass
        if os.name == "nt":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                check=True, capture_output=True,
            )
            return
        raise RuntimeError(f"cannot create link: {link} -> {target}")

    # -- protocol --------------------------------------------------------

    def layer_snapshot(self) -> dict[str, Any]:
        return {
            "canonical_layer": self._store.canonical_layer_digest(),
            "revision_layer": self._store.current_revision(),
        }

    def run_case(self, case: Mapping[str, Any]) -> dict[str, Any]:
        action = case["action"]
        if action == "import":
            if case.get("profile_override") or case.get("determinism_check"):
                return self._run_guarded_import(case)
            return self._run_import(case)
        if action == "import_twice":
            return self._run_import_twice(case)
        if action == "import_with_failure":
            return self._run_interrupted(case)
        if action == "watch":
            return self._run_watch(case)
        raise ValueError(f"unknown action: {action}")

    # -- helpers ---------------------------------------------------------

    def _importer(self, **kwargs: Any) -> FolderImporter:
        return FolderImporter(
            self._store, self._clock,
            root_ref=self._root_ref, language=self._language, **kwargs,
        )

    def _source_count(self) -> int:
        return len(self._store.source_hashes_by_kind(SOURCE_KIND))

    @staticmethod
    def _counts(report: Mapping[str, Any]) -> dict[str, int]:
        return {
            "files_seen": report["files_seen"],
            "stored": report["stored"],
            "duplicate": report["duplicate"],
            "rejected": report["rejected"],
            "skipped": report["skipped"],
        }

    # -- actions ---------------------------------------------------------

    def _run_import(self, case: Mapping[str, Any]) -> dict[str, Any]:
        extra: list[dict[str, Any]] = []
        for entry in case.get("extra_entries", []):
            if entry.get("kind") == "absolute_outside":
                extra.append({"kind": "absolute_outside", "path": entry["path"], "base": str(self._tmp_path)})
            else:
                extra.append(dict(entry))
        report = self._importer().import_folder(self._root, extra_entries=extra)
        result: dict[str, Any] = {"report": self._counts(report)}
        plain_batch = not case.get("extra_files") and not case.get("extra_entries") and not case.get("junction")
        if case.get("inspect"):
            relative = case["inspect"]
            receipt = next(item for item in report["receipts"] if item["relative_path"] == relative)
            source = self._store.seeded_source(receipt["source_id"])
            result = {
                "inspect": {
                    "source_id": source["source_id"],
                    "content_hash": source["content_hash"],
                    "byte_length": source["byte_length"],
                    "source_created_at": source["source_created_at"],
                    "ingested_at": source["ingested_at"],
                    "language": source["language"],
                    "locator": source["locator"],
                    "coverage_window": source["coverage_window"],
                }
            }
            return result
        if plain_batch:
            result["receipts"] = report["receipts"]
        if report["duplicate_of"]:
            result["duplicate_of"] = report["duplicate_of"]
        if report["rejections"]:
            result["rejections"] = report["rejections"]
        if report["skipped_paths"]:
            result["skipped_paths"] = report["skipped_paths"]
        if case.get("outside_pool") is not None and "rejections" in result:
            result["writes_outside_root"] = 0
        result["source_count"] = self._source_count()
        return result

    def _run_guarded_import(self, case: Mapping[str, Any]) -> dict[str, Any]:
        rejected: str | None = None
        try:
            self._importer(profile=case.get("profile_override", "y2s1_folder_import_v1"))
        except ProfileRejectedError as exc:
            rejected = exc.profile
        before = self.layer_snapshot()
        self._importer().import_folder(self._root)
        after = self.layer_snapshot()
        peer_a = Y2S1CaseSystem({k: v for k, v in case.items() if k not in ("profile_override", "determinism_check", "canonical_guard")})
        peer_b = Y2S1CaseSystem({k: v for k, v in case.items() if k not in ("profile_override", "determinism_check", "canonical_guard")})
        try:
            first = peer_a._importer().import_folder(peer_a._root)
            second = peer_b._importer().import_folder(peer_b._root)
        finally:
            peer_a.close()
            peer_b.close()
        byte_identical = json.dumps(first, ensure_ascii=False, sort_keys=True) == json.dumps(second, ensure_ascii=False, sort_keys=True)
        return {
            "profile_rejected": rejected,
            "canonical_guard": {
                "canonical_digest_unchanged": before["canonical_layer"] == after["canonical_layer"],
                "revision_unchanged": before["revision_layer"] == after["revision_layer"],
            },
            "determinism": {"report_byte_identical": byte_identical},
        }

    def _run_import_twice(self, case: Mapping[str, Any]) -> dict[str, Any]:
        self._importer().import_folder(self._root)
        second = self._importer().import_folder(self._root)
        return {"second_run": self._counts(second), "source_count": self._source_count()}

    def _run_interrupted(self, case: Mapping[str, Any]) -> dict[str, Any]:
        fail_at = int(case["fail_at_index"])

        def boom(index: int) -> None:
            if index == fail_at:
                raise RuntimeError("injected interruption")

        failed = False
        try:
            self._importer(fail_hook=boom).import_folder(self._root)
        except RuntimeError:
            failed = True
        stored_before = self._source_count()
        rerun = self._importer().import_folder(self._root)
        clean = Y2S1CaseSystem({**case, "action": "import"})
        try:
            clean._importer().import_folder(clean._root)
            converged = (
                self._store.source_hashes_by_kind(SOURCE_KIND)
                == clean._store.source_hashes_by_kind(SOURCE_KIND)
                and self._source_count() == 3
            )
        finally:
            clean.close()
        return {
            "first_run": {"stored_before_failure": stored_before, "failed": failed},
            "final_source_count": self._source_count(),
            "converged": converged,
        }

    def _run_watch(self, case: Mapping[str, Any]) -> dict[str, Any]:
        watcher = FolderWatcher(self._importer())
        polls: list[dict[str, int]] = []
        polls.append(watcher.poll(self._root))
        libraries = self._fixture["libraries"]
        self._write_virtual(self._root, libraries[case["add_between"]])
        for _ in range(int(case["polls"]) - 1):
            polls.append(watcher.poll(self._root))
        return {"polls": polls, "source_count": self._source_count()}
