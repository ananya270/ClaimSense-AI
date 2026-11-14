"""Unit and integration tests for Claim Ownership, Access Control, Policy Lookup, and PDF Receipt generation."""
import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session
from backend.database.models import User, Claim


class ClaimOwnershipAndReceiptTestCase(unittest.TestCase):
    """Test suite for claim access boundaries, policy number searching, and PDF receipt emission."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        class TestConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = Path(self.temp_dir.name) / "uploads"
            DATABASE_PATH = Path(self.temp_dir.name) / "test_claims.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(Path(self.temp_dir.name) / 'test_claims.db').as_posix()}"
            SECRET_KEY = "ownership-test-secret"

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        from backend.database.db import close_engine
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _create_user(self, username, email, role="user"):
        """Helper to create and return a registered user."""
        with get_db_session() as db:
            user = User(
                username=username,
                email=email,
                full_name=f"{username.capitalize()} FullName",
                role=role,
            )
            user.set_password("Secret123")
            db.add(user)
            db.flush()
            return user.id

    def _login(self, client, identifier, password="Secret123"):
        """Helper to log in with a test client session."""
        return client.post("/api/auth/login", json={"identifier": identifier, "password": password})

    def _submit_claim(self, client, policy_number="POL-112233"):
        """Helper to submit a claim with mock files."""
        data = {
            "claimant_name": "Test Claimant",
            "policy_number": policy_number,
            "vehicle_number": "UP-16-AB-5678",
            "accident_date": "2026-09-20",
            "claim_description": "Rear bumper dent while parking.",
            "policy_document": (io.BytesIO(b"%PDF-1.4 Mock policy schedule"), "policy.pdf"),
            "claim_form": (io.BytesIO(b"%PDF-1.4 Mock claim form"), "form.pdf"),
            "invoice_document": (io.BytesIO(b"%PDF-1.4 Mock invoice"), "bill.pdf"),
            "vehicle_image": (io.BytesIO(b"\xff\xd8\xff Mock vehicle damage photo"), "bumper.jpg"),
        }
        res = client.post("/api/claims", data=data, content_type="multipart/form-data")
        return res

    def test_authenticated_submission_assigns_owner(self):
        """Ensures that submitting while logged in assigns user_id to claim."""
        self._create_user("user_a", "usera@example.com")
        self._login(self.client, "user_a")

        res = self._submit_claim(self.client, "POL-USERA-01")
        self.assertEqual(res.status_code, 201)
        claim_id = res.get_json()["claim_id"]

        with get_db_session() as db:
            claim = db.query(Claim).filter_by(claim_id=claim_id).first()
            self.assertIsNotNone(claim)
            self.assertIsNotNone(claim.user_id)
            self.assertEqual(claim.user.username, "user_a")

    def test_claim_access_boundaries(self):
        """Ensures user B cannot access user A's private claim, and unauthenticated access is rejected."""
        self._create_user("owner_user", "owner@example.com")
        self._create_user("other_user", "other@example.com")

        # 1. Submit claim as owner_user
        client_owner = self.app.test_client()
        self._login(client_owner, "owner_user")
        sub_res = self._submit_claim(client_owner, "POL-PRIVATE-1")
        claim_id = sub_res.get_json()["claim_id"]

        # Owner can access own claim
        get_res_owner = client_owner.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res_owner.status_code, 200)

        # 2. Other user tries to access -> 403 Forbidden
        client_other = self.app.test_client()
        self._login(client_other, "other_user")
        get_res_other = client_other.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res_other.status_code, 403)
        self.assertIn("permission", get_res_other.get_json()["message"])

        # 3. Unauthenticated access -> 401 Unauthorized
        client_anon = self.app.test_client()
        get_res_anon = client_anon.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res_anon.status_code, 401)

        # 4. Assessor can access user A's claim -> 200 OK
        self._create_user("assessor_boundary", "assessor_b@example.com", role="assessor")
        client_assessor = self.app.test_client()
        self._login(client_assessor, "assessor_boundary")
        get_res_assessor = client_assessor.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res_assessor.status_code, 200)

        # 5. Admin can access user A's claim -> 200 OK
        self._create_user("admin_boundary", "admin_b@example.com", role="admin")
        client_admin = self.app.test_client()
        self._login(client_admin, "admin_boundary")
        get_res_admin = client_admin.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res_admin.status_code, 200)

    def test_legacy_unowned_claim_protection(self):
        """Ensures legacy unowned claims are hidden from regular users but visible to assessors/admins."""
        with get_db_session() as db:
            legacy_claim = Claim(
                claim_id="CLM-20260101-LG01",
                user_id=None,
                claimant_name="Legacy Claimant",
                policy_number="POL-LEGACY-001",
                vehicle_number="DL-01-XX-0001",
                accident_date="2026-01-01",
                claim_description="Legacy claim without user_id",
                status="SUBMITTED",
            )
            db.add(legacy_claim)

        # Regular user gets 403 Forbidden
        self._create_user("regular_user", "regular@example.com", role="user")
        client_reg = self.app.test_client()
        self._login(client_reg, "regular_user")
        res_reg = client_reg.get("/api/claims/CLM-20260101-LG01")
        self.assertEqual(res_reg.status_code, 403)

        # Assessor gets 200 OK
        self._create_user("assessor_legacy", "assessor_leg@example.com", role="assessor")
        client_assessor = self.app.test_client()
        self._login(client_assessor, "assessor_legacy")
        res_assessor = client_assessor.get("/api/claims/CLM-20260101-LG01")
        self.assertEqual(res_assessor.status_code, 200)

        # Admin gets 200 OK
        self._create_user("admin_legacy", "admin_leg@example.com", role="admin")
        client_admin = self.app.test_client()
        self._login(client_admin, "admin_legacy")
        res_admin = client_admin.get("/api/claims/CLM-20260101-LG01")
        self.assertEqual(res_admin.status_code, 200)

    def test_policy_number_search(self):
        """Ensures searching by policy number returns authorized claims and requires authentication."""
        self._create_user("policy_holder", "ph@example.com")
        self._create_user("assessor_user", "assessor@example.com", role="assessor")

        client_user = self.app.test_client()
        self._login(client_user, "policy_holder")

        # Submit two claims under same policy
        self._submit_claim(client_user, "POL-MULTI-888")
        self._submit_claim(client_user, "POL-MULTI-888")

        # Unauthenticated search fails with 401
        anon_client = self.app.test_client()
        anon_res = anon_client.get("/api/claims/policy/POL-MULTI-888")
        self.assertEqual(anon_res.status_code, 401)

        # Authenticated search returns both claims
        search_res = client_user.get("/api/claims/policy/POL-MULTI-888")
        self.assertEqual(search_res.status_code, 200)
        data = search_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["claims"]), 2)

        # Search for non-existent policy returns 404
        missing_res = client_user.get("/api/claims/policy/POL-NONEXISTENT")
        self.assertEqual(missing_res.status_code, 404)

        # Assessor can search and find policy_holder's claims
        client_assessor = self.app.test_client()
        self._login(client_assessor, "assessor_user")
        assessor_res = client_assessor.get("/api/claims/policy/POL-MULTI-888")
        self.assertEqual(assessor_res.status_code, 200)
        self.assertEqual(assessor_res.get_json()["count"], 2)

    def test_my_claims_endpoint(self):
        """Ensures GET /api/my-claims returns all claims submitted by the logged-in user."""
        self._create_user("history_user", "history@example.com")
        client = self.app.test_client()
        self._login(client, "history_user")

        # Initially 0 claims
        res0 = client.get("/api/my-claims")
        self.assertEqual(res0.status_code, 200)
        self.assertEqual(res0.get_json()["count"], 0)

        # Submit 2 claims
        self._submit_claim(client, "POL-HIST-01")
        self._submit_claim(client, "POL-HIST-02")

        res2 = client.get("/api/my-claims")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.get_json()["count"], 2)

    def test_receipt_generation_pdf_and_json(self):
        """Ensures /api/claims/<id>/receipt emits downloadable PDF and JSON formats."""
        self._create_user("receipt_user", "receipt@example.com")
        client = self.app.test_client()
        self._login(client, "receipt_user")

        sub_res = self._submit_claim(client, "POL-RECEIPT-999")
        claim_id = sub_res.get_json()["claim_id"]

        # 1. Download PDF receipt
        pdf_res = client.get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res.mimetype, "application/pdf")
        self.assertTrue(len(pdf_res.data) > 1000)
        self.assertTrue(pdf_res.data.startswith(b"%PDF"))
        self.assertIn("attachment", pdf_res.headers.get("Content-Disposition", ""))

        # 2. Retrieve JSON receipt
        json_res = client.get(f"/api/claims/{claim_id}/receipt?format=json")
        self.assertEqual(json_res.status_code, 200)
        data = json_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["claim_id"], claim_id)
        self.assertEqual(data["receipt_type"], "SUBMISSION_RECEIPT")
        self.assertIn("disclaimer", data)
        self.assertIn("registration", data["disclaimer"].lower())

        # 3. Receipt for non-existent claim returns 404
        missing_res = client.get("/api/claims/CLM-20261009-XXXX/receipt")
        self.assertEqual(missing_res.status_code, 404)

        # 4. Unauthorized user receipt download rejected with 403
        self._create_user("intruder", "intruder@example.com")
        client_intruder = self.app.test_client()
        self._login(client_intruder, "intruder")
        unauth_res = client_intruder.get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(unauth_res.status_code, 403)

        # 5. Assessor can download receipt
        self._create_user("assessor_receipt", "assessor_rec@example.com", role="assessor")
        client_assessor = self.app.test_client()
        self._login(client_assessor, "assessor_receipt")
        assessor_receipt_res = client_assessor.get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(assessor_receipt_res.status_code, 200)

        # 6. Unauthenticated receipt download rejected with 401
        anon_receipt_res = self.app.test_client().get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(anon_receipt_res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
