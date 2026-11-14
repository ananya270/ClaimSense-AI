"""Comprehensive security and edge-case test suite for ClaimSense AI (Master Stabilization)."""

import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session
from backend.database.models import User
from backend.services.receipt import generate_claim_receipt_pdf
from backend.utils.validators import is_valid_magic_bytes, sanitize_and_resolve_path


class SecurityAndEdgeCaseTestCase(unittest.TestCase):
    """Test suite covering CSRF protection, CORS boundaries, rate limiting,

    production secrets enforcement, PDF XML escaping, and directory cleanup.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.upload_dir = Path(self.temp_dir.name) / "uploads"
        self.db_path = Path(self.temp_dir.name) / "test_sec.db"

    def tearDown(self):
        from backend.database.db import close_engine
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _get_base_test_config(self):
        temp_dir = self.temp_dir
        class SecTestConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = Path(temp_dir.name) / "uploads"
            DATABASE_PATH = Path(temp_dir.name) / "test_sec.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(Path(temp_dir.name) / 'test_sec.db').as_posix()}"
            SECRET_KEY = "test-security-secret-key-12345"
            CORS_ALLOWED_ORIGINS = "http://127.0.0.1:5000,http://localhost:5000"
        return SecTestConfig

    def test_production_startup_failure_with_insecure_secret(self):
        """Ensures that in production, startup is strictly refused if SECRET_KEY is weak or missing."""
        import importlib
        import backend.config

        # 1. Test with weak known secret
        with patch.dict(os.environ, {"FLASK_ENV": "production", "FLASK_DEBUG": "False", "SECRET_KEY": "changeme"}):
            with self.assertRaises(RuntimeError) as ctx:
                importlib.reload(backend.config)
            self.assertIn("CRITICAL SECURITY CONFIGURATION ERROR", str(ctx.exception))

        # 2. Test with missing/empty secret
        with patch.dict(os.environ, {"FLASK_ENV": "production", "FLASK_DEBUG": "False", "SECRET_KEY": ""}):
            with self.assertRaises(RuntimeError) as ctx2:
                importlib.reload(backend.config)
            self.assertIn("CRITICAL SECURITY CONFIGURATION ERROR", str(ctx2.exception))

        # 3. Reload back to normal test environment
        with patch.dict(os.environ, {"FLASK_ENV": "development", "FLASK_DEBUG": "True", "SECRET_KEY": "test-security-secret-key-12345"}):
            importlib.reload(backend.config)

    def test_cors_origin_restriction(self):
        """Ensures unauthorized origins are rejected and cannot read API responses."""
        app = create_app(self._get_base_test_config())
        client = app.test_client()

        # 1. Request with unauthorized origin
        res_evil = client.get("/api/health", headers={"Origin": "http://malicious-attacker.com"})
        self.assertEqual(res_evil.status_code, 200)
        # CORS header should NOT permit malicious-attacker.com
        allow_origin = res_evil.headers.get("Access-Control-Allow-Origin")
        self.assertNotEqual(allow_origin, "http://malicious-attacker.com")
        self.assertNotEqual(allow_origin, "*")

        # 2. Request with authorized origin
        res_valid = client.get("/api/health", headers={"Origin": "http://127.0.0.1:5000"})
        self.assertEqual(res_valid.status_code, 200)
        self.assertEqual(res_valid.headers.get("Access-Control-Allow-Origin"), "http://127.0.0.1:5000")

    def test_csrf_protection_when_enabled(self):
        """Ensures state-changing POST requests require a valid CSRF token when CSRF is enabled."""
        base_config = self._get_base_test_config()
        class CSRFConfig(base_config):
            ENABLE_CSRF_FOR_TESTS = True
            WTF_CSRF_ENABLED = True
            WTF_CSRF_CHECK_DEFAULT = True

        app = create_app(CSRFConfig)
        client = app.test_client()

        # 1. POST without CSRF token fails with 400
        res_missing = client.post(
            "/api/auth/signup",
            json={
                "full_name": "CSRF Victim",
                "username": "csrf_victim",
                "email": "csrf@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
        )
        self.assertEqual(res_missing.status_code, 400)
        self.assertIn("csrf", res_missing.get_json()["message"].lower())

        # 2. Retrieve valid token from CSRF token endpoint
        token_res = client.get("/api/auth/csrf-token")
        self.assertEqual(token_res.status_code, 200)
        csrf_token = token_res.get_json().get("csrf_token")
        self.assertTrue(csrf_token and len(csrf_token) > 10)

        # 3. POST with retrieved token header succeeds with 201
        res_valid = client.post(
            "/api/auth/signup",
            headers={"X-CSRFToken": csrf_token},
            json={
                "full_name": "CSRF Protected",
                "username": "csrf_protected",
                "email": "csrf_protected@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
        )
        self.assertEqual(res_valid.status_code, 201)

    def test_rate_limiting_enforcement(self):
        """Ensures rate limits throttle brute force attacks on authentication routes."""
        base_config = self._get_base_test_config()
        class RateLimitConfig(base_config):
            ENABLE_RATELIMIT_FOR_TESTS = True
            RATELIMIT_ENABLED = True

        app = create_app(RateLimitConfig)
        client = app.test_client()

        # Rate limit on /api/auth/login is set to 10 per minute
        last_status = None
        for i in range(12):
            res = client.post(
                "/api/auth/login",
                json={"identifier": f"brute_user_{i}", "password": "WrongPassword123"},
            )
            last_status = res.status_code
            if last_status == 429:
                break

        self.assertEqual(last_status, 429)

    def test_pdf_receipt_special_xml_characters_safety(self):
        """Ensures ReportLab PDF generation safely escapes XML characters (<, >, &, \", ') and long words."""
        malicious_claim_data = {
            "claim_id": "CLM-20261114-XSS0",
            "claimant_name": '<script>alert("XSS")</script> & Bob & "Alice"',
            "policy_number": 'POL<>&"TEST"123',
            "vehicle_number": "UP-14-<b>BOLD</b>",
            "accident_date": "2026-11-14",
            "claim_description": "Accident occurred with & symbols, <tags>, 'single' & \"double\" quotes. " + "A" * 80,
            "created_at": "2026-11-14T10:00:00Z",
            "files": {
                "policy_document": {"original_name": 'policy<safe>&"test.pdf', "saved_as": "doc1.pdf", "size_bytes": 1024},
                "claim_form": {"original_name": "form.pdf", "saved_as": "doc2.pdf", "size_bytes": 2048},
                "invoice_document": {"original_name": "bill.pdf", "saved_as": "doc3.pdf", "size_bytes": 4096},
                "vehicle_image": {"original_name": "photo.jpg", "saved_as": "img1.jpg", "size_bytes": 8192},
            },
        }

        # Must generate PDF without throwing xml.parsers.expat.ExpatError or ReportLab ParseError
        pdf_bytes = generate_claim_receipt_pdf(malicious_claim_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_db_transaction_failure_cleans_up_upload_directory(self):
        """Ensures partially uploaded claim files are completely cleaned up if DB commit fails."""
        app = create_app(self._get_base_test_config())
        client = app.test_client()

        # Seed and login user
        with get_db_session() as db:
            user = User(
                username="rollback_user",
                email="rollback@example.com",
                full_name="Rollback User",
                role="user",
            )
            user.set_password("RollbackPass123")
            db.add(user)

        client.post("/api/auth/login", json={"identifier": "rollback_user", "password": "RollbackPass123"})

        claim_data = {
            "claimant_name": "Rollback User",
            "policy_number": "POL-ROLLBACK-001",
            "vehicle_number": "DL-01-RB-9999",
            "accident_date": "2026-09-15",
            "claim_description": "Vehicle rollback accident test.",
            "policy_document": (io.BytesIO(b"%PDF-1.4 mock policy"), "policy.pdf"),
            "claim_form": (io.BytesIO(b"%PDF-1.4 mock claim form"), "claim_form.pdf"),
            "invoice_document": (io.BytesIO(b"%PDF-1.4 mock invoice"), "invoice.pdf"),
            "vehicle_image": (io.BytesIO(b"\xff\xd8\xff mock vehicle image"), "accident.jpg"),
        }

        # Mock database flush to simulate SQLite / DB error
        with patch("backend.routes.claims.get_db_session") as mock_db_ctx:
            mock_session = mock_db_ctx.return_value.__enter__.return_value
            mock_session.flush.side_effect = RuntimeError("Simulated Database Failure")

            res = client.post("/api/claims", data=claim_data, content_type="multipart/form-data")
            self.assertEqual(res.status_code, 500)
            self.assertFalse(res.get_json()["success"])

            # Verify no orphaned claim directory remains in upload folder
            upload_dir = app.config["UPLOAD_FOLDER"]
            subdirs = list(upload_dir.glob("CLM-*"))
            self.assertEqual(len(subdirs), 0, f"Orphaned claim directories found: {subdirs}")

    def test_path_traversal_sanitization(self):
        """Ensures path traversal attempts are detected and rejected."""
        base_dir = self.upload_dir
        base_dir.mkdir(parents=True, exist_ok=True)

        # Attempt to escape base directory
        with self.assertRaises(ValueError) as ctx:
            sanitize_and_resolve_path(base_dir, "../../etc/passwd")
        self.assertIn("traversal", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx2:
            sanitize_and_resolve_path(base_dir, "..\\..\\windows\\system32")
        self.assertIn("traversal", str(ctx2.exception).lower())

        # Valid subpath succeeds
        valid_path = sanitize_and_resolve_path(base_dir, "safe_folder/safe_file.txt")
        self.assertTrue(str(valid_path).startswith(str(base_dir.resolve())))

    def test_magic_byte_validator_functions(self):
        """Ensures magic byte signature inspection correctly validates and rejects files."""
        # PDF
        self.assertTrue(is_valid_magic_bytes(io.BytesIO(b"%PDF-1.7 text"), "pdf"))
        self.assertFalse(is_valid_magic_bytes(io.BytesIO(b"Not a PDF file"), "pdf"))

        # JPEG
        self.assertTrue(is_valid_magic_bytes(io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF"), "jpg"))
        self.assertTrue(is_valid_magic_bytes(io.BytesIO(b"\xff\xd8\xff\xe1..."), "jpeg"))
        self.assertFalse(is_valid_magic_bytes(io.BytesIO(b"GIF89a invalid"), "jpg"))

        # PNG
        self.assertTrue(is_valid_magic_bytes(io.BytesIO(b"\x89PNG\r\n\x1a\n"), "png"))
        self.assertFalse(is_valid_magic_bytes(io.BytesIO(b"%PDF invalid png"), "png"))

        # DOCX (ZIP archive header)
        self.assertTrue(is_valid_magic_bytes(io.BytesIO(b"PK\x03\x04\x14\x00"), "docx"))
        self.assertFalse(is_valid_magic_bytes(io.BytesIO(b"Plain text docx"), "docx"))


if __name__ == "__main__":
    unittest.main()
