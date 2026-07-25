"""Narrow tests for A6-TASK-002 alpha explainability support (synthetic only)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from noetide_micro import alpha_explainability as explain
from noetide_micro.portability import ContextPackError
from noetide_micro.runtime import open_runtime


class A6Task002ExplainabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp.name) / "data"
        runtime = open_runtime(self.data_dir)
        runtime.close()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_paths_descriptor_separates_synthetic_and_real(self) -> None:
        info = explain.paths_descriptor(self.data_dir, "a6_mvp_a_reference_v1")
        self.assertTrue(info["paths_discoverable"])
        self.assertTrue(info["synthetic_real_separated"])
        self.assertNotEqual(info["declared_data_root"], info["default_real_data_root"])
        self.assertEqual(info["synthetic_profile_id"], "a6_mvp_a_reference_v1")

    def test_backup_creates_verified_pack_with_checksum_manifest(self) -> None:
        destination = Path(self.temp.name) / "backup_pack"
        result = explain.create_reference_backup(self.data_dir, destination)
        self.assertTrue(result["backup_created"])
        self.assertTrue(result["manifest_verified"])
        self.assertTrue(result["roundtrip"]["roundtrip_verified"])
        self.assertFalse(result["roundtrip"]["store_mutated_by_verify"])
        self.assertGreater(result["entry_count"], 0)
        self.assertTrue((destination / "manifest.json").is_file())
        self.assertTrue((destination / "checksums.sha256").is_file())
        verified = explain.verify_backup_manifest(destination)
        self.assertTrue(verified["artifacts_present"])
        self.assertEqual(verified["pack_status"], "validated")
        self.assertTrue(verified["checksums_all_match"])

    def test_backup_refuses_existing_destination(self) -> None:
        destination = Path(self.temp.name) / "backup_pack"
        explain.create_reference_backup(self.data_dir, destination)
        with self.assertRaises(ContextPackError):
            explain.create_reference_backup(self.data_dir, destination)

    def test_export_roundtrip_is_stable_and_read_only(self) -> None:
        destination = Path(self.temp.name) / "export_pack"
        result = explain.export_roundtrip(self.data_dir, destination)
        self.assertEqual(result["first_status"], "validated")
        self.assertEqual(result["second_status"], "validated")
        self.assertTrue(result["roundtrip_stable"])
        self.assertTrue(result["revision_unchanged"])

    def test_uninstall_default_preserves_data_directory(self) -> None:
        info = explain.uninstall_info(self.data_dir)
        self.assertFalse(info["default_uninstall_deletes_data"])
        self.assertTrue(info["data_present"])
        self.assertTrue(info["deletion_requires_separate_confirmation"])
        self.assertTrue(info["backup_export_prompt_before_deletion"])
        self.assertTrue((self.data_dir / "noetide.sqlite3").exists())

    def test_deletion_requires_confirmation(self) -> None:
        result = explain.confirm_and_delete_data(self.data_dir, confirm=False)
        self.assertEqual(result, {"deleted": False, "reason": "confirmation_required"})
        self.assertTrue((self.data_dir / "noetide.sqlite3").exists())

    def test_deletion_requires_verified_backup(self) -> None:
        missing = explain.confirm_and_delete_data(self.data_dir, confirm=True)
        self.assertEqual(missing, {"deleted": False, "reason": "backup_required_before_deletion"})
        self.assertTrue((self.data_dir / "noetide.sqlite3").exists())
        bogus = Path(self.temp.name) / "not_a_pack"
        bogus.mkdir()
        (bogus / "manifest.json").write_text(json.dumps({"schema_version": "wrong"}), encoding="utf-8")
        unverified = explain.confirm_and_delete_data(self.data_dir, confirm=True, backup_path=bogus)
        self.assertEqual(unverified, {"deleted": False, "reason": "backup_not_verified"})
        self.assertTrue((self.data_dir / "noetide.sqlite3").exists())

    def test_deletion_succeeds_with_confirmation_and_verified_backup(self) -> None:
        backup = Path(self.temp.name) / "safe_pack"
        explain.create_reference_backup(self.data_dir, backup)
        result = explain.confirm_and_delete_data(self.data_dir, confirm=True, backup_path=backup)
        self.assertTrue(result["deleted"])
        self.assertFalse(self.data_dir.exists())
        self.assertTrue((backup / "manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
