from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro.folder_import import FolderImporter, ProfileRejectedError
from noetide_micro.store import SemanticStore


CLOCK = "2026-08-01T00:00:00+00:00"


def write_file(root: Path, relative: str, text: str, mtime: float = 1785000000.0) -> Path:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    import os
    os.utime(target, (mtime, mtime))
    return target


class FolderImporterCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "root"
        self.root.mkdir(parents=True)
        self.store = SemanticStore(Path(self._tmp.name) / "noetide.sqlite3")

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def importer(self) -> FolderImporter:
        return FolderImporter(self.store, CLOCK, language="zh")

    def test_stored_receipt_and_source_fields(self) -> None:
        write_file(self.root, "a.md", "hello\n")
        report = self.importer().import_folder(self.root)
        self.assertEqual(report["stored"], 1)
        self.assertEqual(report["files_seen"], 1)
        source_id = report["receipts"][0]["source_id"]
        source = self.store.seeded_source(source_id)
        self.assertIsNotNone(source)
        self.assertEqual(source["source_kind"], "folder_text_import")
        self.assertEqual(source["locator"]["relative_path"], "a.md")
        self.assertEqual(source["coverage_window"]["continuous"], True)
        self.assertEqual(source["ingested_at"], CLOCK)

    def test_duplicate_content_not_restored(self) -> None:
        write_file(self.root, "a.md", "same\n")
        write_file(self.root, "b.md", "same\n")
        report = self.importer().import_folder(self.root)
        self.assertEqual(report["stored"], 1)
        self.assertEqual(report["duplicate"], 1)
        self.assertEqual(len(self.store.source_hashes_by_kind("folder_text_import")), 1)

    def test_rescan_is_idempotent(self) -> None:
        write_file(self.root, "a.md", "x\n")
        self.importer().import_folder(self.root)
        second = self.importer().import_folder(self.root)
        self.assertEqual(second["stored"], 0)
        self.assertEqual(second["duplicate"], 1)

    def test_non_whitelist_extension_skipped(self) -> None:
        write_file(self.root, "a.md", "x\n")
        write_file(self.root, "b.exe", "MZ")
        report = self.importer().import_folder(self.root)
        self.assertEqual(report["skipped"], 1)
        self.assertEqual(report["skipped_paths"], ["b.exe"])
        self.assertEqual(report["stored"], 1)

    def test_invalid_utf8_rejected(self) -> None:
        write_file(self.root, "good.md", "ok\n")
        bad = self.root / "bad.md"
        bad.write_bytes(b"\xffinvalid")
        report = self.importer().import_folder(self.root)
        self.assertEqual(report["stored"], 1)
        self.assertEqual(report["rejected"], 1)
        self.assertEqual(report["rejections"][0]["failure"], "invalid_utf8")

    def test_report_deterministic_across_runs(self) -> None:
        write_file(self.root, "a.md", "1\n")
        write_file(self.root, "sub/b.txt", "2\n")
        with tempfile.TemporaryDirectory() as other:
            store_b = SemanticStore(Path(other) / "noetide.sqlite3")
            try:
                first = self.importer().import_folder(self.root)
                second = FolderImporter(store_b, CLOCK, language="zh").import_folder(self.root)
            finally:
                store_b.close()
        self.assertEqual(
            json.dumps(first, ensure_ascii=False, sort_keys=True),
            json.dumps(second, ensure_ascii=False, sort_keys=True),
        )

    def test_unknown_profile_fail_closed(self) -> None:
        with self.assertRaises(ProfileRejectedError):
            FolderImporter(self.store, CLOCK, profile="unknown_profile_v9")


class FolderWatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "root"
        self.root.mkdir(parents=True)
        self.store = SemanticStore(Path(self._tmp.name) / "noetide.sqlite3")

    def tearDown(self) -> None:
        self.store.close()
        self._tmp.cleanup()

    def test_poll_imports_only_new_files(self) -> None:
        from noetide_micro.folder_import import FolderWatcher
        write_file(self.root, "a.md", "1\n")
        watcher = FolderWatcher(FolderImporter(self.store, CLOCK))
        first = watcher.poll(self.root)
        self.assertEqual(first, {"stored": 1, "duplicate": 0})
        write_file(self.root, "b.md", "2\n")
        second = watcher.poll(self.root)
        self.assertEqual(second, {"stored": 1, "duplicate": 1})
        third = watcher.poll(self.root)
        self.assertEqual(third, {"stored": 0, "duplicate": 2})

    def test_interrupted_import_rerun_converges(self) -> None:
        from noetide_micro.folder_import import FolderWatcher
        write_file(self.root, "a.md", "1\n")
        write_file(self.root, "b.md", "2\n")
        write_file(self.root, "c.md", "3\n")

        def boom(index: int) -> None:
            if index == 1:
                raise RuntimeError("injected interruption")

        failing = FolderImporter(self.store, CLOCK, fail_hook=boom)
        with self.assertRaises(RuntimeError):
            failing.import_folder(self.root)
        self.assertEqual(len(self.store.source_hashes_by_kind("folder_text_import")), 1)
        report = FolderImporter(self.store, CLOCK).import_folder(self.root)
        self.assertEqual(report["stored"], 2)
        self.assertEqual(len(self.store.source_hashes_by_kind("folder_text_import")), 3)

    def test_poll_skips_non_whitelist_silently(self) -> None:
        from noetide_micro.folder_import import FolderWatcher
        write_file(self.root, "a.md", "1\n")
        write_file(self.root, "skip.bin", "x")
        watcher = FolderWatcher(FolderImporter(self.store, CLOCK))
        self.assertEqual(watcher.poll(self.root), {"stored": 1, "duplicate": 0})


if __name__ == "__main__":
    unittest.main()
