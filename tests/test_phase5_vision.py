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
    create_opencv_visual_analysis,
    assess_image_quality,
    enhance_contrast_clahe,
    reduce_noise,
    detect_edges_and_contours,
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

    # -------------------------------------------------------------
    # 8. OpenCV Fallback & Quality Assessment Tests
    # -------------------------------------------------------------
    def test_opencv_preprocessing_and_quality_assessment(self):
        """Verifies OpenCV preprocessing pipeline, CLAHE enhancement, bilateral denoising, and edge detection."""
        real_img_path = self.cardd_dir / "test" / "images" / "000023.jpg"
        pil_img, np_img, meta = load_and_preprocess_image(real_img_path)

        # 1. Quality Assessment
        qa = assess_image_quality(np_img)
        self.assertIn("laplacian_variance", qa)
        self.assertIn("contrast_std", qa)
        self.assertIn("quality_grade", qa)
        self.assertGreater(qa["laplacian_variance"], 0.0)
        self.assertGreater(qa["contrast_std"], 0.0)

        # 2. CLAHE Enhancement
        enhanced = enhance_contrast_clahe(np_img)
        self.assertEqual(enhanced.shape, np_img.shape)

        # 3. Noise Reduction
        denoised = reduce_noise(enhanced, method="bilateral")
        self.assertEqual(denoised.shape, np_img.shape)

        # 4. Edge and Contour Analysis
        edges_contours = detect_edges_and_contours(np_img)
        self.assertIn("edge_pixels", edges_contours)
        self.assertIn("edge_density_pct", edges_contours)
        self.assertIn("salient_contours", edges_contours)
        self.assertGreater(edges_contours["edge_pixels"], 0)
        self.assertGreater(len(edges_contours["salient_contours"]), 0)

    def test_opencv_fallback_detection_mode(self):
        """Verifies detector in OpenCV fallback mode returns zero semantic damage detections and rich CV observations."""
        detector = VehicleDamageDetector.get_instance(self.weights_path)
        real_img_path = self.cardd_dir / "test" / "images" / "000023.jpg"

        res = detector.detect_damage(real_img_path, force_opencv_fallback=True)
        self.assertEqual(res["detection_method"], "opencv_traditional_cv")
        self.assertEqual(res["total_detections"], 0, "OpenCV fallback must NOT fabricate damage detections.")
        self.assertEqual(res["damage_categories"], [], "No semantic damage categories should be asserted.")
        self.assertEqual(res["highest_confidence"], 0.0)
        self.assertFalse(res["has_damage"])
        self.assertIn("opencv_observations", res)
        obs = res["opencv_observations"]
        self.assertIn("image_quality", obs)
        self.assertIn("contour_analysis", obs)
        self.assertIn("limitations_notice", obs)

    def test_opencv_visual_analysis_generation(self):
        """Verifies OpenCV visual analysis produces diagnostic visualization without false damage boxes."""
        real_img_path = self.cardd_dir / "test" / "images" / "000023.jpg"
        pil_img, np_img, meta = load_and_preprocess_image(real_img_path)
        qa = assess_image_quality(np_img)
        contours = detect_edges_and_contours(np_img)

        out_path = self.tmp / "opencv_visual_test.jpg"
        vis = create_opencv_visual_analysis(
            image_input=real_img_path,
            observations={"image_quality": qa, "contour_analysis": contours},
            output_path=out_path,
        )
        self.assertEqual(vis.size, (meta["width"], meta["height"]))
        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 1000)

    def test_api_analyze_damage_with_opencv_fallback(self):
        """Verifies POST /api/claims/<claim_id>/analyze-damage with fallback=true persists fallback record and produces valid PDF."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # 1. Execute damage analysis in fallback mode
        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"force_opencv": True})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        analysis = data["analysis"]
        self.assertEqual(analysis["detection_method"], "opencv_traditional_cv")
        self.assertEqual(analysis["total_detections"], 0)
        self.assertIsNotNone(analysis["opencv_observations"])

        # 2. Database record check
        with get_db_session() as db:
            db_analysis = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).order_by(VehicleDamageAnalysis.id.desc()).first()
            self.assertIsNotNone(db_analysis)
            self.assertEqual(db_analysis.detection_method, "opencv_traditional_cv")
            self.assertEqual(db_analysis.total_detections, 0)
            # Ensure zero false detections in vehicle_damage_detections
            detections = db.query(VehicleDamageDetection).filter_by(analysis_id=db_analysis.id).all()
            self.assertEqual(len(detections), 0)

        # 3. GET /api/claims/<claim_id>/annotated-image serves the opencv analysis image
        img_res = self.client.get(f"/api/claims/{cid}/annotated-image")
        self.assertEqual(img_res.status_code, 200)
        self.assertEqual(img_res.content_type, "image/jpeg")

        # 4. Generate consolidated PDF and verify OpenCV Fallback layout
        claim_res = self.client.get(f"/api/claims/{cid}")
        pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict=claim_res.get_json()["data"],
            extracted_rows=[],
            upload_root=self.upload_dir,
        )
        import fitz
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            pdf_text = " ".join([page.get_text() for page in doc])
            self.assertIn("OPENCV", pdf_text.upper())
            self.assertIn("FALLBACK", pdf_text.upper())
            self.assertIn("MORPHOLOGICAL", pdf_text.upper())

    # -------------------------------------------------------------
    # 9. Page 5 Dynamic Status & Isolation Verification Tests
    # -------------------------------------------------------------
    def test_pdf_page5_completed_yolov8_analysis(self):
        """Verifies completed YOLOv8 analysis populates Page 5 with live detections, confidence, and latency."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # 1. Run YOLOv8 damage analysis
        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10})
        self.assertEqual(res.status_code, 200)
        da = res.get_json()["analysis"]
        expected_count = da["total_detections"]

        # 2. Retrieve consolidated PDF report
        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            self.assertGreaterEqual(len(doc), 5)
            p5 = doc[4].get_text()
            self.assertIn("Page 5: Vehicle Damage Detection Analysis", p5)
            self.assertIn("Completed", p5)
            self.assertIn("Total Damages Identified", p5)
            self.assertIn(str(expected_count), p5)
            self.assertIn("Peak Confidence", p5)
            self.assertIn("Average Confidence", p5)
            self.assertIn("Inference Latency", p5)
            self.assertIn("Detection Method", p5)
            self.assertNotIn("Automated vehicle damage analysis has not yet been executed", p5)

    def test_pdf_page5_opencv_fallback_analysis(self):
        """Verifies OpenCV fallback analysis populates Page 5 with structural diagnostics and no fake detections."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # 1. Run damage analysis with OpenCV fallback forced
        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"force_opencv": True})
        self.assertEqual(res.status_code, 200)

        # 2. Retrieve consolidated PDF report
        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            p5 = doc[4].get_text()
            p5_clean = " ".join(p5.split())
            self.assertIn("Page 5: Vehicle Damage Detection Analysis", p5_clean)
            self.assertIn("Completed (OpenCV Traditional CV Fallback - Structural Only)", p5_clean)
            self.assertIn("Structural analysis without semantic damage predictions", p5_clean)
            self.assertIn("OpenCV Morphological & Quality Assessment", p5_clean)

    def _clear_claim_damage_analysis(self, claim_id: str):
        """Helper to safely clear damage analysis records and their child detection records."""
        with get_db_session() as db:
            analyses = db.query(VehicleDamageAnalysis).filter_by(claim_id=claim_id).all()
            for a in analyses:
                db.query(VehicleDamageDetection).filter_by(analysis_id=a.id).delete()
                db.delete(a)
            db.commit()

    def test_pdf_page5_no_analysis_displays_pending(self):
        """Verifies Page 5 displays Pending when no analysis has been executed for the claim."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Clear auto-executed analysis to test pre-inference Pending state
        self._clear_claim_damage_analysis(cid)

        # Retrieve consolidated PDF report without executing damage analysis
        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            p5 = doc[4].get_text()
            self.assertIn("Page 5: Vehicle Damage Detection Analysis", p5)
            self.assertIn("Pending", p5)
            self.assertIn("Automated vehicle damage analysis has not yet been executed for this claim", p5)
            self.assertIn("Not analyzed", p5)
            self.assertNotIn("Completed", p5)

    def test_pdf_page5_failed_analysis_displays_failed(self):
        """Verifies Page 5 displays Failed when vehicle damage analysis recorded a failure status."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Insert a failed analysis record directly into DB
        with get_db_session() as db:
            failed_analysis = VehicleDamageAnalysis(
                claim_id=cid,
                model_name="YOLOv8n-CarDD",
                model_version="v1.0",
                detection_method="yolov8_cardd",
                total_detections=0,
                damage_categories="[]",
                highest_confidence=0.0,
                average_confidence=0.0,
                analysis_status="failed",
                processing_time_ms=15.0,
                device="cpu",
            )
            db.add(failed_analysis)
            db.commit()

        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            p5 = doc[4].get_text()
            self.assertIn("Page 5: Vehicle Damage Detection Analysis", p5)
            self.assertIn("Failed", p5)
            self.assertIn("Vehicle damage analysis failed during execution", p5)
            self.assertNotIn("Pending (Automated vehicle damage analysis has not yet been executed", p5)

    def test_pdf_page5_cross_claim_isolation(self):
        """Verifies Page 5 strictly isolates claims and never displays another claim's analysis results."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid_a = self._create_test_claim(real_img)
        cid_b = self._create_test_claim(real_img)

        # Clear Claim B analysis so it has no analysis executed
        self._clear_claim_damage_analysis(cid_b)

        # Run analysis ONLY for Claim A
        res_a = self.client.post(f"/api/claims/{cid_a}/analyze-damage", json={"conf_threshold": 0.10})
        self.assertEqual(res_a.status_code, 200)
        da_a = res_a.get_json()["analysis"]
        self.assertGreater(da_a["total_detections"], 0)

        # Claim B has no analysis executed: PDF for Claim B must display Pending
        pdf_res_b = self.client.get(f"/api/claims/{cid_b}/document-report")
        self.assertEqual(pdf_res_b.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res_b.data, filetype="pdf") as doc:
            p5_b = doc[4].get_text()
            self.assertIn("Pending", p5_b)
            self.assertNotIn("Completed", p5_b)
            self.assertNotIn(f"{da_a['total_detections']} detections", p5_b)

        # Also test direct report generation with a poisoned/cross-claim dictionary
        poisoned_claim_dict = {
            "claim_id": cid_b,
            "damage_analysis": {
                "claim_id": cid_a,
                "total_detections": 999,
                "analysis_status": "completed",
                "damage_categories": ["dent", "scratch"],
            }
        }
        poisoned_pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict=poisoned_claim_dict,
            extracted_rows=[],
            upload_root=self.upload_dir,
        )
        with fitz.open(stream=poisoned_pdf_bytes, filetype="pdf") as doc:
            p5_poisoned = doc[4].get_text()
            # Must reject Claim A's analysis and display Pending for Claim B
            self.assertIn("Pending", p5_poisoned)
            self.assertNotIn("999", p5_poisoned)
            self.assertNotIn("Completed", p5_poisoned)

    def test_pdf_page5_regenerating_pdf_after_inference_updates_page5(self):
        """Verifies generating a PDF before inference shows Pending, and regenerating after inference shows Completed."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Clear initial auto-analysis to test pre-inference Pending state
        self._clear_claim_damage_analysis(cid)

        import fitz

        # 1. First PDF generation before inference: must show Pending
        pdf_res_pre = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res_pre.status_code, 200)
        with fitz.open(stream=pdf_res_pre.data, filetype="pdf") as doc:
            p5_pre = doc[4].get_text()
            self.assertIn("Pending", p5_pre)
            self.assertNotIn("Completed", p5_pre)

        # 2. Run damage inference
        res = self.client.post(f"/api/claims/{cid}/analyze-damage", json={"conf_threshold": 0.10})
        self.assertEqual(res.status_code, 200)
        da = res.get_json()["analysis"]
        total_det = da["total_detections"]

        # 3. Regenerate PDF report: must dynamically update Page 5 to Completed
        pdf_res_post = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res_post.status_code, 200)
        with fitz.open(stream=pdf_res_post.data, filetype="pdf") as doc:
            p5_post = doc[4].get_text()
            self.assertIn("Completed", p5_post)
            self.assertIn(str(total_det), p5_post)
            self.assertNotIn("Automated vehicle damage analysis has not yet been executed", p5_post)

    # -------------------------------------------------------------
    # 10. Automated Lifecycle & Concurrency Verification Tests
    # -------------------------------------------------------------
    def test_auto_execution_on_new_claim_submission(self):
        """Verifies submitting a new claim with valid photo immediately triggers Phase 5 without manual intervention."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # 1. Verify VehicleDamageAnalysis was automatically created in DB on claim submission
        with get_db_session() as db:
            analyses = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).all()
            self.assertEqual(len(analyses), 1, "Exactly one analysis must be created automatically on claim submission.")
            analysis = analyses[0]
            self.assertEqual(analysis.analysis_status, "completed")
            self.assertGreaterEqual(analysis.total_detections, 1)
            self.assertIsNotNone(analysis.annotated_image_path)
            self.assertIsNotNone(analysis.image_hash)

            # Check detection records
            detections = db.query(VehicleDamageDetection).filter_by(analysis_id=analysis.id).all()
            self.assertEqual(len(detections), analysis.total_detections)
            for d in detections:
                self.assertIn(d.category, CARDD_CLASS_NAMES.values())
                self.assertGreater(d.confidence, 0.0)
            total_det = analysis.total_detections

        # 2. Verify Page 5 of consolidated PDF immediately reflects Completed status
        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            p5 = doc[4].get_text()
            self.assertIn("Page 5: Vehicle Damage Detection Analysis", p5)
            self.assertIn("Completed", p5)
            self.assertIn(str(total_det), p5)
            self.assertNotIn("Pending (Automated vehicle damage analysis has not yet been executed", p5)

    def test_auto_execution_skipped_for_synthetic_graphic(self):
        """Verifies new claim with synthetic graphic skips damage detection and PDF Page 5 shows awaiting evidence."""
        synth_img = Image.new("RGB", (900, 600), color=(248, 250, 252))
        synth_path = self.tmp / "test_policy_schedule_graphic.jpg"
        synth_img.save(synth_path, format="JPEG")
        cid = self._create_test_claim(synth_path)

        # 1. Verify no VehicleDamageAnalysis record was created
        with get_db_session() as db:
            analyses = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).all()
            self.assertEqual(len(analyses), 0, "No damage analysis should be created for synthetic graphic.")

        # 2. Verify PDF Page 5 displays Awaiting Valid Vehicle Evidence
        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            p5 = doc[4].get_text()
            self.assertIn("Page 5: Vehicle Damage Detection Analysis", p5)
            self.assertTrue("AWAITING" in p5.upper() or "PENDING" in p5.upper())
            self.assertIn("Not analyzed", p5)
            self.assertNotIn("Completed", p5)

    def test_replacement_photo_auto_triggers_fresh_analysis(self):
        """Verifies uploading replacement photo for a flagged claim automatically executes fresh analysis."""
        # 1. Initial claim with synthetic graphic
        synth_img = Image.new("RGB", (900, 600), color=(248, 250, 252))
        synth_path = self.tmp / "flagged_initial.jpg"
        synth_img.save(synth_path, format="JPEG")
        cid = self._create_test_claim(synth_path)

        with get_db_session() as db:
            self.assertEqual(db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).count(), 0)

        # 2. Upload authentic replacement photo
        real_img_path = self.cardd_dir / "test" / "images" / "000023.jpg"
        with open(real_img_path, "rb") as f:
            real_bytes = f.read()

        rep_res = self.client.post(
            f"/api/claims/{cid}/replace-image",
            data={"vehicle_image": (io.BytesIO(real_bytes), "replacement_car.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(rep_res.status_code, 200)
        rep_data = rep_res.get_json()
        self.assertIsNotNone(rep_data.get("damage_analysis"))

        # 3. Verify analysis was persisted in DB
        with get_db_session() as db:
            analyses = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).all()
            self.assertEqual(len(analyses), 1)
            analysis = analyses[0]
            self.assertEqual(analysis.analysis_status, "completed")
            self.assertGreater(analysis.total_detections, 0)
            total_det = analysis.total_detections

        # 4. Verify PDF report immediately reflects Completed status
        pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
        self.assertEqual(pdf_res.status_code, 200)

        import fitz
        with fitz.open(stream=pdf_res.data, filetype="pdf") as doc:
            p5 = doc[4].get_text()
            self.assertIn("Completed", p5)
            self.assertIn(str(total_det), p5)

    def test_pdf_download_idempotency_no_duplicate_inference(self):
        """Verifies repeated PDF generation does not re-run YOLO or create duplicate database records."""
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Initial analysis count
        with get_db_session() as db:
            initial_count = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).count()
            initial_det_count = db.query(VehicleDamageDetection).count()
            self.assertEqual(initial_count, 1)

        # Download PDF multiple times
        for _ in range(3):
            pdf_res = self.client.get(f"/api/claims/{cid}/document-report")
            self.assertEqual(pdf_res.status_code, 200)

        # Ensure no new records were added
        with get_db_session() as db:
            after_count = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).count()
            after_det_count = db.query(VehicleDamageDetection).count()
            self.assertEqual(initial_count, after_count)
            self.assertEqual(initial_det_count, after_det_count)

    def test_two_new_claims_isolated_auto_execution(self):
        """Verifies two different new claims execute inference independently and never mix results."""
        img1 = self.cardd_dir / "test" / "images" / "000023.jpg"
        img2 = self.cardd_dir / "test" / "images" / "000042.jpg"
        cid1 = self._create_test_claim(img1)
        cid2 = self._create_test_claim(img2)

        with get_db_session() as db:
            da1 = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid1).first()
            da2 = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid2).first()
            self.assertIsNotNone(da1)
            self.assertIsNotNone(da2)
            self.assertNotEqual(da1.id, da2.id)
            self.assertEqual(da1.claim_id, cid1)
            self.assertEqual(da2.claim_id, cid2)
            det1_count = da1.total_detections
            det2_count = da2.total_detections

        # Fetch PDFs for both claims
        import fitz
        pdf1 = self.client.get(f"/api/claims/{cid1}/document-report")
        with fitz.open(stream=pdf1.data, filetype="pdf") as doc:
            p5_1 = doc[4].get_text()
            self.assertIn("Completed", p5_1)
            self.assertIn(str(det1_count), p5_1)

        pdf2 = self.client.get(f"/api/claims/{cid2}/document-report")
        with fitz.open(stream=pdf2.data, filetype="pdf") as doc:
            p5_2 = doc[4].get_text()
            self.assertIn("Completed", p5_2)
            self.assertIn(str(det2_count), p5_2)

    def test_concurrent_claim_damage_detection_thread_safety(self):
        """Verifies thread-locking prevents concurrent duplicate inference on the same claim."""
        import threading
        real_img = self.cardd_dir / "test" / "images" / "000023.jpg"
        cid = self._create_test_claim(real_img)

        # Clear to test concurrency from unanalyzed state
        self._clear_claim_damage_analysis(cid)

        from backend.services.vision import process_claim_damage_detection

        results = []
        errors = []

        def worker():
            try:
                res = process_claim_damage_detection(claim_id=cid, upload_base=self.upload_dir)
                results.append(res)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent workers encountered errors: {errors}")
        self.assertEqual(len(results), 4)

        # Verify only one analysis record exists in DB due to mutex and idempotency
        with get_db_session() as db:
            count = db.query(VehicleDamageAnalysis).filter_by(claim_id=cid).count()
            self.assertEqual(count, 1, "Thread safety must prevent duplicate analysis creation.")

    def test_kcm0_history_and_integrity_preserved(self):
        """Verifies previous claim CLM-20261116-KCM0 records and YOLOv8 detections are preserved in production database."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        prod_db_path = self.repo_root / "data" / "claimsense.db"
        if not prod_db_path.exists():
            prod_db_path = self.repo_root / "backend" / "database" / "claimsense.db"
        if not prod_db_path.exists():
            self.skipTest("Production database not found.")
        prod_engine = create_engine(f"sqlite:///{prod_db_path}")
        ProdSession = sessionmaker(bind=prod_engine)
        with ProdSession() as prod_db:
            try:
                kcm0_claim = prod_db.query(Claim).filter_by(claim_id="CLM-20261116-KCM0").first()
            except Exception:
                self.skipTest("Claims table not available in target database.")
                return
            if not kcm0_claim:
                self.skipTest("Historical claim CLM-20261116-KCM0 not present in database.")
                return
            analyses = prod_db.query(VehicleDamageAnalysis).filter_by(claim_id="CLM-20261116-KCM0").all()
            self.assertGreater(len(analyses), 0)
            latest = sorted(analyses, key=lambda a: a.id)[-1]
            self.assertEqual(latest.analysis_status, "completed")
            self.assertEqual(latest.detection_method, "yolov8_cardd")
            self.assertGreater(latest.total_detections, 0)
            detections = prod_db.query(VehicleDamageDetection).filter_by(analysis_id=latest.id).all()
            self.assertEqual(len(detections), latest.total_detections)


if __name__ == "__main__":
    unittest.main()
