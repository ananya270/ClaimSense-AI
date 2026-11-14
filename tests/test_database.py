"""Unit tests for Phase 3 SQLite database schema, persistence, and legacy migration."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import inspect

from backend.database.db import (
    init_database,
    get_db_session,
    migrate_existing_claims_from_disk,
)
from backend.database.models import (
    User,
    Claim,
    Document,
    ClaimImage,
    ExtractedInformation,
    ImageAnalysis,
    VerificationResult,
    RiskAssessment,
    Report,
)


class DatabaseArchitectureTestCase(unittest.TestCase):
    """Verifies relational database tables, constraints, foreign keys, and migration."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_claimsense.db"
        self.db_uri = f"sqlite:///{self.db_path.as_posix()}"
        self.engine = init_database(self.db_uri)

    def tearDown(self):
        from backend.database.db import close_engine
        close_engine()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_schema_tables_exist(self):
        """Verifies that all Phase 3 required and future-ready tables are created."""
        inspector = inspect(self.engine)
        table_names = set(inspector.get_table_names())

        required_tables = {
            "users",
            "claims",
            "documents",
            "claim_images",
            "extracted_information",
            "image_analysis",
            "verification_results",
            "risk_assessments",
            "reports",
        }
        for table in required_tables:
            self.assertIn(table, table_names, f"Table '{table}' must exist in SQLite database.")

    def test_user_creation_and_password_hashing(self):
        """Ensures users persist correctly and passwords are encrypted, never stored in plain text."""
        with get_db_session() as db:
            user = User(
                username="anshg",
                email="ansh@example.com",
                full_name="Ansh Gupta",
                role="user",
            )
            raw_password = "SecurePassword123"
            user.set_password(raw_password)
            db.add(user)
            db.flush()
            user_id = user.id

        with get_db_session() as db:
            saved_user = db.query(User).filter_by(id=user_id).first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.username, "anshg")
            self.assertNotEqual(saved_user.password_hash, raw_password)
            self.assertTrue(saved_user.check_password(raw_password))
            self.assertFalse(saved_user.check_password("WrongPassword"))
            # Ensure serialization does not leak password
            user_dict = saved_user.to_dict()
            self.assertNotIn("password_hash", user_dict)
            self.assertNotIn("password", user_dict)

    def test_claim_persistence_and_relationships(self):
        """Ensures claims, documents, and images persist and honor foreign key cascades."""
        claim_id = "CLM-20261009-TEST"

        with get_db_session() as db:
            user = User(
                username="ankity",
                email="ankit@example.com",
                full_name="Ankit Yadav",
            )
            user.set_password("pass123")
            db.add(user)
            db.flush()

            claim = Claim(
                claim_id=claim_id,
                user_id=user.id,
                claimant_name="Ankit Yadav",
                policy_number="POL-2026-XYZ",
                vehicle_number="UP-14-AA-1111",
                accident_date="2026-09-10",
                claim_description="Side collision test claim.",
                status="SUBMITTED",
            )
            db.add(claim)
            db.flush()

            doc = Document(
                claim_id=claim_id,
                document_type="POLICY_DOCUMENT",
                file_path=f"{claim_id}/documents/policy.pdf",
                original_filename="policy.pdf",
                stored_filename="policy_doc.pdf",
                file_extension="pdf",
                file_size=2048,
            )
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT",
                file_path=f"{claim_id}/images/car.jpg",
                original_filename="car.jpg",
                stored_filename="vehicle_car.jpg",
                file_extension="jpg",
                file_size=4096,
            )
            db.add(doc)
            db.add(img)

        # Verify retrieval and relationships
        with get_db_session() as db:
            retrieved = db.query(Claim).filter_by(claim_id=claim_id).first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.policy_number, "POL-2026-XYZ")
            self.assertEqual(len(retrieved.documents), 1)
            self.assertEqual(len(retrieved.images), 1)
            self.assertEqual(retrieved.documents[0].document_type, "POLICY_DOCUMENT")
            self.assertEqual(retrieved.images[0].original_filename, "car.jpg")
            self.assertEqual(retrieved.user.username, "ankity")

            # Check to_dict format
            data = retrieved.to_dict(include_evidence=True)
            self.assertEqual(data["claim_id"], claim_id)
            self.assertIn("files", data)
            self.assertIn("policy_document", data["files"])
            self.assertIn("vehicle_image", data["files"])

    def test_legacy_metadata_migration(self):
        """Verifies that legacy metadata.json on disk is safely migrated to SQLite."""
        upload_dir = Path(self.temp_dir.name) / "uploads"
        legacy_claim_id = "CLM-20261008-LEGACY"
        legacy_claim_dir = upload_dir / legacy_claim_id
        legacy_claim_dir.mkdir(parents=True)

        metadata_content = {
            "claim_id": legacy_claim_id,
            "claimant_name": "Legacy Claimant",
            "policy_number": "POL-LEGACY-001",
            "vehicle_number": "DL-05-ZZ-9999",
            "accident_date": "2026-08-01",
            "claim_description": "Legacy claim migrated from Phase 2.",
            "status": "SUBMITTED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": {
                "policy_document": {
                    "original_name": "policy.pdf",
                    "saved_as": "policy_policy.pdf",
                    "relative_path": f"{legacy_claim_id}/documents/policy_policy.pdf",
                    "size_bytes": 1024,
                },
                "vehicle_image": {
                    "original_name": "vehicle.png",
                    "saved_as": "vehicle_image_vehicle.png",
                    "relative_path": f"{legacy_claim_id}/images/vehicle_image_vehicle.png",
                    "size_bytes": 2048,
                },
            },
        }

        with open(legacy_claim_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata_content, f)

        # Run migration
        migrated = migrate_existing_claims_from_disk(upload_dir)
        self.assertEqual(migrated, 1)

        # Verify record exists in SQLite
        with get_db_session() as db:
            claim = db.query(Claim).filter_by(claim_id=legacy_claim_id).first()
            self.assertIsNotNone(claim)
            self.assertEqual(claim.claimant_name, "Legacy Claimant")
            self.assertEqual(claim.policy_number, "POL-LEGACY-001")
            self.assertEqual(len(claim.documents), 1)
            self.assertEqual(len(claim.images), 1)


if __name__ == "__main__":
    unittest.main()
