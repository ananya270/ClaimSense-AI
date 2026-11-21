"""Unit and integration regression tests for ClaimSense AI Critical UX & Processing Bug Fixes.

Verifies:
1. Issue 1: Asynchronous processing pipeline execution does not encounter DetachedInstanceError.
2. Model Safety: VehicleDamageAnalysis guarantees non-null default values for max_confidence and related fields.
3. Issue 3: Claimant-submitted narrative is properly preserved and exposed via the claim details endpoint.
"""
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_engine, init_database, close_engine, get_db_session
from backend.database.models import (
    Base,
    User,
    Claim,
    ClaimImage,
    Document,
    ProcessingTask,
    VehicleDamageAnalysis,
)
from backend.services.tasks.claim_tasks import execute_claim_processing_pipeline


class TestCriticalBugFixes(unittest.TestCase):
    """Regression test cases verifying the critical UX and processing bug fixes."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="claimsense_fixes_test_"))
        cls.test_db_path = cls.temp_dir / "test_fixes.db"
        cls.test_uploads_dir = cls.temp_dir / "uploads"
        cls.test_reports_dir = cls.temp_dir / "reports"
        cls.test_backups_dir = cls.temp_dir / "backups"

        cls.test_uploads_dir.mkdir(parents=True, exist_ok=True)
        cls.test_reports_dir.mkdir(parents=True, exist_ok=True)
        cls.test_backups_dir.mkdir(parents=True, exist_ok=True)

        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{cls.test_db_path.as_posix()}"
            UPLOAD_FOLDER = cls.test_uploads_dir
            REPORTS_FOLDER = cls.test_reports_dir
            DATA_FOLDER = cls.temp_dir
            WTF_CSRF_ENABLED = False
            RATELIMIT_ENABLED = False
            SECRET_KEY = "test-secret-key-32chars-minimum-len"

        cls.test_config = TestConfig
        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        close_engine()
        import shutil
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        with get_db_session() as db:
            user = db.query(User).filter_by(id=1).first()
            if not user:
                user = User(
                    id=1,
                    username="test_user_fixes",
                    email="testfixes@example.com",
                    full_name="Test Fixes User",
                    role="claimant",
                    password_hash="pbkdf2:sha256:260000$dummy$hash",
                )
                db.add(user)
                db.commit()

    def test_01_vehicle_damage_analysis_null_confidence_safety(self):
        """Verifies VehicleDamageAnalysis instantiation handles None and missing fields gracefully without IntegrityError."""
        with get_db_session() as db:
            # Create a test claim
            claim_id = "CLM-20261121-TEST"
            claim = Claim(
                claim_id=claim_id,
                user_id=1,
                claimant_name="Jane Doe",
                policy_number="POL-123456",
                vehicle_number="MH12AB1234",
                accident_date="2026-11-20",
                claim_description="A test collision narrative for safety checks.",
                status="SUBMITTED",
            )
            db.add(claim)
            db.commit()

            # Instantiate VehicleDamageAnalysis with max_confidence=None and verify safe default
            analysis = VehicleDamageAnalysis(
                claim_id=claim_id,
                image_path="test/path.jpg",
                highest_confidence=0.0,
                max_confidence=None,
                total_damages_detected=None,
                average_confidence=None,
                inference_time_ms=None,
                processing_time_ms=None,
            )
            self.assertEqual(analysis.max_confidence, 0.0)
            self.assertEqual(analysis.total_damages_detected, 0)
            self.assertEqual(analysis.average_confidence, 0.0)
            self.assertEqual(analysis.inference_time_ms, 0.0)

            # Insert into database to ensure SQLite NOT NULL constraint does not fail
            db.add(analysis)
            db.commit()
            self.assertIsNotNone(analysis.id)

    def test_02_async_pipeline_executes_without_detached_instance_error(self):
        """Verifies execute_claim_processing_pipeline runs without SQLAlchemy DetachedInstanceError."""
        claim_id = "CLM-20261121-PIPE"
        with get_db_session() as db:
            claim = Claim(
                claim_id=claim_id,
                user_id=1,
                claimant_name="Rajesh Sharma",
                policy_number="POL-998877",
                vehicle_number="DL01XY9988",
                accident_date="2026-11-19",
                claim_description="Vehicle hit a stationary pole in the parking lot damaging front bumper.",
                status="SUBMITTED",
            )
            db.add(claim)

            # Create document and image records
            doc = Document(
                claim_id=claim_id,
                document_type="POLICY_DOCUMENT",
                file_path="dummy_policy.pdf",
                original_filename="dummy_policy.pdf",
                stored_filename="dummy_policy.pdf",
                file_extension="pdf",
                file_size=2048,
            )
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT",
                file_path="dummy_image.jpg",
                original_filename="dummy_image.jpg",
                stored_filename="dummy_image.jpg",
                file_extension="jpg",
                file_size=1024,
            )
            task = ProcessingTask(
                task_id="task-test-pipeline-01",
                claim_id=claim_id,
                status="PENDING",
                current_stage="INTAKE",
                progress_percent=0,
            )
            db.add(doc)
            db.add(img)
            db.add(task)
            db.commit()

        # Execute pipeline
        result = execute_claim_processing_pipeline(claim_id=claim_id, task_id="task-test-pipeline-01")
        self.assertTrue(result.get("success"), f"Pipeline execution failed: {result.get('error')}")

        with get_db_session() as db:
            updated_task = db.query(ProcessingTask).filter_by(task_id="task-test-pipeline-01").first()
            self.assertIsNotNone(updated_task)
            self.assertEqual(updated_task.status, "COMPLETED")
            self.assertEqual(updated_task.progress_percent, 100)

    def test_03_claimant_narrative_visibility_endpoint(self):
        """Verifies GET /api/claims/<claim_id> returns the full claimant-submitted narrative."""
        claim_id = "CLM-20261121-NARR"
        expected_narrative = "While driving down Main Street at 40km/h, a reversing vehicle struck the rear left fender."
        with get_db_session() as db:
            claim = Claim(
                claim_id=claim_id,
                user_id=1,
                claimant_name="Amit Patel",
                policy_number="POL-334455",
                vehicle_number="KA03AB4455",
                accident_date="2026-11-18",
                claim_description=expected_narrative,
                status="SUBMITTED",
            )
            db.add(claim)
            db.commit()

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "claimant"

        res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        claim_data = data.get("data", {})
        self.assertEqual(claim_data.get("claim_description"), expected_narrative)


if __name__ == "__main__":
    unittest.main()
