"""Dedicated Regression Test Suite for Vehicle Replacement Image Upload & YOLOv8 Damage Detection.

Covers all 15 scenarios specified in Section 9 of the bugfix specification:
1. Missing or invalid claim ID format (400)
2. Nonexistent claim ID (404)
3. Unauthenticated access without session (401)
4. Unauthorized user access (403)
5. Claim with no vehicle photograph on disk (400)
6. Claim with synthetic graphic / document card (400 with requires_replacement: True)
7. Successful replacement image upload with authentic vehicle photo (200)
8. Replacement image validation rejection for synthetic image (400)
9. Successful damage detection on replacement image (200, detections, annotated image)
10. Verification that replacement image, NOT original, was analyzed
11. Verification that original image file is preserved on disk
12. Verification that original image record is preserved in database
13. Annotated image retrieval endpoint returns valid JPEG (200)
14. Damage history endpoint returns analysis runs (200)
15. Response Content-Type is application/json on all JSON endpoints (no HTML).
"""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from PIL import Image

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session, close_engine
from backend.database.models import Claim, ClaimImage, VehicleDamageAnalysis, User


class VehicleDamageBugfixTestSuite(unittest.TestCase):
    """Verifies that vehicle replacement image upload and damage detection work end-to-end without JSON/HTML errors."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.cardd_img = cls.repo_root / "datasets" / "CarDD_300" / "test" / "images" / "000023.jpg"
        assert cls.cardd_img.exists(), f"CarDD test image missing at {cls.cardd_img}"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)
        self.upload_dir = self.tmp / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        class TestCfg(Config):
            TESTING = True
            UPLOAD_FOLDER = self.upload_dir
            DATABASE_PATH = self.tmp / "test_bugfix.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(self.tmp / 'test_bugfix.db').as_posix()}"

        self.app = create_app(TestCfg)
        self.client = self.app.test_client()

        # Seed Primary User A (owner)
        with get_db_session() as db:
            user_a = User(
                username="claimant_owner",
                email="owner@example.com",
                full_name="Owner Claimant",
                role="user",
            )
            user_a.set_password("OwnerPassword123")
            db.add(user_a)

            # Seed Secondary User B (unauthorized)
            user_b = User(
                username="other_claimant",
                email="other@example.com",
                full_name="Other Claimant",
                role="user",
            )
            user_b.set_password("OtherPassword123")
            db.add(user_b)
            db.flush()

            self.user_a_id = user_a.id
            self.user_b_id = user_b.id

        # Authenticate as User A by default
        self._login_user("claimant_owner", "OwnerPassword123")

    def tearDown(self):
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def _login_user(self, username, password):
        return self.client.post("/api/auth/login", json={"identifier": username, "password": password})

    def _logout(self):
        return self.client.post("/api/auth/logout")

    def _create_claim_with_image(self, img_path: Path) -> str:
        with open(img_path, "rb") as f:
            img_bytes = f.read()

        payload = {
            "claimant_name": "Test Claimant",
            "policy_number": "POL-2026-BUGFIX",
            "vehicle_number": "DL-01-AB-1234",
            "accident_date": "2026-11-01",
            "claim_description": "Vehicle collision causing visible structural damage to panel.",
            "policy_document": (io.BytesIO(b"%PDF-1.4 test policy content"), "policy.pdf"),
            "claim_form": (io.BytesIO(b"%PDF-1.4 test claim form content"), "claim_form.pdf"),
            "invoice_document": (io.BytesIO(b"%PDF-1.4 test repair invoice content"), "invoice.pdf"),
            "vehicle_image": (io.BytesIO(img_bytes), img_path.name),
        }
        res = self.client.post("/api/claims", data=payload, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 201)
        return res.get_json()["claim_id"]

    def _make_synthetic_image(self, filename="synthetic_card.jpg") -> Path:
        p = self.tmp / filename
        img = Image.new("RGB", (800, 600), color=(250, 250, 250))
        img.save(p, format="JPEG")
        return p

    # -------------------------------------------------------------
    # Test Case 1: Missing or Invalid Claim ID (400)
    # -------------------------------------------------------------
    def test_tc1_invalid_claim_id_format_returns_400(self):
        for bad_id in ["invalid_id", "123", "CLM-BAD-FORMAT", "CLM-999"]:
            res = self.client.post(f"/api/claims/{bad_id}/analyze-damage", json={})
            self.assertEqual(res.status_code, 400)
            self.assertIn("application/json", res.content_type)
            data = res.get_json()
            self.assertFalse(data["success"])
            self.assertIn("Invalid Claim ID format", data["error"])

    # -------------------------------------------------------------
    # Test Case 2: Nonexistent Claim ID (404)
    # -------------------------------------------------------------
    def test_tc2_nonexistent_claim_id_returns_404(self):
        nonexistent = "CLM-20261120-9999"
        res = self.client.post(f"/api/claims/{nonexistent}/analyze-damage", json={})
        self.assertEqual(res.status_code, 404)
        self.assertIn("application/json", res.content_type)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Not Found")

    # -------------------------------------------------------------
    # Test Case 3: Unauthenticated Access Without Session (401)
    # -------------------------------------------------------------
    def test_tc3_unauthenticated_access_returns_401(self):
        synth = self._make_synthetic_image("synth1.jpg")
        cid = self._create_claim_with_image(synth)

        # Log out
        self._logout()

        # Both replace-image and analyze-damage must reject unauthenticated requests
        res_rep = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(b"test"), "test.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res_rep.status_code, 401)
        self.assertIn("application/json", res_rep.content_type)
        self.assertFalse(res_rep.get_json()["success"])

        res_an = self.client.post(f"/api/claims/{cid}/analyze-damage", json={})
        self.assertEqual(res_an.status_code, 401)
        self.assertIn("application/json", res_an.content_type)
        self.assertFalse(res_an.get_json()["success"])

    # -------------------------------------------------------------
    # Test Case 4: Unauthorized User Access (403)
    # -------------------------------------------------------------
    def test_tc4_unauthorized_user_access_returns_403(self):
        synth = self._make_synthetic_image("synth2.jpg")
        cid = self._create_claim_with_image(synth)

        # Switch to User B (unauthorized caller)
        self._login_user("other_claimant", "OtherPassword123")

        res_rep = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(b"test"), "test.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res_rep.status_code, 403)
        self.assertIn("application/json", res_rep.content_type)
        self.assertFalse(res_rep.get_json()["success"])

        res_an = self.client.post(f"/api/claims/{cid}/analyze-damage", json={})
        self.assertEqual(res_an.status_code, 403)
        self.assertIn("application/json", res_an.content_type)
        self.assertFalse(res_an.get_json()["success"])

    # -------------------------------------------------------------
    # Test Case 5: Claim With No Vehicle Photograph on Disk (400)
    # -------------------------------------------------------------
    def test_tc5_claim_with_no_vehicle_photo_returns_400(self):
        synth = self._make_synthetic_image("synth_del.jpg")
        cid = self._create_claim_with_image(synth)

        # Intentionally remove image file from disk to simulate missing evidence
        img_folder = self.upload_dir / cid / "images"
        for f in img_folder.glob("*"):
            f.unlink()

        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={})
        self.assertEqual(res.status_code, 400)
        self.assertIn("application/json", res.content_type)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Missing Evidence")

    # -------------------------------------------------------------
    # Test Case 6: Claim With Synthetic Graphic / Document Render (400, requires_replacement: True)
    # -------------------------------------------------------------
    def test_tc6_synthetic_graphic_rejected_with_requires_replacement(self):
        synth = self._make_synthetic_image("synth_doc.jpg")
        cid = self._create_claim_with_image(synth)

        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={})
        self.assertEqual(res.status_code, 400)
        self.assertIn("application/json", res.content_type)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Invalid Vehicle Evidence")
        self.assertTrue(data.get("requires_replacement"))
        self.assertIn("validation", data)
        self.assertFalse(data["validation"]["is_valid_vehicle_photo"])

    # -------------------------------------------------------------
    # Test Case 7: Successful Replacement Image Upload With Authentic Photo (200)
    # -------------------------------------------------------------
    def test_tc7_successful_replacement_image_upload(self):
        synth = self._make_synthetic_image("synth_orig.jpg")
        cid = self._create_claim_with_image(synth)

        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        res = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "genuine_accident.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/json", res.content_type)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["original_preserved"])
        self.assertTrue(data["validation"]["is_valid_vehicle_photo"])
        self.assertEqual(data["validation"]["status"], "validated_photo")

    # -------------------------------------------------------------
    # Test Case 8: Replacement Image Validation Rejection For Synthetic Image (400)
    # -------------------------------------------------------------
    def test_tc8_replacement_image_validation_rejection_for_synthetic_image(self):
        synth = self._make_synthetic_image("synth_initial.jpg")
        cid = self._create_claim_with_image(synth)

        # Upload another synthetic image as replacement
        bad_replacement = Image.new("RGB", (600, 400), color=(255, 255, 255))
        buf = io.BytesIO()
        bad_replacement.save(buf, format="JPEG")
        buf.seek(0)

        res = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (buf, "bad_replacement.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("application/json", res.content_type)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Invalid Vehicle Evidence")
        self.assertTrue(data.get("requires_replacement"))
        self.assertFalse(data["validation"]["is_valid_vehicle_photo"])

    # -------------------------------------------------------------
    # Test Case 9: Successful Damage Detection on Replacement Image (200, detections)
    # -------------------------------------------------------------
    def test_tc9_successful_damage_detection_on_replacement_image(self):
        synth = self._make_synthetic_image("synth_for_damage.jpg")
        cid = self._create_claim_with_image(synth)

        # Upload genuine replacement
        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        rep_res = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "replacement_cardd.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(rep_res.status_code, 200)

        # Execute damage detection
        an_res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10, "force": True})
        self.assertEqual(an_res.status_code, 200)
        self.assertIn("application/json", an_res.content_type)
        an_data = an_res.get_json()
        self.assertTrue(an_data["success"])
        analysis = an_data["analysis"]
        self.assertEqual(analysis["model_name"], "YOLOv8n-CarDD")
        self.assertGreaterEqual(analysis["total_detections"], 1)
        self.assertGreater(analysis["highest_confidence"], 0.10)
        self.assertIn("detections", analysis)
        self.assertGreaterEqual(len(analysis["detections"]), 1)

    # -------------------------------------------------------------
    # Test Case 10: Verification That Replacement Image, NOT Original, Was Analyzed
    # -------------------------------------------------------------
    def test_tc10_replacement_image_not_original_was_analyzed(self):
        synth = self._make_synthetic_image("synth_to_check.jpg")
        cid = self._create_claim_with_image(synth)

        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        rep_res = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "verified_replacement.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(rep_res.status_code, 200)

        # Run analysis
        an_res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10, "force": True})
        self.assertEqual(an_res.status_code, 200)
        analysis = an_res.get_json()["analysis"]

        # Check DB record points to replacement image path
        with get_db_session() as db:
            db_analysis = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).order_by(VehicleDamageAnalysis.id.desc()).first()
            self.assertIsNotNone(db_analysis)
            self.assertIn("replacement_vehicle_image", db_analysis.image_path)
            self.assertNotIn("synth_to_check", db_analysis.image_path)

            # Check that the image linked to the analysis has image_type REPLACEMENT_VEHICLE_ACCIDENT
            if db_analysis.image_id:
                analyzed_img = db.query(ClaimImage).filter_by(image_id=db_analysis.image_id).first()
                self.assertIsNotNone(analyzed_img)
                self.assertEqual(analyzed_img.image_type, "REPLACEMENT_VEHICLE_ACCIDENT")

    # -------------------------------------------------------------
    # Test Case 11: Verification That Original Image File is Preserved on Disk
    # -------------------------------------------------------------
    def test_tc11_original_image_file_preserved_on_disk(self):
        synth = self._make_synthetic_image("preserved_original.jpg")
        cid = self._create_claim_with_image(synth)

        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "second_photo.jpg")},
            content_type="multipart/form-data",
        )

        images_dir = self.upload_dir / cid / "images"
        orig_files = list(images_dir.glob("vehicle_image_preserved_original.jpg"))
        rep_files = list(images_dir.glob("replacement_vehicle_image_second_photo.jpg"))

        self.assertEqual(len(orig_files), 1, "Original file must exist on disk.")
        self.assertEqual(len(rep_files), 1, "Replacement file must exist on disk.")
        self.assertTrue(orig_files[0].exists())
        self.assertTrue(rep_files[0].exists())

    # -------------------------------------------------------------
    # Test Case 12: Verification That Original Image Record is Preserved in Database
    # -------------------------------------------------------------
    def test_tc12_original_image_record_preserved_in_database(self):
        synth = self._make_synthetic_image("db_orig.jpg")
        cid = self._create_claim_with_image(synth)

        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "db_rep.jpg")},
            content_type="multipart/form-data",
        )

        with get_db_session() as db:
            images = db.query(ClaimImage).filter_by(claim_id=cid).order_by(ClaimImage.image_id.asc()).all()
            self.assertEqual(len(images), 2, "Database must retain both original and replacement ClaimImage rows.")
            self.assertEqual(images[0].image_type, "VEHICLE_ACCIDENT")
            self.assertEqual(images[0].original_filename, "db_orig.jpg")
            self.assertEqual(images[1].image_type, "REPLACEMENT_VEHICLE_ACCIDENT")
            self.assertEqual(images[1].original_filename, "db_rep.jpg")

    # -------------------------------------------------------------
    # Test Case 13: Annotated Image Retrieval Endpoint Returns Valid JPEG (200)
    # -------------------------------------------------------------
    def test_tc13_annotated_image_retrieval_returns_valid_jpeg(self):
        synth = self._make_synthetic_image("annot_test.jpg")
        cid = self._create_claim_with_image(synth)

        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "annot_rep.jpg")},
            content_type="multipart/form-data",
        )

        self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10, "force": True})

        res = self.client.get(f"/api/claims/{cid}/annotated-image")
        self.assertEqual(res.status_code, 200)
        self.assertIn("image/", res.content_type)
        self.assertGreater(len(res.data), 1000)

        # Verify it can be decoded as an image
        img = Image.open(io.BytesIO(res.data))
        self.assertGreater(img.width, 0)
        self.assertGreater(img.height, 0)

    # -------------------------------------------------------------
    # Test Case 14: Damage History Endpoint Returns Analysis Runs (200)
    # -------------------------------------------------------------
    def test_tc14_damage_history_endpoint_returns_runs(self):
        synth = self._make_synthetic_image("hist_test.jpg")
        cid = self._create_claim_with_image(synth)

        with open(self.cardd_img, "rb") as f:
            real_bytes = f.read()

        self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "hist_rep.jpg")},
            content_type="multipart/form-data",
        )

        # Execute analysis twice to produce history
        self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10, "force": True})

        res = self.client.get(f"/api/claims/{cid}/damage-history")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/json", res.content_type)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["total_runs"], 1)
        self.assertIn("history", data)
        self.assertEqual(len(data["history"]), data["total_runs"])

    # -------------------------------------------------------------
    # Test Case 15: Response Content-Type is application/json on all JSON Endpoints (No HTML)
    # -------------------------------------------------------------
    def test_tc15_response_content_type_is_json_on_all_endpoints(self):
        synth = self._make_synthetic_image("json_test.jpg")
        cid = self._create_claim_with_image(synth)

        endpoints = [
            ("POST", f"/api/claims/{cid}/analyze-damage", {"conf_threshold": 0.15}),
            ("GET", f"/api/claims/{cid}/damage-analysis", None),
            ("GET", f"/api/claims/{cid}/damage-history", None),
            ("GET", f"/api/claims/{cid}", None),
            ("POST", f"/api/claims/CLM-NONEXISTENT-9999/analyze-damage", {}),
            ("POST", "/api/claims/INVALID/analyze-damage", {}),
        ]

        for method, ep, body in endpoints:
            if method == "POST":
                res = self.client.post(ep, json=body or {})
            else:
                res = self.client.get(ep)

            self.assertIn(
                "application/json",
                res.content_type,
                f"Endpoint {method} {ep} returned {res.content_type} instead of application/json!",
            )
            raw = res.get_data(as_text=True)
            self.assertFalse(
                raw.strip().startswith("<!doctype") or raw.strip().startswith("<!DOCTYPE") or "<html" in raw.lower(),
                f"Endpoint {method} {ep} returned HTML instead of JSON: {raw[:100]}",
            )
            # Must parse as valid JSON
            parsed = json.loads(raw)
            self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
