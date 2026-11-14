"""Unit and integration tests for Phase 3 Authentication endpoints."""
import json
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session
from backend.database.models import User


class AuthenticationTestCase(unittest.TestCase):
    """Test suite for user registration, authentication, session lifecycle, and security."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_auth.db"

        class TestConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = Path(self.temp_dir.name) / "uploads"
            DATABASE_PATH = Path(self.temp_dir.name) / "test_auth.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(Path(self.temp_dir.name) / 'test_auth.db').as_posix()}"
            SECRET_KEY = "test-secret-key-12345"

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        from backend.database.db import close_engine
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _signup_user(self, full_name="Ansh Gupta", username="ansh_g", email="ansh@abes.ac.in", password="Password@123", confirm=None):
        if confirm is None:
            confirm = password
        return self.client.post(
            "/api/auth/signup",
            json={
                "full_name": full_name,
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirm,
            },
        )

    def test_successful_signup(self):
        """Ensures a new user can register successfully."""
        response = self._signup_user()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("message"), "Account created successfully")

        # Verify password is encrypted in database
        with get_db_session() as db:
            user = db.query(User).filter_by(username="ansh_g").first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, "Password@123")
            self.assertTrue(user.check_password("Password@123"))

    def test_duplicate_username_rejected(self):
        """Ensures duplicate username returns 409 Conflict."""
        self._signup_user(username="duplicate_user", email="user1@example.com")
        res = self._signup_user(username="duplicate_user", email="user2@example.com")
        self.assertEqual(res.status_code, 409)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("already taken", data["message"])

    def test_duplicate_email_rejected(self):
        """Ensures duplicate email returns 409 Conflict."""
        self._signup_user(username="user1", email="shared@example.com")
        res = self._signup_user(username="user2", email="shared@example.com")
        self.assertEqual(res.status_code, 409)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("already registered", data["message"])

    def test_invalid_email_format_rejected(self):
        """Ensures malformed email returns 400 Bad Request."""
        res = self._signup_user(email="notanemail")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Invalid email format", data["message"])

    def test_password_mismatch_rejected(self):
        """Ensures mismatched confirmation password returns 400."""
        res = self._signup_user(password="Pass1234", confirm="DifferentPass")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("do not match", data["message"])

    def test_short_password_rejected(self):
        """Ensures password shorter than 8 characters returns 400."""
        res = self._signup_user(password="123", confirm="123")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("at least 8 characters", data["message"])

    def test_successful_login_with_username_and_email(self):
        """Ensures user can log in with both username and email, receiving safe user payload."""
        self._signup_user(username="john_doe", email="john@example.com", password="SecretPassword123")

        # 1. Login with username
        res1 = self.client.post(
            "/api/auth/login",
            json={"identifier": "john_doe", "password": "SecretPassword123"},
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1["success"])
        self.assertEqual(data1["user"]["username"], "john_doe")
        self.assertNotIn("password", data1["user"])
        self.assertNotIn("password_hash", data1["user"])

        # 2. Login with email
        res2 = self.client.post(
            "/api/auth/login",
            json={"identifier": "john@example.com", "password": "SecretPassword123"},
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2["success"])
        self.assertEqual(data2["user"]["email"], "john@example.com")

    def test_invalid_login_rejected(self):
        """Ensures invalid password or nonexistent user returns 401."""
        self._signup_user(username="valid_user", password="CorrectPassword123")

        # Wrong password
        res1 = self.client.post(
            "/api/auth/login",
            json={"identifier": "valid_user", "password": "WrongPassword123"},
        )
        self.assertEqual(res1.status_code, 401)
        self.assertFalse(res1.get_json()["success"])

        # Nonexistent user
        res2 = self.client.post(
            "/api/auth/login",
            json={"identifier": "ghost_user", "password": "CorrectPassword"},
        )
        self.assertEqual(res2.status_code, 401)
        self.assertFalse(res2.get_json()["success"])

    def test_me_and_logout_lifecycle(self):
        """Ensures /api/auth/me tracks active session and logout invalidates session."""
        self._signup_user(username="session_user", password="Password123")

        # Unauthenticated /me
        res_anon = self.client.get("/api/auth/me")
        self.assertEqual(res_anon.status_code, 401)

        # Log in
        self.client.post(
            "/api/auth/login",
            json={"identifier": "session_user", "password": "Password123"},
        )

        # Authenticated /me
        res_me = self.client.get("/api/auth/me")
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.get_json()["user"]["username"], "session_user")

        # Logout
        res_logout = self.client.post("/api/auth/logout")
        self.assertEqual(res_logout.status_code, 200)

        # /me after logout should now fail
        res_post_logout = self.client.get("/api/auth/me")
        self.assertEqual(res_post_logout.status_code, 401)

    def test_inactive_user_enforcement(self):
        """Ensures inactive / disabled users cannot log in or perform authenticated actions."""
        self._signup_user(username="disabled_user", password="Password123")

        # Manually deactivate user in DB
        with get_db_session() as db:
            user = db.query(User).filter_by(username="disabled_user").first()
            user.is_active = False
            db.flush()

        # Login attempt fails with 403
        login_res = self.client.post(
            "/api/auth/login",
            json={"identifier": "disabled_user", "password": "Password123"},
        )
        self.assertEqual(login_res.status_code, 403)
        self.assertIn("inactive", login_res.get_json()["message"].lower())

    def test_password_complexity_rules(self):
        """Ensures passwords require letters, numbers, and minimum 8 characters."""
        # Only numbers
        res_num = self._signup_user(username="u_num", password="12345678", confirm="12345678")
        self.assertEqual(res_num.status_code, 400)
        self.assertIn("both letters and numbers", res_num.get_json()["message"])

        # Only letters
        res_alpha = self._signup_user(username="u_alpha", password="abcdefghij", confirm="abcdefghij")
        self.assertEqual(res_alpha.status_code, 400)
        self.assertIn("both letters and numbers", res_alpha.get_json()["message"])


if __name__ == "__main__":
    unittest.main()
