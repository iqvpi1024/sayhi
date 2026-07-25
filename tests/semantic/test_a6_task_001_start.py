from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import start

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class A6Task001StartTests(unittest.TestCase):
    def test_clean_start_initializes_declared_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dev"
            self.assertEqual(start.run(["--data-root", str(root)]), 0)
            self.assertTrue((root / "noetide.sqlite3").is_file())
            from noetide_micro.runtime import open_runtime
            runtime = open_runtime(root)
            try:
                self.assertEqual(runtime.revision(), "rev_010")
                pragmas = runtime._store.pragma_values()
            finally:
                runtime.close()
            self.assertEqual(pragmas["foreign_keys"], 1)
            self.assertEqual(pragmas["journal_mode"].lower(), "delete")
            self.assertEqual(pragmas["synchronous"], 2)

    def test_corrupt_database_refuses_start_and_leaves_file_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dev"
            root.mkdir(parents=True)
            db = root / "noetide.sqlite3"
            payload = b"definitely not a sqlite database payload"
            db.write_bytes(payload)
            self.assertEqual(start.run(["--data-root", str(root)]), start.EXIT_DATABASE_CORRUPT)
            self.assertEqual(db.read_bytes(), payload)

    def test_unusable_data_root_fails_without_writing_elsewhere(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "blocker"
            blocker.write_text("occupied", encoding="utf-8")
            target = blocker / "child"
            self.assertEqual(start.run(["--data-root", str(target)]), start.EXIT_DATA_ROOT_UNUSABLE)
            self.assertFalse(target.exists())
            self.assertEqual(blocker.read_text(encoding="utf-8"), "occupied")

    def test_clean_removes_only_default_devdata_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            default_root = Path(tmp) / "devdata"
            default_root.mkdir(parents=True)
            (default_root / "noetide.sqlite3").write_bytes(b"synthetic")
            original = start.DEFAULT_DEV_ROOT
            start.DEFAULT_DEV_ROOT = default_root
            try:
                self.assertEqual(start.run(["--clean"]), 0)
                self.assertFalse(default_root.exists())
            finally:
                start.DEFAULT_DEV_ROOT = original

    def test_clean_refuses_paths_outside_default_devdata_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "keepme"
            outside.mkdir(parents=True)
            (outside / "data.bin").write_bytes(b"important")
            default_root = Path(tmp) / "devdata"
            original = start.DEFAULT_DEV_ROOT
            start.DEFAULT_DEV_ROOT = default_root
            try:
                self.assertEqual(start.run(["--data-root", str(outside), "--clean"]), start.EXIT_CLEAN_REFUSED)
            finally:
                start.DEFAULT_DEV_ROOT = original
            self.assertTrue((outside / "data.bin").is_file())

    def test_runtime_check_accepts_supported_python(self) -> None:
        self.assertTrue(start.check_runtime())


if __name__ == "__main__":
    unittest.main()
