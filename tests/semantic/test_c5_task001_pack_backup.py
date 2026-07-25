"""Narrow C5-TASK-001 checks for the pack_backup module."""

from __future__ import annotations

import shutil
import sys
import tempfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from noetide_micro import pack_backup
from noetide_micro.store import SemanticStore


CLOCK = "2026-07-26T00:00:00+00:00"
KEY = "c5-synthetic-backup-key-v1"


class PackBackupTask001Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="c5_task001_")
        self.addCleanup(shutil.rmtree, self._tmpdir, True)
        self.db_path = Path(self._tmpdir) / "c5.sqlite3"
        self.store = SemanticStore(self.db_path)
        self.store.add_revision("rev_c5_task001", CLOCK, "seed")
        self.store.add_canonical_object("EP1", {"object_type": "episode", "object_revision": "rev_c5_task001", "occurred_on": "2026-07-10"})

    def test_export_and_deterministic_markdown(self) -> None:
        first = Path(self._tmpdir) / "pack1"
        second = Path(self._tmpdir) / "pack2"
        self.assertEqual(pack_backup.export_markdown_pack(self.store, first, CLOCK)["outcome"], "exported")
        self.assertEqual(pack_backup.export_markdown_pack(self.store, second, CLOCK)["outcome"], "exported")
        for name in pack_backup._MARKDOWN_FILES:
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
        self.assertIn("# Canonical Objects", (first / "markdown/canonical.md").read_text(encoding="utf-8"))
        self.assertEqual(pack_backup.export_markdown_pack(self.store, first, CLOCK)["outcome"], "rejected")

    def test_verify_and_tamper_fail_closed(self) -> None:
        pack = Path(self._tmpdir) / "pack"
        pack_backup.export_markdown_pack(self.store, pack, CLOCK)
        self.assertEqual(pack_backup.verify_pack(pack)["status"], "validated")
        target = pack / "canonical.json"
        target.write_bytes(target.read_bytes() + b"tamper")
        self.assertEqual(pack_backup.verify_pack(pack)["status"], "rejected_hash_mismatch")

    def test_unknown_and_missing_files_fail_closed(self) -> None:
        pack = Path(self._tmpdir) / "pack"
        pack_backup.export_markdown_pack(self.store, pack, CLOCK)
        (pack / "unknown.txt").write_text("x", encoding="utf-8")
        self.assertEqual(pack_backup.verify_pack(pack)["status"], "rejected_unknown_file")
        (pack / "unknown.txt").unlink()
        (pack / "markdown/ledger.md").unlink()
        self.assertEqual(pack_backup.verify_pack(pack)["status"], "rejected_hash_mismatch")

    def test_backup_restore_roundtrip_and_wrong_key(self) -> None:
        backup = Path(self._tmpdir) / "b.nobak"
        result = pack_backup.create_backup(self.db_path, KEY, backup, CLOCK)
        self.assertEqual(result["outcome"], "created")
        self.assertNotEqual(backup.read_bytes(), self.db_path.read_bytes())
        self.assertEqual(result["receipt"]["encryption"], "stdlib_deterministic_v1")
        restored = Path(self._tmpdir) / "restored.sqlite3"
        outcome = pack_backup.restore_backup(backup, KEY, restored)
        self.assertEqual(outcome["outcome"], "restored")
        self.assertEqual(restored.read_bytes(), self.db_path.read_bytes())
        wrong = Path(self._tmpdir) / "wrong.sqlite3"
        self.assertEqual(pack_backup.restore_backup(backup, "wrong-key", wrong)["outcome"], "rejected")
        self.assertFalse(wrong.exists())
        self.assertEqual(pack_backup.restore_backup(backup, KEY, restored)["outcome"], "rejected")

    def test_deletion_receipt_honesty(self) -> None:
        receipt = pack_backup.build_deletion_receipt("obj1", CLOCK, {"backup": "pending_expiry", "export_copy": "out_of_control"})
        self.assertEqual(len(receipt["components"]), 8)
        self.assertEqual(receipt["components"]["backup"], "pending_expiry")
        self.assertEqual(receipt["components"]["export_copy"], "out_of_control")
        self.assertEqual(receipt["overall"], "deleted")
        failed = pack_backup.build_deletion_receipt("obj1", CLOCK, {}, fail_component="cache")
        self.assertEqual(failed["components"]["cache"], "failed")
        self.assertEqual(failed["overall"], "partial_failure")
        self.assertFalse(failed["claimed_deleted"])


if __name__ == "__main__":
    unittest.main()
