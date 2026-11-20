"""Unit and integration validation tests for the Phase 10 Stage 2 Load Testing Framework."""

import tempfile
import unittest
from pathlib import Path
from sqlalchemy import text

from backend.database.db import get_engine, close_engine, get_db_session
from backend.database.models import User, Claim
from tests.load.config import (
    PROFILES,
    SLA_TARGETS,
    TEST_USERS,
    ASSESSOR_USER,
    PRESEEDED_POLICIES,
    MINIMAL_VALID_PDF_BYTES,
    MINIMAL_VALID_JPEG_BYTES,
    generate_claim_payload,
)
from tests.load.server import seed_test_database, make_load_test_app


class LoadTestingValidationTestCase(unittest.TestCase):
    """Verifies load testing configuration, fixtures, seeding, and server factory isolation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.isolated_path = Path(self.temp_dir.name)

    def tearDown(self):
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_load_config_and_sla_definitions(self):
        """Validates that all required concurrency profiles and SLAs are defined."""
        self.assertIn("10_users", PROFILES)
        self.assertIn("25_users", PROFILES)
        self.assertIn("50_users", PROFILES)

        self.assertEqual(PROFILES["10_users"]["users"], 10)
        self.assertEqual(PROFILES["25_users"]["users"], 25)
        self.assertEqual(PROFILES["50_users"]["users"], 50)

        # SLA targets
        self.assertLessEqual(SLA_TARGETS["max_mean_latency_ms"], 500.0)
        self.assertLessEqual(SLA_TARGETS["max_error_rate_pct"], 0.1)
        self.assertTrue(SLA_TARGETS["zero_data_corruption"])

    def test_02_synthetic_binary_fixtures(self):
        """Verifies synthetic PDF and JPEG binary signatures for multipart submission."""
        self.assertTrue(MINIMAL_VALID_PDF_BYTES.startswith(b"%PDF-"))
        self.assertTrue(b"%%EOF" in MINIMAL_VALID_PDF_BYTES)

        self.assertTrue(MINIMAL_VALID_JPEG_BYTES.startswith(b"\xFF\xD8"))
        self.assertTrue(MINIMAL_VALID_JPEG_BYTES.endswith(b"\xFF\xD9"))

    def test_03_claim_payload_generator(self):
        """Verifies deterministic claim payload generation across users."""
        payload_1 = generate_claim_payload(1, 1)
        payload_2 = generate_claim_payload(2, 2)

        self.assertIn("claimant_name", payload_1)
        self.assertIn("policy_number", payload_1)
        self.assertIn("vehicle_number", payload_1)
        self.assertIn("accident_date", payload_1)
        self.assertIn("claim_description", payload_1)

        self.assertNotEqual(payload_1["claimant_name"], payload_2["claimant_name"])
        self.assertNotEqual(payload_1["vehicle_number"], payload_2["vehicle_number"])

    def test_04_isolated_database_seeding(self):
        """Ensures seed_test_database populates 50 users, 1 assessor, and 10 claims without touching prod."""
        db_path = self.isolated_path / "test_seed.db"
        seed_test_database(db_path, enable_wal=False)

        with get_db_session() as db:
            user_count = db.query(User).count()
            claim_count = db.query(Claim).count()

            # 50 simulated users + 1 assessor = 51 users
            self.assertEqual(user_count, 51)
            # 10 pre-seeded claims
            self.assertEqual(claim_count, 10)

            # Check that passwords are encrypted
            u1 = db.query(User).filter_by(username="load_user_01").first()
            self.assertIsNotNone(u1)
            self.assertTrue(u1.check_password("LoadTestPassword123!"))
            self.assertFalse(u1.check_password("WrongPassword"))

    def test_05_load_test_app_factory_and_journal_mode(self):
        """Verifies make_load_test_app creates an isolated Flask app with ping route and journal controls."""
        app = make_load_test_app(self.isolated_path, enable_wal=True)
        client = app.test_client()

        ping_res = client.get("/api/load-test/ping")
        self.assertEqual(ping_res.status_code, 200)
        data = ping_res.get_json()
        self.assertEqual(data["status"], "ready")
        self.assertEqual(data["journal_mode"], "wal")
        self.assertEqual(data["busy_timeout"], 5000)

        # Check CSRF route is available
        csrf_res = client.get("/api/auth/csrf-token")
        self.assertEqual(csrf_res.status_code, 200)
        csrf_data = csrf_res.get_json()
        self.assertTrue(csrf_data["success"])
        self.assertIn("csrf_token", csrf_data)


if __name__ == "__main__":
    unittest.main()
