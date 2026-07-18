"""Connector integration tests for MVP-C."""

from __future__ import annotations

import unittest

from noetide_micro.importer import SyntheticImporter


class ConnectorTests(unittest.TestCase):
    """Integration tests for synthetic data importer."""

    def setUp(self) -> None:
        self.importer = SyntheticImporter(None, {}, "2031-10-15T02:00:00Z")

    def test_connector_001_import_synthetic_text(self) -> None:
        """Synthetic text can be imported."""
        receipt = self.importer.import_text(
            "person_alpha and person_beta had a meeting.",
            "synthetic_meeting_001",
            ["person_alpha", "person_beta"],
        )
        self.assertEqual(receipt["status"], "stored")
        self.assertEqual(receipt["source_id"], "synthetic_meeting_001")
        self.assertEqual(receipt["hash_algorithm"], "sha256")

    def test_connector_002_reject_phone_number(self) -> None:
        """Real phone numbers are rejected."""
        with self.assertRaises(ValueError):
            self.importer.import_text(
                "Call me at 13800138000",
                "real_phone_001",
                ["person_alpha"],
            )

    def test_connector_003_reject_email(self) -> None:
        """Real email addresses are rejected."""
        with self.assertRaises(ValueError):
            self.importer.import_text(
                "Email me at test@example.com",
                "real_email_001",
                ["person_alpha"],
            )

    def test_connector_004_explicit_synthetic_marker(self) -> None:
        """Explicit [SYNTHETIC] marker is accepted."""
        receipt = self.importer.import_text(
            "[SYNTHETIC] This is a test scenario.",
            "synthetic_test_001",
            ["person_alpha"],
        )
        self.assertEqual(receipt["status"], "stored")

    def test_connector_005_receipt_has_required_fields(self) -> None:
        """Receipt contains all required fields per Ingestion Contract."""
        receipt = self.importer.import_text(
            "synthetic_event_001",
            "synthetic_event_001",
            ["person_alpha"],
        )
        required_fields = [
            "receipt_id", "source_id", "status", "hash_algorithm",
            "byte_length", "media_type", "ingested_at", "locator_scheme",
            "policy_profile_ref", "policy_resolution_status", "effective_policy",
            "actor",
        ]
        for field in required_fields:
            self.assertIn(field, receipt)


if __name__ == "__main__":
    unittest.main()
