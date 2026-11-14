"""Unit and integration tests for Claim Submission Module (Phase 2)."""

import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.config import Config
from backend.utils.validators import generate_claim_id, is_valid_claim_id_format


class ClaimSubmissionTestCase(unittest.TestCase):
    """Test suite for claim submission endpoints, file validation, and storage."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.upload_dir = Path(self.temp_dir.name) / "uploads"

        class TestConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = Path(self.temp_dir.name) / "uploads"
            DATABASE_PATH = Path(self.temp_dir.name) / "test.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(Path(self.temp_dir.name) / 'test.db').as_posix()}"

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        from backend.database.db import close_engine
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _get_valid_claim_data(self):
        """Helper to generate a valid form data payload with dummy files."""
        return {
            "claimant_name": "John Doe",
            "policy_number": "POL-98765432",
            "vehicle_number": "DL-01-AB-1234",
            "accident_date": "2026-09-15",
            "claim_description": "Vehicle was hit from the front side while stationary at traffic lights.",
            "policy_document": (io.BytesIO(b"%PDF-1.4 dummy policy document content"), "policy.pdf"),
            "claim_form": (io.BytesIO(b"%PDF-1.4 dummy claim form content"), "claim_form.pdf"),
            "invoice_document": (io.BytesIO(b"%PDF-1.4 dummy repair bill invoice"), "invoice.pdf"),
            "vehicle_image": (io.BytesIO(b"\xff\xd8\xff dummy jpeg image bytes"), "accident.jpg"),
        }

    def test_claim_id_generation_and_format(self):
        """Ensure generated Claim IDs match CLM-YYYYMMDD-XXXX format and are unique."""
        ids = {generate_claim_id() for _ in range(50)}
        self.assertEqual(len(ids), 50, "Generated Claim IDs must be unique.")
        for cid in ids:
            self.assertTrue(
                is_valid_claim_id_format(cid),
                f"Claim ID {cid} does not match required format CLM-YYYYMMDD-XXXX.",
            )

    def test_successful_claim_submission(self):
        """Ensure valid submission returns 201 Created and expected JSON response."""
        data = self._get_valid_claim_data()
        response = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 201)
        res_json = response.get_json()

        self.assertTrue(res_json.get("success"))
        claim_id = res_json.get("claim_id")
        self.assertIsNotNone(claim_id)
        self.assertTrue(is_valid_claim_id_format(claim_id))
        self.assertEqual(res_json.get("message"), "Claim submitted successfully")
        self.assertIn("data", res_json)
        self.assertEqual(res_json["data"]["claimant_name"], "John Doe")
        self.assertEqual(res_json["data"]["policy_number"], "POL-98765432")

    def test_file_storage_structure(self):
        """Ensure uploaded files and metadata.json are properly saved to disk."""
        data = self._get_valid_claim_data()
        response = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 201)
        claim_id = response.get_json()["claim_id"]

        claim_dir = self.upload_dir / claim_id
        docs_dir = claim_dir / "documents"
        images_dir = claim_dir / "images"
        meta_file = claim_dir / "metadata.json"

        # Verify directory structure
        self.assertTrue(claim_dir.exists())
        self.assertTrue(docs_dir.exists())
        self.assertTrue(images_dir.exists())
        self.assertTrue(meta_file.exists())

        # Verify files are stored
        doc_files = list(docs_dir.iterdir())
        image_files = list(images_dir.iterdir())
        self.assertEqual(len(doc_files), 3)  # policy, claim form, invoice
        self.assertEqual(len(image_files), 1)  # vehicle image

        # Verify metadata content
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["claim_id"], claim_id)
        self.assertEqual(meta["claimant_name"], "John Doe")
        self.assertEqual(meta["status"], "SUBMITTED")
        self.assertIn("vehicle_image", meta["files"])

    def test_missing_required_field(self):
        """Ensure submission fails with 400 when a required text field is missing."""
        data = self._get_valid_claim_data()
        del data["policy_number"]

        response = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertFalse(res_json["success"])
        self.assertIn("Missing required field: 'policy_number'", str(res_json["details"]))

    def test_missing_required_file(self):
        """Ensure submission fails with 400 when a required file is missing."""
        data = self._get_valid_claim_data()
        del data["vehicle_image"]

        response = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertFalse(res_json["success"])
        self.assertIn("Missing required file: 'vehicle_image'", str(res_json["details"]))

    def test_invalid_file_type(self):
        """Ensure submission fails with 400 when an unallowed file extension is uploaded."""
        data = self._get_valid_claim_data()
        # Disallowed document format
        data["policy_document"] = (io.BytesIO(b"malicious script"), "script.exe")

        response = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertFalse(res_json["success"])
        self.assertIn("invalid format '.exe'", str(res_json["details"]))

    def test_invalid_image_type(self):
        """Ensure vehicle image only accepts allowed image extensions."""
        data = self._get_valid_claim_data()
        # PDF is not accepted for vehicle_image
        data["vehicle_image"] = (io.BytesIO(b"%PDF document"), "photo.pdf")

        response = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertFalse(res_json["success"])
        self.assertIn("invalid format '.pdf'", str(res_json["details"]))

    def test_get_claim_by_id(self):
        """Ensure GET /api/claims/<id> returns submitted metadata."""
        data = self._get_valid_claim_data()
        post_res = self.client.post(
            "/api/claims",
            data=data,
            content_type="multipart/form-data",
        )
        claim_id = post_res.get_json()["claim_id"]

        get_res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(get_res.status_code, 200)
        res_json = get_res.get_json()
        self.assertTrue(res_json["success"])
        self.assertEqual(res_json["data"]["claim_id"], claim_id)

    def test_get_nonexistent_claim(self):
        """Ensure GET /api/claims/<id> for non-existent claim returns 404."""
        response = self.client.get("/api/claims/CLM-20261008-ZZ99")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
