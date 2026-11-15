"""Test suite verifying Dashboard Cleanup and Three-Section UI Redesign."""
import io
import json
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session, init_database
from backend.database.models import Base, User, Claim, Document, ClaimImage


class TestUIRedesignAndThreeSections(unittest.TestCase):
    """Verifies that the dashboard HTML removes technical panels and supports three independent sections."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.upload_dir = Path(self.temp_dir.name) / "uploads"
        self.db_path = Path(self.temp_dir.name) / "test_ui.db"

        class TestConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = Path(self.temp_dir.name) / "uploads"
            DATABASE_PATH = Path(self.temp_dir.name) / "test_ui.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(Path(self.temp_dir.name) / 'test_ui.db').as_posix()}"

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        from backend.database.db import close_engine
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_dashboard_html_removes_technical_panels(self):
        """Verify that the 3 technical sections are completely removed from user dashboard."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        # The three technical sections MUST be removed
        self.assertNotIn("Backend System Status", html)
        self.assertNotIn("Verification Pipeline Architecture", html)
        self.assertNotIn("Module Foundation Status", html)
        self.assertNotIn("class=\"card health-card\"", html)
        self.assertNotIn("class=\"card pipeline-card\"", html)
        self.assertNotIn("class=\"card modules-card\"", html)
        self.assertNotIn("module-table", html)
        self.assertNotIn("pipeline-steps", html)

    def test_dashboard_html_contains_three_independent_sections(self):
        """Verify the presence of three independent sections and clean navigation pills."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        # Navigation Pills
        self.assertIn('id="pill-nav-submit"', html)
        self.assertIn('id="pill-nav-search"', html)
        self.assertIn('id="pill-nav-myclaims"', html)

        # Three Independent Section Containers
        self.assertIn('id="section-submit"', html)
        self.assertIn('id="section-lookup"', html)
        self.assertIn('id="section-myclaims"', html)

        # Section 1 components
        self.assertIn('id="claim-form"', html)
        self.assertIn('id="claimant_name"', html)
        self.assertIn('id="policy_number"', html)
        self.assertIn('id="vehicle_number"', html)
        self.assertIn('id="accident_date"', html)
        self.assertIn('id="incident_location"', html)
        self.assertIn('id="claim_description"', html)
        self.assertIn('id="policy_document"', html)
        self.assertIn('id="claim_form_file"', html)
        self.assertIn('id="invoice_document"', html)
        self.assertIn('id="vehicle_image"', html)
        self.assertIn('id="submission-success-card"', html)

        # Section 2 components
        self.assertIn('id="policy-search-form"', html)
        self.assertIn('id="search-policy-input"', html)
        self.assertIn('id="policy-search-results"', html)

        # Section 3 components
        self.assertIn('id="myclaims-filter-input"', html)
        self.assertIn('id="myclaims-sort-select"', html)
        self.assertIn('id="my-claims-list"', html)

        # Modals
        self.assertIn('id="modal-claim-details"', html)
        self.assertIn('id="modal-claim-evidence"', html)

    def test_claim_submission_and_incident_location(self):
        """Test submitting a claim with incident_location and retrieving it."""
        # 1. Register & login
        reg_res = self.client.post(
            "/api/auth/signup",
            json={
                "username": "tester",
                "email": "tester@example.com",
                "full_name": "Test User",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        self.assertEqual(reg_res.status_code, 201)

        login_res = self.client.post(
            "/api/auth/login",
            json={"identifier": "tester", "password": "Password123!"},
        )
        self.assertEqual(login_res.status_code, 200)

        # 2. Submit claim
        data = {
            "claimant_name": "Rajesh Sharma",
            "policy_number": "POL-2024-88391",
            "vehicle_number": "MH-12-DE-4052",
            "accident_date": "2026-09-28",
            "incident_location": "MG Road, Pune, Maharashtra",
            "claim_description": "Rear bumper collision at MG Road intersection.",
            "policy_document": (io.BytesIO(b"%PDF-1.4 sample policy"), "policy.pdf"),
            "claim_form": (io.BytesIO(b"%PDF-1.4 sample claim form"), "claim_form.pdf"),
            "invoice_document": (io.BytesIO(b"%PDF-1.4 sample invoice"), "invoice.pdf"),
            "vehicle_image": (io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00"), "photo.jpg"),
        }

        submit_res = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(submit_res.status_code, 201)
        res_json = submit_res.get_json()
        self.assertTrue(res_json["success"])
        claim_id = res_json["claim_id"]

        # 3. Retrieve claim by ID
        get_res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res.status_code, 200)
        claim_data = get_res.get_json()["data"]
        self.assertEqual(claim_data["claimant_name"], "Rajesh Sharma")
        self.assertEqual(claim_data["incident_location"], "MG Road, Pune, Maharashtra")

        # 4. Retrieve claim by Policy Number
        pol_res = self.client.get("/api/claims/policy/POL-2024-88391")
        self.assertEqual(pol_res.status_code, 200)
        self.assertEqual(len(pol_res.get_json()["claims"]), 1)

        # 5. Retrieve claim via unified search
        search_res = self.client.get(f"/api/claims/search?q={claim_id}")
        self.assertEqual(search_res.status_code, 200)
        self.assertEqual(len(search_res.get_json()["claims"]), 1)

        # 6. Retrieve My Submissions
        my_res = self.client.get("/api/my-claims")
        self.assertEqual(my_res.status_code, 200)
        my_claims = my_res.get_json()["claims"]
        self.assertEqual(len(my_claims), 1)
        self.assertEqual(my_claims[0]["claim_id"], claim_id)

        # 7. Retrieve Evidence Files
        doc_res = self.client.get(f"/api/claims/{claim_id}/evidence/policy")
        self.assertEqual(doc_res.status_code, 200)

        img_res = self.client.get(f"/api/claims/{claim_id}/evidence/image")
        self.assertEqual(img_res.status_code, 200)

        # 8. Receipt & Document report
        receipt_res = self.client.get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(receipt_res.status_code, 200)
        self.assertEqual(receipt_res.mimetype, "application/pdf")

        report_res = self.client.get(f"/api/claims/{claim_id}/document-report")
        self.assertEqual(report_res.status_code, 200)
        self.assertEqual(report_res.mimetype, "application/pdf")


if __name__ == "__main__":
    unittest.main()
