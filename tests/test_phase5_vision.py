"""Phase 5 Vehicle Damage Detection Automated Test Suite.

Validates CarDD dataset integrity, trained YOLOv8 model loading, inference,
spatial region calculation, image annotation, backend API endpoints,
database persistence, and PDF report integration.
"""

import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session, close_engine
from backend.database.models import (
    User,
    Claim,
    ClaimImage,
    VehicleDamageAnalysis,
    VehicleDamageDetection,
)
from backend.services.vision import (
    VehicleDamageDetector,
    determine_spatial_region,
    create_annotated_image,
    get_category_color,
    get_model_evaluation_metrics,
    load_and_preprocess_image,
    CARDD_CLASS_NAMES,
)
from backend.services.receipt import generate_document_intelligence_report_pdf


class Phase5VisionTestSuite(unittest.TestCase):
    """Complete test suite for Phase 5 Computer Vision damage detection pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.cardd_dir = cls.repo_root / "datasets" / "CarDD_300"
        cls.weights_path = cls.repo_root / "models" / "vehicle_damage" / "best.pt"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)
        self.upload_dir = self.tmp / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        class TestCfg(Config):
            TESTING = True
            UPLOAD_FOLDER = self.upload_dir
            DATABASE_PATH = self.tmp / "test_phase5.db"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{(self.tmp / 'test_phase5.db').as_posix()}"

        self.app = create_app(TestCfg)
        self.client = self.app.test_client()

        # Seed authenticated user
        with get_db_session() as db:
            user = User(
                username="vision_tester",
                email="vision_tester@example.com",
                full_name="Vision Tester",
                role="user",
            )
            user.set_password("VisionSecurePass123")
            db.add(user)
            db.flush()
            self.user_id = user.id

        self.client.post(
            "/api/auth/login",
            json={"identifier": "vision_tester", "password": "VisionSecurePass123"},
        )

    def tearDown(self):
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # -------------------------------------------------------------
    # 1. CarDD Dataset Verification Tests
    # -------------------------------------------------------------
    def test_cardd_dataset_splits_and_integrity(self):
        """Verifies untouched CarDD dataset directories, image counts, and formats."""
        self.assertTrue(self.cardd_dir.exists(), f"CarDD dataset directory missing: {self.cardd_dir}")
        
        train_imgs = list((self.cardd_dir / "train" / "images").glob("*.jpg"))
        val_imgs = list((self.cardd_dir / "val" / "images").glob("*.jpg"))
        test_imgs = list((self.cardd_dir / "test" / "images").glob("*.jpg"))

        self.assertEqual(len(train_imgs), 210, "CarDD train split must contain exactly 210 images.")
        self.assertEqual(len(val_imgs), 45, "CarDD val split must contain exactly 45 images.")
        self.assertEqual(len(test_imgs), 45, "CarDD test split must contain exactly 45 images.")
        self.assertEqual(len(train_imgs) + len(val_imgs) + len(test_imgs), 300)

        # Verify class definitions match the 6 CarDD categories
        self.assertEqual(len(CARDD_CLASS_NAMES), 6)
        expected_classes = ["dent", "scratch", "crack", "glass shatter", "lamp broken", "tire flat"]
        for exp in expected_classes:
            self.assertIn(exp, CARDD_CLASS_NAMES.values())

    # -------------------------------------------------------------
    # 2. Model Checkpoint & Architecture Tests
    # -------------------------------------------------------------
    def test_model_weights_checkpoint_and_classes(self):
        """Verifies best.pt model checkpoint exists and is loadable with 6 classes."""
        phase5_best = self.repo_root / "models" / "phase5" / "best.pt"
        self.assertTrue(phase5_best.exists(), f"Phase 5 checkpoint missing: {phase5_best}")
        self.assertTrue((self.repo_root / "models" / "phase5" / "last.pt").exists())
        self.assertTrue((self.repo_root / "models" / "phase5" / "dataset.yaml").exists())
        self.assertTrue(self.weights_path.exists(), f"Trained weights checkpoint not found: {self.weights_path}")
        detector = VehicleDamageDetector.get_instance(phase5_best)
        self.assertIsNotNone(detector.model)
        self.assertEqual(len(detector.model.names), 6)
        self.assertEqual(detector.device, "cpu")

    def test_evaluation_metrics_report_available(self):
        """Verifies genuine evaluation report exists and contains valid metrics."""
        eval_data = get_model_evaluation_metrics()
        self.assertEqual(eval_data.get("status"), "evaluated")
        self.assertEqual(eval_data.get("num_test_images"), 45)
        self.assertIn("overall_metrics", eval_data)
        self.assertGreater(eval_data["overall_metrics"]["map50"], 0.05)
        self.assertIn("per_class_metrics", eval_data)
        self.assertEqual(len(eval_data["per_class_metrics"]), 6)
        # Verify reports/phase5 directory contains metrics
        self.assertTrue((self.repo_root / "reports" / "phase5" / "evaluation_results.json").exists())
        self.assertTrue((self.repo_root / "reports" / "phase5" / "evaluation_metrics.csv").exists())

    # -------------------------------------------------------------
    # 3. Vision Inference & Spatial Calculations Tests
    # -------------------------------------------------------------
    def test_spatial_region_quadrants(self):
        """Verifies spatial region detection divides bounding boxes correctly."""
        w, h = 1000, 1000
        # Upper left
        self.assertEqual(determine_spatial_region([50, 50, 150, 150], w, h), "front_left")
        # Upper center
        self.assertEqual(determine_spatial_region([450, 50, 550, 150], w, h), "front_center")
        # Upper right
        self.assertEqual(determine_spatial_region([850, 50, 950, 150], w, h), "front_right")
        # Center
        self.assertEqual(determine_spatial_region([450, 450, 550, 550], w, h), "center")
        # Lower center
        self.assertEqual(determine_spatial_region([450, 850, 550, 950], w, h), "rear_center")
        # Lower right
        self.assertEqual(determine_spatial_region([850, 850, 950, 950], w, h), "rear_right")

    def test_detector_inference_on_real_cardd_image(self):
        """Runs detector on real CarDD test image and verifies structured detections."""
        detector = VehicleDamageDetector.get_instance(self.weights_path)
        test_img_path = self.cardd_dir / "test" / "images" / "000023.jpg"
        self.assertTrue(test_img_path.exists())

        res = detector.detect_damage(test_img_path, conf_threshold=0.10)
        self.assertEqual(res["model_name"], "YOLOv8n-CarDD")
        self.assertEqual(res["device"], "cpu")
        self.assertGreaterEqual(res["total_detections"], 1)
        self.assertGreater(res["highest_confidence"], 0.10)
        self.assertGreater(res["processing_time_ms"], 0.0)

        for det in res["detections"]:
            self.assertIn("category", det)
            self.assertIn("confidence", det)
            self.assertIn("location_region", det)
            self.assertEqual(len(det["bbox"]), 4)

    def test_detector_handles_blank_no_damage_image(self):
        """Verifies detector handles an image with zero damage without errors."""
        detector = VehicleDamageDetector.get_instance(self.weights_path)
        # Create solid gray image
        blank_img = Image.new("RGB", (400, 300), color=(180, 180, 180))
        res = detector.detect_damage(blank_img, conf_threshold=0.30)
        self.assertEqual(res["total_detections"], 0)
        self.assertEqual(res["damage_categories"], [])
        self.assertEqual(res["highest_confidence"], 0.0)
        self.assertFalse(res["has_damage"])

    # -------------------------------------------------------------
    # 4. Annotated Image Generation Tests
    # -------------------------------------------------------------
    def test_create_annotated_image_preserves_dimensions_and_draws(self):
        """Verifies annotation renders bounding boxes and produces a valid output file."""
        test_img = Image.new("RGB", (600, 400), color=(200, 210, 220))
        detections = [
            {
                "detection_index": 1,
                "category": "dent",
                "confidence": 0.85,
                "confidence_percentage": 85.0,
                "bbox": [50, 50, 200, 180],
                "location_region": "front_left",
            },
            {
                "detection_index": 2,
                "category": "scratch",
                "confidence": 0.62,
                "confidence_percentage": 62.0,
                "bbox": [300, 200, 500, 350],
                "location_region": "rear_right",
            },
        ]
        out_path = self.tmp / "annotated_sample.jpg"
        annotated = create_annotated_image(test_img, detections, output_path=out_path)
        self.assertEqual(annotated.size, (600, 400))
        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 500)

        # Verify category color mapping
        self.assertEqual(get_category_color("dent"), (59, 130, 246))
        self.assertEqual(get_category_color("scratch"), (234, 179, 8))

    # -------------------------------------------------------------
    # 5. Backend Routes Integration Tests
    # -------------------------------------------------------------
    def _create_test_claim(self, img_source_path: Path) -> str:
        """Helper to create a claim in SQLite and upload directory with a real vehicle photo."""
        with open(img_source_path, "rb") as f:
            img_bytes = f.read()

        payload = {
            "claimant_name": "Vision Test User",
            "policy_number": "POL-VISION-9999",
            "vehicle_number": "MH-02-CV-2026",
            "accident_date": "2026-10-10",
            "claim_description": "Vehicle side impacted at low speed.",
            "policy_document": (io.BytesIO(b"%PDF-1.4 dummy policy document"), "policy.pdf"),
            "claim_form": (io.BytesIO(b"%PDF-1.4 dummy claim form"), "form.pdf"),
            "invoice_document": (io.BytesIO(b"%PDF-1.4 dummy invoice"), "invoice.pdf"),
            "vehicle_image": (io.BytesIO(img_bytes), img_source_path.name),
        }
        res = self.client.post("/api/claims", data=payload, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 201)
        return res.get_json()["claim_id"]

    def test_vision_status_endpoint(self):
        """Verifies GET /api/vision/status, /api/vision/metrics, and /api/model/status."""
        for endpoint in ["/api/vision/status", "/api/vision/metrics", "/api/model/status", "/api/phase5/metrics"]:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200, f"Endpoint {endpoint} failed")
            data = res.get_json()
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], "ready")
            self.assertEqual(data["model_name"], "YOLOv8n-CarDD")
            self.assertIn("evaluation_metrics", data)

    def test_analyze_damage_endpoint_and_persistence(self):
        """Verifies POST /api/claims/<claim_id>/analyze-damage runs inference, persists to DB, and creates annotated image."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # 1. Execute damage analysis
        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        analysis = data["analysis"]
        self.assertEqual(analysis["claim_id"], cid)
        self.assertGreaterEqual(analysis["total_detections"], 1)
        self.assertIsNotNone(analysis["annotated_image_path"])

        # 2. Verify database records
        with get_db_session() as db:
            db_analyses = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).all()
            self.assertEqual(len(db_analyses), 1)
            db_analysis = db_analyses[0]
            self.assertEqual(db_analysis.total_detections, analysis["total_detections"])

            db_detections = db.query(VehicleDamageDetection).filter_by(analysis_id=db_analysis.id).all()
            self.assertEqual(len(db_detections), analysis["total_detections"])
            for d in db_detections:
                self.assertIsNotNone(d.category)
                self.assertGreater(d.confidence, 0.0)

        # 3. Verify GET /api/claims/<claim_id>/damage-analysis
        get_res = self.client.get(f"/api/claims/{cid}/damage-analysis")
        self.assertEqual(get_res.status_code, 200)
        self.assertTrue(get_res.get_json()["analyzed"])

        # 4. Verify GET /api/claims/<claim_id>/damage-history
        hist_res = self.client.get(f"/api/claims/{cid}/damage-history")
        self.assertEqual(hist_res.status_code, 200)
        self.assertEqual(hist_res.get_json()["total_runs"], 1)

        # 5. Verify GET /api/claims/<claim_id>/annotated-image
        img_res = self.client.get(f"/api/claims/{cid}/annotated-image")
        self.assertEqual(img_res.status_code, 200)
        self.assertEqual(img_res.content_type, "image/jpeg")
        self.assertGreater(len(img_res.data), 1000)

    def test_damage_endpoints_access_authorization(self):
        """Verifies unauthorized users cannot access damage analysis endpoints."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Logout user
        self.client.post("/api/auth/logout")

        # Unauthorized access check
        self.assertEqual(self.client.get(f"/api/claims/{cid}/damage-analysis").status_code, 401)
        self.assertEqual(self.client.post(f"/api/claims/{cid}/analyze-damage").status_code, 401)
        self.assertEqual(self.client.get(f"/api/claims/{cid}/annotated-image").status_code, 401)

    # -------------------------------------------------------------
    # 6. Consolidated PDF Report Integration Tests
    # -------------------------------------------------------------
    def test_consolidated_pdf_includes_vehicle_damage_section(self):
        """Verifies generated report PDF includes the Phase 5 Vehicle Damage Detection Analysis section."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Run damage analysis first
        self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10})

        # Fetch claim dict
        claim_res = self.client.get(f"/api/claims/{cid}")
        self.assertEqual(claim_res.status_code, 200)
        claim_dict = claim_res.get_json()["data"]

        # Generate report PDF
        pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict=claim_dict,
            extracted_rows=[],
            upload_root=self.upload_dir,
        )
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 5000)

        # Verify section title is present in PDF text stream
        import fitz
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            all_text = " ".join([page.get_text() for page in doc])
            self.assertIn("VEHICLE DAMAGE DETECTION ANALYSIS", all_text.upper())
            self.assertIn("YOLOV8", all_text.upper())
            self.assertIn("CARDD", all_text.upper())

    # -------------------------------------------------------------
    # 7. Invalid Evidence & Replacement Workflow Tests (Task 1 & 5)
    # -------------------------------------------------------------
    def test_invalid_synthetic_graphic_flagged_and_rejected_from_damage_inference(self):
        """Ensures synthetic graphics / document renders are flagged and rejected from YOLO damage inference."""
        # 1. Create a synthetic graphic with high uniform color fraction (>90% white/gray)
        synth_img = Image.new("RGB", (900, 600), color=(248, 250, 252))
        synth_path = self.tmp / "synthetic_policy_graphic.jpg"
        synth_img.save(synth_path, format="JPEG")

        cid = self._create_test_claim(synth_path)

        # 2. Attempt damage detection on synthetic graphic - MUST BE REJECTED with 400
        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.15})
        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(json_data["error"], "Invalid Vehicle Evidence")
        self.assertTrue(json_data.get("requires_replacement"))
        self.assertEqual(json_data["validation"]["status"], "invalid_graphic")

        # 3. Verify PDF generation for claim with flagged graphic displays Pending and Warning
        claim_res = self.client.get(f"/api/claims/{cid}")
        pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict=claim_res.get_json()["data"],
            extracted_rows=[],
            upload_root=self.upload_dir,
        )
        import fitz
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            pdf_text = " ".join([page.get_text() for page in doc])
            self.assertIn("SYNTHETIC GRAPHIC", pdf_text.upper())
            self.assertIn("PENDING", pdf_text.upper())

    def test_replacement_photograph_workflow_and_audit_preservation(self):
        """Verifies uploading an authentic replacement photo enables damage analysis while preserving original audit trail."""
        # 1. Start with synthetic graphic
        synth_img = Image.new("RGB", (900, 600), color=(248, 250, 252))
        synth_path = self.tmp / "initial_synthetic_graphic.jpg"
        synth_img.save(synth_path, format="JPEG")
        cid = self._create_test_claim(synth_path)

        # 2. Upload authentic replacement photograph from CarDD dataset
        real_img_path = self.cardd_dir / "test" / "images" / "000023.jpg"
        with open(real_img_path, "rb") as f:
            real_bytes = f.read()

        rep_res = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "genuine_accident_photo.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(rep_res.status_code, 200)
        rep_json = rep_res.get_json()
        self.assertTrue(rep_json["success"])
        self.assertTrue(rep_json["validation"]["is_valid_vehicle_photo"])
        self.assertEqual(rep_json["validation"]["status"], "validated_photo")

        # 3. Verify both original and replacement images are preserved in database
        with get_db_session() as db:
            images = db.query(ClaimImage).filter_by(claim_id=cid).order_by(ClaimImage.created_at.asc()).all()
            self.assertEqual(len(images), 2, "Both original and replacement images must be preserved in DB audit log.")
            self.assertEqual(images[0].original_filename, "initial_synthetic_graphic.jpg")
            self.assertEqual(images[1].original_filename, "genuine_accident_photo.jpg")

        # 4. Now damage analysis succeeds with 200 using the replacement photograph
        analysis_res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10})
        self.assertEqual(analysis_res.status_code, 200)
        analysis_json = analysis_res.get_json()
        self.assertTrue(analysis_json["success"])
        self.assertGreaterEqual(analysis_json["analysis"]["total_detections"], 1)

        # 5. Generate consolidated PDF and verify both audit trail and annotated photos are included
        claim_res = self.client.get(f"/api/claims/{cid}")
        pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict=claim_res.get_json()["data"],
            extracted_rows=[],
            upload_root=self.upload_dir,
        )
        import fitz
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            pdf_text = " ".join([page.get_text() for page in doc])
            self.assertIn("EVIDENCE AUDIT TRAIL", pdf_text.upper())
            self.assertIn("VEHICLE DAMAGE DETECTION ANALYSIS", pdf_text.upper())
            self.assertIn("COMPLETED", pdf_text.upper())


if __name__ == "__main__":
    unittest.main()
